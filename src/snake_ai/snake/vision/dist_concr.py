# This module contains the implementation of the classes that calculates the distances

# Author: Álvaro Torralba
# Date: 17/05/2023
# Version: 0.0.1

from snake_ai.snake.vision.dist_abc import ABCDistance
import numpy as np
import math


class Euclidean(ABCDistance):
    """
    Implements the Euclidean distance
    """
    def dist(self, dim: tuple[int, int], p1: np.ndarray, p2: np.ndarray) -> float:
        """
        Returns the Euclidean distance between to points normalized respect to the maximum grid distance
        :param dim: grid size
        :param p1: from point
        :param p2: to point
        :return: Euclidean distance
        """
        max_dist = math.sqrt((dim[0] - 1) ** 2 + (dim[1] - 1) ** 2)
        return np.linalg.norm(p1 - p2) / max_dist


class Manhattan(ABCDistance):
    """
    This class implements the Manhattan distance
    """
    def dist(self, dim: tuple[int, int], p1: np.ndarray, p2: np.ndarray) -> float:
        """
        Returns the Manhattan distance between two points normalized respect to the maximum grid distance
        :param dim: grid dimensions
        :param p1: from point
        :param p2: to point
        :return: Manhattan distance
         """
        x, y = dim[0] - 1, dim[1] - 1
        max_dist = np.sum(np.absolute(np.array([0, 0]) - np.array([x, y])))
        return np.sum(np.absolute(p1 - p2)) / max_dist


class Binary(ABCDistance):
    def dist(self, dim: tuple[int, int], p1: np.ndarray, p2: np.ndarray) -> float:
        """
        Just returns one, ones a collision is detected, is it done is this way to be compatible with the previous
        versions
        :param dim: grid dimensions
        :param p1: from point
        :param p2: to point
        :return: Binary detection
         """
        return 1.0