# This module is intended to contain the class that implements the main logic of the Snake game

# Author: Álvaro Torralba
# Date: 14/05/2023
# Version: 0.0.1


from snake_ai.snake.enums import GameDirection, GridDict, Step, NNDirection
from snake_ai.snake.snake_core._data import BlockLinkedList, Node, StatsStruct
from snake_ai.snake.vision import GridOps
from collections import namedtuple
import numpy as np
import random

Cell = namedtuple('Cell', 'row, col')


class SnakeCore:
    """
    Contains the base functionality for the snake
    """

    # Class constants
    MODES = {'human', 'auto'}

    def __init__(self, size: tuple[int, int], dist_calculator: str, mode: str):
        """
        Constructor
        :param size: Grid size
        :param dist_calculator: the name of one the implemented distances calculator
        :param mode: flag to indicate if the extra calculations for NN controlling must be processed
        :param
        """
        if size[0] < 10 or size[1] < 10:
            raise ValueError("Minimum grid size supported (10 , 10)")
        if mode not in SnakeCore.MODES:
            raise ValueError(f"Mode {mode} not supported. Supported modes {SnakeCore.MODES}")
        # Create flag for auto player calculations
        elif mode == 'auto':
            self._auto = True
        else:
            self._auto = False
        self._vision: np.ndarray = np.empty(0)
        self._dist = GridOps(dist_calculator)
        self._rows = size[0]
        self._cols = size[1]
        self._snake = BlockLinkedList()
        self._apple: Cell
        self._grid = np.zeros((self._rows, self._cols))
        self._running = True
        self._completed = False
        self._stats_data = StatsStruct(rows=self._rows, cols=self._cols)
        self._moves_limit = 0
        self._place_snake()
        self._spawn_apple()
        self._set_cmp()
        if self._auto:
            self._set_vision()
            self._moves_limit = 100

    @property
    def vision(self) -> np.ndarray:
        return self._vision

    @property
    def stats(self) -> dict:
        return self._stats_data.get_stats()

    @property
    def alive(self) -> bool:
        return self._running and not self._completed

    @property
    def direction(self) -> GameDirection:
        return self._snake.head.dir[0]

    @property
    def head(self) -> Node:
        return self._snake.head

    @property
    def tail(self) -> Node:
        return self._snake.tail

    @property
    def grid(self) -> np.ndarray:
        return self._grid

    @grid.setter
    def grid(self, args: tuple[int, int, int]):
        self._grid[args[0]][args[1]] = args[2]

    def _set_cmp(self) -> None:
        """
        Sets the length of the current min path to the apple
        :return:
        """
        self._stats_data.cmp = len(self._dist.a_star(self.grid, self.head.pos(), self._apple))

    def _place_snake(self) -> None:
        """
        Places the initial snake in the grid at the bottom center
        :return None:
        """
        # Set initial position
        row = self._rows // 2 + 2
        col = self._cols // 2
        # Add three blocks to the body
        for i in range(3):
            self._snake.add((row - i, col), GameDirection.UP)
            if i == 2:
                self.grid = (row - i, col, GridDict.HEAD.value)
            else:
                self.grid = (row - i, col, GridDict.BODY.value)

    def _spawn_apple(self) -> None:
        """
        Places the apple in a random free spot of the grid
        :return None:
        """
        row_indices, col_indices = np.where(self.grid == 0)
        indices = list(zip(row_indices, col_indices))
        index = indices[random.randint(0, len(indices) - 1)]
        self._apple = Cell(index[0], index[1])
        # Update the apple position in the grid
        self.grid = (self._apple.row, self._apple.col, GridDict.APPLE.value)
        # calculate minimal path from the head to the apple
        self._set_cmp()

    def _collision(self) -> bool:
        """
        Checks if the head is colliding with any of the possible objects (wall, body)
        :return bool: if there is a collision
        """
        # Collide against the walls
        if self.head.row > self._rows - 1 or self.head.row < 0 or self.head.col < 0 or self.head.col > self._cols - 1:
            return True
        # Collide against the body
        if self.head.pos() in self._snake.body_map:
            return True
        return False

    def _grow(self) -> bool:
        """
        Checks if the head is colliding with the apple
        :return bool:
        """
        if self.head.pos() == self._apple:
            return True
        return False

    def next_state(self, direction: GameDirection) -> None:
        """
        Calculates the next state of the game based on the current state and the input to the system
        :param direction:
        :return:
        """
        i, j = self.head.pos()
        turn = self.direction != direction
        score = False
        # Determine the next position of the head
        if direction == GameDirection.UP:
            i += Step.Y.value['up']
        elif direction == GameDirection.DOWN:
            i += Step.Y.value['down']
        elif direction == GameDirection.LEFT:
            j += Step.X.value['left']
        elif direction == GameDirection.RIGHT:
            j += Step.X.value['right']

        # Update head
        self._snake.add((i, j), direction)
        # Check collisions
        if self._collision():
            self._running = False
        # Kill process if to many steps are being taken
        if self._auto and self._moves_limit == 0:
            self._running = False
        # Update grid head position
        if self._running:
            self.grid = (self.head.row, self.head.col, GridDict.HEAD.value)
            self.grid = (self.head.prev.row, self.head.prev.col, GridDict.BODY.value)
            # Produce vision for auto-controller
            if self._auto:
                self._set_vision()
            # Update tail
            if not self._grow():
                self.grid = (self.tail.row, self.tail.col, GridDict.EMPTY.value)
                self._snake.pop()
                self._moves_limit -= 1
                self._stats_data.add_move(turn=turn, score=score)
                # Update current minimum path if necessary
                if self._stats_data.cmp == 0:
                    self._set_cmp()
            # Spawn new apple
            else:
                score = True
                self._stats_data.add_move(turn=turn, score=score)
                self._moves_limit = 150
                # Check if the game is completed else spawn a new apple
                self._completed = self._stats_data.completed()
                if not self._completed:
                    self._spawn_apple()
        else:
            self._stats_data.final_stats()

    def _set_vision(self) -> None:
        """
        Creates an array based on the vision over 8 axis (45º) every slice of four elements indicates with the 3 first
        element the type of object detect [wall, body, apple] and fourth one indicates the distance
        :return:
        """
        axis = self._dist.vision(self.grid)
        head_dir = NNDirection[self.head.dir[0].name].value
        tail_dir = NNDirection[self.tail.dir[0].name].value
        self._vision = np.concatenate((axis, head_dir, tail_dir))
