# This module is intended to contain the classes that implements different initializations methods
# of n-dimensional arrays and Activations functions applied element wise to the n-dimensional arrays

# Author: Álvaro Torralba
# Date: 18/05/2023
# Version: 0.0.1

from snake_ai.function_factory_abc import FunctionFactory
import math
import numpy as np


class NNFunctionFactory(FunctionFactory):
    """
    This class is meant to return an initialization or activation function by providing its name to a getter method
    """
    def __init__(self):
        super().__init__(globals(), __name__)


class _Activation:
    """
    This class provides different activation functions applied element wise to numpy n-dimensional arrays.
    """

    @staticmethod
    def relu(matrix: np.ndarray) -> np.ndarray:
        """
        ReLU activation function
        :param matrix: matrix on which to apply the ReLU
        :return relu: a matrix with the same dimensions with the relu function applied to each element
        """
        relu = np.maximum(0, matrix)
        return relu

    @staticmethod
    def sigmoid(matrix: np.ndarray) -> np.ndarray:
        """
        Sigmoid activation function
        :param matrix: matrix on which to apply sigmoid
        :return relu: a matrix with the same dimensions with the sigmoid function applied element wise
        """
        return 1 / (1 + np.exp(-matrix))

    @staticmethod
    def tanh(matrix: np.ndarray) -> np.ndarray:
        """
        Hyperbolic tangent activation function
        :param matrix: matrix on which to apply tanh
        :return relu: a matrix with the same dimensions with the tanh function applied element wise
        """
        return np.tanh(matrix)

    @staticmethod
    def softmax(matrix: np.ndarray) -> np.ndarray:
        """
        Softmax activation function
        :param matrix: matrix on which to apply softmax
        :return relu: a matrix with the same dimensions with the softmax function applied element wise
        """
        #shifted_matrix = matrix - np.max(matrix)
        exp = np.exp(matrix)
        return exp / np.sum(exp)


class _Initialization:
    """
    This class provides different initialization functions for producing n-dimensional arrays
    """

    @staticmethod
    def glorot(dimensions: tuple[int, int]) -> np.ndarray:
        """
        Initializes a [1-2]-dimensional array with using Glorot's method
        :param dimensions: rows and columns of the [1-2]-dimensional array
        :return: initialized matrix
        """
        if 0 < len(dimensions) < 3:
            if dimensions[0] > 0 and dimensions[1] > 0:
                fan_in, fan_out = dimensions[0], dimensions[1]
                stddev = math.sqrt(2.0 / (fan_in + fan_out))
                return np.random.normal(loc=0.0, scale=stddev, size=dimensions)
        return np.empty(0)

    @staticmethod
    def he(dimensions: tuple[int, int]) -> np.ndarray:
        """
        Initializes a [1-2]-dimensional array with using He's method
        :param dimensions: rows and columns of the [1-2]-dimensional array
        :return: initialized matrix
        """
        if 0 < len(dimensions) < 3:
            if dimensions[0] > 0 and dimensions[1] > 0:
                stddev = math.sqrt(2.0 / dimensions[0])
                return np.random.normal(loc=0.0, scale=stddev, size=dimensions)
        return np.empty(0)

    @staticmethod
    def lecun(dimensions: tuple[int, int]) -> np.ndarray:
        """
        Initializes a [1-2]-dimensional array with using LeCun's method
        :param dimensions: rows and columns of the [1-2]-dimensional array
        :return: initialized matrix
        """
        if 0 < len(dimensions) < 3:
            if dimensions[0] > 0 and dimensions[1] > 0:
                stddev = math.sqrt(1.0 / dimensions[0])
                return np.random.normal(loc=0.0, scale=stddev, size=dimensions)
        return np.empty(0)

    @staticmethod
    def zero(dimensions: tuple[int, int]) -> np.ndarray:
        """
        Initializes a [1-2]-dimensional array with zero values
        :param dimensions: rows and columns of the [1-2]-dimensional array
        :return: initialized matrix
        """
        if 0 < len(dimensions) < 3:
            if dimensions[0] > 0 and dimensions[1] > 0:
                return np.zeros(dimensions)
        return np.empty(0)
