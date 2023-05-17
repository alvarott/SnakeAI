# This module contains the API for the classes that implements distance calculations in a grid

# Author: Álvaro Torralba
# Date: 17/05/2023
# Version: 0.0.1

from abc import  ABCMeta, abstractmethod
import numpy as np

class ABCDistance(metaclass=ABCMeta):
    """
    Distances interface
    """
    @abstractmethod
    def dist(self, dim: tuple[int, int], p1: np.ndarray, p2: np.ndarray) -> float | int:
        """
        Should return the distances between two points
        :param args:
        :return:
        """
        pass