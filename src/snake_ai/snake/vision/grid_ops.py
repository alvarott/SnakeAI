# This module contains utils for grid operations used to feed the NN and statistical operations

# Author: Álvaro Torralba
# Date: 17/05/2023
# Version: 0.0.1

import numpy as np
from snake_ai.snake.enums import GridDict, NNVision, Step
from snake_ai.snake.vision.dist_factory import DistanceFactory
from queue import PriorityQueue


class GridOps:
    """
    This class provides the operations with in the grid where is displayed the snake board
    """
    def __init__(self, dist_calc: str):
        """
        Constructor
        :param dist_calc: flag to indicate which method to be used for calculating distances
        """
        self._dist_calc = DistanceFactory().get_instance(dist_calc)

    @staticmethod
    def _belong(dimensions: tuple[int, int], point: np.ndarray) -> bool:
        """
        Checks if a given point belong to and N x M grid
        :param dimensions: weight and height of the grid
        :param point: celll
        :return:
        """
        dim = np.array([dimensions[0]-1, dimensions[1]-1])
        if np.all(point >= 0) and (np.all((point <= dim) == True)):
            return True
        else:
            return False

    def _axis_vision(self, matrix: np.ndarray, center: np.ndarray, x_step: int = 0, y_step: int = 0) -> np.ndarray:
        """
        Calculates the distance from a cell along a scroll to find an object, used to find the distance between
        the head of the snake and the rest of possible objects
        :param matrix: grid where to calculate the distance
        :param center: cells from where to calculate the distance
        :param x_step: displacement over x at each iteration
        :param y_step: displacement over y at each iteration
        :return vision: an array of four elements where the 3 first digits indicates the type of object
        found in the axis [wall, body, apple] and the fourth one the distance to it
        """
        step = np.array([y_step, x_step])
        ref = center + step
        collision = False
        vision = []
        # Loop locking for collisions
        while GridOps._belong(matrix.shape, ref):
            value = matrix[ref[0], ref[1]]
            if value in (GridDict.BODY.value, GridDict.APPLE.value):
                collision = True
                dist = self._dist_calc.dist(matrix.shape, center, ref)
                vision = list(NNVision[GridDict(value).name].value)
                vision.append(dist)
                break
            else:
                ref = ref + step
        # If a position outside the grid is reached without finding a collision the distance to the wall is calculated
        # instead
        if not collision:
            dist = self._dist_calc.dist(matrix.shape, center, ref - step)
            vision = list(NNVision.WALL.value)
            vision.append(dist)
        return np.array(vision)

    def vision(self, matrix: np.ndarray) -> np.ndarray:
        """
        Uses the method bellow over 8 axes around the origin cell to check for collisions
        :param matrix: grid where to look at
        :return: an array with the vision over each axis concatenated
        """
        center_y, center_x = np.where(matrix == GridDict.HEAD.value)
        center = np.array([center_y[0], center_x[0]])
        vision = np.empty(0)
        # Calculate te distances in all axes
        for step_x in Step.X.value.values():
            for step_y in Step.Y.value.values():
                if step_x == 0 and step_y == 0:
                    continue
                else:
                    vision = np.append(vision, self._axis_vision(matrix, center, step_x, step_y))
        return vision

    @staticmethod
    def _graph(matrix: np.ndarray) -> dict[tuple[int, int], list[tuple[int, int]]]:
        """
        It produces a dictionary that represents a graph that in turn represent the grid
        :param matrix: grid on which the graph is produced
        :return:
        """
        edges = [Step.X.value['right'], Step.X.value['left']]
        x, y = matrix.shape
        max_cell = (x - 1, y - 1)
        graph = {}
        neighbours = []
        valid_neighbours = []
        for i in range(x):
            for j in range(y):
                if matrix[i, j] != 1:
                    for w in range(len(edges)):
                        neighbours.append((i, j + edges[w]))
                        neighbours.append((i + edges[w], j))
                    for neighbour in neighbours:
                        if ((0 <= neighbour[0] <= max_cell[0]) and (0 <= neighbour[1] <= max_cell[1])) and matrix[neighbour] != 1:
                            valid_neighbours.append(neighbour)
                    graph.update([((i, j), list(valid_neighbours))])
                    neighbours.clear()
                    valid_neighbours.clear()
        return graph

    def a_star(self, matrix: np.ndarray, start_cell: tuple[int, int], target_cell: tuple[int, int]):
        """
        This function implements the A* algorithm over a graph between to points
        :param matrix: grid where to calculate the path
        :param start_cell: origin cell
        :param target_cell: target cell
        :return path: the path found between the two cells if exists
        """

        def upd_score(g_score: float, node: tuple[int, int], predecessor: tuple[int, int] = None):
            nonlocal path, processed, open_hash, f_scores, g_scores, open
            if g_score < g_scores[node]:
                g_scores[node] = g_score
                f_scores[node] = g_score + self._dist_calc.dist(grid_dim, np.array(start_cell), np.array(target_cell))
                if predecessor is not None:
                    path[node] = predecessor
                if node not in open_hash:
                    processed += 1
                    open.put((f_scores[node], processed, node))
                    open_hash.add(node)

        def path_reverse(path: dict[tuple[int, int], tuple[int, int]]):
            current = target_cell
            start = start_cell
            rev_path = []
            while current != start:
                rev_path.append(path[current])
                current = path[current]
            rev_path.reverse()
            return rev_path

        graph = self._graph(matrix)
        grid_dim = matrix.shape
        path = {}
        processed = -1
        open = PriorityQueue()
        open_hash = set()
        f_scores = {node: float('inf') for node in graph.keys()}
        g_scores = {node: float('inf') for node in graph.keys()}
        # Insert starting node
        upd_score(g_score=0, node=start_cell)
        # Process neighbours
        while not open.empty():
            node = open.get()[2]
            open_hash.remove(node)
            tmp_score = g_scores[node] + 1
            # Check if the target node was reached
            if node == target_cell:
                return path_reverse(path)
            # Process all adjacent nodes
            for neighbour in graph[node]:
                upd_score(g_score=tmp_score, node=neighbour, predecessor=node)
        return []
