# This module contains the class that implements a mediator between all the gui windows
import time

# Author: Álvaro Torralba
# Date: 19/06/2023
# Version: 0.0.1

from snake_ai.snake.game_displayer.game_vsai_displayer import GameVSAIDisplayer
from snake_ai.snake.game_displayer.game_model_displayer import GameModelDisplayer
from snake_ai.gui.start_win import StartWindow
from snake_ai.gui.main_menu_win import MainMenuWindow
from snake_ai.gui.vs_ai_config_win import GameConfigWindow
import customtkinter as ctk

class GUIMediator:
    def __init__(self):
        self._start_win = StartWindow(self)
        self._main_menu_win = None
        self._vsai_conf_win = None
        self._model_conf_win = None
        self._start_win._window.mainloop()

    def main_menu(self):
        self._main_menu_win = MainMenuWindow(self._start_win.window,self)
        self._win_transition(current_win=self._start_win.window, next_win=self._main_menu_win.window)

    def back_to_main(self, current_win: ctk.CTk):
        self._win_transition(current_win=current_win, next_win=self._main_menu_win.window)

    def main_to_vsai(self):
        if self._vsai_conf_win is None:
            self._vsai_conf_win = GameConfigWindow(self._main_menu_win.window,self, 'vsai')
        self._win_transition(current_win=self._main_menu_win.window, next_win=self._vsai_conf_win.window)

    def launch_vsai(self, game_size: tuple[int, int], game_speed: int, show_path: bool, graphics: str, brain_path: str):
        game = GameVSAIDisplayer(size=game_size, speed=game_speed, show_path=show_path, dist_calculator='Binary',
                                 graphics=graphics, brain_path=brain_path)
        self._vsai_conf_win.window.withdraw()
        game.run()
        self._vsai_conf_win.window.deiconify()

    def main_to_try_model(self):
        if self._model_conf_win is None:
            self._model_conf_win = GameConfigWindow(self._main_menu_win.window, self, 'model')
        self._win_transition(current_win=self._main_menu_win.window, next_win=self._model_conf_win.window)

    def launch_model(self, game_size: tuple[int, int], game_speed: int, show_path: bool, graphics: str, brain_path: str):
        game = GameModelDisplayer(size=game_size, speed=game_speed + 7 , show_path=show_path, dist_calculator='Binary',
                                 graphics=graphics, brain_path=brain_path)
        self._model_conf_win.window.withdraw()
        game.run()
        self._model_conf_win.window.deiconify()

    def training_config_window(self):
        print('training conf')
        self.exit()

    def training_widow(self):
        self.exit()

    def statistics_window(self):
        print('statistics')
        self.exit()

    def exit(self):
        self._start_win.window.destroy()

    def _win_transition(self, current_win: ctk.CTk, next_win:ctk.CTk, step: float = 0.00008):
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

if __name__ == '__main__':
    a = GUIMediator()