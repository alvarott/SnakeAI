# This module contains the class that can create and run multiple snake base processes in parallel

# Author: Álvaro Torralba
# Date: 27/05/2023
# Version: 0.0.1

from snake_ai.snake.game_process.snake_ai_process import SnakeAI
import multiprocessing
import numpy as np


class SnakeBatch:
    """This class is intended to create, maintain and run several Snake base AI controlled processes"""

    def __init__(self, individuals: int, cpu_cores: int, size: tuple[int, int], dist_calculator: str, input: int,
                 output: int, hidden: list[int], output_init: str, bias: bool, bias_init: str, hidden_init: str,
                 output_act: str, hidden_act: str):
        self._processes: dict[int, SnakeAI] = {SnakeAI.obj_counter:
                                               SnakeAI(size=size, dist_calculator=dist_calculator, input=input,
                                                       output=output, hidden=hidden, bias=bias, bias_init=bias_init,
                                                       output_init=output_init, hidden_init=hidden_init,
                                                       output_act=output_act, hidden_act=hidden_act)
                                               for _ in range(individuals)}
        self._cpu_cores = cpu_cores
        self.results = {}

    def _run(self, individual: SnakeAI) -> tuple[int, dict[str, float]]:
        """
        Calls an individual execution
        :param individual: individual to be executed
        :return stats: id of the individual and a dict containing the performance stats
        """
        return individual.simulate()

    def run_all(self) -> None:
        """
        Runs all the individual and collects all the performance results
        :return:
        """
        pool = multiprocessing.Pool(processes=self._cpu_cores)
        results = pool.map(self._run, [process for process in list(self._processes.values())])
        pool.close()
        pool.join()
        self.results = results

    def get_individual(self, identifier: int) -> SnakeAI:
        """
        Returns an individual object from the batch
        :param identifier: individual id
        :return: individual object
        """
        return self._processes[identifier]

    def get_population(self) -> dict[int, np.ndarray]:
        """
        Produces a dictionary with the id and the codification of each individual
        :return population: the dictionary just described
        """
        population: dict[int, np.ndarray] = {}
        for id, value in self._processes.items():
            population[id] = value.nn_code
        return population

    def update_brains(self, brains: dict[int, np.ndarray]) -> None:
        """
        Updates all the NN in the individuals in the batch
        :param brains: list of array codifications
        :return:
        """
        for id, brain in brains.items():
            self._processes[id].nn_code = brain
