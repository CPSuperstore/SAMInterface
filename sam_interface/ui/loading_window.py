from typing import Optional, Union, Tuple

import customtkinter


class LoadingWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, fg_color: Optional[Union[str, Tuple[str, str]]] = None, **kwargs):
        super().__init__(*args, fg_color=fg_color, **kwargs)
        self.loading = True

        self.title("Loading...")
        self.resizable(False, False)
        self.geometry("500x290")

        customtkinter.CTkLabel(self, text="Loading").grid(row=0, column=0)

    def stop(self):
        self.loading = False

    def start(self):
        self.transient(self.master)
        self.grab_set()

        while self.loading:
            self.update_idletasks()
            self.update()

        self.destroy()
