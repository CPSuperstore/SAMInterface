import os
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

    def draw(self):
        self.clock.tick(self.framerate_cap)
        self.fps = self.clock.get_fps()

        if self.fps != 0:
            self.delta_t = 1 / self.fps

        self.render()
        pygame.display.update()

    @abc.abstractmethod
    def render(self):
        pass
