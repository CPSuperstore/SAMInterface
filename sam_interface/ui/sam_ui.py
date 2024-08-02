import tkinter as tk

import numpy as np
import pygame

import sam_interface.segment_manager
import sam_interface.ui.base_interface as base_interface
import sam_interface.ui.widget.pygame_widget as pygame_widget

pygame.init()


class SAMWidget(pygame_widget.PygameWidget):

    def __init__(
            self, segment_manager: sam_interface.segment_manager.SegmentManager,
            parent, screen_size: tuple, framerate_cap: int = 60
    ):
        super().__init__(parent, screen_size, framerate_cap)
        self.segment_manager = segment_manager
        self.image = pygame.image.load(segment_manager.image_path).convert()

        self.real_image_size = np.array(self.image.get_size())
        self.scale_factor = 1
        self.display_image_pos = np.array([0, 0])

        self.center_image()

    def center_image(self):
        width, height = self.image.get_size()

        width_ratio = self.screen_width / width
        height_ratio = self.screen_height / height
        self.scale_factor = min(width_ratio, height_ratio)

        new_width = width * self.scale_factor
        new_height = height * self.scale_factor

        self.image = pygame.transform.scale(self.image, (new_width, new_height))
        self.display_image_pos = np.array((
            int((self.screen_width / 2) - (new_width / 2)),
            int((self.screen_height / 2) - (new_height / 2))
        ))

    def render(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                click_pos = event.pos
                image_pos = (
                    (click_pos[0] - self.display_image_pos[0]) / self.scale_factor,
                    (click_pos[1] - self.display_image_pos[1]) / self.scale_factor
                )
                if (
                        image_pos[0] < 0 or image_pos[1] < 0 or
                        image_pos[0] > self.real_image_size[0] or
                        image_pos[1] > self.real_image_size[1]
                ):
                    continue

                print(image_pos)

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.image, self.display_image_pos)
        pygame.display.update()


class SAMInterface(base_interface.BaseInterface):
    def __init__(self, segment_manager: sam_interface.segment_manager.SegmentManager):
        super().__init__((800, 500))

        self.sam_widget = SAMWidget(segment_manager, self, (800, 450))
        self.sam_widget.pack()

        self.segment_manager = segment_manager

        tk.Button(self, text="Preview", command=self.preview_segmentation).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(self, text="Export As...", command=self.export_segmentation).pack(side=tk.LEFT, padx=10, pady=10)

    def preview_segmentation(self):
        pass

    def export_segmentation(self):
        pass
