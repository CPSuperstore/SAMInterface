import logging
import os.path
import threading
import tkinter.messagebox as messagebox
import traceback

import customtkinter
import numpy as np
import pygame
from PIL import Image, ImageOps
from customtkinter import filedialog

import sam_interface.export as export
import sam_interface.preferences as preferences
import sam_interface.segment_manager
import sam_interface.ui.base_interface as base_interface
import sam_interface.ui.base_top_level as base_top_level
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


class ExportInterface(base_top_level.BaseTopLevel):
    def __init__(self, segment_manager, master=None):
        super().__init__(master, (500, 575), "Segmentation Exporter")

        config = dict(sticky='EW', pady=5, padx=10, columnspan=3)

        customtkinter.CTkLabel(self, text="Export Segmentation").grid(row=0, column=0, **config)

        self.mask_tree_variable = customtkinter.IntVar(value=1)
        self.vector_tree_variable = customtkinter.IntVar(value=1)
        self.save_raster_variable = customtkinter.IntVar(value=1)
        self.save_centroids_variable = customtkinter.IntVar(value=1)
        self.detail_mask_tree_variable = customtkinter.IntVar(value=1)
        self.detail_polygon_tree_variable = customtkinter.IntVar(value=1)
        self.detail_raster_variable = customtkinter.IntVar(value=1)
        self.min_size_variable = customtkinter.IntVar(value=5)
        self.threshold_variable = customtkinter.DoubleVar(value=0.05)
        self.segment_manager = segment_manager

        self.export_path_variable = customtkinter.StringVar()
        self.export_name_variable = customtkinter.StringVar(
            value=os.path.splitext(os.path.basename(self.segment_manager.image_path))[0]
        )

        prefs = preferences.get_preferences()
        self.export_path_variable.set("" if prefs["last_export_dir"] is None else prefs["last_export_dir"])

        customtkinter.CTkCheckBox(
            self, text='Export Mask Tree', variable=self.mask_tree_variable
        ).grid(row=1, column=0, **config)

        customtkinter.CTkCheckBox(
            self, text='Export Vector Tree', variable=self.vector_tree_variable
        ).grid(row=2, column=0, **config)

        customtkinter.CTkCheckBox(
            self, text='Export Raster', variable=self.save_raster_variable
        ).grid(row=3, column=0, **config)

        customtkinter.CTkCheckBox(
            self, text='Export Polygon Centroids', variable=self.save_centroids_variable
        ).grid(row=4, column=0, **config)

        customtkinter.CTkCheckBox(
            self, text='Export Detailed Mask Tree', variable=self.detail_mask_tree_variable
        ).grid(row=5, column=0, **config)

        customtkinter.CTkCheckBox(
            self, text='Export Detailed Polygon Tree', variable=self.detail_polygon_tree_variable
        ).grid(row=6, column=0, **config)

        customtkinter.CTkCheckBox(
            self, text='Export Detailed Raster', variable=self.detail_raster_variable
        ).grid(row=7, column=0, **config)

        customtkinter.CTkButton(
            self, text='Browse', command=self.select_save_directory
        ).grid(row=8, column=0, sticky='EW', pady=5, padx=10)

        export_path_textbox = customtkinter.CTkEntry(self, textvariable=self.export_path_variable)
        export_path_textbox.grid(row=8, column=1, sticky='EW', pady=5, padx=1)

        export_name_textbox = customtkinter.CTkEntry(self, textvariable=self.export_name_variable)
        export_name_textbox.grid(row=8, column=2, sticky='EW', pady=5, padx=10)

        customtkinter.CTkLabel(self, text="Flood Fill Settings (Polygon Detail Only)").grid(row=9, column=0, **config)

        self.min_area_label = customtkinter.CTkLabel(self, text="Loading...")
        self.min_area_label.grid(row=10, column=0)

        customtkinter.CTkSlider(
            self, from_=0, to=100, number_of_steps=100, variable=self.min_size_variable,
            command=self.update_min_area_label
        ).grid(row=10, column=1, columnspan=2, sticky='EW', pady=5, padx=10)

        self.threshold_label = customtkinter.CTkLabel(self, text="Loading...")
        self.threshold_label.grid(row=11, column=0)

        customtkinter.CTkSlider(
            self, from_=0, to=1, variable=self.threshold_variable,
            command=self.update_threshold
        ).grid(row=11, column=1, columnspan=2, sticky='EW', pady=5, padx=10)

        customtkinter.CTkLabel(
            self, text="A higher threshold will result in less segments\n0% will include exact colors only"
        ).grid(row=12, column=0, columnspan=3, sticky='EW', pady=0, padx=10)

        customtkinter.CTkButton(
            self, text="Export", command=self.begin_export
        ).grid(row=13, column=0, **config)

        self.grid_columnconfigure(0, weight=2, uniform="Silent_Creme")
        self.grid_columnconfigure(1, weight=5, uniform="Silent_Creme")
        self.grid_columnconfigure(2, weight=3, uniform="Silent_Creme")

        self.update_min_area_label()
        self.update_threshold()

        self.export_error = False

    def update_min_area_label(self, *_):
        self.min_area_label.configure(text="Min Area ({})".format(int(self.min_size_variable.get())))

    def update_threshold(self, *_):
        self.threshold_label.configure(text="Threshold ({}%)".format(int(self.threshold_variable.get() * 100)))

    def select_save_directory(self):
        prefs = preferences.get_preferences()

        filename = filedialog.askdirectory(
            title='Select a directory to export files to',
            initialdir=prefs["last_export_dir"]
        )

        if filename == "":
            return

        prefs["last_export_dir"] = filename
        preferences.save_preferences(prefs)

        self.export_path_variable.set(filename)

    def begin_export(self):
        path = self.export_path_variable.get()
        name = self.export_name_variable.get()

        if path == "":
            messagebox.showerror("Validation Error", "You must select an export path to proceed!")
            return

        if name == "":
            messagebox.showerror("Validation Error", "You must select an export path to proceed!")
            return

        if not os.path.isdir(path):
            messagebox.showerror(
                "Validation Error",
                "The provided export path '{}' does not point to an existing directory!".format(path)
            )
            return

        loading_window = self.get_loading_window(self, cancel_button=True)

        loading_thread = threading.Thread(
            target=self.export, args=[
                path, name, loading_window,
                self.mask_tree_variable.get(), self.vector_tree_variable.get(), self.save_raster_variable.get(),
                self.save_centroids_variable.get(),
                self.detail_mask_tree_variable.get(),
                self.detail_polygon_tree_variable.get(),
                self.detail_raster_variable.get(),
                self.min_size_variable.get(),
                self.threshold_variable.get()
            ], daemon=True
        )
        loading_thread.start()
        loading_window.start()

        if self.export_error:
            messagebox.showerror(
                "Export Failed!",
                "Unhandled exception encountered during export process\n"
                "See console for details"
            )
            self.export_error = False

        elif not loading_window.canceled:
            messagebox.showinfo(
                "Export Succeeded",
                "Successfully exported all files to '{}'!".format(path)
            )

    def export(
            self, path, name, loading_window, save_mask_tree: bool = True, save_vector_tree: bool = True,
            save_raster: bool = True, save_centroids: bool = True,
            save_detail_mask_tree: bool = True, save_detail_vector_tree: bool = True,
            save_detail_raster: bool = True, min_area: int = 5,
            tolerance: float = 0.05
    ):
        try:
            export.full_export(
                self.segment_manager, path, name, save_mask_tree, save_vector_tree,
                save_raster, save_centroids, save_detail_mask_tree, save_detail_vector_tree, save_detail_raster,
                min_area, tolerance
            )

        except Exception:
            traceback.print_exc()
            self.export_error = True

        loading_window.close()


class PreviewInterface(base_top_level.BaseTopLevel):
    def __init__(self, segment_manager, master=None):
        super().__init__(master, None, "Segmentation Preview")

        self.segment_manager = segment_manager

        image = export.to_flat_image(self.segment_manager)
        image = ImageOps.contain(Image.fromarray(image), (500, 500))
        img = customtkinter.CTkImage(light_image=image, dark_image=image, size=image.size)

        panel = customtkinter.CTkLabel(self, image=img, text="")
        panel.pack(side="bottom", fill="both", expand=True)


class SAMInterface(base_interface.BaseInterface):
    def __init__(self, segment_manager: sam_interface.segment_manager.SegmentManager, on_close_callback=None):
        super().__init__((800, 500), on_close_callback=on_close_callback)

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
            self, text="Save As...", command=self.save_as
        ).pack(side=customtkinter.LEFT, padx=10, pady=10)

        customtkinter.CTkButton(
            self, text="Main Menu", command=self.close
        ).pack(side=customtkinter.RIGHT, padx=10, pady=10)

    def save_as(self):
        path = filedialog.asksaveasfilename(
            confirmoverwrite=True, defaultextension=".dat", filetypes=[
                ("Segment Manager Backup", "*.dat")
            ], title="Save Segmentation State"
        )

        if path == "":
            return

        logging.info("Saving state to '{}'...".format(path))
        self.segment_manager.save(path)

        logging.info("Save successful")

        messagebox.showinfo(
            "Save Successful",
            "Successfully saved segmentation manager to '{}'".format(path)
        )

    def preview_segmentation(self):
        preview = PreviewInterface(self.segment_manager)
        preview.start()

    def export_segmentation(self):
        exporter = ExportInterface(self.segment_manager)
        exporter.start()
