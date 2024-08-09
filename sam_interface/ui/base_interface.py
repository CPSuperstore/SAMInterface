import typing

import customtkinter
import darkdetect
import pygame

import sam_interface.ui.loading_window as loading_window

import sam_interface.ui.widget.pygame_widget as pygame_widget

if darkdetect.isDark():
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("dark-blue")


class BaseInterface(customtkinter.CTk):
    def __init__(self, window_size: tuple, title: str = "Segment Anything Interface", on_close_callback=None):
        super().__init__()
        self.title(title)
        self.geometry("{}x{}".format(*window_size))
        self.running = False
        self.on_close_callback = on_close_callback

    def close(self):
        pygame_widgets = self.get_pygame_widgets()

        for widget in pygame_widgets:
            widget.stop_rendering()

        self.running = False
        self.destroy()

        pygame.quit()

        if self.on_close_callback:
            self.on_close_callback()

    def get_pygame_widgets(self) -> typing.List[pygame_widget.PygameWidget]:
        return [
            widget for widget in self.winfo_children() if isinstance(widget, pygame_widget.PygameWidget)
        ]

    def start(self):
        self.running = True

        self.protocol("WM_DELETE_WINDOW", self.close)
        self.resizable(False, False)

        pygame_widgets = self.get_pygame_widgets()

        for widget in pygame_widgets:
            widget.start_rendering()

        while self.running:
            # for widget in pygame_widgets:
            #     widget.draw()

            self.update_idletasks()
            self.update()

    def get_loading_window(self, master=None, text: str = None, cancel_button: bool = False) -> loading_window.LoadingWindow:
        return loading_window.LoadingWindow(text, self if master is None else master, cancel_button=cancel_button)
