import numpy as np
import scipy.ndimage as ndimage

import segmentation.base_segmentation as base_segmentation


class FloodFillSegmentation(base_segmentation.BaseSegmentation):
    def __init__(self, min_area: int, tolerance: float, silent: bool = False):
        super().__init__(min_area, silent=silent)
        self.tolerance = tolerance

    def flood(self, image: np.ndarray, mask: np.ndarray, seed):
        iteration = 0

        accepted_mask: np.ndarray = np.zeros(mask.shape, dtype=np.bool_)
        initial_color: np.ndarray = image[seed]
        accepted_mask[*seed] = True

        mask = mask.copy()

        while True:
            iteration += 1

            dilated = ndimage.binary_dilation(accepted_mask, iterations=2, mask=mask)
            frontier = np.logical_and(dilated, np.logical_not(accepted_mask))

            if frontier.sum() == 0:
                break

            coordinates = np.where(frontier == 1)
            distance = np.linalg.norm(np.subtract(image[coordinates], initial_color), axis=1)

            accepted_coordinates = np.where(distance < self.tolerance)[0]
            rejected_coordinates = np.where(distance >= self.tolerance)[0]

            if len(accepted_coordinates) == 0:
                break

            np_coordinates = np.array(coordinates)

            for c in np_coordinates.T[accepted_coordinates]:
                accepted_mask[*c] = 1

            for c in np_coordinates.T[rejected_coordinates]:
                mask[*c] = 0

        return accepted_mask

    def _segment(self, image: np.ndarray, mask: np.ndarray = None):
        masks = []

        if mask is None:
            mask = np.ones(image.shape[:2], dtype=bool)

        remaining_mask = mask.copy()

        while True:
            candidate_seeds = np.where(remaining_mask == 1)

            if len(candidate_seeds[0]) == 0:
                break

            seed = (candidate_seeds[0][0], candidate_seeds[1][0])
            fill_mask = self.flood(image, remaining_mask, seed)

            remaining_mask = np.logical_and(remaining_mask, np.logical_not(fill_mask))
            masks.append(fill_mask)

        return masks
