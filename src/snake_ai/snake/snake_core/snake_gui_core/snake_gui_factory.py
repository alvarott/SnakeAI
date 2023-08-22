# This module contains a factory class for the different implementations of the snake GUI core

# Author: Álvaro Torralba
# Date: 17/05/2023
# Version: 0.0.1

from snake_ai.class_factory_abc import FactoryABS
import snake_ai.snake.snake_core.snake_gui_core as gui_core


class SnakeGUIFactory(FactoryABS):
    """
    Implements a factory for SnakeGUI like objects
    """
    def __init__(self):
        super().__init__(gui_core)

    def get_instance(self, core_name: str, game_size: tuple[int, int], mode: str, show_path: bool,
                     vision: str) -> gui_core.SnakeGUI:
        """
        Creates an instance of a SnakeCore like object
        :param core_name: name of the snake core to be instantiated
        :param game_size: grid size
        :param mode: flag to indicate the mode: human controlled or auto controlled
        :param show_path: flag to indicate if the min path must be displayed while rendering
        """
        if core_name in self._classes:
            return self._classes[core_name](size=game_size, mode=mode, show_path=show_path, vision=vision)
        else:
            raise ValueError(f"No core implementation found with the name: {core_name}."
                             f" Found implementations: {self._classes.keys()}")
