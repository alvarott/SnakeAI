# This module contains the API and common functionality for any GUI implementation of the Snake Game

# Author: Álvaro Torralba
# Date: 15/05/2023
# Version: 0.0.1

from importlib import resources as rc
from snake_ai.snake import resources as rsc
from snake_ai.snake.snake_core.snake_core import SnakeCore
from snake_ai.snake.enums import GameDirection
from abc import abstractmethod, ABC
import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.surface import Surface
import os


class SnakeGUI(SnakeCore, ABC):
    """
    API for Snake GUI implementations
    Note that this class and all its child classes has direct dependencies with pygame,
    before attempting to run any of its methods the pygame engine must be initialized,
    otherwise exceptions will be raised
    """

    # Class constants
    BLOCK_SIZE = 30

    def __init__(self, size: tuple[int, int], img_folder: str, dist_calculator: str, mode: str, show_path: bool = False):
        """
        Constructor
        :param size: Size of the grid
        :param img_folder: folder for the image resources
        :param dist_calculator: flag to select the distance calculator to be used
        :param mode: flag to indicate the mode: human controlled or auto controlled
        :param show_path: flag to indicate if the min path must be displayed while rendering
        """
        super().__init__(size=size, dist_calculator=dist_calculator, mode=mode)
        self._width = self._cols * SnakeGUI.BLOCK_SIZE
        self._height = self._rows * SnakeGUI.BLOCK_SIZE
        self._dim = (self._width, self._height)
        self._a_star = show_path
        self._surface = Surface(self._dim)
        self._min_path: list[tuple[int, int]] = []
        self._images: dict[str, Surface] = {}
        self._load_resources(img_folder)

    def _render_min_pth(self, surface: Surface):
        """
        Renders the min path between the head and the apple
        :return surface: min path image on the grid
        """
        if self._a_star:
            self._min_path = self._dist.a_star(self.grid, self.head.pos(), self._apple)
            for cell in self._min_path[1:]:
                surface.blit(self._images['path'], SnakeGUI._cell_to_pixels(cell))

    def _load_resources(self, images_path: str) -> None:
        """
        All images must be place in a folder inside the folder images in the package resources
        :param images_path: folder that contains the resources
        :return:
        """
        # Load images and fonts
        source = rc.files(rsc).joinpath(f'images/{images_path}')
        with os.scandir(source) as files:
            for file in files:
                try:
                    self._images[file.name[0:file.name.index('.')]] = pygame.image.load(
                        source.joinpath(file.name).open('br')).convert_alpha()
                except pygame.error:
                    raise pygame.error("Pygame display module must be initialized and set before processing images")

    @property
    def a_star(self):
        return self._a_star

    @property
    def surface(self) -> Surface:
        """
        This method must return the graphic state of the game as pygame.Surface to be displayed by pygame engine
        :return Surface: image to be rendered as game state
        """
        return self._surface

    @abstractmethod
    def render_surface(self):
        """
        This method must provide a game state image after each it iteration to be displayed
        :return:
        """
        pass

    def next_state(self, direction: GameDirection):
        """
        Overwrites the parent class method adding the image processing to the method
        :param direction:
        :return:
        """
        super().next_state(direction)

    @staticmethod
    def _cell_to_pixels(index: tuple[int, int]) -> tuple[int, int]:
        """
        Converts a grid matrix position to their relative position measured in pixels, note that
        the parameters are inverted due row value correspond to the "y" axis and the column to the "x"
        :param index: index of the cell in the grid
        :return: (x,y) pixel position tuple
        """
        return index[1] * SnakeGUI.BLOCK_SIZE, index[0] * SnakeGUI.BLOCK_SIZE
