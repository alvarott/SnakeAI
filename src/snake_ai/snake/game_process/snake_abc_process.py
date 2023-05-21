# This module contains the API for implementing the classes that will contain
# all the elements to process a game iteration

# Author: Álvaro Torralba
# Date: 16/05/2023
# Version: 0.0.1

from abc import abstractmethod, ABC
from snake_ai.snake.snake_core import SnakeCore, SnakeGUI
from snake_ai.snake.snake_controller import GameController


class SnakeProcess(ABC):

    def __init__(self, size: tuple[int, int], core: SnakeCore | SnakeGUI, controller: GameController):
        """
        Constructor
        :param size: game grid size
        :param core: object instance of a SnakeCore like implementation
        :param controller: object instance of a GameController like implementation
        """
        self._core = core
        self._controller = controller
        self._size = size
        self._running: bool = self._core.alive

    @property
    def running(self) -> bool:
        """
        Flag to check if the game should continue running
        :return:
        """
        return self._core.alive

    @property
    def core(self) -> SnakeCore:
        """
        Hold the core object instance
        :return:
        """
        return self._core

    @property
    def stats(self) -> dict:
        """
        This method should return the stats of the game execution performed to be used by a GA
        :return:
        """
        return self._core.stats

    @abstractmethod
    def step(self, *args, **kwargs):
        """
        Making use of a snake implementation and a game driver must implement the game data flow logic
        :return:
        """
        action = self._controller.action(*args, **kwargs)
        self._core.next_state(action)
        self._running = self._core.alive
