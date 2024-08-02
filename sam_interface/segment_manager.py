import os.path
import pickle
import typing

import numpy as np
import pygame
import shapely
import torch
import logging
from segment_anything import SamPredictor, sam_model_registry, SamAutomaticMaskGenerator
from scipy.ndimage import label

import cv2


class SegmentManager:
    def __init__(
            self, image_path: str, checkpoint_key: str = "default",
            checkpoint_path: str = "checkpoints/sam_vit_h_4b8939.pth"
    ):
        self.checkpoint_key = checkpoint_key
        self.checkpoint_path = checkpoint_path
        self.image_path = image_path

        self.masks = []
        self.mask_outlines = []

        logging.info("Reading image '{}' into memory...".format(os.path.abspath(self.image_path)))
        self.image = cv2.imread(self.image_path)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        logging.info("Detecting if CUDA is installed...")
        if torch.cuda.is_available():
            logging.info("CUDA detected. Using GPU {}.".format(torch.cuda.get_device_name(torch.cuda.current_device())))
            self.device = "cuda"

        else:
            logging.warning("CUDA not enabled! Using CPU instead. This will result in longer processing times.")
            self.device = "cpu"

        logging.info("Loading SAM model from checkpoint '{}'...".format(os.path.abspath(checkpoint_path)))
        self.sam = self.get_sam()

        logging.info("Automatically detecting segments...")
        self.auto_detect_masks()

        self.sam.to(device=self.device)

        logging.info("Loading image into SAM predictor...")
        self.predictor = SamPredictor(self.sam)
        self.predictor.set_image(self.image)

    def get_sam(self):
        return sam_model_registry[self.checkpoint_key](checkpoint=self.checkpoint_path)

    @classmethod
    def load(cls, path: str) -> typing.Self:
        with open(path, 'rb') as f:
            return pickle.loads(f.read())

    def save(self, path: str):
        with open(path, 'wb') as f:
            f.write(pickle.dumps(self))

    def auto_detect_masks(self):
        mask_generator = SamAutomaticMaskGenerator(self.sam)
        masks = mask_generator.generate(self.image)

        for mask in masks:
            self.add_mask(mask["segmentation"])

    def add_mask(self, mask: np.ndarray) -> bool:
        mask = mask.T

        if (mask[:5, :].sum() > 1 and mask[-5:, :].sum() > 1) or (mask[:, :5].sum() > 1 and mask[:, -5:].sum() > 1):
            return False

        for other in self.masks:
            mask = np.logical_and(mask, np.logical_not(other))

        if np.sum(mask) < 10:
            return False

        surf = pygame.pixelcopy.make_surface(mask.astype(int) * 255)
        surf.set_colorkey((0, 0, 0))

        pg_mask = pygame.mask.from_surface(surf)
        outline = pg_mask.outline()

        if len(outline) < 4:
            return False

        polygon = shapely.Polygon(outline)

        if polygon.area < 10:
            return False

        self.masks.append(mask)
        self.mask_outlines.append(np.array(outline))

        return True

    def add_point(self, point):
        masks, scores, _ = self.predictor.predict(
            point_coords=np.array([point]),
            point_labels=np.array([1]),
            multimask_output=True,
        )

        labeled_mask, features = label(masks[np.argmax(scores)])
        for feature in np.unique(labeled_mask):
            if feature == 0:
                continue

            self.add_mask(labeled_mask == feature)

    def remove_point(self, point):
        removal = []
        for i, mask in enumerate(self.masks):
            surf = pygame.pixelcopy.make_surface(mask.astype(int) * 255)
            surf.set_colorkey((0, 0, 0))

            mask = pygame.mask.from_surface(surf)

            if mask.get_at(point):
                removal.append(i)

        removal.reverse()

        for i in removal:
            del self.masks[i]
            del self.mask_outlines[i]
