# This module contains the class that implements the GUI training window

# Author: Álvaro Torralba
# Date: 08/08/2023
# Version: 0.0.1

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from multiprocessing.sharedctypes import Value, Array
from multiprocessing import Queue, Event, Lock
from snake_ai.gui._data import Colors, GAShortNames
from snake_ai.gui.panels import ProgressBar
from snake_ai.gui.abc_win import WindowABC
from snake_ai.trainer.worker import Worker
from matplotlib.figure import Figure
from snake_ai.data import Folders
import matplotlib.pyplot as plt
from tkinter import messagebox
from datetime import timedelta
from threading import Thread
from time import time, sleep
import customtkinter as ctk
import os


class TrainingWindow(WindowABC):
    """
    Implements the training window
    """
    def __init__(self, top_level: ctk.CTk, mediator, configuration: dict, prev_population: dict):
        super().__init__(size=(1700, 610), resizeable=False, top_level=top_level, mediator=mediator)
        plt.style.use('bmh')
        # Configuration
        self._prev_population = prev_population
        self._config = configuration
        self._colors = Colors()
        self._short = GAShortNames()
        self._start_time = 0.0
        self._accumulated_time = 0.0

        # GUI control variables
        self._limit_score = self._config['game_size'][0] * self._config['game_size'][1] - 3
        self._best_score = 0
        self._max_progress = 0
        self._running = ctk.BooleanVar(value=False)
        self._displaying = ctk.BooleanVar(value=False)
        self._started = False
        self._iterations = ctk.IntVar(value=0)
        self._block_display = True
        self._update_time = ctk.BooleanVar(value=False)
        self._initializing = ctk.BooleanVar(value=False)

        # Multiprocessing shared and control variables
        self._data_queue = Queue()
        self._done_queue = Queue()
        self._training_flag = Value('i', 0)
        self._worker_state = Array('c', b'cr')
        self._file_lock = Lock()
        self._sync_event = Event()
        self._worker = Worker(loop_flag=self._training_flag, data_queue=self._data_queue,
                              termination_queue=self._done_queue, sync=self._sync_event, file_lock=self._file_lock,
                              worker_state=self._worker_state)

        # Master Frames
        self._master_frame = ctk.CTkFrame(master=self.window)
        self._conf_frame = ctk.CTkFrame(master=self._master_frame)
        self._set_frame = ctk.CTkFrame(master=self._conf_frame, border_width=1, border_color='white')
        self._nn_frame = ctk.CTkFrame(master=self._conf_frame, border_width=1, border_color='white')
        self._ga_frame = ctk.CTkFrame(master=self._conf_frame, border_width=1, border_color='white')
        self._prg_frame = ctk.CTkFrame(master=self._conf_frame, border_width=1, border_color='white')

        # Figures
        self._moves_fig = Figure(figsize=(5, 3.5), dpi=100)
        self._score_fig = Figure(figsize=(5, 3.5), dpi=100)
        self._efficiency_fig = Figure(figsize=(5, 3.5), dpi=100)
        self._score_hist_fig = Figure(figsize=(5, 3.5), dpi=100)
        self._fitness_fig = Figure(figsize=(5, 3.5), dpi=100)

        # Plots
        self._moves_plot = self._moves_fig.add_subplot()
        self._score_plot = self._score_fig.add_subplot()
        self._efficiency_plot = self._efficiency_fig.add_subplot()
        self._scores_plot = self._score_hist_fig.add_subplot()
        self._fitness_plot = self._fitness_fig.add_subplot()
        # Plot labels
        self._moves_plot.set_title('Average Moves')
        self._score_plot.set_title('Individual Score')
        self._efficiency_plot.set_title('Average Efficiency')
        self._scores_plot.set_title('Last Population Scores')
        self._fitness_plot.set_title('Average Fitness')

        # Plot Data
        self._avg_fitness = []
        self._avg_score = []
        self._avg_moves = []
        self._last_scores = []
        self._avg_efficiency = []

        # Canvas
        self._moves_canvas = FigureCanvasTkAgg(figure=self._moves_fig, master=self._master_frame)
        self._score_canvas = FigureCanvasTkAgg(figure=self._score_fig, master=self._master_frame)
        self._efficiency_canvas = FigureCanvasTkAgg(figure=self._efficiency_fig, master=self._master_frame)
        self._scores_hist_canvas = FigureCanvasTkAgg(figure=self._score_hist_fig, master=self._master_frame)
        self._fitness_canvas = FigureCanvasTkAgg(figure=self._fitness_fig, master=self._master_frame)

        # Buttons
        self._start_stop_button = self._NextWinButton(master=self._prg_frame, text='Start',
                                                      font=self._buttons_font,
                                                      command=self._start_behavior,
                                                      width=100, height=20)
        self._display_button = self._NextWinButton(master=self._prg_frame, text='Display', font=self._buttons_font,
                                                   width=100, height=20,
                                                   command=self._display_behavior)
        self._kill_button = self._NextWinButton(master=self._prg_frame, text='Back', font=self._buttons_font,
                                                width=100, height=20,
                                                command=self._kill_behavior)
        # Fonts
        self._font = ctk.CTkFont(family='console', size=12)
        self._font13b = ctk.CTkFont(family='console', size=13, weight="bold")
        self._font_bold = ctk.CTkFont(family='console', size=12, weight="bold")

        # General configuration labels
        self._conf_title = ctk.CTkLabel(master=self._set_frame, text=' General Config', font=self._font_bold,
                                        text_color=self._colors.blue_text)
        self._model_name = ctk.CTkLabel(master=self._set_frame, text=' Model name', font=self._font_bold)
        self._model_name_value = ctk.CTkLabel(master=self._set_frame,
                                              text=f": {self._config['model']}",
                                              font=self._font)
        self._game_size = ctk.CTkLabel(master=self._set_frame, text=' Game Size', font=self._font_bold)
        self._game_size_value = ctk.CTkLabel(master=self._set_frame,
                                             text=f': {configuration["game_size"][0]}x{configuration["game_size"][1]}',
                                             font=self._font)
        self._conf_vision = ctk.CTkLabel(master=self._set_frame, text=' Vision', font=self._font_bold)
        self._conf_vision_value = ctk.CTkLabel(master=self._set_frame, text=f': {configuration["vision"]}',
                                               font=self._font)
        self._conf_cpu = ctk.CTkLabel(master=self._set_frame, text=' Cpu Cores', font=self._font_bold)
        self._conf_cpu_value = ctk.CTkLabel(master=self._set_frame, text=f': {configuration["cpu"]}', font=self._font)

        # NN configuration labels
        self._conf_neu = ctk.CTkLabel(master=self._nn_frame, text=' Neural Config', font=self._font_bold,
                                      text_color=self._colors.blue_text)
        self._conf_layers = ctk.CTkLabel(master=self._nn_frame, text=' Hidden_arch.', font=self._font_bold)
        self._conf_layers_valuer = ctk.CTkLabel(master=self._nn_frame, text=f': {configuration["hidden"]}',
                                                font=self._font)
        self._conf_hiddeni = ctk.CTkLabel(master=self._nn_frame, text=' Hidden_init', font=self._font_bold)
        self._conf_hiddeni_value = ctk.CTkLabel(master=self._nn_frame, text=f': {configuration["hidden_init"]}',
                                                font=self._font)
        self._conf_hiddena = ctk.CTkLabel(master=self._nn_frame, text=' Hidden_act', font=self._font_bold)
        self._conf_hiddena_value = ctk.CTkLabel(master=self._nn_frame, text=f': {configuration["hidden_act"]}',
                                                font=self._font)
        self._conf_outputi = ctk.CTkLabel(master=self._nn_frame, text=' Output_init', font=self._font_bold)
        self._conf_outputi_value = ctk.CTkLabel(master=self._nn_frame, text=f': {configuration["output_init"]}',
                                                font=self._font)
        self._conf_outputa = ctk.CTkLabel(master=self._nn_frame, text=' Output_act', font=self._font_bold)
        self._conf_outputa_value = ctk.CTkLabel(master=self._nn_frame, text=f': {configuration["output_act"]}',
                                                font=self._font)
        self._conf_bias = ctk.CTkLabel(master=self._nn_frame, text=' Bias', font=self._font_bold)
        self._conf_bias_value = ctk.CTkLabel(master=self._nn_frame, text=f': {configuration["bias"]}',
                                             font=self._font)
        self._conf_biasi = ctk.CTkLabel(master=self._nn_frame, text=' Bias_init', font=self._font_bold)
        self._conf_biasi_value = ctk.CTkLabel(master=self._nn_frame, text=f': {configuration["bias_init"]}',
                                              font=self._font)

        # GA configuration labels
        self._conf_ga = ctk.CTkLabel(master=self._ga_frame, text=' Genetic Config', font=self._font_bold,
                                     text_color=self._colors.blue_text)
        self._conf_population = ctk.CTkLabel(master=self._ga_frame, text=' Population', font=self._font_bold)
        self._conf_population_value = ctk.CTkLabel(master=self._ga_frame, text=f': {configuration["population"]}',
                                                   font=self._font)
        self._conf_selection = ctk.CTkLabel(master=self._ga_frame, text=' Selection', font=self._font_bold)
        self._conf_selection_value = ctk.CTkLabel(master=self._ga_frame,
                                                  text=f': {self._short.names_map[configuration["selection"]]}',
                                                  font=self._font)
        self._conf_cross = ctk.CTkLabel(master=self._ga_frame, text=' XO', font=self._font_bold)
        xo_param = ('' if self._short.params_map[configuration["crossover"]] == '' else
                    f'({self._short.params_map[configuration["crossover"]]}='
                    f'{configuration["crossover_param"][0]})')
        self._conf_cross_value = ctk.CTkLabel(master=self._ga_frame,
                                              text=f': {self._short.names_map[configuration["crossover"]]}{xo_param}',
                                              font=self._font)
        self._conf_cross_rate = ctk.CTkLabel(master=self._ga_frame, text=' XO Rate', font=self._font_bold)
        self._conf_cross_rate_value = ctk.CTkLabel(master=self._ga_frame,
                                                   text=f': {configuration["crossover_rate"]}',
                                                   font=self._font)
        self._conf_mut = ctk.CTkLabel(master=self._ga_frame, text=' Mut.', font=self._font_bold)
        self._conf_mut_value = ctk.CTkLabel(master=self._ga_frame,
                                            text=f': {self._short.names_map[configuration["mutation"]]}'
                                                 f'({self._short.params_map[configuration["mutation"]]}='
                                                 f'{configuration["mutation_param"][0]})',
                                            font=self._font)
        self._conf_mut_rate = ctk.CTkLabel(master=self._ga_frame, text=' Mut. Rate', font=self._font_bold)
        self._conf_mut_rate_value = ctk.CTkLabel(master=self._ga_frame,
                                                 text=f': {configuration["mutation_rate"]}',
                                                 font=self._font)
        self._conf_replace = ctk.CTkLabel(master=self._ga_frame, text=' Rep.', font=self._font_bold)
        self._conf_replace_value = ctk.CTkLabel(master=self._ga_frame,
                                                text=f': {configuration["replacement"]}',
                                                font=self._font)
        self._conf_offspring = ctk.CTkLabel(master=self._ga_frame, text=' Offspring', font=self._font_bold)
        self._conf_offspring_value = ctk.CTkLabel(master=self._ga_frame,
                                                  text=f': {configuration["offspring"]}',
                                                  font=self._font)

        # Progress labels
        self._pgr_state = ctk.CTkLabel(master=self._prg_frame,
                                       text='Status: not initialized,     Elapsed Time: 00:00:00.00',
                                       font=self._font13b)
        self._pgr_best = ctk.CTkLabel(master=self._prg_frame, text=f'All Time Best Score: 0,    Current Best Score: 0',
                                      font=self._font13b)
        self._pgr_generation = ctk.CTkLabel(master=self._prg_frame, text='Generation: 0', font=self._font13b)

        # Progressbar
        self._pgrbar_val = ctk.IntVar(value=0)
        self._pgrbar = ProgressBar(master=self._prg_frame, variable=self._pgrbar_val, height=18)

        # Master frame griding
        self._master_frame.grid_propagate(False)
        self._master_frame.rowconfigure(index=(0, 1), weight=6, uniform='s')
        # self._master_frame.rowconfigure(index=2, weight=1, uniform='s')
        self._master_frame.columnconfigure(index=(0, 1, 2), weight=1, uniform='s')

        # Configuration frame griding
        self._conf_frame.grid_propagate(False)
        self._conf_frame.rowconfigure(index=0, weight=7, uniform='s')
        self._conf_frame.rowconfigure(index=1, weight=6, uniform='s')
        self._conf_frame.columnconfigure(index=(0, 1, 2), weight=1, uniform='s')

        # General configuration frame griding
        self._set_frame.grid_propagate(False)
        self._set_frame.rowconfigure(index=(0, 1, 2, 3, 4, 5, 6, 7, 8), weight=1, uniform='b')
        self._conf_frame.columnconfigure(index=(0, 1), weight=1, uniform='b')

        # NN configuration frame griding
        self._nn_frame.grid_propagate(False)
        self._nn_frame.rowconfigure(index=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9), weight=1, uniform='a')
        self._conf_frame.columnconfigure(index=(0, 1), weight=1, uniform='a')

        # GA configuration frame griding
        self._ga_frame.grid_propagate(False)
        self._ga_frame.rowconfigure(index=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10), weight=1, uniform='d')
        self._ga_frame.columnconfigure(index=(0, 1), weight=1, uniform='d')

        # Progress configuration frame griding
        self._prg_frame.grid_propagate(False)
        self._prg_frame.rowconfigure(index=(0, 1, 2, 3, 4, 5), weight=1, uniform='f')
        self._prg_frame.columnconfigure(index=0, weight=1, uniform='f')

        # Frame Placements
        self._master_frame.pack(fill='both', expand=True)
        self._conf_frame.grid(column=1, row=1, sticky='news', padx=5, pady=5)
        self._set_frame.grid(column=0, row=0, sticky='news')
        self._nn_frame.grid(column=1, row=0, sticky='news')
        self._ga_frame.grid(column=2, row=0, sticky='news')
        self._prg_frame.grid(column=0, columnspan=3, row=1, sticky='news')

        # Plot placements
        self._moves_canvas.get_tk_widget().grid(column=0, row=0, sticky='news', padx=5, pady=5)
        self._score_canvas.get_tk_widget().grid(column=1, row=0, sticky='news', padx=5, pady=5)
        self._efficiency_canvas.get_tk_widget().grid(column=2, row=0, sticky='news', padx=5, pady=5)
        self._scores_hist_canvas.get_tk_widget().grid(column=0, row=1, sticky='news', padx=5, pady=5)
        self._fitness_canvas.get_tk_widget().grid(column=2, row=1, sticky='news', padx=5, pady=5)

        # General configuration labels placement
        self._conf_title.grid(column=0, row=0, columnspan=2, rowspan=2, sticky='sw', pady=1, padx=1)
        self._model_name.grid(column=0, row=3, sticky='w', padx=2)
        self._model_name_value.grid(column=1, row=3, sticky='w', padx=2)
        self._game_size.grid(column=0, row=4, sticky='w', padx=2)
        self._game_size_value.grid(column=1, row=4, sticky='w', padx=2)
        self._conf_cpu.grid(column=0, row=5, sticky='w', padx=2)
        self._conf_cpu_value.grid(column=1, row=5, sticky='w', padx=2)
        self._conf_vision.grid(column=0, row=6, sticky='w', padx=2)
        self._conf_vision_value.grid(column=1, row=6, sticky='w', padx=2)

        # NN configuration labels placement
        self._conf_neu.grid(column=0, row=0, columnspan=2, rowspan=2, sticky='sw', pady=1, padx=1)
        self._conf_layers.grid(column=0, row=2, sticky='w', padx=2)
        self._conf_layers_valuer.grid(column=1, row=2, sticky='w', padx=2)
        self._conf_hiddeni.grid(column=0, row=3, sticky='w', padx=2)
        self._conf_hiddeni_value.grid(column=1, row=3, sticky='w', padx=2)
        self._conf_hiddena.grid(column=0, row=4, sticky='w', padx=2)
        self._conf_hiddena_value.grid(column=1, row=4, sticky='w', padx=2)
        self._conf_outputi.grid(column=0, row=5, sticky='w', padx=2)
        self._conf_outputi_value.grid(column=1, row=5, sticky='w', padx=2)
        self._conf_outputa.grid(column=0, row=6, sticky='w', padx=2)
        self._conf_outputa_value.grid(column=1, row=6, sticky='w', padx=2)
        self._conf_bias.grid(column=0, row=7, sticky='w', padx=2)
        self._conf_bias_value.grid(column=1, row=7, sticky='w', padx=2)
        self._conf_biasi.grid(column=0, row=8, sticky='w', padx=2)
        self._conf_biasi_value.grid(column=1, row=8, sticky='w', padx=2)

        # GA configuration labels placements
        self._conf_ga.grid(column=0, row=0, columnspan=2, rowspan=2, sticky='sw', pady=1, padx=1)
        self._conf_population.grid(column=0, row=2, sticky='w', padx=2)
        self._conf_population_value.grid(column=1, row=2, sticky='w', padx=2)
        self._conf_selection.grid(column=0, row=3, sticky='w', padx=2)
        self._conf_selection_value.grid(column=1, row=3, sticky='w', padx=2)
        self._conf_cross.grid(column=0, row=4, sticky='w', padx=2)
        self._conf_cross_value.grid(column=1, row=4, sticky='w', padx=2)
        self._conf_cross_rate.grid(column=0, row=5, sticky='w', padx=2)
        self._conf_cross_rate_value.grid(column=1, row=5, sticky='w', padx=2)
        self._conf_mut.grid(column=0, row=6, sticky='w', padx=2)
        self._conf_mut_value.grid(column=1, row=6, sticky='w', padx=2)
        self._conf_mut_rate.grid(column=0, row=7, sticky='w', padx=2)
        self._conf_mut_rate_value.grid(column=1, row=7, sticky='w', padx=2)
        self._conf_replace.grid(column=0, row=8, sticky='w', padx=2)
        self._conf_replace_value.grid(column=1, row=8, sticky='w', padx=2)
        self._conf_offspring.grid(column=0, row=9, sticky='w', padx=2)
        self._conf_offspring_value.grid(column=1, row=9, sticky='w', padx=2)

        # Progress labels placement
        self._pgr_state.grid(row=0, sticky='s', padx=2, pady=2)
        self._pgr_generation.grid(row=1, sticky='s', padx=2, pady=2)
        self._pgr_best.grid(row=2, sticky='s', padx=2, pady=2)
        self._pgrbar.grid(row=3, sticky='s', padx=2, pady=2)

        # Buttons placement
        self._start_stop_button.place(x=108, y=100)
        self._display_button.place(x=233, y=100)
        self._display_button.configure(state='disabled')
        self._kill_button.place(x=358, y=100)

        # Traces
        self._running.trace('w', self._set_stopped)
        self._displaying.trace('w', self._set_displaying)
        self._iterations.trace('w', self._plotting)
        self._update_time.trace('w', self._timer)

    def _plotting(self, *args) -> None:
        """
        Plots the data after each training iteration and unlocks the model display button
        :param args:
        :return:
        """
        if self._block_display:
            self._display_button.configure(state='normal')
            self._block_display = False
        self._update_plots()

    def _update_plots(self) -> None:
        """
        Updates all the plots with the available collected data
        :return:
        """
        def work():
            # Clean plots
            self._moves_plot.clear()
            self._score_plot.clear()
            self._efficiency_plot.clear()
            self._scores_plot.clear()
            self._fitness_plot.clear()

            # Limit memory usage
            if len(self._avg_moves) > 10000:
                self._avg_score = self._avg_score[1:]
                self._avg_moves = self._avg_moves[1:]
                self._avg_efficiency = self._avg_efficiency[1:]
                self._avg_fitness = self._avg_fitness[1:]

            # Update plots
            x = [i for i in range(1, len(self._avg_score) + 1)]
            self._moves_plot.plot(x, self._avg_moves)
            self._score_plot.plot(x, self._avg_score)
            self._efficiency_plot.plot(x, self._avg_efficiency)
            self._scores_plot.hist(self._last_scores, bins=15, edgecolor='black')
            self._fitness_plot.plot(x, self._avg_fitness)

            # Titles
            self._moves_plot.set_title('Average Moves')
            self._score_plot.set_title('Average Score')
            self._efficiency_plot.set_title('Average Efficiency')
            self._scores_plot.set_title('Last Population Scores')
            self._fitness_plot.set_title('Average Fitness')

            # Draw plots
            self._moves_canvas.draw()
            self._score_canvas.draw()
            self._efficiency_canvas.draw()
            self._scores_hist_canvas.draw()
            self._fitness_canvas.draw()

            # Synchronize with child process
            self._sync_event.set()
            self._trace_queue()

        thread = Thread(target=work)
        thread.start()

    def _closing_button_event(self) -> None:
        """
        Defines the behavior when the user tries to close the window
        :return:
        """
        if self._displaying.get() or self._running.get() or self._initializing.get():
            messagebox.showerror(title='Processes Running', message='Please stop all running processes before closing',
                                 parent=self.window)
        else:
            # Close all queues
            self._data_queue.close()
            self._done_queue.close()
            self._data_queue.join_thread()
            self._done_queue.join_thread()
            super()._closing_button_event()

    def _timer(self, *args) -> None:
        """
        Updates a timer over the GUI showing the elapsed execution time
        :param args:
        :return:
        """
        def loop():
            if self._accumulated_time == 0:
                accumulated = 0
            else:
                accumulated = self._accumulated_time
            while self._update_time.get():
                seconds = (time() - self._start_time) + accumulated
                self._pgr_state.configure(text=f'Status: Running,     '
                                               f'Elapsed Time: {self._elapsed_time_str(seconds)}')
                self._accumulated_time = seconds
                sleep(0.1)
        thread = Thread(target=loop)
        thread.start()

    def _elapsed_time_str(self, seconds: float) -> str:
        """
        Converts a number of seconds to a human-readable format
        :return: human-readable time
        """
        if self._start_time > 0.0:
            elapse_time = str(timedelta(seconds=seconds))
            if '.' in elapse_time:
                elapse_time = elapse_time[:elapse_time.index('.') + 3]
            else:
                elapse_time = '0:00:00.00'
        else:
            elapse_time = '0:00:00.00'
        return elapse_time

    def _set_displaying(self, *args) -> None:
        """
        Enables the button that allows to display the best current individual
        :param args:
        :return:
        """
        if self._display_button.cget('state') == 'normal':
            self._display_button.configure(state='disabled')
        else:
            self._display_button.configure(state='normal')

    def _set_stopped(self, *args) -> None:
        """
        Updates the GUI when the training pass to a stopped mode
        :param args:
        :return:
        """
        if not self._started:
            self._pgr_state.configure(text=f'Status: Stopped,     '
                                           f'Elapsed Time: {self._elapsed_time_str(self._accumulated_time)}')
            self._start_stop_button.configure(text='Start', state='normal')
            self._kill_button.configure(state='normal')

    def _kill_behavior(self) -> None:
        """
        Defines the terminate button behavior
        """
        if self._displaying.get():
            messagebox.showerror(title='Processes Running', message='Pleased stop all running processes before closing',
                                 parent=self.window)
        else:
            self._mediator.back_to_training_config(self.window)

    def _display_behavior(self) -> None:
        """
        Implements the behavior of the display button opening and displaying a game showing the best current individual
        """
        def display():
            self._displaying.set(True)
            self._mediator.display_training(game_size=self._config['game_size'],
                                            game_speed=25,
                                            show_path=False,
                                            graphics='SnakeHWGUI',
                                            lock=self._file_lock,
                                            brain_path=os.path.join(Folders.models_folder,
                                                                    self._config['model'] + '.nn'))
            self._displaying.set(False)

        thread = Thread(target=display)
        thread.start()

    def _trace_queue(self) -> None:
        """
        Controls the waiting loop while the working child process writes data to consume over the pipe
        :return:
        """
        self.window.after(500, self._check_queue)

    def _check_queue(self):
        """
        Checks if the child worker process has written over the queue it also controls the next execution or the
        abortion of the process
        :return:
        """
        if self._started:
            if self._data_queue.empty():
                self._trace_queue()
            else:
                self._refresh_gui()
        else:
            if self._worker_state.value == b'wr':
                self._trace_queue()
            elif self._worker_state.value == b'wt':
                self._refresh_gui()
            else:
                if self._done_queue.empty() and self._running.get():
                    self._trace_queue()
                else:
                    self._running.set(False)
                    self._worker.batch.update_brains(self._done_queue.get())

    def _trace_start(self, thread: Thread):
        """
        Traces creation of the subprocess to avoid GUI freezing
        :param thread:
        :return:
        """
        if thread.is_alive():
            self.window.after(500, self._trace_start, thread)
        else:
            # Trace child progress
            self._start_stop_button.configure(state='normal')
            self._trace_queue()

    def _training(self) -> None:
        """
        Sets up the GUI control variables to start the training and starts it
        :return:
        """
        self._start_stop_button.configure(text='Stop', state='disabled')
        self._start_time = time()
        self._update_time.set(True)
        self._started = True
        self._running.set(True)
        # Spawn child process using a thread to decrease freezing from GUI
        self._training_flag.value = 1
        thread = Thread(target=self._worker.train)
        thread.start()
        self._trace_start(thread)

    def _start_behavior(self) -> None:
        """
        Implements the behavior of the start button, starting or stopping the training
        :return:
        """
        # Initialize and run training
        if not self._started and self._iterations.get() == 0:
            self._initializing.set(True)
            self._kill_button.configure(text='Terminate', state='disabled')
            self._init_training_instances()
        # Stop training
        elif self._started:
            self._update_time.set(False)
            self._start_stop_button.configure(state='disabled')
            self._pgr_state.configure(text=f'Status: Ending,     '
                                           f'Elapsed Time: {self._elapsed_time_str(self._accumulated_time)}')
            self._started = False
            # Flag child process to terminate
            self._training_flag.value = 0
        # Resume training
        else:
            self._kill_button.configure(state='disabled')
            self._training()

    def _update_best(self, new_max_sc: float) -> None:
        """
        Updates the best recorded individual score and fitness
        :param new_max_sc: last generation maximal score
        :return:
        """
        self._best_score = self._best_score if self._best_score > new_max_sc else new_max_sc

    def _update_progressbar(self, total_max_sc: int) -> None:
        """
        Updates de progressbar
        :param total_max_sc: number of individuals that have reached the maximum score
        :return:
        """
        if total_max_sc > 0:
            progress = 50 + ((total_max_sc / self._config['population']) * 50)
        else:
            progress = (self._best_score / self._limit_score) * 50
        self._max_progress = self._max_progress if self._max_progress > progress else progress
        self._pgrbar.set(self._max_progress / 100)

    def _trace_init(self, thread: Thread) -> None:
        """
        Traces the initialization method to prevent the GUI from freezing
        :param thread:
        :return:
        """
        if thread.is_alive():
            self.window.after(500, self._trace_init, thread)
        else:
            self._initializing.set(False)
            self._training()

    def _init_training_instances(self) -> None:
        """
        Initiates all the necessary instances for the training
        :return:
        """
        def work():
            self._worker.init(self._config, self._prev_population)
        # Update UI
        self._start_stop_button.configure(state='disabled')
        self._pgr_state.configure(text=f'Status: Initializing,     '
                                       f'Elapsed Time: {self._elapsed_time_str(self._accumulated_time)}')
        self._pgr_state.update()
        thread = Thread(target=work)
        thread.start()
        self._trace_init(thread)

    def _refresh_gui(self) -> None:
        """
        Refresh the GUI state after an iteration
        :return:
        """
        def work():
            plot_data = self._data_queue.get()
            # Update plots data
            self._avg_fitness.append(plot_data['fitness_avg'])
            self._avg_score.append(plot_data['score_avg'])
            self._last_scores = plot_data['scores']
            self._avg_moves.append(plot_data['moves_avg'])
            self._avg_efficiency.append(plot_data['efficiencies_avg'])
            # Update GUI stats
            self._update_best(new_max_sc=plot_data['score_max'])
            self._update_progressbar(plot_data['total_max_sc'])
            self._iterations.set(self._iterations.get() + 1)
            self._pgr_generation.configure(text=f'Generation: {self._iterations.get()}')
            self._pgr_best.configure(text=f'All Time Best Score: {self._best_score},'
                                          f'    Current Best Score: {plot_data["score_max"]}')
        thread = Thread(target=work)
        thread.start()
