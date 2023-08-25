# This module implements the class that performs the genetic process over a population
# Does not provide an initialization method because this task is performed by the NN

# Author: Álvaro Torralba
# Date: 29/05/2023
# Version: 0.0.1

from snake_ai.genetic.genetic_functions import GAFunctionFactory
import numpy as np
import random


class GA:
    """
    Class intended to perform the genetic process
    """
    def __init__(self, selection: str, fitness: str, crossover: str, crossover_rate: float, mutation: str,
                 mutation_rate: float, offspring: int, crossover_params: dict, mutations_params: dict,
                 selection_params: dict):
        self._factory = GAFunctionFactory()
        self._selection = self._factory.get_function('selection', selection)
        self._fitness = self._factory.get_function('fitness', fitness)
        self._crossover = self._factory.get_function('crossover', crossover)
        self._mutation = self._factory.get_function('mutation', mutation)
        self._mutation_rate = mutation_rate
        self._crossover_rate = crossover_rate
        self._offspring = offspring
        self._crossover_params = crossover_params
        self._mutation_params = mutations_params
        self._selection_params = selection_params

    @staticmethod
    def coupling(parents: list[int]):
        if len(parents) % 2 != 0:
            raise ValueError('Pairing just support a even number of parents')
        population = list(parents)
        couples = []
        for _ in range(len(parents) // 2):
            p1 = random.randint(0, len(population) - 1)
            p1 = population.pop(p1)
            p2 = random.randint(0, len(population) - 1)
            p2 = population.pop(p2)
            couples.append((p1, p2))
        return couples

    def next_gen(self, population: dict[int, np.ndarray], scores: list[tuple[int, dict[str, float]]]):
        # Calculate population fitness
        population_fitness = self._fitness(scores)
        # Select parents and form couples
        if self._offspring % 2 != 0:
            offspring = self._offspring + 1
        else:
            offspring = self._offspring
        parents = self._selection(num_parents=offspring, population_fitness=population_fitness,
                                  **self._selection_params)
        couples = GA.coupling(parents)
        parents = {key: population[key] for key in parents}
        # Produce children
        children = []
        for pair in couples:
            if random.uniform(0, 1) < self._crossover_rate:
                children.extend(self._crossover(parents[pair[0]], parents[pair[1]], **self._crossover_params))
            else:
                children.append(parents[pair[0]])
                children.append(parents[pair[1]])
        # Mutate children
        for i in range(len(children)):
            children[i] = self._mutation(children[i], self._mutation_rate, **self._mutation_params)
        # Replacement
        sorted_population = [k for k, v in sorted(population_fitness.items(), key=lambda item: item[1])]
        for i in range(self._offspring):
            population[sorted_population[i]] = children[i]
        return sorted_population[-1], population_fitness
