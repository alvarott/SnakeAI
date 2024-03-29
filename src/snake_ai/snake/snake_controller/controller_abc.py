# This module contains the API for implementing classes that controls the move of the snake
# by processing the state of the game or the peripherals

# Author: Álvaro Torralba
# Date: 16/05/2023
# Version: 0.0.1

from snake_ai.snake.enums import GameDirection
from abc import abstractmethod, ABC


class GameController(ABC):

    @abstractmethod
    def action(self, *args, **kwargs) -> GameDirection:
        """
        This method must return the next direction that it follows the snake
        :return GameDirection:
        """