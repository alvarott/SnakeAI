# This module contains the class that implement the necessary tools for autocontrol of the game using a NN

# Author: Álvaro Torralba
# Date: 20/05/2023
# Version: 0.0.1

from snake_ai.snake.snake_controller.controller_abc import GameController
from snake_ai.snake.enums import GameDirection, NNOutput
import numpy as np
from snake_ai.neural.nn import NN


class AIController(GameController):
    """
    Implements an auto-controller for the snake
    """
    def __init__(self, input: int, output: int, hidden: list[int], output_init: str, bias: bool, bias_init: str,
                 hidden_init: str, output_act: str, hidden_act: str):
        self._nn = NN(input=input, output=output, hidden=hidden, output_init=output_init, bias=bias,
                      bias_init=bias_init, hidden_init=hidden_init, output_act=output_act, hidden_act=hidden_act)

    @property
    def nn_code(self) -> np.ndarray:
        """
        NN weights and biases encoding as 1D-array
        :return: Array containing the weights and biases of the NN
        """
        return self._nn.encode()

    @nn_code.setter
    def nn_code(self, code: np.ndarray) -> None:
        """
        Sets new values for the NN passed as a coding array
        :param code: NN codification as an array
        :return:
        """
        self._nn.decode(code)

    @property
    def nn_activation(self) -> dict[int, list[float]]:
        """
        Holds all the nodes outputs for the last forward propagation
        :return: dictionary containing the values of each layer
        """
        return self._nn.activations

    @property
    def brain(self) -> NN:
        """
        NN instance that controls the snake
        :return:
        """
        return self._nn

    @brain.setter
    def brain(self, new_brain: NN) -> None:
        """
        NN setter
        :param new_brain:
        :return:
        """
        self._nn = new_brain

    @property
    def layers(self):
        return self._nn.layers

    def action(self, current_dir: GameDirection,  vision: np.ndarray) -> GameDirection:
        """
        This method must return the next direction that it follows the snake
        :return GameDirection:
        """
        # Clock wise turning direction
        clk_dirs = [GameDirection.UP, GameDirection.LEFT, GameDirection.DOWN, GameDirection.RIGHT]
        # Obtain next state
        output = self._nn.forward_prop(vision)
        # Translate output to action
        max_index = np.argmax(output)
        binary_out = np.zeros_like(output)
        binary_out[max_index] = 1
        binary_out = NNOutput(binary_out.tolist())
        # Calculate next direction
        current_idx = clk_dirs.index(current_dir)
        if binary_out == NNOutput.LEFT:
            next_dir = clk_dirs[(current_idx + 1) % len(clk_dirs)]
        elif binary_out == NNOutput.RIGHT:
            next_dir = clk_dirs[(current_idx - 1) % len(clk_dirs)]
        else:
            next_dir = current_dir
        return next_dir
