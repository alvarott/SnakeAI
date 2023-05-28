# This module contains the class that implements the entire logic to process a game step with human control

# Author: Álvaro Torralba
# Date: 20/05/2023
# Version: 0.0.1

from snake_ai.snake.snake_controller import HumanController
from snake_ai.snake.game_process.snake_gui_process import SnakeGUIProcess


class SnakeHuman(SnakeGUIProcess):
    def __init__(self, size: tuple[int, int], core: str, dist_calculator: str, show_path: bool):
        super().__init__(size=size, core=core, dist_calculator=dist_calculator, mode='human', show_path=show_path,
                         controller=HumanController())
