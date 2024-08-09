import customtkinter

import sam_interface.ui.base_top_level as base_top_level


class LoadingWindow(base_top_level.BaseTopLevel):
    def __init__(self, text: str = None, master=None, cancel_button: bool = False):
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

        self.canceled = False

        self.cancel_callback: callable = lambda _: 0

        if cancel_button:
            customtkinter.CTkButton(
                self, text="Continue In Background", command=self.cancel
            ).grid(row=2, column=0, **config)

        self.grid_columnconfigure(0, weight=1)

    def cancel(self):
        self.running = False
        self.cancel_callback(self)
        self.canceled = True

    def start(self):
        self.transient(self.master)
        self.grab_set()

        self.running = True
        while self.running:
            self.progress_bar.update()
            self.update_idletasks()
            self.update()

        self.destroy()
