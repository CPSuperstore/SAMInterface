import os
import threading
import tkinter as tk
import abc

import pygame

pygame.init()


class PygameWidget(tk.Frame, abc.ABC):
    def __init__(self, parent, screen_size: tuple, framerate_cap: int = 60):
        super().__init__(parent)
        self.parent = parent
        self.screen_size = screen_size
        self.screen_width, self.screen_height = screen_size

        self.embed = tk.Frame(self, width=self.screen_width, height=self.screen_height)
        self.embed.pack()

        os.environ['SDL_WINDOWID'] = str(self.embed.winfo_id())
        os.environ['SDL_VIDEODRIVER'] = 'windib'

        self.screen = pygame.display.set_mode(screen_size)

        self.clock = pygame.time.Clock()
        self.fps = 0
        self.delta_t = 0
        self.framerate_cap = framerate_cap

        self.running = False
        self.render_timer = None

    def draw(self):
        self.clock.tick(self.framerate_cap)
        self.fps = self.clock.get_fps()

        if self.fps != 0:
            self.delta_t = 1 / self.fps

        self.render()
        pygame.display.update()

    def start_rendering(self):
        self.running = True
        self._render_loop()

    def stop_rendering(self):
        self.running = False
        if self.render_timer:
            self.render_timer.cancel()

    def _render_loop(self):
        if self.running:
            self.draw()
            self.render_timer = threading.Timer(1.0 / 60.0, self._render_loop)
            self.render_timer.start()

    @abc.abstractmethod
    def render(self):
        pass
