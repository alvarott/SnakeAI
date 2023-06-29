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
            #fitness = moves + (2 ** score + score**2.1*500)- (score**1.2*(0.25*moves)**1.25)
            # fitness = score ** 5 + (moves ** 2 - (0.7*turns) ** 1.8)/100
            #fitness = (score ** 5 + score ** 5 * efficiency + moves ** 2 )
            #fitness = moves ** 5 * efficiency
            fitness = score ** 5 + (moves / 100 ) ** 5
            #fitness = (moves ** 3 * efficiency) / 1000000
            return fitness
        results: dict[int, float] = {}
        max_fitness = 0
        best = {}
        for individual in individuals:
            max_score = individual[1]['max_score']
            score = individual[1]['score']
            effi = individual[1]['efficiency']
            moves = individual[1]['moves']
            turns = individual[1]['turns']
            fitness = function(max_score, score, effi, moves, turns)
            if fitness > max_fitness:
                max_fitness = fitness
                best = individual
            results[individual[0]] = function(max_score, score, effi, moves, turns)
        print(f'best = {max_fitness}, values = {best}')
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

    @staticmethod
    def coupling(parents: list[int]):
        if len(parents) % 2 != 0:
            raise ValueError('Pairing just support a even number of parents')
        population = list(parents)
        couples = []
        for _ in range(len(parents) // 2):
            p1 = random.randint(0, len(population) -1)
            p1 = population.pop(p1)
            p2 = random.randint(0, len(population) -1)
            p2 = population.pop(p2)
            couples.append((p1,p2))
        return couples

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

        Equation 9.9, 9.10, 9.11
        @TODO: Study the case
        """
        # Calculate Gamma (Eq. 9.11)
        rand = np.random.random(parent1.shape)
        gamma = np.empty(parent1.shape)
        gamma[rand <= 0.5] = (2 * rand[rand <= 0.5]) ** (1.0 / (eta + 1))  # First case of equation 9.11
        gamma[rand > 0.5] = (1.0 / (2.0 * (1.0 - rand[rand > 0.5]))) ** (1.0 / (eta + 1))  # Second case

        # Calculate Child 1 chromosome (Eq. 9.9)
        chromosome1 = 0.5 * ((1 + gamma) * parent1 + (1 - gamma) * parent2)
        # Calculate Child 2 chromosome (Eq. 9.10)
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


if __name__ == '__main__':

    scores = [
            (1, {'max_score': 97, 'score': 5, 'moves': 6, 'turns': 2, 'accuracy': 0, 'efficiency': 0}) ,
            (2, {'max_score': 97, 'score': 20, 'moves': 12, 'turns': 3, 'accuracy': 0, 'efficiency': 0}) ,
            (3, {'max_score': 97, 'score': 13, 'moves': 80, 'turns': 80, 'accuracy': 0, 'efficiency': 0}) ,
            (4, {'max_score': 97, 'score': 0, 'moves': 12, 'turns': 12, 'accuracy': 0, 'efficiency': 0}) ,
            (5, {'max_score': 97, 'score': 17, 'moves': 8, 'turns': 1, 'accuracy': 0, 'efficiency': 0}) ,
            (6, {'max_score': 97, 'score': 26, 'moves': 13, 'turns': 7, 'accuracy': 0, 'efficiency': 0}) ,
            (7, {'max_score': 97, 'score': 26, 'moves': 80, 'turns': 80, 'accuracy': 0, 'efficiency': 0}) ,
            (8, {'max_score': 97, 'score': 26, 'moves': 6, 'turns': 0, 'accuracy': 0, 'efficiency': 0}) ,
            (9, {'max_score': 97, 'score': 5, 'moves': 29, 'turns': 23, 'accuracy': 0, 'efficiency': 0}),
            (10, {'max_score': 97, 'score': 15, 'moves': 80, 'turns': 80, 'accuracy': 0, 'efficiency': 0}) ,
            (11, {'max_score': 97, 'score': 22, 'moves': 6, 'turns': 0, 'accuracy': 0, 'efficiency': 0}) ,
            (12, {'max_score': 97, 'score': 50, 'moves': 6, 'turns': 0, 'accuracy': 0.010309278350515464, 'efficiency': 1.0}) ,
            ]
    from snake_ai.snake.game_process.snake_batch_process import SnakeBatch
    import multiprocessing
    a = SnakeBatch(12, multiprocessing.cpu_count(), (10, 10), 'Manhattan', 40, 3, [2], bias=True, bias_init='he',
                   output_init='he',
                   hidden_init='he', output_act='softmax', hidden_act='tanh')
    b = a.get_population()
    fitness = GAFunctionFactory().get_function('fitness', 'fitness1')
    selection = GAFunctionFactory().get_function('selection', 'tournament')
    cross = GAFunctionFactory().get_function('crossover', 'whole_arithmetic')
    f = fitness(scores)
    sorted_dict = {k: v for k, v in sorted(f.items(), key=lambda item: item[1])}
    print(sorted_dict)
    s = selection(20, f,3)
    print(s)
    print(_Selection.coupling(s))




    individual = np.random.uniform(-1, 1, 10)
    individual2 = np.random.uniform(-1, 1, 10)
    print(list(individual))
    print(list(individual2),'\n')

    cross(individual, individual2, 0.4
          )
    print([0.0] * 4)

    for i in range(-1 , 2 , 2):
        print(i)