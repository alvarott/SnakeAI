# This module contains the class that implements the entire logic to process a game step with NN control just as
# process without any graphics processing for execution as a batch

# Author: Álvaro Torralba
# Date: 21/05/2023
# Version: 0.0.1

from snake_ai.snake.snake_core.snake_core import SnakeCore
from snake_ai.snake.snake_controller import AIController
from snake_ai.snake.game_process.snake_abc_process import SnakeProcess
from snake_ai.snake.game_process.snake_ai_abc_process import SnakeAIABC


class SnakeAI(SnakeProcess, SnakeAIABC):
    """
    Implements the entire game execution in a lightweight manner to optimize the NN training
    """
    # Object instances counter
    obj_counter = 1

    def __init__(self, size: tuple[int, int], dist_calculator: str, input: int, output: int, hidden: list[int],
                 output_init: str, bias: bool, bias_init: str, hidden_init: str, output_act: str, hidden_act: str
                 ):
        """
        Constructor
        :param size: game grid size
        :param dist_calculator: Distance calculator name
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
        controller = AIController(input=input, output=output, hidden=hidden, output_init=output_init, bias=bias,
                                  bias_init=bias_init, hidden_init=hidden_init, output_act=output_act,
                                  hidden_act=hidden_act)
        SnakeProcess.__init__(self, size=size, core=SnakeCore(size=size, dist_calculator=dist_calculator, mode='auto'),
                              controller=controller)
        SnakeAIABC.__init__(self, controller)
        self._id = SnakeAI.obj_counter
        SnakeAI.obj_counter += 1

    @property
    def id(self) -> int:
        """
        Identifier of the class instance
        :return id:
        """
        return self._id

    def step(self) -> None:
        """
        Making use of a snake implementation and a game driver must implement the game data flow logic
        :return:
        """
        super().step(self.core.direction, self.core.vision)

    def simulate(self) -> tuple[int, dict[str, float]]:
        """
        Runs the entire game loop
        :return:
        """
        while self.running:
            self.step()
        return self.id, self.stats
