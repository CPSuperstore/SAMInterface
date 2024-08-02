import customtkinter

import sam_interface.ui.base_top_level as base_top_level


class LoadingWindow(base_top_level.BaseTopLevel):
    def __init__(self, text: str = None, master=None):
        super().__init__(master, (300, 100), "Loading...")

        if text is None:
            text = "Loading"

        self.disable_closing()

        config = dict(
            sticky='NEWS', pady=5, padx=10
        )

        customtkinter.CTkLabel(self, text=text).grid(row=0, column=0, **config)
        self.progress_bar = customtkinter.CTkProgressBar(self, mode="indeterminate")
        self.progress_bar.grid(row=1, column=0, **config)
        self.progress_bar.start()

        self.grid_columnconfigure(0, weight=1)

    def start(self):
        self.transient(self.master)
        self.grab_set()

        self.running = True
        while self.running:
            self.progress_bar.update()
            self.update_idletasks()
            self.update()

        self.destroy()
