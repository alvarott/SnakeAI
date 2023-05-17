# This module contains a graphic extended processing implementation of the Snake game

# Author: Álvaro Torralba
# Date: 18/05/2023
# Version: 0.0.1

from snake_ai.snake.snake_core.snake_gui_core.snake_gui_abc import SnakeGUI
from pygame.surface import Surface
import pygame
import math


class SnakeHWGUI(SnakeGUI):
    """
    This class implements a graphic extended version
    """

    # Class constant
    IMAGES = 'ext_gui'

    def __init__(self, size: tuple[int, int], dist_calculator: str, mode: str, show_path: bool = False):
        """
        Constructor
        :param size: grid size
        :param dist_calculator: flag to select the distance calculator to be used
        :param mode: flag to indicate the mode: human controlled or auto controlled
        :param show_path: flag to indicate if the min path must be displayed while rendering
        """
        super().__init__(size=size, img_folder=SnakeHWGUI.IMAGES, dist_calculator=dist_calculator, mode=mode, show_path=show_path)
        self._background: Surface = self._build_background()
        self._apples: list[Surface] = self._load_apples()
        self._apple_idx: float = 0
        self.render_surface()

    def _load_apples(self) -> list[Surface]:
        """
        Creates a dictionary with the apple images
        :return dict:
        """
        apples = []
        for key, value in self._images.items():
            if key.startswith('apple'):
                apples.insert(0, pygame.transform.scale(value, (50, 50)))
        return apples

    # Provisional background implementation
    def _build_background(self):
        """
        Builds the background image
        :return:
        """
        ref_cell = [0, 0]
        background = Surface(self._dim)
        for i in range(self._rows):
            for j in range(self._cols):
                background.blit(self._images['background'], (ref_cell[0], ref_cell[1]))
                ref_cell[1] += SnakeGUI.BLOCK_SIZE
            ref_cell[0] += SnakeGUI.BLOCK_SIZE
            ref_cell[1] = 0
        return background

    def render_surface(self) -> None:
        """
        Produces all the objects to be rendered in the game board
        :return:
        """
        surface = Surface(self._dim)
        # Render background
        surface.blit(self._background, (0, 0))
        # Render apple
        self._render_apple(surface)
        # Render path
        self._render_min_pth(surface)
        # Render Snake Head
        surface.blit(self._images[f'head_{self.head.dir[0].value}'], SnakeGUI._cell_to_pixels(self.head.pos()))
        # Render Snake tail
        surface.blit(self._images[f'tail_{self.tail.dir[0].value}'], SnakeGUI._cell_to_pixels(self.tail.pos()))
        # Render body
        current = self.tail.next
        for i in range(self._snake.length-2):
            # Render pre tail
            if i == 0:
                if current.dir[1].value is not None:
                    name = f'pre_tail_{current.dir[0].value}_{current.dir[1].value}'
                else:
                    name = f'pre_tail_{current.dir[0].value}'
                surface.blit(self._images[name], SnakeGUI._cell_to_pixels(current.pos()))
            # Render rest of the body
            else:
                if current.dir[1].value is not None:
                    name = f'body_{current.dir[0].value}_{current.dir[1].value}'
                else:
                    name = f'body_{current.dir[0].value}'
                surface.blit(self._images[name], SnakeGUI._cell_to_pixels(current.pos()))
            current = current.next
        # Render scoreboard
        score = self._fonts['pixel_font'].render(f"Score: {self._stats_data.score}", True, (255, 205, 255))
        surface.blit(score, (self._width - score.get_width(), 0))
        self._surface = surface

    def _render_apple(self, surface: Surface):
        """
        Produces the apple animation to be rendered
        :param surface: surface where to place the apple
        :return:
        """
        image = self._apples[math.floor(self._apple_idx)]
        rect = image.get_rect(center=(SnakeGUI._cell_to_pixels((self._apple[0] + 0.5, self._apple[1] + 0.5))))
        surface.blit(image, rect)
        self._apple_idx += 0.3
        if self._apple_idx >= len(self._apples):
            self._apple_idx = 0
