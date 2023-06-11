# This module is intended to contain the class that provides with different implementations of the fitness function

# Author: Álvaro Torralba
# Date: 28/05/2023
# Version: 0.0.1

from snake_ai.function_factory_abc import FunctionFactory
import math


class FitnessFunctionFactory(FunctionFactory):
    """
    This class is meant to return a fitness function by providing its name to a getter method
    """
    def __init__(self):
        super().__init__(globals(), __name__)


class _Fitness:
    """
    This is meant to contain different implementations of the fitness function
    """
    @staticmethod
    def fitness1(individuals: list[tuple[int, dict[str, float]]]) -> dict[int, float]:
        """
        Calculates the fitness over all snake individuals
        :param individuals: lists with individuals id's and them performance stats
        :return results: dictionary with the individual id and its fitness value pairs
        """
        def function(max_score: float, score: float, efficiency: float, moves: float, turns: float):
            """
            Auxiliary function that contains the mathematical logic of the fitness function
            :param max_score: maximum possible score
            :param score: real score
            :param efficiency: efficiency as the average of steps taken in relation with the minimum possible path
            :param moves: number of total moves
            :param turns: number of total turns
            :return fitness:  fitness value
            """
            fitness = score ** 3.5 + (efficiency * max_score) ** 3.2 + (math.log(moves - turns * 0.7) - math.log(10 * 6)
                                                                        + max_score) ** 3.3
            return fitness

        results: dict[int, float] = {}
        for individual in individuals:
            max_score = individual[1]['max_score']
            score = individual[1]['score']
            effi = individual[1]['efficiency']
            moves = individual[1]['moves']
            turns = individual[1]['turns']
            results[individual[0]] = function(max_score, score, effi, moves, turns)
        return results
