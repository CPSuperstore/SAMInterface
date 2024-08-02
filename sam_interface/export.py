import numpy as np

import sam_interface.segment_manager


def to_flat_image(segment_manager: sam_interface.segment_manager.SegmentManager) -> np.ndarray:
    result = np.zeros_like(segment_manager.image)

    for mask in segment_manager.masks:
        result[mask.T] = np.median(segment_manager.image[mask.T], axis=0)

    return result
