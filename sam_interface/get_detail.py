import numpy as np
import tqdm

import vector_node
import segmentation


def get_detail(image: np.ndarray, parent: vector_node.MaskNode, segmentation_method: segmentation.BaseSegmentation):
    for child in tqdm.tqdm(parent.children):
        remaining_mask = child.mask.copy()

        children, _ = segmentation_method.segment_with_remainder(image, child.mask)

        for c in children:
            child.children.append(vector_node.MaskNode(c, color=np.median(image[c], axis=0)))
            remaining_mask = np.logical_and(remaining_mask, np.logical_not(c))

        if remaining_mask.sum() > 0:
            child.color = np.median(image[remaining_mask], axis=0)
