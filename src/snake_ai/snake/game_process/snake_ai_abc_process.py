# This module contains the parent class for snake ai processes

# Author: Álvaro Torralba
# Date: 21/05/2023
# Version: 0.0.1

from abc import ABC
from snake_ai.snake.snake_controller.auto_controller import AIController
import numpy as np


class SnakeAIABC(ABC):
    """
    This class holds the common methods for all Snake AI Controlled processes
    """
    def __init__(self, controller: AIController):
        self._controller = controller

    @property
    def nn_code(self) -> np.ndarray:
        """
        Produces the codification of the NN that is running the snake
        :return nn_code: codification of the current brain of the snake
        """
        return self._controller.nn_code

    @nn_code.setter
    def nn_code(self, code: np.ndarray) -> None:
        """
        Sets the NN that acts as brain of the snake, through a codification of the NN passed as an array
        :param code: codification of the NN
        :return:
        """
        self._controller.nn_code = code

    @property
    def nn_activations(self) -> dict[int, list[float]]:
        """
        Access the NN to get the outputs of all the layer from the last forward propagation
        :return:
        """
        return self._controller.nn_activation
