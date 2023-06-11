# This module implements the class that performs the genetic process over a population
# Does not provide an initialization method because this task is performed by the NN

# Author: Álvaro Torralba
# Date: 29/05/2023
# Version: 0.0.1

from snake_ai.genetic.genetic_functions import GAFunctionFactory
import numpy as np
import math
import random


class GA:
    """
    Class intended to perform the genetic process
    """
    def __init__(self, selection: str, fitness: str, crossover: str, crossover_rate: float, mutation: str,
                 mutation_rate: float):
        self._factory = GAFunctionFactory()
        self._selection = self._factory.get_function('selection',selection)
        self._fitness = self._factory.get_function('fitness', fitness)
        self._crossover = self._factory.get_function('crossover', crossover)
        self._mutation = self._factory.get_function('mutation', mutation)
        self._mutation_rate = mutation_rate
        self._crossover_rate = crossover_rate

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

    def next_gen(self, population: dict[int, np.ndarray], scores: list[tuple[int, dict[str, float]]],
                 offspring: int,  selection_pressure: float = None, sigma: float = None):
        # Calculate population fitness
        population_fitness = self._fitness(scores)
        # Select parents and form couples
        if offspring % 2 != 0:
            offspring += 1
        parents = self._selection(num_parents=offspring, population_fitness=population_fitness)
        couples = GA.coupling(parents)
        parents = {key: population[key] for key in parents}
        # Produce children
        children = []
        for pair in couples:
            if random.uniform(0,1) < self._crossover_rate:
                children.extend(self._crossover(parents[pair[0]], parents[pair[1]], 0.4))
            else:
                children.append(parents[pair[0]])
                children.append(parents[pair[1]])
        # Mutate children
        for i in range(len(children)):
           children[i] = self._mutation(children[i], self._mutation_rate, sigma)
        # Replacement
        sorted_population = [k for k, v in sorted(population_fitness.items(), key=lambda item: item[1])]
        print(population_fitness[sorted_population[-1]])
        for i in range(offspring):
            population[sorted_population[i]] = children[i]
        return sorted_population[-1]


if __name__ == '__main__':
    from snake_ai.snake.game_process.snake_batch_process import SnakeBatch
    import multiprocessing
    c = SnakeBatch(6, multiprocessing.cpu_count(), (10, 10), 'Manhattan', 32, 3, [2], bias=True, bias_init='he',
                   output_init='he',
                   hidden_init='he', output_act='softmax', hidden_act='relu')
    b = c.get_population()
    a = GA(selection='tournament', fitness='fitness1', crossover='whole_arithmetic', crossover_rate=0.9, mutation='gaussian', mutation_rate=0.05)
    c.run()
    scores = c.results

    for i, j in b.items():
        print(i, list(j))

    print(a.next_gen(population=b, scores=scores, offspring=4, selection_pressure=1.7, sigma=0.5))
    print('\n')
    for i, j in b.items():
        print(i, list(j))


