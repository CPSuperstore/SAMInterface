import os
import threading
import tkinter.messagebox as messagebox

import customtkinter
from customtkinter import filedialog
import CTkListbox

import sam_interface.segment_manager as segment_manager
import sam_interface.ui.base_interface as base_interface
import sam_interface.ui.sam_ui as sam_ui
import sam_interface.preferences as preferences


class MainMenuInterface(base_interface.BaseInterface):
    def __init__(self, on_close_callback=None):
        super().__init__((500, 300), on_close_callback=on_close_callback)

        self.image_path_variable = customtkinter.StringVar()
        self.segment_manager = None

        config = dict(
            sticky='NEWS', padx=10, columnspan=2
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=6)

        customtkinter.CTkLabel(self, text="Segment Anything Model Interface").grid(row=0, column=0, **config)

        customtkinter.CTkLabel(self, text="Recent Files").grid(row=1, column=0, **config)

        self.recent_files = CTkListbox.CTkListbox(self, command=self.select_recent_file)
        self.recent_files.grid(row=2, column=0, **config)

        for i, recent_file in enumerate(preferences.get_recent_files()):
            self.recent_files.insert(i, os.path.basename(recent_file))

        customtkinter.CTkLabel(self, text="Open New File").grid(row=3, column=0, **config)

        customtkinter.CTkButton(
            self, text='Browse', command=self.select_import_directory
        ).grid(row=4, column=0, sticky='EW', pady=5, padx=10)

        export_path_textbox = customtkinter.CTkEntry(self, textvariable=self.image_path_variable)
        export_path_textbox.grid(row=4, column=1, sticky='EW', pady=5, padx=10)

        customtkinter.CTkButton(
            self, text='Begin Segmentation', command=self.start_segmentation
        ).grid(row=5, column=0, **config)

    def select_recent_file(self, _):
        index = self.recent_files.curselection()
        path = preferences.get_recent_files()[index]

        self.image_path_variable.set(path)
        self.start_segmentation()

    def select_import_directory(self):
        prefs = preferences.get_preferences()

        filename = filedialog.askopenfilename(
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg"),
                ("Segment Manager Backup", "*.dat")
            ],
            title='Select image to segment',
            initialdir=prefs["last_import_dir"]
        )

        if filename == "":
            return

        prefs["last_import_dir"] = os.path.dirname(filename)
        preferences.save_preferences(prefs)

        self.image_path_variable.set(filename)

    def load_image(self, loading_window, path: str):
        sam_checkpoint = preferences.get_preferences()

        if path.endswith(".dat"):
            self.segment_manager = segment_manager.SegmentManager.load(path)

        else:
            self.segment_manager = segment_manager.SegmentManager(
                path,
                checkpoint_key=sam_checkpoint["model_type"],
                checkpoint_path=sam_checkpoint["checkpoint_path"]
            )
            self.segment_manager.save("segment_manager.dat")

        loading_window.close()

    def start_segmentation(self):
        path = self.image_path_variable.get()
        preferences.add_recent_file(path)

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
