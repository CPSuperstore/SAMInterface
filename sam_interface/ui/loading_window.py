from typing import Optional, Union, Tuple

import customtkinter


class LoadingWindow(customtkinter.CTkToplevel):
    def __init__(self, text: str = None, *args, fg_color: Optional[Union[str, Tuple[str, str]]] = None, **kwargs):
        super().__init__(*args, fg_color=fg_color, **kwargs)
        self.loading = True

        if text is None:
            text = "Loading"

        self.title("Loading...")
        self.resizable(False, False)
        self.geometry("300x100")

        self.protocol("WM_DELETE_WINDOW", lambda: 0)

        config = dict(
            sticky='NEWS', pady=5, padx=10
        )

        customtkinter.CTkLabel(self, text=text).grid(row=0, column=0, **config)
        self.progress_bar = customtkinter.CTkProgressBar(self, mode="indeterminate")
        self.progress_bar.grid(row=1, column=0, **config)
        self.progress_bar.start()

        self.grid_columnconfigure(0, weight=1)

    def stop(self):
        self.loading = False

    def start(self):
        self.transient(self.master)
        self.grab_set()

        while self.loading:
            self.progress_bar.update()
            self.update_idletasks()
            self.update()

        self.destroy()
