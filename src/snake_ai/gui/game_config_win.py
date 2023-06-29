# This module contains the class that implements the GUI main menu

# Author: Álvaro Torralba
# Date: 19/06/2023
# Version: 0.0.1

from snake_ai.gui.panels import IOFile, SegmentedPanel
from snake_ai.gui.abc_win import WindowABC
from snake_ai.snake.enums import GameSize, GameSpeed
import customtkinter as ctk


class GameConfigWindow(WindowABC):

    game_graphics = {'Light weight': 'SnakeLWGUI', 'Extended': 'SnakeHWGUI', }
    a_star = {'Yes': True, 'No': False}
    game_sizes = {'Small': GameSize.SMALL, 'Medium': GameSize.MEDIUM, 'Large': GameSize.LARGE}
    game_speed = {'Slow': GameSpeed.SLOW, 'Normal': GameSpeed.NORMAL, 'Fast': GameSpeed.FAST}

    def __init__(self, top_level: ctk.CTk, mediator, game_type:str):
        super().__init__(size=(300, 400), resizeable=False, top_level=top_level, mediator=mediator)
        if game_type == 'vsai':
            mediator_call = self._mediator.launch_vsai
        elif game_type == 'model':
            mediator_call = self._mediator.launch_model
        else:
            raise ValueError(f'{game_type} not a supported game type')
        # Fonts
        self._error_font = ctk.CTkFont(family='Console', size=11)
        # Panels
        self._graphics = SegmentedPanel(master=self.window, width=300, height=50, text='Graphic Settings',
                                        options=list(GameConfigWindow.game_graphics.keys()))
        self._graphics.configure(border_color='grey', border_width=1)
        self._a_star = SegmentedPanel(master=self.window, width=300, height=50, text='Show A*',
                                      options=list(GameConfigWindow.a_star.keys()))
        self._a_star.configure(border_color='grey', border_width=1)
        self._size = SegmentedPanel(master=self.window, width=300, height=50, text='Game Size',
                                    options=list(GameConfigWindow.game_sizes.keys()))
        self._size.configure(border_color='grey', border_width=1)
        self._speed = SegmentedPanel(master=self.window, width=300, height=50, text='Game Speed',
                                     options=list(GameConfigWindow.game_speed.keys()))
        self._speed.configure(border_color='grey', border_width=1)
        self._dialog = IOFile(master=self.window, width=300, height=65, text='Select Model')
        self._dialog.configure(border_color='grey', border_width=1)
        # Trace
        self._dialog.error_var.trace('w', self._start_behavior)
        # Labels
        self._title = ctk.CTkLabel(master=self.window, text='Configuration', font=self._title_font)
        self._error = ctk.CTkLabel(master=self.window, text_color='red', font=self._error_font,
                                   textvariable=self._dialog.error_var, bg_color='transparent')
        # Buttons
        self._back_button = self._NextWinButton(master=self.window, text='Back', border_color='grey', border_width=1,
                                                font=self._buttons_font,
                                                command=lambda: self._mediator.back_to_main(self.window),
                                                width=100, height=20)
        self._start_button = self._NextWinButton(master=self.window, text='Start', border_color='grey', border_width=1,
                                                 font=self._buttons_font,
                                                 command=lambda: mediator_call(
                                                     game_size=GameConfigWindow.game_sizes[self._size.value].value,
                                                     game_speed=GameConfigWindow.game_speed[self._speed.value].value,
                                                     show_path=GameConfigWindow.a_star[self._a_star.value],
                                                     graphics=GameConfigWindow.game_graphics[self._graphics.value],
                                                     brain_path=self._dialog.value),
                                                 width=100, height=20)
        # Placement
        self._title.pack()
        self._graphics.pack(padx=4, pady=5)
        self._a_star.pack(padx=4, pady=5)
        self._size.pack(padx=4, pady=5)
        self._speed.pack(padx=4, pady=5)
        self._dialog.pack(padx=4, pady=5)
        self._error.place(x=8, y=337)
        self._back_button.place(x=25, y=365)
        self._start_button.place(x=175, y=365)

    def _start_behavior(self, *args):
        print(self._dialog.error_var.get())
        if self._dialog.error_var.get() != '':
            self._start_button.configure(state='disabled')
        else:
            self._start_button.configure(state='enabled')
