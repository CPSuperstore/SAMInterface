import os

import numpy as np

import sam_interface.segment_manager
import vector_node
import sam_interface.get_detail as get_detail
import segmentation
import logging


def to_flat_image(segment_manager: sam_interface.segment_manager.SegmentManager) -> np.ndarray:
    logging.info("Generating flat image...")
    result = np.zeros_like(segment_manager.image)

    for mask in segment_manager.masks:
        result[mask.T] = np.median(segment_manager.image[mask.T], axis=0)

    logging.info("Flat image ready")
    return result


def to_mask_node(segment_manager: sam_interface.segment_manager.SegmentManager) -> vector_node.MaskNode:
    parent = vector_node.MaskNode(np.ones(segment_manager.image.shape[:2]).astype(bool), level=0)
    parent.filled_mask = np.ones(segment_manager.image.shape[:2]).astype(bool)

    for mask in segment_manager.masks:
        parent.mask = parent.difference(mask.T)

        node = vector_node.MaskNode(mask.T, color=segment_manager.image[mask.T].mean(axis=0) / 255, level=1)
        parent.add_child(node)

    parent.color = segment_manager.image[parent.mask].mean(axis=0) / 255
    return parent


def full_export(
        segment_manager: sam_interface.segment_manager.SegmentManager, export_path: str,
        save_mask_tree: bool = True, save_vector_tree: bool = True, save_raster: bool = True,
        save_centroids: bool = True, export_detail: bool = True
):
    def export_process(mt: vector_node.MaskNode, detailed: bool = False):
        suffix = "_detailed" if detailed else ""
        logging_suffix = " detailed" if detailed else ""

        if save_mask_tree:
            logging.info("Saving{} mask tree...".format(logging_suffix))
            mt.save(os.path.join(export_path, "mask_tree{}.dat".format(suffix)))

        height, width, _ = segment_manager.image.shape

        polygon_tree = mt.to_vector_node()
        polygon_tree.exterior = np.array([
            [0, 0], [0, width], [height, width], [height, 0]
        ])

        if save_vector_tree:
            logging.info("Saving{} polygon tree...".format(logging_suffix))
            polygon_tree.save(os.path.join(export_path, "polygon_tree{}.dat".format(suffix)))

        if save_raster:
            logging.info("Saving{} polygon raster...".format(logging_suffix))
            polygon_tree.to_raster(os.path.join(export_path, "polygon_raster{}.png".format(suffix)))

        if save_centroids and not detailed:
            logging.info("Saving polygon centroids...")
            centroids: np.ndarray = np.array([c.get_centroid() for c in polygon_tree.children])
            np.save(os.path.join(export_path, "centroid_coordinates.npy"), centroids)

    mask_tree = to_mask_node(segment_manager)
    export_process(mask_tree)

    if export_detail:
        logging.info("Sub-segmenting to get detail...")
        get_detail.get_detail(segment_manager.image / 255, mask_tree, segmentation.FloodFillSegmentation(5, 0.05, silent=True))
        export_process(mask_tree, True)

    logging.info("Export complete")
