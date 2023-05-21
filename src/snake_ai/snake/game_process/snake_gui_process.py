# This module contains the class that implements the game main loop with a graphic user interface

# Author: Álvaro Torralba
# Date: 16/05/2023
# Version: 0.0.1

from snake_ai.snake.snake_controller import GameController
from snake_ai.snake.game_process.snake_abc_process import SnakeProcess
from snake_ai.snake.snake_core import SnakeGUIFactory
from pygame import Surface
from abc import ABC


class SnakeGUIProcess(SnakeProcess, ABC):
    """
    Base Abstract class for graphical implementations of the game process
    It relies on the use of the pygame library
    """

    def __init__(self, size: tuple[int, int], core: str, dist_calculator: str, mode: str, show_path: bool,
                 controller: GameController):
        """
        Constructor
        :param size: game grid size
        :param core: name of one of the SnakeGUI like implementations
        :param dist_calculator: name of the distance calculator class implementation
        :param mode: flag to indicate if the game is played by an AI or a human
        :param show_path: flag to indicate if the minimum shortest path must be rendered while playing
        :param controller: object instance of a controller implementation
        """
        self._gui_factory = SnakeGUIFactory()
        super().__init__(size=size,
                         core=self._gui_factory.get_instance(core_name=core, game_size=size,
                                                             dist_calculator=dist_calculator, mode=mode,
                                                             show_path=show_path),
                         controller=controller)

    @property
    def surface(self) -> Surface:
        """
        Hold the last game state as a pygame Surface
        :return: the rendered surface
        """
        return self._core.surface

    def step(self, **kwargs) -> None:
        """
        Base function to define a one step state change logic in the game
        :param kwargs: Any necessary parameter
        :return:
        """
        super().step(**kwargs)
        if self._core.alive:
            self._core.render_surface()
