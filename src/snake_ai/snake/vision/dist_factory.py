# This module contains a factory class for the different implementations of the distances

# Author: Álvaro Torralba
# Date: 17/05/2023
# Version: 0.0.1

from snake_ai.class_factory_abc import FactoryABS
import snake_ai.snake.vision.dist_concr as distances


class DistanceFactory(FactoryABS):
    """
    Implements a factory for GameController like objects
    """
    def __init__(self):
        super().__init__(distances)

    def get_instance(self, distance_name: str) -> distances.ABCDistance:
        """
        Creates an instance of a SnakeCore like object
        :param distance_name: name the distance calculator class
        :return instance: object instance
        """
        if distance_name in self._classes:
            return self._classes[distance_name]()
        else:
            raise ValueError(f"No implementation found with the name: {distance_name}."
                             f" Found implementations: {self._classes.keys()}")
