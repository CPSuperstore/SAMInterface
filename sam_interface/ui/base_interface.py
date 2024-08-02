import tkinter as tk
import typing

import darkdetect
import sv_ttk
import sam_interface.ui.widget.pygame_widget as pygame_widget


class BaseInterface(tk.Tk):
    def __init__(self, window_size: tuple, title: str = "Segment Anything Interface"):
        super().__init__()
        self.title(title)
        self.geometry("{}x{}".format(*window_size))
        self.running = False

        sv_ttk.set_theme(darkdetect.theme())

    def close(self):
        self.running = False

    def start(self):
        self.running = True

        self.protocol("WM_DELETE_WINDOW", self.close)
        self.resizable(False, False)

        pygame_widgets: typing.List[pygame_widget.PygameWidget] = [
            widget for widget in self.winfo_children() if isinstance(widget, pygame_widget.PygameWidget)
        ]

        while self.running:
            for widget in pygame_widgets:
                widget.draw()

            self.update_idletasks()
            self.update()
