# This module is intended to contain all the custom data structures necessary for the snake logic

# Author: Álvaro Torralba
# Date: 14/05/2023
# Version: 0.0.1

from dataclasses import dataclass
from snake_ai.snake.enums import GameDirection


class Node:
    """
    This class represent the minimal unit(block) that forms the Snake
    """
    def __init__(self, row: int, column: int, direction: GameDirection, previous=None, next=None):
        """
        Constructor
        :param row: row that occupied in the grid matrix
        :param column: column that occupied in the grid matrix
        :param direction: direction where is moving the block
        :param previous: previous node
        :param next: next node
        """
        self.row = row
        self.col = column
        self._dir = [direction, GameDirection.NONE]
        self.prev = previous
        self.next = next

    def __eq__(self, other) -> bool:
        if isinstance(other, Node):
            return self.row == other.row and self.col == other.col and self.dir == other.dir
        else:
            raise ValueError(f'{type(self)} and {type(other)} are not comparable')

    def __str__(self) -> str:
        return f'[({self.row},{self.col}) : {self.dir}] --> '

    @property
    def dir(self):
        return self._dir

    @dir.setter
    def dir(self, new_dir: tuple[GameDirection, GameDirection]) -> None:
        self._dir = [new_dir[0], new_dir[1]]

    def pos(self) -> tuple[int, int]:
        """
        Produces a tuple with (x, y) position of the node
        :return pos: cell index of the node
        """
        return self.row, self.col


class BlockLinkedList:
    """
    This class represents and holds the entire snake body information within the grid matrix
    """
    def __init__(self):
        self.head: Node | None = None
        self.tail: Node | None = None
        self.body_map: list[tuple[int, int]] = []
        self.length: int = 0

    def __str__(self) -> str:
        if self.length != 0:
            current = self.head
            string = ''
            while True:
                string += current.__str__()
                if current.prev is None:
                    break
                else:
                    current = current.prev
            return string
        else:
            return '[]'

    def add(self, position: tuple[int, int], direction: GameDirection) -> None:
        """
        Adds a new block to the current body of the snake
        :param position: position in the grid where to place the block
        :param direction: direction in which the block is moving
        :return:
        """
        new_head = Node(row=position[0], column=position[1], direction=direction)
        if self.length == 0:
            self.tail = new_head
            self.head = new_head
        else:
            self.body_map.insert(0, (self.head.row, self.head.col))
            new_head.prev = self.head
            self.head.next = new_head
            self.head = new_head
            # Update neck direction
            if self.head.dir != self.head.prev.dir:
                self.head.prev.dir[1] = self.head.dir[0]
        self.length += 1

    def pop(self) -> None:
        """
        Pops the tail of the linked list
        :return None:
        """
        # Update tail position and direction
        current = self.tail.next
        current.prev = None
        self.tail = current
        current.dir = (current.next.dir[0], GameDirection.NONE)
        self.body_map.pop()
        self.length -= 1


@dataclass
class StatsStruct:
    """
    Data class to hold the performance metrics
    """
    max_score: int
    score: int
    total_moves: int
    moves: int
    mpa: list[float]  # Moves per apple
    cmp: int  # Current minimal path
    turns: int
    accuracy: float
    efficiency: float

    def __init__(self, rows: int, cols: int):
        """
        Constructor
        :param rows: number of rows in the grid
        :param cols: number of columns in the grid
        """
        self.score = 0
        self.max_score = (rows * cols) - 3
        self.moves = 0
        self.total_moves = 0
        self.turns = 0
        self.cmp = -1
        self.mpa = []
        self.accuracy = 0
        self.efficiency = 0

    def __str__(self) -> str:
        string = f"""
        Final score : {self.score}
        Total moves : {self.total_moves}
        Total turns : {self.turns}
        Accuracy : {self.accuracy}
        Efficiency : {self.efficiency}
        """
        return string

    def _add_mpa(self) -> None:
        """
        Adds a new entry to the "moves per apple" list using the current moves and the current min path
        :return None:
        """
        if self.cmp > 0:
            self.mpa.append(1 / (self.moves / self.cmp))

    def _set_efficiency(self) -> None:
        """
        Calculates the efficiency average ratio at the point that is called
        :return efficiency: efficiency ratio
        """
        if len(self.mpa) != 0:
            self.efficiency = sum(self.mpa) / len(self.mpa)

    def _set_accuracy(self) -> None:
        """
        Calculates the accuracy ratio
        :return accuracy:
        """
        if self.score != 0:
            self.accuracy = self.score / self.max_score

    def add_move(self, turn: bool, score: bool) -> None:
        """
        Aggregates one move to the overall registering if there was turn and score
        :param turn: bool to indicate if there was a turn
        :param score: bool to indicate if the score must be increase
        :return:
        """
        self.total_moves += 1
        self.moves += 1
        if turn:
            self.turns += 1
        if score:
            self._add_mpa()
            self.score += 1
            self.moves = 0

    def completed(self):
        """
        Checks if the maximal punctuation has been reached
        :return bool:
        """
        self._set_efficiency()
        self._set_accuracy()
        if self.score == self.max_score:
            return True
        return False

    def get_stats(self) -> dict[str, int | float]:
        """
        Produces a dictionary with all the stats
        :return dict:
        """
        return dict({'max_score': self.max_score,'score': self.score, 'moves': self.total_moves, 'turns': self.turns,
                     'accuracy': self.accuracy, 'efficiency': self.efficiency})
