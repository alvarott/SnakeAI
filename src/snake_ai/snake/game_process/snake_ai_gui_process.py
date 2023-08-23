# This module contains the class that implements the entire logic to process a game step with NN control producing
# a graphical output of the game state

# Author: Álvaro Torralba
# Date: 20/05/2023
# Version: 0.0.1

from snake_ai.snake.snake_controller import AIController
from snake_ai.snake.game_process.snake_gui_process import SnakeGUIProcess
from snake_ai.neural.nn import NN


class SnakeAIGUI(SnakeGUIProcess):
    """
    Implements a graphical snake process controlled by a NN
    """
    def __init__(self, size: tuple[int, int], core: str, show_path: bool, brain: NN, vision: str, mode: str):
        """
        Constructor
        :param size: game grid size
        :param core: SnakeGUI name to be used as core
        :param show_path: rendering min path flag
        :param brain: NN that controls the snake
        """
        self._controller = AIController(input=1, output=1, hidden=[1], output_init='he', bias=False,
                                        bias_init='he', hidden_init='he', output_act='relu',
                                        hidden_act='relu')
        self._controller.brain = brain
        SnakeGUIProcess.__init__(self, size=size, core=core, mode=mode, show_path=show_path, vision=vision,
                                 controller=self._controller)

    @property
    def controller(self) -> AIController:
        """
        Game controller instance
        :return:
        """
        return self._controller
