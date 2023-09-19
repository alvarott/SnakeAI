# This module contains the class that implements all the logic to do the training logic

# Author: Álvaro Torralba
# Date: 06/09/2023
# Version: 0.0.1

from snake_ai.snake.game_process.snake_batch_process import SnakeBatch
from multiprocessing import Queue, Event, Process
from multiprocessing.sharedctypes import Value, Array
from snake_ai.genetic.genetic_algorithm import GA
from snake_ai.gui._data import GeneticConfig
from snake_ai.data import Folders
from snake_ai.trainer.stats import Stats
from snake_ai.IO import IO


class Worker:
    def __init__(self, loop_flag: Value, data_queue: Queue, termination_queue: Queue, sync: Event,
                 worker_state: Array):
        """
        Constructor
        :param loop_flag: flag to control if the process still alive
        :param data_queue: queue where to put the produced data to be consumed for the mainloop
        :param termination_queue: queue to notify that the process has finished
        :param sync: event used for synchronization with the mainloop
        :param worker_state: flag to know the current worker status and help with synchronization
        """
        self._batch: SnakeBatch | None = None
        self._ga: GA | None = None
        self._stats_producer: Stats | None = None
        self._model_name: str | None = None
        self._ga_map = GeneticConfig()
        self._loop_flag = loop_flag
        self._data_queue = data_queue
        self._done_queue = termination_queue
        self._event = sync
        self._worker_state = worker_state

    @property
    def batch(self):
        return self._batch

    def init(self, config: dict, prev_population: dict | None = None) -> None:
        """
        Initiates the all the individuals and the genetic algorithm necessary objects
        :param config: initialization configuration
        :param prev_population: previous population if any
        :return: 
        """
        self._model_name = config['model']
        # Create stats generator object
        self._stats_producer = Stats(config['game_size'][0] * config['game_size'][1] - 3)
        # Create population
        self._batch = SnakeBatch(individuals=config['population'],
                                 cpu_cores=config['cpu'],
                                 size=config['game_size'],
                                 input=22,
                                 output=3,
                                 hidden=config['hidden'],
                                 vision=config['vision'],
                                 bias=config['bias'],
                                 bias_init=config['bias_init'],
                                 output_init=config['output_init'],
                                 hidden_init=config['hidden_init'],
                                 output_act=config['output_act'],
                                 hidden_act=config['hidden_act'])
        if prev_population is not None:
            pop = {}
            limit = (len(prev_population) if len(prev_population) <= config['population'] else
                     config['population'])
            for i in range(1, limit + 1):
                pop[i] = prev_population[i]
            self._batch.update_brains(pop)
        # Create GA instance
        self._ga = GA(selection=config['selection'],
                      selection_params={self._ga_map.params_name[config['selection']]:
                                        config['selection_param'][0]}
                      if config['selection_param'][1] == 'normal' else {},
                      fitness='fitness1',
                      crossover=config['crossover'],
                      crossover_params={self._ga_map.params_name[config['crossover']]:
                                        config['crossover_param'][0]}
                      if config['crossover_param'][1] == 'normal' else {},
                      crossover_rate=config['crossover_rate'],
                      mutation=config['mutation'],
                      mutations_params={self._ga_map.params_name[config['mutation']]:
                                        config['mutation_param'][0]}
                      if config['mutation_param'][1] == 'normal' else {},
                      mutation_rate=config['mutation_rate'],
                      offspring=config['population'] if config['replacement'] == 'generational'
                      else config['offspring']
                      )

    @staticmethod
    def _work(model_name: str, batch: SnakeBatch, ga: GA, alive: Value, data_queue: Queue, termination_queue: Queue,
              event: Event, stats_producer: Stats, state: Array) -> None:
        """
        Runs a loop training the models while 'alive' flag is activated
        :param model_name: name that is going to be used to save the model at disc
        :param alive: flag to control if the process still alive
        :param data_queue: queue where to put the produced data to be consumed for the mainloop
        :param termination_queue: queue to notify that the process has finished
        :param event: event used for synchronization with the mainloop
        :params stats_producer: stats producer object
        :params state: flag to describe the worker state
        :return:
        """
        while alive.value:
            state.value = b'wr'
            # Run the games
            population = batch.get_population_brains()
            batch.run()
            stats = batch.results
            # Run genetic process
            best, fitness = ga.next_gen(population=population, scores=stats)
            batch.update_brains(population)
            # Save current best and las population
            try:
                IO.save(Folders.models_folder, model_name + '.nn', batch.get_individual(best))
                IO.save(Folders.populations_folder, model_name + '.pop', batch.population)
            except:
                pass
            # Pass execution stats to main process
            data_queue.put(stats_producer.generation_stats(stats, fitness))
            # Synchronize with the main process
            state.value = b'wt'
            if event.wait(120):
                event.clear()
            else:
                break
        else:
            state.value = b'sv'
            # Send the current population status to the parent process
            termination_queue.put(batch.get_population_brains())

    def train(self):
        """
        Wraps the _work method two executed as a new process
        :return:
        """
        process = Process(target=Worker._work, args=(self._model_name, self._batch, self._ga, self._loop_flag,
                                                     self._data_queue, self._done_queue, self._event,
                                                     self._stats_producer, self._worker_state))
        process.start()



# Fixed mainthread overload, causing app to fail, training and displaying simultaneously is no loger possible"