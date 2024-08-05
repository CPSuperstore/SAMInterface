import os
import sys
import threading
import time

import customtkinter
from customtkinter import filedialog
import tkinter.messagebox as messagebox
import sam_interface.segment_manager as segment_manager

import sam_interface.ui.base_interface as base_interface
import sam_interface.ui.sam_ui as sam_ui


class MainMenuInterface(base_interface.BaseInterface):
    def __init__(self, on_close_callback=None):
        super().__init__((500, 200), on_close_callback=on_close_callback)

        self.image_path_variable = customtkinter.StringVar()
        self.segment_manager = None

        config = dict(
            sticky='NEWS', pady=10, padx=10, columnspan=2
        )

        customtkinter.CTkLabel(self, text="Segment Anything Model Interface").grid(row=0, column=0, **config)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=6)

        customtkinter.CTkButton(
            self, text='Browse', command=self.select_save_directory
        ).grid(row=1, column=0, sticky='EW', pady=5, padx=10)

        export_path_textbox = customtkinter.CTkEntry(self, textvariable=self.image_path_variable)
        export_path_textbox.grid(row=1, column=1, sticky='EW', pady=5, padx=10)

        customtkinter.CTkButton(
            self, text='Begin Segmentation', command=self.start_segmentation
        ).grid(row=2, column=0, **config)

    def select_save_directory(self):
        filename = filedialog.askopenfilename(filetypes=[
            ("Image Files", "*.png *.jpg *.jpeg"),
            ("Segment Manager Backup", "*.dat")
        ])

        if filename == "":
            return

        self.image_path_variable.set(filename)

    def load_image(self, loading_window, path: str):
        if path.endswith(".dat"):
            self.segment_manager = segment_manager.SegmentManager.load(path)

        else:
            self.segment_manager = segment_manager.SegmentManager(path)

        loading_window.close()

    def start_segmentation(self):
        path = self.image_path_variable.get()

        if path == "":
            messagebox.showerror("Validation Error", "You must select an image to proceed!")
            return

        if not os.path.isfile(path):
            messagebox.showerror(
                "Validation Error",
                "The provided export path '{}' does not point to an existing file!".format(path)
            )
            return

        loading_window = self.get_loading_window()

        loading_thread = threading.Thread(target=self.load_image, args=[loading_window, path])
        loading_thread.start()

        loading_window.start()

        self.withdraw()

        sam = sam_ui.SAMInterface(self.segment_manager, self.deiconify)
        sam.start()

        # sys.exit(0)
