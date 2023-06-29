# This module is intended to contain the auxiliary enumerate classes

# Author: Álvaro Torralba
# Date: 14/05/2023
# Version: 0.0.1


from enum import Enum


class GridDict(Enum):
    """
    Enumerate class representing the meaning of the values inside the grid matrix that holds the game state
    """
    HEAD = 2
    BODY = 1
    APPLE = -1
    EMPTY = 0


class NNDirection(Enum):
    """
    Enumerate class representing the directions as entries for the NN
    """
    UP = [1, 0, 0, 0]
    DOWN = [0, 1, 0, 0]
    LEFT = [0, 0, 1, 0]
    RIGHT = [0, 0, 0, 1]


class NNOutput(Enum):
    """
    Enumerate class representing the possible outputs of the NN
    """
    LEFT = [1.0, 0.0, 0.0]
    STRAIGHT = [0.0, 1.0, 0.0]
    RIGHT = [0.0, 0.0, 1.0]


class Step(Enum):
    """
    Enumerate class containing the increments that should be applied to the current position when a move is performed
    """
    X = {"right": 1, "left": -1, "None": 0}
    Y = {"up": -1, "down": 1, "None": 0}


class GameDirection(Enum):
    """
    Enumerate class representing the possible directions that the snake can take
    """
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'
    NONE = None


class GameSize(Enum):
    """
    Enumerate class containing the possibles grid dimensions
    """
    SMALL = (15, 15)
    MEDIUM = (20, 20)
    LARGE = (25, 25)


class GameSpeed(Enum):
    """
    Enumerate class containing the possible game speeds
    """
    SLOW = 10
    NORMAL = 18
    FAST = 23
