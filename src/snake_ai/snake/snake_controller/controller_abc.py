# This module contains the API for implementing classes that controls the move of the snake
# by processing the state of the game or the peripherals

# Author: Álvaro Torralba
# Date: 16/05/2023
# Version: 0.0.1

from snake_ai.snake.enums import GameDirection
from abc import abstractmethod, ABC


class GameController(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def action(self, *args) -> GameDirection:
        """
        This method must return the next direction that it follows the snake
        :return GameDirection:
        """