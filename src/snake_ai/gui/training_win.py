# This module contains the class that implements the GUI training window

# Author: Álvaro Torralba
# Date: 08/08/2023
# Version: 0.0.1

from snake_ai.snake.game_process.snake_batch_process import SnakeBatch
from snake_ai.gui._data import Colors, GAShortNames, GeneticConfig
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from snake_ai.genetic.genetic_algorithm import GA
from snake_ai.gui.panels import ProgressBar
from snake_ai.gui.abc_win import WindowABC
from matplotlib.figure import Figure
from multiprocessing import Process, Queue
from snake_ai.data import Folders
import matplotlib.pyplot as plt
from tkinter import messagebox
from datetime import timedelta
from threading import Thread
import customtkinter as ctk
from time import time, sleep
from snake_ai.IO import IO
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
        self._ga_map = GeneticConfig()
        self._start_time = 0.0
        self._accumulated_time = 0.0
        # Training Objects
        self._batch: SnakeBatch | None = None
        self._ga: GA | None = None
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
        self._turns_fig = Figure(figsize=(5, 3.5), dpi=100)
        self._fitness_fig = Figure(figsize=(5, 3.5), dpi=100)

        # Plots
        self._moves_plot = self._moves_fig.add_subplot()
        self._score_plot = self._score_fig.add_subplot()
        self._efficiency_plot = self._efficiency_fig.add_subplot()
        self._turns_plot = self._turns_fig.add_subplot()
        self._fitness_plot = self._fitness_fig.add_subplot()
        # Plot labels
        self._moves_plot.set_title('Average Moves')
        self._score_plot.set_title('Individual Score')
        self._efficiency_plot.set_title('Average Efficiency')
        self._turns_plot.set_title('Average Turns')
        self._fitness_plot.set_title('Average Fitness')

        # Plot Data
        self._avg_fitness = []
        self._avg_score = []
        self._avg_moves = []
        self._avg_turns = []
        self._avg_efficiency = []

        # Canvas
        self._moves_canvas = FigureCanvasTkAgg(figure=self._moves_fig, master=self._master_frame)
        self._score_canvas = FigureCanvasTkAgg(figure=self._score_fig, master=self._master_frame)
        self._efficiency_canvas = FigureCanvasTkAgg(figure=self._efficiency_fig, master=self._master_frame)
        self._turns_canvas = FigureCanvasTkAgg(figure=self._turns_fig, master=self._master_frame)
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
        self._game_size = ctk.CTkLabel(master=self._set_frame, text=' Game Size', font=self._font_bold)
        self._game_size_value = ctk.CTkLabel(master=self._set_frame,
                                             text=f': ({configuration["game_size"][0]}x{configuration["game_size"][1]})',
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
                                       text='Status: not initialized,     Elapsed Time: 00:00:00.000',
                                       font=self._font13b)
        self._pgr_best = ctk.CTkLabel(master=self._prg_frame, text=f'ATB Sc: 0,    CB Sc: 0, '
                                                                   f'    ATB Fit: 0.00M,    CB Fit: 0.00M',
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
        # self._conf_frame.rowconfigure(index=2, weight=2, uniform='s')
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
        self._turns_canvas.get_tk_widget().grid(column=0, row=1, sticky='news', padx=5, pady=5)
        self._fitness_canvas.get_tk_widget().grid(column=2, row=1, sticky='news', padx=5, pady=5)

        # General configuration labels placement
        self._conf_title.grid(column=0, row=0, columnspan=2, rowspan=2, sticky='sw', pady=1, padx=1)
        self._game_size.grid(column=0, row=3, sticky='w', padx=2)
        self._game_size_value.grid(column=1, row=3, sticky='w', padx=2)
        self._conf_cpu.grid(column=0, row=4, sticky='w', padx=2)
        self._conf_cpu_value.grid(column=1, row=4, sticky='w', padx=2)
        self._conf_vision.grid(column=0, row=5, sticky='w', padx=2)
        self._conf_vision_value.grid(column=1, row=5, sticky='w', padx=2)

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

        # GUI & multiprocessing control
        self._limit_score = self._config['game_size'][0] * self._config['game_size'][1] - 3
        self._best_score = 0
        self._best_fit = 0
        self._max_progress = 0
        self._running = ctk.BooleanVar(value=False)
        self._displaying = ctk.BooleanVar(value=False)
        self._started = False
        self._iterations = ctk.IntVar(value=0)
        self._block_display = True
        self._update_time = ctk.BooleanVar(value=False)
        self._data_queue = Queue()
        self._flag_queue = Queue()
        self._worker = Worker(self._flag_queue, self._data_queue)
        self._initializing = ctk.BooleanVar(value=False)

        # Traces
        self._running.trace('w', self._set_stopped)
        self._displaying.trace('w', self._set_displaying)
        self._iterations.trace('w', self._plotting)
        self._update_time.trace('w', self._timer)

    def _work(self) -> None:
        """
        Wrapper method to prevent GUI for freezing while creating the child process
        :return:
        """
        thread = Thread(target=self._worker.work, args=(self._batch, self._ga))
        thread.start()

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
            self._turns_plot.clear()
            self._fitness_plot.clear()

            # Update plots
            x = [i for i in range(1, len(self._avg_score) + 1)]
            self._moves_plot.plot(x, self._avg_moves)
            self._score_plot.plot(x, self._avg_score)
            self._efficiency_plot.plot(x, self._avg_efficiency)
            self._turns_plot.plot(x, self._avg_turns)
            self._fitness_plot.plot(x, self._avg_fitness)

            # Titles
            self._moves_plot.set_title('Average Moves')
            self._score_plot.set_title('Average Score')
            self._efficiency_plot.set_title('Average Efficiency')
            self._turns_plot.set_title('Average Turns')
            self._fitness_plot.set_title('Average Fitness')

            # Draw plots
            self._moves_canvas.draw()
            self._score_canvas.draw()
            self._efficiency_canvas.draw()
            self._turns_canvas.draw()
            self._fitness_canvas.draw()

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
            self._flag_queue.close()
            self._data_queue.join_thread()
            self._flag_queue.join_thread()
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
        elif self._iterations.get() == 0:
            self._mediator.back_to_training_config(self.window, False)
        else:
            self._mediator.back_to_training_config(self.window, True)

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
                                            brain_path=os.path.join(Folders.models_folder,
                                                                    self._config['model'] + '.nn'))
            self._displaying.set(False)

        thread = Thread(target=display)
        thread.start()

    def _trace_queue(self, active: bool) -> None:
        """
        Controls the waiting loop while the working child process writes data to consume over the pipe
        :param active: flag to continue or stop the traicing
        :return:
        """
        if active:
            self._trace_id = self.window.after(500, self._check_queue)
        else:
            self.window.after_cancel(self._trace_id)

    def _check_queue(self):
        """
        Checks if the child worker process has written over the queue it also controls the next execution or the
        abortion of the process
        :return:
        """
        if self._started:
            if self._flag_queue.empty():
                self._trace_queue(True)
            else:
                self._flag_queue.get()
                self._refresh_gui()
                self._work()
                self._trace_queue(True)
        else:
            if self._flag_queue.empty() and self._running:
                self._trace_queue(True)
            else:
                self._flag_queue.get()
                self._refresh_gui()
                self._trace_queue(False)
                self._running.set(False)

    def _training(self) -> None:
        """
        Sets up the GUI control variables to start the training and starts it
        :return:
        """
        self._start_stop_button.configure(text='Stop', state='normal')
        self._start_time = time()
        self._update_time.set(True)
        self._started = True
        self._running.set(True)
        self._work()
        self._trace_queue(True)

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
        # Resume training
        else:
            self._kill_button.configure(state='disabled')
            self._training()

    def _update_best(self, new_max_sc: float, new_max_fit: float) -> None:
        """
        Updates the best recorded individual score and fitness
        :param new_max_sc: last generation maximal score
        :param new_max_fit: last generation maximal fitness
        :return:
        """
        self._best_score = self._best_score if self._best_score > new_max_sc else new_max_sc
        self._best_fit = self._best_fit if self._best_fit > new_max_fit else new_max_fit

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
            self._trace_id = self.window.after(500, self._trace_init, thread)
        else:
            self.window.after_cancel(self._trace_id)
            self._initializing.set(False)
            self._training()

    def _init_training_instances(self) -> None:
        """
        Initiates all the necessary instances for the training
        :return:
        """
        def work():
            # Create population
            self._batch = SnakeBatch(individuals=self._config['population'],
                                     cpu_cores=self._config['cpu'],
                                     size=self._config['game_size'],
                                     input=22,
                                     output=3,
                                     hidden=self._config['hidden'],
                                     vision=self._config['vision'],
                                     bias=self._config['bias'],
                                     bias_init=self._config['bias_init'],
                                     output_init=self._config['output_init'],
                                     hidden_init=self._config['hidden_init'],
                                     output_act=self._config['output_act'],
                                     hidden_act=self._config['hidden_act'])
            if self._prev_population is not None:
                pop = {}
                limit = (len(self._prev_population) if len(self._prev_population) <= self._config['population'] else
                         self._config['population'])
                for i in range(1, limit + 1):
                    pop[i] = self._prev_population[i]
                self._batch.update_brains(pop)
            # Create GA instance
            self._ga = GA(selection=self._config['selection'],
                          selection_params={self._ga_map.params_name[self._config['selection']]:
                                            self._config['selection_param'][0]}
                          if self._config['selection_param'][1] == 'normal' else {},
                          fitness='fitness1',
                          crossover=self._config['crossover'],
                          crossover_params={self._ga_map.params_name[self._config['crossover']]:
                                            self._config['crossover_param'][0]}
                          if self._config['crossover_param'][1] == 'normal' else {},
                          crossover_rate=self._config['crossover_rate'],
                          mutation=self._config['mutation'],
                          mutations_params={self._ga_map.params_name[self._config['mutation']]:
                                            self._config['mutation_param'][0]}
                          if self._config['mutation_param'][1] == 'normal' else {},
                          mutation_rate=self._config['mutation_rate'],
                          offspring=self._config['population'] if self._config['replacement'] == 'generational'
                          else self._config['offspring']
                          )
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
            population, best, stats, fitness = self._data_queue.get()
            self._batch.update_brains(population)
            # Produce generation statistics
            plot_data = Stats.generation_stats(stats, fitness, self._limit_score)
            # Update plots data
            self._avg_fitness.append(plot_data[0])
            self._avg_score.append(plot_data[1])
            self._avg_turns.append(plot_data[2])
            self._avg_moves.append(plot_data[3])
            self._avg_efficiency.append(plot_data[4])
            # Update GUI stats
            self._update_best(new_max_sc=plot_data[5], new_max_fit=plot_data[6])
            self._update_progressbar(plot_data[7])
            self._iterations.set(self._iterations.get() + 1)
            self._pgr_generation.configure(text=f'Generation: {self._iterations.get()}')
            self._pgr_best.configure(text=f'ATB Sc: {self._best_score},    CB Sc: {plot_data[5]}, '
                                          f'    ATB Fit: {self._best_fit:.2f}M,    CB Fit: {plot_data[6]:.2f}M')
            # Save current best and las population
            IO.save(Folders.models_folder, self._config['model'] + '.nn', self._batch.get_individual(best))
            IO.save(Folders.populations_folder, self._config['model'] + '.pop', self._batch.population)

        thread = Thread(target=work)
        thread.start()


class Stats:
    """
    Generates the plotting data from populations metrics
    """
    @staticmethod
    def generation_stats(population_stats: list[tuple[int, dict[str, float]]], fitness: dict[int, float],
                         limit_score: int) -> tuple:
        # Get all the values
        scores = []
        moves = []
        turns = []
        efficiencies = []
        for i in population_stats:
            moves.append(i[1]['moves'])
            turns.append(i[1]['turns'])
            scores.append(i[1]['score'])
            efficiencies.append(i[1]['efficiency'])
        # Calculate averages
        fitness_avg = sum(list(fitness.values())) / len(fitness)
        fitness_max = max(list(fitness.values()))
        score_avg = sum(scores) / len(scores)
        score_max = max(scores)
        total_max_sc = scores.count(limit_score)
        turns_avg = sum(turns) / len(turns)
        moves_avg = sum(moves) / len(moves)
        efficiencies_avg = sum(efficiencies) / len(efficiencies)
        return (fitness_avg, score_avg, turns_avg, moves_avg, efficiencies_avg, score_max, (fitness_max / 1000000),
                total_max_sc)


class Worker:
    """
    This class provides a pickable working class to be call inside the main class (which is not pickable) as a process
    """
    def __init__(self, flag_queue: Queue, data_queue: Queue,):
        self._data = data_queue
        self._flag = flag_queue

    def _work(self, batch: SnakeBatch, ga: GA) -> None:
        """
        Executes all the snake games and writes the results over a pipe
        :param batch: snake batch object containing all game instances
        :param ga: genetic algorithm instance object
        :return:
        """
        # Run all snakes
        population = batch.get_population_brains()
        batch.run()
        # Genetic process
        stats = batch.results
        best, fitness = ga.next_gen(population=population, scores=stats)
        self._data.put((population, best, stats, fitness))
        self._flag.put('ready')

    def work(self, batch: SnakeBatch, ga: GA) -> None:
        """
        Main method wrapper to be called as a process
        :param batch: snake batch object containing all game instances
        :param ga: genetic algorithm instance object
        :return:
        """
        process = Process(target=self._work, args=(batch, ga,))
        process.start()
