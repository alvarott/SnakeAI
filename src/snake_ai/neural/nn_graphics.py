# This module implements a class that renders in pygame the state of a NN

# Author: Álvaro Torralba
# Date: 21/05/2023
# Version: 0.0.1

from pygame import Surface
import pygame


class NNGraph:

    # Class Constants
    BLUE_BASE = (0, 150, 255)
    BLUE_LINE_STR = (0, 202, 252)
    BLUE_LINE_MID = (9, 37, 43)
    BLUE_LINE_WEAK = (56, 67, 69)
    BLACK = (0, 0, 0)
    WIDTH = 900
    HEIGHT = 900

    def __init__(self, layers: list[int]):
        """
        Constructor
        :param layers: list with number of nodes in each layer
        """
        self._surface = Surface((NNGraph.WIDTH, NNGraph.HEIGHT))
        self._layers = layers
        self._y_mid = NNGraph.HEIGHT / 2
        self._rect = 20
        self._x_centers = self._x_indices()
        self._y_centers = self._y_indices()
        self._points = self._set_points()
        self._nodes = self._draw_nodes()

    def _set_points(self) -> dict[int, list[tuple[float, float]]]:
        """
        Sets a dictionary with the x,y coordinates center of each node
        :return points: dictionary with the coordinates of each layer
        """
        points = {}
        p_layer = []
        for i in range(len(self._x_centers)):
            for y in self._y_centers[i]:
                p_layer.append((self._x_centers[i], y))
            sorted_list = sorted(p_layer, key=lambda x: (x[0], x[1]))
            points[i] = list(sorted_list)
            sorted_list.clear()
            p_layer.clear()
        return points

    def _x_indices(self) -> list[float]:
        """
        Sets the axes where to place the layers over the 'x' axis
        :return x_centers: list of centers
        """
        length = NNGraph.WIDTH / (len(self._layers) + 1)
        x_centers = []
        for i in range(1, len(self._layers) + 1):
            x_centers.append(length * i)
        return x_centers

    def _y_indices(self) -> dict[int, list[float]]:
        """
        Sets the position over the 'y' axis where to place every node
        :return y_centers: y position of each center node in each layer
        """
        y_centers = {}
        for i in range(len(self._layers)):
            layer = self._layers[i]
            centers = []
            # If even number of nodes
            if layer % 2 != 0:
                centers.append(self._y_mid)
                for j in range(1, ((layer - 1) // 2) + 1):
                    centers.extend([(self._y_mid + self._rect * j), (self._y_mid - self._rect * j)])
            # If odd number of nodes
            else:
                offset = 10
                for j in range((layer // 2)):
                    centers.extend([(self._y_mid + offset) + (self._rect * j), (self._y_mid - offset) - (self._rect * j)])
            y_centers[i] = list(centers)
            centers.clear()
        return y_centers

    def _draw_lines(self, activations: dict[int, list[float]]) -> None:
        """
        Draws the connection between nodes that have been activated
        :param activations: output of each layer after forward propagation
        :return:
        """
        for i in range(len(activations)):
            points = self._points[i + 1]
            for j in range(len(activations[i])):
                if activations[i][j] > 0:
                    if 0 < activations[i][j] < 0.3:
                        line = NNGraph.BLUE_LINE_WEAK
                    elif 0.3 < activations[i][j] < 0.6:
                        line = NNGraph.BLUE_LINE_MID
                    else:
                        line = NNGraph.BLUE_LINE_STR
                    current = points[j]
                    for node in self._points[i]:
                        pygame.draw.line(self._surface, line, node, current, 1)

    def _draw_nodes(self) -> Surface:
        """
        Creates and static image with all the nodes
        :return surface: image that contains all the nodes rendering
        """
        surface = Surface((NNGraph.WIDTH, NNGraph.HEIGHT))
        for nodes in self._points.values():
            for node in nodes:
                pygame.draw.circle(surface, NNGraph.BLUE_BASE, node, 8)
                pygame.draw.circle(surface, NNGraph.BLACK, node, 7.5)
        return surface

    def draw_nn(self, activations: dict[int, list[float]]) -> Surface:
        """
        Combines all the nodes and connection to produce a final image of the current state of the NN
        :param activations: output of each layer after forward propagation
        :return surface: rendering of the NN
        """
        self._surface.fill(NNGraph.BLACK)
        self._draw_lines(activations)
        self._surface.blit(self._nodes, (0, 0))
        return self._surface
