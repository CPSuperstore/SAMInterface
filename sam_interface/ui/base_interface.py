import typing

import customtkinter
import darkdetect
import sam_interface.ui.loading_window as loading_window

import sam_interface.ui.widget.pygame_widget as pygame_widget

if darkdetect.isDark():
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("dark-blue")


class BaseInterface(customtkinter.CTk):
    def __init__(self, window_size: tuple, title: str = "Segment Anything Interface"):
        super().__init__()
        self.title(title)
        self.geometry("{}x{}".format(*window_size))
        self.running = False

        # sv_ttk.set_theme(darkdetect.theme())

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

    def get_loading_window(self, master=None, text: str = None) -> loading_window.LoadingWindow:
        return loading_window.LoadingWindow(text, self if master is None else master)
