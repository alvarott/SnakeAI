# This module is intended to contain the classes that provides the necessary functions to perform GA operations

# Author: Álvaro Torralba
# Date: 28/05/2023
# Version: 0.0.1

from snake_ai.function_factory_abc import FunctionFactory
import random
import numpy as np


class GAFunctionFactory(FunctionFactory):
    """
    This class is meant to be a function factory for the GAs
    """
    def __init__(self):
        super().__init__(globals(), __name__)


class _Fitness:
    """
    This class contains different implementations of the fitness function
    """
    @staticmethod
    def fitness1(individuals: list[tuple[int, dict[str, float]]]) -> dict[int, float]:
        """
        Calculates the fitness over all snake individuals
        :param individuals: lists with individuals id's and them performance stats
        :return results: dictionary with the individual id and its fitness value pairs
        """
        def function(max_score: float, score: float, efficiency: float, moves: float):
            """
            Auxiliary function that contains the mathematical logic of the fitness function
            :param max_score: maximum possible score
            :param score: real score
            :param efficiency: efficiency as the average of steps taken in relation with the minimum possible path
            :param moves: number of total moves
            :return fitness:  fitness value
            """
            fitness = (score ** 5 + (moves / 100) ** 5)
            extra = 0
            if score == max_score:
                extra = (score * efficiency) ** 5
            return fitness + extra

        results: dict[int, float] = {}
        # Calculate population's fitness
        for individual in individuals:
            max_score = individual[1]['max_score']
            score = individual[1]['score']
            effi = individual[1]['efficiency']
            moves = individual[1]['moves']
            fitness = function(max_score, score, effi, moves)
            results[individual[0]] = fitness
        return results


class _Selection:
    """
    This class is meant to contain all the different selection techniques over a population
    """
    @staticmethod
    def stochastic(num_parents: int, population_fitness: dict[int, float]) -> list[int]:
        """
        Stochastic universal sampling
        :param num_parents: number of parents to be selected
        :param population_fitness: list of individuals fitness and their ids
        :return parents: list of the selected parents for reproduction
        """
        fitness_sum = sum(individual for individual in population_fitness.values())
        normalized_fitness = [individual / fitness_sum for individual in population_fitness.values()]
        cumulative_fitness = [sum(normalized_fitness[:i+1]) for i in range(len(normalized_fitness))]
        step = 1 / num_parents
        pointer = random.uniform(0, step)
        index = 0
        parents = []
        while len(parents) < num_parents:
            if pointer <= cumulative_fitness[index]:
                while pointer <= cumulative_fitness[index]:
                    parents.append(index + 1)
                    pointer += step
            index += 1
        return parents

    @staticmethod
    def roulette_wheel(num_parents: int, population_fitness: dict[int, float]) -> list[int]:
        """
         Roulette wheel sampling
         :param num_parents: number of parents to selected
         :param population_fitness: list of individuals fitness and their ids
         :return parents: list of the selected parents for reproduction
         """
        fitness_sum = sum(individual for individual in population_fitness.values())
        normalized_fitness = [individual / fitness_sum for individual in population_fitness.values()]
        cumulative_fitness = [sum(normalized_fitness[:i + 1]) for i in range(len(normalized_fitness))]
        parents = []
        while len(parents) < num_parents:
            index = 1
            pointer = 0
            selected = random.uniform(0, 1)
            for fitness in cumulative_fitness:
                pointer += fitness
                if pointer >= selected:
                    parents.append(index)
                    break
                index += 1
        return parents

    @staticmethod
    def tournament(num_parents: int, population_fitness: dict[int, float], tournament_size: int) -> list[int]:
        """
        Tournament sampling
        :param num_parents: number of parents to be selected
        :param population_fitness: parents fitness and its ids
        :param tournament_size: number of individuals by tournament
        :return: list of the selected parents for reproduction
        """
        if tournament_size < 2:
            raise ValueError('Tournament size should equal or higher than 2')
        parents = []
        for _ in range(num_parents):
            contenders = _Selection.stochastic(tournament_size, population_fitness)
            winner = max(contenders, key=lambda fitness: population_fitness[fitness])
            parents.append(winner)
        return parents


class _Crossover:
    """
    This class is meant to contain all the different reproduction techniques over a population
    """
    @staticmethod
    def uniform(parent1: np.ndarray, parent2: np.ndarray) -> list[np.ndarray]:
        """
        Uniform crossover
        :param parent1:
        :param parent2:
        :return: a list with the new two individuals
        """
        children1 = parent1.copy()
        children2 = parent2.copy()
        random_vector = np.random.uniform(0, 1, size=parent1.shape)
        children1[random_vector > 0.5] = parent2[random_vector > 0.5]
        children2[random_vector > 0.5] = parent1[random_vector > 0.5]
        return [children1, children2]

    @staticmethod
    def sp_arithmetic(parent1: np.ndarray, parent2: np.ndarray, alpha: float) -> list[np.ndarray]:
        """
        Single point arithmetic crossover
        :param parent1:
        :param parent2:
        :param alpha: range[0-1] factor used to determine how much influence has a parent in one of the children genes
        :return: a list with the new two individuals
        """
        cross_point = random.randint(1, len(parent1) - 1)
        blended_p1 = parent1[cross_point:] * alpha + parent2[cross_point:] * (1 - alpha)
        blended_p2 = parent2[cross_point:] * alpha + parent1[cross_point:] * (1 - alpha)
        children1 = np.concatenate((parent1[:cross_point], blended_p1))
        children2 = np.concatenate((parent2[:cross_point], blended_p2))
        return [children1, children2]

    @staticmethod
    def whole_arithmetic(parent1: np.ndarray, parent2: np.ndarray, alpha: float) -> list[np.ndarray]:
        """
        Whole arithmetic crossover
        :param parent1:
        :param parent2:
        :param alpha: [0-1] factor used to determine how much influence has a parent in one of the children genes
        :return: a list with the new two individuals
        """
        children1 = parent1 * alpha + parent2 * (1 - alpha)
        children2 = parent2 * alpha + parent1 * (1 - alpha)
        return [children1, children2]

    @staticmethod
    def sbx(parent1: np.ndarray, parent2: np.ndarray, eta: float) -> list[np.ndarray, np.ndarray]:
        """
        This crossover is specific to floating-point representation.
        Simulate behavior of one-point crossover for binary representations.

        For large values of eta there is a higher probability that offspring will be created near the parents.
        For small values of eta, offspring will be more distant from parents
        Source :
        """
        # Calculate Gamma
        rand = np.random.random(parent1.shape)
        gamma = np.empty(parent1.shape)
        gamma[rand <= 0.5] = (2 * rand[rand <= 0.5]) ** (1.0 / (eta + 1))  # First case
        gamma[rand > 0.5] = (1.0 / (2.0 * (1.0 - rand[rand > 0.5]))) ** (1.0 / (eta + 1))  # Second case

        # Calculate Child 1 chromosome
        chromosome1 = 0.5 * ((1 + gamma) * parent1 + (1 - gamma) * parent2)
        # Calculate Child 2 chromosome
        chromosome2 = 0.5 * ((1 - gamma) * parent1 + (1 + gamma) * parent2)

        return [chromosome1, chromosome2]


class _Mutation:
    """
    This class contains all the different mutation techniques over individuals
    """
    @staticmethod
    def gaussian(individual: np.ndarray, mutation_rate: float, sigma: float) -> np.ndarray:
        """
        Gaussian mutation
        :param individual: individual to which to apply the mutation
        :param mutation_rate: probability that has each gene to mutate
        :param sigma: variance for the gaussian distribution with mean 0
        :return: mutated individual
        """
        random_vector = np.random.uniform(0, 1, individual.shape)
        mask = random_vector <= mutation_rate
        mutation = np.random.normal(loc=0, scale=sigma, size=individual.shape)
        individual = np.where(mask, individual + mutation, individual)
        return individual
