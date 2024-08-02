import abc
import math
import typing

import numpy as np
import scipy.ndimage as ndimage


def color_stretch(image, mask=None, max_value: float = 1, sigmoid_const: float = 10):
    if mask is None:
        mask = np.ones_like(image).astype(bool)

    if len(image[mask]) == 0:
        return None

    if image[mask].min() == image[mask].max():
        return image.copy()

    amplified = (image - image[mask].min()) * (max_value / (image[mask].max() - image[mask].min()))
    amplified[np.logical_not(mask)] = 0

    if sigmoid_const is not None and sigmoid_const >= 0:
        amplified = 1 / (1 + math.e ** (-sigmoid_const * amplified + (sigmoid_const / 2)))

    return amplified


class BaseSegmentation(abc.ABC):
    def __init__(self, min_area: int, silent: bool = False):
        super().__init__()
        self.min_area = min_area
        self.silent = silent

    def segment(self, image: np.ndarray, mask: np.ndarray = None) -> typing.List[np.ndarray]:
        image = color_stretch(image, mask)
        return self._segment(image, mask)

    def segment_with_remainder(
            self, image: np.ndarray, mask: np.ndarray = None, offset: int = 5
    ) -> typing.Tuple[typing.List[np.ndarray], np.ndarray]:

        segments = self.segment(image, mask)
        remainder = np.ones(image.shape[:2], dtype=bool)

        valid_segments = []
        for segment in segments:
            if segment[:, :offset + 1].sum() > 0 and segment[:, -offset + 1:].sum() > 0:
                remainder = np.logical_or(remainder, segment)
                continue

            if segment[:offset + 1].sum() > 0 and segment[-offset + 1:].sum() > 0:
                remainder = np.logical_or(remainder, segment)
                continue

            if segment.sum() < self.min_area:
                remainder = np.logical_or(remainder, segment)
                continue

            valid_segments.append(ndimage.binary_fill_holes(segment))

        accepted = []
        for i, outer in enumerate(valid_segments):
            area = outer.sum()

            for j, inner in enumerate(valid_segments):
                if i == j:
                    continue

                if np.logical_and(outer, inner).sum() == area:
                    break

            else:
                accepted.append(outer)

        return accepted, remainder

    @abc.abstractmethod
    def _segment(self, image: np.ndarray, mask: np.ndarray = None):
        pass
