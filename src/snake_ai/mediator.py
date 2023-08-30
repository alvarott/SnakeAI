# This module contains the class that implements a mediator between all application components


# Author: Álvaro Torralba
# Date: 19/06/2023
# Version: 0.0.1

from snake_ai.snake.game_displayer.game_vsai_displayer import GameVSAIDisplayer
from snake_ai.snake.game_displayer.game_model_displayer import GameModelDisplayer
from snake_ai.gui.training_win import TrainingWindow
from snake_ai.gui.training_config_win import TrainingConfigWindow
from snake_ai.gui.game_config_win import GameConfigWindow
from snake_ai.gui.main_menu_win import MainMenuWindow
from snake_ai.gui.start_win import StartWindow
from snake_ai.gui.stats_win import StatsWindow
from snake_ai.neural.nn import NN
import customtkinter as ctk
from snake_ai.IO import IO
import os


class APPMediator:

    supported_vision = ['binary', 'real']

    def __init__(self):
        self._start_win = StartWindow(self)
        self._main_menu_win = None
        self._vsai_conf_win = None
        self._model_conf_win = None
        self._training_conf_win = None
        self._training_win = None
        self._stats_win = None
        self._running_model = None

    def start(self) -> None:
        """
        Starts the GUI main loop
        """
        self._start_win.window.mainloop()

    def main_menu(self) -> None:
        """
        Creates and opens the main manu window
        """
        self._main_menu_win = MainMenuWindow(self._start_win.window, self)
        self._win_transition(current_win=self._start_win.window, next_win=self._main_menu_win.window)

    def back_to_main(self, current_win: ctk.CTk) -> None:
        """
        Hides the current window and pops out the main manu window
        :param current_win: current opened window instance
        :return:
        """
        self._win_transition(current_win=current_win, next_win=self._main_menu_win.window)

    def back_to_training_config(self, current_win: ctk.CTk, destroy: bool) -> None:
        """
        Hides the current window and pops out the training configuration window,
        the current window can be also destroyed
        :param current_win: current opened window instance
        :param destroy: boolean flag to indicate if the current window has to be destroyed
        :return:
        """
        self._win_transition(current_win=current_win, next_win=self._training_conf_win.window)
        if destroy:
            del self._training_win
            self._training_win = None

    def main_to_vsai(self) -> None:
        """
        Creates the game configuration window and displays it
        :return:
        """
        if self._vsai_conf_win is None:
            self._vsai_conf_win = GameConfigWindow(self._main_menu_win.window, self, 'vsai')
        self._win_transition(current_win=self._main_menu_win.window, next_win=self._vsai_conf_win.window)

    def launch_vsai(self, game_size: tuple[int, int], game_speed: int, show_path: bool, graphics: str,
                    brain_path: str) -> None | str:
        """
        Creates and runs a game instance human controlled
        :param game_size: size of game grid
        :param game_speed: screen refresh speed
        :param show_path: bool flag to display A* path
        :param graphics: graphic interface flavor
        :param brain_path: absolute path to a model file
        :return:
        """
        model = self._check_model(brain_path)
        if isinstance(model, tuple):
            game = GameVSAIDisplayer(size=game_size, speed=game_speed, show_path=show_path, graphics=graphics,
                                     brain=model[1], vision=model[0])
            self._vsai_conf_win.window.withdraw()
            game.run()
            self._vsai_conf_win.window.deiconify()
            return None
        else:
            return model

    def display_training(self, game_size: tuple[int, int], game_speed: int, show_path: bool, graphics: str,
                         brain_path: str) -> None:
        """
        Creates and runs a snake AI controlled game from the training window process
        :param game_size: grid size
        :param game_speed: game FPS
        :param show_path: flag to control the displaying of A* path
        :param graphics: game graphics flavor
        :param brain_path: game controller path
        :return:
        """
        model = self._check_model(brain_path)
        if isinstance(model, tuple):
            self._running_model = brain_path
            game = GameModelDisplayer(size=(game_size[0], game_size[1]), speed=game_speed, show_path=show_path,
                                      graphics=graphics, brain=model[1], vision=model[0], mediator=self, reload=True)
            game.force_init()
            game.run()
            self._running_model = None

    def main_to_try_model(self) -> None:
        """
        Creates and displays the model test window
        :return:
        """
        if self._model_conf_win is None:
            self._model_conf_win = GameConfigWindow(self._main_menu_win.window, self, 'model')
        self._win_transition(current_win=self._main_menu_win.window, next_win=self._model_conf_win.window)

    def launch_model(self, game_size: tuple[int, int], game_speed: int, show_path: bool, graphics: str,
                     brain_path: str) -> str | None:
        """
         Creates and runs a game instance AI controlled
         :param game_size: size of game grid
         :param game_speed: screen refresh speed
         :param show_path: bool flag to display A* path
         :param graphics: graphic interface flavor
         :param brain_path: absolute path to a model file
         :return:
         """
        model = self._check_model(brain_path)
        if isinstance(model, tuple):
            game = GameModelDisplayer(size=(game_size[0]-5, game_size[1]-5), speed=game_speed + 7, show_path=show_path,
                                      graphics=graphics, brain=model[1], vision=model[0],
                                      name=os.path.basename(brain_path[:brain_path.index('.')]) + '.sts')
            self._model_conf_win.window.withdraw()
            game.run()
            self._model_conf_win.window.deiconify()
            return None
        else:
            return model

    def main_to_training_config(self) -> None:
        """
        Creates and displays de training configuration window
        :return:
        """
        if self._training_conf_win is None:
            self._training_conf_win = TrainingConfigWindow(self._main_menu_win.window, self)
        self._win_transition(current_win=self._main_menu_win.window, next_win=self._training_conf_win.window)

    def training_widow(self, params: dict, prev_population: dict | None) -> None:
        """
        Creates and displays the training window
        :param params: list of params collected at the training configuration window
        :param prev_population: instances of previous population to continue a past training
        :return:
        """
        self._training_win = TrainingWindow(self._training_conf_win.window, self, params, prev_population)
        self._win_transition(current_win=self._training_conf_win.window, next_win=self._training_win.window)

    def statistics_window(self) -> None:
        """
        Creates and displays the statistics window
        :return:
        """
        if self._stats_win is None:
            self._stats_win = StatsWindow(self._main_menu_win.window, self)
        self._win_transition(current_win=self._main_menu_win.window, next_win=self._stats_win.window)

    def reload_model(self):
        """
        Loads the current model under training
        :return:
        """
        if self._running_model is not None:
            model = self._check_model(self._running_model)
            return model[1]
        return None

    def exit(self) -> None:
        """
        Ends the application mainloop
        :return:
        """
        self._start_win.window.destroy()

    def _win_transition(self, current_win: ctk.CTk, next_win: ctk.CTk, step: float = 0.00008) -> None:
        """
        Auxiliary method to transitioning between windows
        :param current_win: current window instance to hide
        :param next_win: next window instance to popout
        :param step: counter to smooth the transition
        :return:
        """
        current = 1
        next = 0
        if next_win.state() == 'withdrawn':
            next_win.deiconify()
        while current > 0:
            current -= step
            next += step
            current_win.attributes('-alpha', current)
            next_win.attributes('-alpha', next)
            next_win.update()
        current_win.withdraw()

    def _check_model(self, model_path: str) -> tuple[str, NN] | str:
        """
        Auxiliary method to check the models to be run
        :param model_path:
        :return:
        """
        if os.path.isfile(model_path):
            model = IO.load(model_path, dict)
            if model in [-1, -2, -3]:
                return 'bad type'
            elif isinstance(model['model'], NN) and model['vision'] in APPMediator.supported_vision:
                return model['vision'], model['model']
            else:
                return 'bad type'
        else:
            return 'file not found'
