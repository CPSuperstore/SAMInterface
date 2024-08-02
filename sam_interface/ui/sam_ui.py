import os.path

import customtkinter
import numpy as np
import pygame
from PIL import Image, ImageOps
from customtkinter import filedialog
import tkinter.messagebox as messagebox

import sam_interface.export as export
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

        self.polygon_overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)

        self.real_image_size = np.array(self.image.get_size())
        self.scale_factor = 1
        self.display_image_pos = np.array([0, 0])

        self.center_image()
        self.update_polygon_list()

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

    def update_polygon_list(self):
        self.polygon_overlay.fill((255, 255, 255, 0))

        for points in self.segment_manager.mask_outlines:
            points = points * self.scale_factor + self.display_image_pos
            pygame.draw.polygon(self.polygon_overlay, (255, 0, 255, 64), points)

        for points in self.segment_manager.mask_outlines:
            points = points * self.scale_factor + self.display_image_pos
            pygame.draw.lines(self.polygon_overlay, (0, 255, 255), True, points, 1)

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

                if event.button == pygame.BUTTON_LEFT:
                    self.segment_manager.add_point(image_pos)

                if event.button == pygame.BUTTON_RIGHT:
                    self.segment_manager.remove_point(image_pos)

                self.update_polygon_list()

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.image, self.display_image_pos)
        self.screen.blit(self.polygon_overlay, (0, 0))

        pygame.display.update()


class SAMInterface(base_interface.BaseInterface):
    def __init__(self, segment_manager: sam_interface.segment_manager.SegmentManager):
        super().__init__((800, 500))

        self.sam_widget = SAMWidget(segment_manager, self, (800, 450))
        self.sam_widget.pack()

        self.segment_manager = segment_manager

        customtkinter.CTkButton(
            self, text="Preview", command=self.preview_segmentation
        ).pack(side=customtkinter.LEFT, padx=10, pady=10)

        customtkinter.CTkButton(
            self, text="Export Segmentation", command=self.export_segmentation
        ).pack(side=customtkinter.LEFT, padx=10, pady=10)

        customtkinter.CTkButton(
            self, text="Main Menu", command=self.close
        ).pack(side=customtkinter.RIGHT, padx=10, pady=10)

    def preview_segmentation(self):
        window = customtkinter.CTkToplevel(self)
        window.resizable(False, False)

        image = export.to_flat_image(self.segment_manager)
        image = ImageOps.contain(Image.fromarray(image), (500, 500))
        img = customtkinter.CTkImage(light_image=image, dark_image=image, size=(500, 500))

        panel = customtkinter.CTkLabel(window, image=img, text="")
        panel.pack(side="bottom", fill="both", expand=True)

        window.transient(self)
        window.grab_set()
        self.wait_window(window)

    def export_segmentation(self):
        def select_save_directory():
            filename = filedialog.askdirectory()

            if filename == "":
                return

            export_path.set(filename)

        def begin_export():
            path = export_path.get()

            if path == "":
                messagebox.showerror("Validation Error", "You must select an export path to proceed!")
                return

            if not os.path.isdir(path):
                messagebox.showerror(
                    "Validation Error",
                    "The provided export path '{}' does not point to an existing directory!".format(path)
                )
                return

            export.full_export(
                self.segment_manager, path,
                mask_tree.get(), vector_tree.get(), save_raster.get(), save_centroids.get(), export_detail.get(),
            )

            messagebox.showinfo(
                "Export Succeeded",
                "Successfully exported all files to '{}'!".format(path)
            )

        window = customtkinter.CTkToplevel(self)
        window.resizable(False, False)
        window.geometry("500x290")

        config = dict(sticky='EW', pady=5, padx=10, columnspan=2)

        customtkinter.CTkLabel(window, text="Export Segmentation").grid(row=0, column=0, **config)

        mask_tree = customtkinter.IntVar(value=1)
        vector_tree = customtkinter.IntVar(value=1)
        save_raster = customtkinter.IntVar(value=1)
        save_centroids = customtkinter.IntVar(value=1)
        export_detail = customtkinter.IntVar(value=1)

        export_path = customtkinter.StringVar()

        customtkinter.CTkCheckBox(
            window, text='Export Mask Tree', variable=mask_tree
        ).grid(row=1, column=0, **config)

        customtkinter.CTkCheckBox(
            window, text='Export Vector Tree', variable=vector_tree
        ).grid(row=2, column=0, **config)

        customtkinter.CTkCheckBox(
            window, text='Export Raster', variable=save_raster
        ).grid(row=3, column=0, **config)

        customtkinter.CTkCheckBox(
            window, text='Export Polygon Centroids', variable=save_centroids
        ).grid(row=4, column=0, **config)

        customtkinter.CTkCheckBox(
            window, text='Extract Polygon Detail', variable=export_detail
        ).grid(row=5, column=0, **config)

        customtkinter.CTkButton(
            window, text='Browse', command=select_save_directory
        ).grid(row=6, column=0, sticky='EW', pady=5, padx=10)

        export_path_textbox = customtkinter.CTkEntry(window, textvariable=export_path)
        export_path_textbox.grid(row=6, column=1, sticky='EW', pady=5, padx=10)

        customtkinter.CTkButton(
            window, text="Export", command=begin_export
        ).grid(row=7, column=0, **config)

        # export_path_textbox.in

        window.grid_columnconfigure(0, weight=1)
        window.grid_columnconfigure(1, weight=6)
        window.transient(self)
        window.grab_set()
        self.wait_window(window)
