import os
import threading
import time
import tkinter as tk
import tkinter.filedialog as filedialog

import darkdetect
import pygame
import sv_ttk
from PIL import Image, ImageTk

pygame.init()


class PygameSurface(tk.Frame):
    def __init__(self, parent, screen_size: tuple):
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
        self.framerate_cap = 60

        self.display_image: pygame.Surface = pygame.Surface((1, 1))
        self.display_image_pos = (0, 0)
        self.real_image_size = (0, 0)
        self.scale_factor = 1

    def draw(self):
        self.clock.tick(self.framerate_cap)
        self.fps = self.clock.get_fps()

        if self.fps != 0:
            self.delta_t = 1 / self.fps

        self.render()

    def render(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                click_pos = event.pos
                image_pos = (
                        (click_pos[0] - self.display_image_pos[0]) / self.scale_factor,
                        (click_pos[1] - self.display_image_pos[1]) / self.scale_factor
                )
                if (
                        image_pos[0] < 0 or image_pos[1] < 0 or
                        image_pos[0] > self.real_image_size[0] or
                        image_pos[1] > self.real_image_size[1]
                ):
                    continue

                print(image_pos)

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.display_image, self.display_image_pos)
        pygame.display.update()

    def set_image(self, filename: str):
        image = pygame.image.load(filename).convert()
        width, height = image.get_size()
        self.real_image_size = image.get_size()

        width_ratio = self.screen_width / width
        height_ratio = self.screen_height / height
        self.scale_factor = min(width_ratio, height_ratio)

        new_width = width * self.scale_factor
        new_height = height * self.scale_factor

        self.display_image = pygame.transform.scale(image, (new_width, new_height))
        self.display_image_pos = (
            int((self.screen_width / 2) - (new_width / 2)),
            int((self.screen_height / 2) - (new_height / 2))
        )


class MainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Segment Anything Interface")
        self.geometry("800x500")

        self.pygame_surface = PygameSurface(self, (800, 450))
        self.pygame_surface.pack()

        self.running = True

        tk.Button(self, text="Import Image", command=self.import_image).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(self, text="Preview", command=self.preview_segmentation).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(self, text="Export As...", command=self.export_segmentation).pack(side=tk.LEFT, padx=10, pady=10)

        sv_ttk.set_theme(darkdetect.theme())

    def import_image(self):
        selected_file = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if selected_file == "":
            return

        self.pygame_surface.set_image(selected_file)

    def preview_segmentation(self):
        pass

    def export_segmentation(self):
        pass

    def close(self):
        self.running = False

    def start(self):
        self.running = True

        self.protocol("WM_DELETE_WINDOW", self.close)
        self.resizable(False, False)

        while self.running:
            self.pygame_surface.draw()
            self.update_idletasks()
            self.update()


def start_app():
    app = MainApp()
    app.start()
