# This module contains the class that implements the GUI main menu

# Author: Álvaro Torralba
# Date: 19/06/2023
# Version: 0.0.1

from snake_ai.gui.abc_win import WindowABC
from snake_ai.gui import resources as rsc
from importlib import resources as rc
from snake_ai.gui._data import Colors
import customtkinter as ctk
from PIL import Image
import os


class MainMenuWindow(WindowABC):
    def __init__(self, top_level: ctk.CTk, mediator):
        super().__init__(size=(300, 400), resizeable=False, top_level=top_level, mediator=mediator)
        # Button images
        self._images = {}
        self._load_images()
        # Frame container
        self._options_frame = ctk.CTkFrame(self.window)
        self._options_frame.pack(expand=True, fill='both')
        # VS_AI button
        self._vs_ai_button = self._NextWinButton(master=self._options_frame, text='     Play vs AI ',
                                                 font=self._buttons_font,
                                                 command=self._mediator.main_to_vsai,
                                                 image=self._images['joystick'], compound='left',
                                                 corner_radius=0,
                                                 fg_color=Colors.bg_grey,
                                                 hover_color=Colors.entry_grey)
        self._vs_ai_button.pack(expand=True, fill='both')
        # Try Model button
        self._try_model_button = self._NextWinButton(master=self._options_frame, text='     Test Model ',
                                                     font=self._buttons_font, command=self._mediator.main_to_try_model,
                                                     image=self._images['snake'], compound='left',
                                                     corner_radius=0,
                                                     fg_color=Colors.bg_grey,
                                                     hover_color=Colors.entry_grey
                                                     )
        self._try_model_button.pack(expand=True, fill='both')
        # Train Model button
        self._train_model_button = self._NextWinButton(master=self._options_frame, text='     Train Model',
                                                       font=self._buttons_font,
                                                       command=self._mediator.main_to_training_config,
                                                       image=self._images['dumbbell'], compound='left',
                                                       corner_radius=0,
                                                       fg_color=Colors.bg_grey,
                                                       hover_color=Colors.entry_grey
                                                       )
        self._train_model_button.pack(expand=True, fill='both')
        # Statistics button
        self._check_stats_button = self._NextWinButton(master=self._options_frame, text='     Statistics ',
                                                       font=self._buttons_font,
                                                       command=self._mediator.statistics_window,
                                                       image=self._images['plot'], compound='left',
                                                       corner_radius=0,
                                                       fg_color=Colors.bg_grey,
                                                       hover_color=Colors.entry_grey
                                                       )
        self._check_stats_button.pack(expand=True, fill='both')
        # Exit button
        self._exit_button = self._NextWinButton(master=self._options_frame, text='     Exit       ',
                                                font=self._buttons_font,
                                                command=self._mediator.exit,
                                                image=self._images['exit'], compound='left',
                                                fg_color=Colors.bg_grey,
                                                hover_color=Colors.entry_grey
                                                )
        self._exit_button.pack(expand=True, fill='both')
        self.window.lift()

    def _load_images(self):
        source = str(rc.files(rsc))
        with os.scandir(source) as files:
            for file in files:
                if '.png' in file.name:
                    raw_image = Image.open(os.path.join(source, file.name))
                    image = ctk.CTkImage(raw_image, size=(30,30))
                    self._images[file.name[0:file.name.index('.')]] = image