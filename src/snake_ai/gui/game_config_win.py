# This module contains the class that implements the GUI main menu

# Author: Álvaro Torralba
# Date: 19/06/2023
# Version: 0.0.1

from snake_ai.gui.panels import IOFile, SegmentedPanel
from snake_ai.gui.abc_win import WindowABC
from snake_ai.snake.enums import GameSize, GameSpeed
import customtkinter as ctk
from tkinter import messagebox
import os
from snake_ai.data import Folders


class GameConfigWindow(WindowABC):

    game_graphics = {'Light weight': 'SnakeLWGUI', 'Extended': 'SnakeHWGUI', }
    a_star = {'Yes': True, 'No': False}
    game_sizes = {'Small': GameSize.SMALL, 'Medium': GameSize.MEDIUM, 'Large': GameSize.LARGE}
    game_speed = {'Slow': GameSpeed.SLOW, 'Normal': GameSpeed.NORMAL, 'Fast': GameSpeed.FAST}

    def __init__(self, top_level: ctk.CTk, mediator, game_type: str):
        super().__init__(size=(300, 400), resizeable=False, top_level=top_level, mediator=mediator,
                         anchor_prev='topleft')
        if game_type == 'vsai':
            self._mediator_call = self._mediator.launch_vsai
        elif game_type == 'model':
            self._mediator_call = self._mediator.launch_model
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
        self._dialog = IOFile(master=self.window, width=300, height=65, text='Select Model', locking_window=self.window,
                              default_file_path=os.path.join(Folders.models_folder, 'binary_40_spa.nn'),
                              file_types=[("model files (*.nn)", "*.nn"), ("all files (*.*)", "*.*")])
        self._dialog.configure(border_color='grey', border_width=1)
        # Trace
        self._dialog.error_var.trace('w', self._start_behavior)
        self._dialog.value_var.trace('w', self._rest_error_state)
        # Labels
        self._title = ctk.CTkLabel(master=self.window, text='Game Configuration', font=self._title_font)
        self._error = ctk.CTkLabel(master=self.window, text_color='red', font=self._error_font,
                                   textvariable=self._dialog.error_var, bg_color='transparent')
        # Buttons
        self._back_button = self._NextWinButton(master=self.window, text='Back', font=self._buttons_font,
                                                command=lambda: self._mediator.back_to_main(self.window),
                                                width=100, height=20)
        self._start_button = self._NextWinButton(master=self.window, text='Start', font=self._buttons_font,
                                                 command=self._start_launch,
                                                 width=100, height=20)
        # Placement
        self._title.pack()
        self._graphics.pack(padx=4, pady=5)
        self._a_star.pack(padx=4, pady=5)
        self._size.pack(padx=4, pady=5)
        self._speed.pack(padx=4, pady=5)
        self._dialog.pack(padx=4, pady=5)
        self._error.place(x=8, y=337)
        self._back_button.place(x=37.5, y=365)
        self._start_button.place(x=162.5, y=365)

    def _start_behavior(self, *args):
        if self._dialog.error_var.get() != '':
            self._start_button.configure(state='disabled')
        else:
            self._start_button.configure(state='enabled')

    def _rest_error_state(self, *args):
        self._dialog.error_var.set('')

    def _start_launch(self):
        call = self._mediator_call(
                            game_size=GameConfigWindow.game_sizes[self._size.value].value,
                            game_speed=GameConfigWindow.game_speed[self._speed.value].value,
                            show_path=GameConfigWindow.a_star[self._a_star.value],
                            graphics=GameConfigWindow.game_graphics[self._graphics.value],
                            brain_path=self._dialog.value)
        if call is not None:
            self._dialog.file_var.set('')
            if call == 'bad type':
                self._dialog.error_var.set('The selected file does not contain a supported file type')
                messagebox.showerror('File type error', 'The selected file does not contain a supported file type',
                                     parent=self.window)
            elif call == 'file not found':
                self._dialog.error_var.set('The selected file has vanished')
                messagebox.showerror('File not found', 'The selected file has vanished from the specified path',
                                     parent=self.window)
