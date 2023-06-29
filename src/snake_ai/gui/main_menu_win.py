# This module contains the class that implements the GUI main menu

# Author: Álvaro Torralba
# Date: 19/06/2023
# Version: 0.0.1

from snake_ai.gui.abc_win import WindowABC
import customtkinter as ctk


class MainMenuWindow(WindowABC):
    def __init__(self, top_level: ctk.CTk, mediator):
        super().__init__(size=(300, 400), resizeable=False, top_level=top_level, mediator=mediator)
        self.set_layout(columns=1, columns_weight=1, rows=7, rows_weights=1, uniform='main_menu')
        # Frame container
        self._options_frame = ctk.CTkFrame(self.window)
        # Frame grid division
        self._options_frame.columnconfigure(index=0, weight=1, uniform='s')
        for row in range(4):
            self._options_frame.rowconfigure(index=row, weight=1, uniform='s')
        self._options_frame.grid(column=0, row=1, rowspan=4, sticky='nsew', padx=15, pady=5)
        # VS_AI button
        self._vs_ai_button = self._NextWinButton(master=self._options_frame, text='Play vs AI', font=self._buttons_font,
                                                 command=self._mediator.main_to_vsai)
        self._vs_ai_button.grid(column=0, row=0, sticky='nsew', padx=10, pady=5)
        # Try Model button
        self._try_model_button = self._NextWinButton(master=self._options_frame, text='Test Model',
                                                     font=self._buttons_font, command=self._mediator.main_to_try_model)
        self._try_model_button.grid(column=0, row=1, sticky='nsew', padx=10, pady=5)
        # Train Model button
        self._train_model_button = self._NextWinButton(master=self._options_frame, text='Train Model',
                                                       font=self._buttons_font,
                                                       command=self._mediator.training_config_window)
        self._train_model_button.grid(column=0, row=2, sticky='nsew', padx=10, pady=5)
        # Statistics button
        self._check_stats_button = self._NextWinButton(master=self._options_frame, text='Statistics',
                                                     font=self._buttons_font, command=self._mediator.statistics_window)
        self._check_stats_button.grid(column=0, row=3, sticky='nsew', padx=10, pady=5)
        # Title
        self._menu_title = ctk.CTkLabel(master=self._window, text='Main Menu', font=self._title_font)
        self._menu_title.grid(column=0, row=0, pady=2, sticky='s')
        # Exit button
        self._exit_button = self._NextWinButton(master=self._window, text='Exit', border_color='grey',
                                                border_width=2, font=self._buttons_font, command=self._mediator.exit)
        self._exit_button.grid(column=0, row=5, pady=10, rowspan=2)
        self.window.lift()

