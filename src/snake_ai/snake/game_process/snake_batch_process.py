# This module contains the class that can create and run multiple snake base processes in parallel

# Author: Álvaro Torralba
# Date: 27/05/2023
# Version: 0.0.1

from snake_ai.snake.game_process.snake_ai_process import SnakeAI
from snake_ai.data import Population
import multiprocessing
import numpy as np


class SnakeBatch:
    """This class is intended to create, maintain and run several Snake base AI controlled processes"""

    def __init__(self, individuals: int, cpu_cores: int, size: tuple[int, int], input: int, vision: str,
                 output: int, hidden: list[int], output_init: str, bias: bool, hidden_init: str,
                 output_act: str, hidden_act: str, bias_init: str = 'zero'):
        SnakeAI.reset_obj_counter()
        self._processes: dict[int, SnakeAI] = {SnakeAI.obj_counter:
                                               SnakeAI(size=size, input=input, output=output, hidden=hidden, bias=bias,
                                                       bias_init=bias_init, output_init=output_init,
                                                       hidden_init=hidden_init, output_act=output_act,
                                                       hidden_act=hidden_act, vision=vision)
                                               for _ in range(individuals)}
        self._cpu_cores = cpu_cores
        self.results = {}
        self._pop_dat = Population()
        self._population = {
            self._pop_dat.vision[0]: vision,
            self._pop_dat.hidden[0]: hidden,
            self._pop_dat.hidden_init[0]: hidden_init,
            self._pop_dat.hidden_act[0]: hidden_act,
            self._pop_dat.output_init[0]: output_init,
            self._pop_dat.output_act[0]: output_act,
            self._pop_dat.bias[0]: bias,
            self._pop_dat.bias_init[0]: bias_init,
            self._pop_dat.population[0]: self.get_population_brains()
        }

    @property
    def population(self):
        self._population['population'] = self.get_population_brains()
        return self._population

    def _run(self, individual: SnakeAI) -> tuple[int, dict[str, float]]:
        """
        Calls an individual execution
        :param individual: individual to be executed
        :return stats: id of the individual and a dict containing the performance stats
        """
        return individual.simulate()

    def run(self) -> None:
        """
        Runs all the individual and collects all the performance results
        :return:
        """
        pool = multiprocessing.Pool(processes=self._cpu_cores)
        results = pool.map(self._run, [process for process in list(self._processes.values())])
        pool.close()
        pool.join()
        self.results = results

    def get_individual(self, identifier: int) -> dict:
        """
        Returns an individual object from the batch
        :param identifier: individual id
        :return: individual object
        """
        return {'vision': self._processes[identifier].vision, 'model': self._processes[identifier].controller.brain}

    def get_population_brains(self) -> dict[int, np.ndarray]:
        """
        Produces a dictionary with the id and the codification of each individual
        :return population: the dictionary just described
        """
        population: dict[int, np.ndarray] = {}
        for id, value in self._processes.items():
            population[id] = value.controller.nn_code
        return population

    def update_brains(self, brains: dict[int, np.ndarray]) -> None:
        """
        Updates all the NN in the individuals in the batch
        :param brains: list of array codifications
        :return:
        """
        for id, brain in brains.items():
            self._processes[id].controller.nn_code = brain
