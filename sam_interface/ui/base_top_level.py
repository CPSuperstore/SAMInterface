import abc
import typing

if typing.TYPE_CHECKING:
    import sam_interface.ui.loading_window as loading_window

import customtkinter


class BaseTopLevel(customtkinter.CTkToplevel, abc.ABC):
    def __init__(self, master=None, window_size: tuple = None, title: str = "Segment Anything Interface"):
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)

        if window_size is not None:
            self.geometry("{}x{}".format(*window_size))

        self.running = False

    def close(self):
        self.running = False

    def start(self):
        self.transient(self.master)
        self.grab_set()
        self.master.wait_window(self)

    def disable_closing(self):
        self.protocol("WM_DELETE_WINDOW", lambda: 0)

    def on_update(self):
        pass

    def get_loading_window(self, master=None, text: str = None) -> 'loading_window.LoadingWindow':
        return self.master.get_loading_window(master, text)
