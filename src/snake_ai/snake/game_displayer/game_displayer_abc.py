# This module contains the base class for displaying and controlling snake games main loop

# Author: Álvaro Torralba
# Date: 03/06/2023
# Version: 0.0.1

from snake_ai.snake import resources as rsc
from importlib import resources as rc
from abc import ABC, abstractmethod
import pygame
import os


class GameDisplayerABC(ABC):
    """
    API for displayer classes
    """
    def __init__(self, show_path: bool):
        self._screen: pygame.Surface
        self._a_star = show_path
        self._scaled = False
        self._scale_factor = None
        self._game_width = None
        self._game_height = None
        self._alive = True
        self._initializing = True
        self._running = False
        self._ended = False
        self._fonts = {}
        self._fonts_s = {}
        self._fonts_m = {}
        self._images = {}

    def init_pygame(self, screen_dim: tuple[int, int]) -> None:
        """
        Initiates the pygame module
        :param screen_dim:
        :return:
        """
        pygame.init()
        self._screen = pygame.display.set_mode(screen_dim)
        self._game_width = screen_dim[0]
        self._game_height = screen_dim[1]

    def _load_resources(self) -> None:
        """
        Loads the necessary resources
        :return:
        """
        # Load fonts
        source = rc.files(rsc).joinpath('fonts')
        with os.scandir(str(source))as files:
            for file in files:
                self._fonts[file.name[0:file.name.index('.')]] = pygame.font.Font(source.joinpath(file.name)
                                                                                  .open('br'), 25)
                self._fonts_s[file.name[0:file.name.index('.')]] = pygame.font.Font(source.joinpath(file.name)
                                                                                    .open('br'), 13)
                self._fonts_m[file.name[0:file.name.index('.')]] = pygame.font.Font(source.joinpath(file.name)
                                                                                    .open('br'), 22)
        # Load Images
        source = rc.files(rsc).joinpath(f'images/shared')
        with os.scandir(str(source)) as files:
            for file in files:
                self._images[file.name[0:file.name.index('.')]] = pygame.image.load(
                    source.joinpath(file.name).open('br')).convert_alpha()

    @abstractmethod
    def run(self):
        """
        Game main loop
        :return:
        """
        pass

    @abstractmethod
    def _reset(self):
        """
        Resets the game state
        :return:
        """
        pass
