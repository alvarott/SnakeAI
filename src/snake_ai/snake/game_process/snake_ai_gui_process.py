# This module contains the class that implements the entire logic to process a game step with NN control producing
# a graphical output of the game state

# Author: Álvaro Torralba
# Date: 20/05/2023
# Version: 0.0.1

from snake_ai.snake.snake_controller import AIController
from snake_ai.snake.game_process.snake_gui_process import SnakeGUIProcess
from snake_ai.snake.game_process.snake_ai_abc_process import SnakeAIABC
from snake_ai.neural.nn import NN

class SnakeAIGUI(SnakeGUIProcess, SnakeAIABC):
    """
    Implements a graphical snake process controlled by a NN
    """
    def __init__(self, size: tuple[int, int], core: str, dist_calculator: str, show_path: bool, brain: NN):
        """
        Constructor
        :param size: game grid size
        :param core: SnakeGUI name to be used as core
        :param dist_calculator: Distance calculator name
        :param show_path: rendering min path flag
        :param input: input nodes to the NN
        :param output: output nodes from the NN
        :param hidden: list with the number of nodes of each hidden layer
        :param output_init: output layer weights initialization method to be used
        :param bias: flag to introduce or not bias vector
        :param bias_init: bias initialization method to be used
        :param hidden_init: hidden layers initialization method to be used
        :param output_act: output layer activation function
        :param hidden_act: hidden layers activation function
        """
        controller = AIController(input=1, output=1, hidden=[1], output_init='he', bias=False,
                                  bias_init='he', hidden_init='he', output_act='relu',
                                  hidden_act='relu')
        controller.brain = brain
        SnakeGUIProcess.__init__(self, size=size, core=core, dist_calculator=dist_calculator, mode='auto',
                                 show_path=show_path,
                                 controller=controller)
        SnakeAIABC.__init__(self, controller)
