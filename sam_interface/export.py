import os
import shutil
import time

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
        segment_manager: sam_interface.segment_manager.SegmentManager, export_path: str, export_name: str,
        save_mask_tree: bool = True, save_vector_tree: bool = True, save_raster: bool = True,
        save_centroids: bool = True, save_detail_mask_tree: bool = True, save_detail_vector_tree: bool = True,
        save_detail_raster: bool = True, min_area: int = 5, tolerance: float = 0.05
):
    export_path = os.path.join(export_path, export_name)

    if not os.path.isdir(export_path):
        os.makedirs(export_path)

    mask_tree = to_mask_node(segment_manager)

    if save_mask_tree:
        logging.info("Saving mask tree...")
        mask_tree.save(os.path.join(export_path, "{}_mask_tree.dat".format(export_name)))

    height, width, _ = segment_manager.image.shape

    polygon_tree = mask_tree.to_vector_node()
    polygon_tree.exterior = np.array([
        [0, 0], [0, width], [height, width], [height, 0]
    ])

    if save_vector_tree:
        logging.info("Saving polygon tree...")
        polygon_tree.save(os.path.join(export_path, "{}_polygon_tree.dat".format(export_name)))

    if save_raster:
        logging.info("Saving polygon raster...")
        polygon_tree.to_raster(os.path.join(export_path, "{}_polygon_raster.png".format(export_name)))

    if save_centroids:
        logging.info("Saving polygon centroids...")
        centroids: np.ndarray = np.array([c.get_centroid() for c in polygon_tree.children])
        np.save(os.path.join(export_path, "{}_centroid_coordinates.npy".format(export_name)), centroids)

    if save_detail_vector_tree or save_detail_mask_tree or save_detail_raster:
        logging.info("Sub-segmenting to get detail...")
        get_detail.get_detail(
            segment_manager.image / 255, mask_tree,
            segmentation.FloodFillSegmentation(min_area, tolerance, silent=True)
        )

        if save_detail_mask_tree:
            logging.info("Saving detailed mask tree...")
            mask_tree.save(os.path.join(export_path, "{}_mask_tree_detailed.dat".format(export_name)))

        height, width, _ = segment_manager.image.shape

        polygon_tree = mask_tree.to_vector_node()
        polygon_tree.exterior = np.array([
            [0, 0], [0, width], [height, width], [height, 0]
        ])

        if save_detail_vector_tree:
            logging.info("Saving detailed polygon tree...")
            polygon_tree.save(os.path.join(export_path, "{}_polygon_tree_detailed.dat".format(export_name)))

        if save_detail_raster:
            logging.info("Saving detailed polygon raster...")
            polygon_tree.to_raster(os.path.join(export_path, "{}_polygon_raster_detailed.png".format(export_name)))

    logging.info("Copying original image to export directory...")
    _, file_ext = os.path.splitext(segment_manager.image_path)
    shutil.copy(segment_manager.image_path, os.path.join(export_path, "{}{}".format(export_name, file_ext)))

    logging.info("Export complete")
