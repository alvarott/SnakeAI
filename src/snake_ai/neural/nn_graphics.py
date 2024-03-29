# This module implements a class that renders in pygame the state of a NN

# Author: Álvaro Torralba
# Date: 21/05/2023
# Version: 0.0.1

from snake_ai.snake import resources as rsc
from importlib import resources as rc
import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.surface import Surface


class NNGraph:

    # Class Constants
    BLUE_BASE = (0, 150, 255)
    BLUE_LINE_STR = (0, 202, 252)
    BLUE_LINE_MID = (9, 37, 43)
    BLUE_LINE_WEAK = (56, 67, 69)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    WIDTH = 795
    HEIGHT = 810

    def __init__(self, layers: list[int], input_labels: list[str] = None, output_labels: list[str] = None):
        """
        Constructor
        :param layers: list with number of nodes in each layer
        """
        if input_labels is not None and layers[0] != len(input_labels):
            raise ValueError("Labels length for input layer does not match with number of nodes")
        if output_labels is not None and layers[-1] != len(output_labels):
            raise ValueError("Labels length for output layer does not match with number of nodes")
        self._inputs = input_labels
        self._outputs = output_labels
        self._surface = Surface((NNGraph.WIDTH, NNGraph.HEIGHT), pygame.SRCALPHA)
        self._layers = layers
        self._y_mid = NNGraph.HEIGHT / 2
        self._rect = 20
        self._x_centers = self._x_indices()
        self._y_centers = self._y_indices()
        self._points = self._set_points()
        self._font = pygame.font.Font(rc.files(rsc).joinpath('fonts').joinpath("pixel_font.ttf").open('br'), 18)

    @property
    def surface(self):
        return self._surface

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
        length = (NNGraph.WIDTH - 260) / (len(self._layers) - 1)
        x_centers = []
        for i in range(len(self._layers)):
            x_centers.append(130 + (length * i))
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
            max_out = max(activations[i])
            for j in range(len(activations[i])):
                if activations[i][j] > max_out * 0.5:
                    line = NNGraph.BLUE_LINE_STR
                    current = points[j]
                    for node in self._points[i]:
                        pygame.draw.line(self._surface, line, node, current, 1)

    def _draw_nodes(self, input_values: list[float]):
        """
        Creates and static image with all the nodes
        :return surface: image that contains all the nodes rendering
        """
        font = pygame.font.Font(None, 16)
        layers = list(self._points.values())
        for i in range(len(layers)):
            nodes = layers[i]
            for j in range(len(nodes)):
                pygame.draw.circle(self._surface, NNGraph.BLUE_BASE, nodes[j], 8)
                pygame.draw.circle(self._surface, NNGraph.BLACK, nodes[j], 7.5)
                # Render input labels
                if i == 0 and self._inputs is not None:
                    text = f"{self._inputs[j]}  :  "
                    number = f"{input_values[j]:.2f}"
                    text_lb = font.render(text, True, NNGraph.WHITE)
                    num_lb = font.render(number, True, NNGraph.WHITE)
                    num_lb_rect = text_lb.get_rect(centery=nodes[j][1], left=nodes[j][0] - 35)
                    text_lb_rect = text_lb.get_rect(centery=nodes[j][1], right=num_lb_rect.left - 3)
                    self._surface.blit(text_lb, text_lb_rect)
                    self._surface.blit(num_lb, num_lb_rect)
                # Render output labels
                if i == len(layers) - 1:
                    text = f"{self._outputs[j]}"
                    label = font.render(text, True, NNGraph.WHITE)
                    lb_rect = label.get_rect(centery=nodes[j][1], left=nodes[j][0] + 15)
                    self._surface.blit(label, lb_rect)

    def draw_nn(self, input_values: list[float], activations: dict[int, list[float]] = None) -> Surface:
        """
        Combines all the nodes and connection to produce a final image of the current state of the NN
        :param activations: output of each layer after forward propagation
        :param input_values: the actual values that are being provided to the NN in that iteration
        :return surface: rendering of the NN
        """
        if max(self._layers) > 40 or len(self._layers) > 13:
            label = self._font.render("The neural network is too wide to be represented",
                                      True, NNGraph.WHITE)
            lb_rect = label.get_rect(center=(NNGraph.WIDTH / 2, NNGraph.HEIGHT / 2))
            self._surface.blit(label, lb_rect)
        else:
            self._surface = Surface((NNGraph.WIDTH, NNGraph.HEIGHT), pygame.SRCALPHA)
            self._draw_lines(activations)
            self._draw_nodes(input_values)
        return self._surface
