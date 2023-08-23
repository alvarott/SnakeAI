# This module contains the class that implements the app starting window


# Author: Álvaro Torralba
# Date: 19/06/2023
# Version: 0.0.1

from snake_ai.gui.abc_button import ButtonABC
from snake_ai.gui.abc_win import WindowABC
from snake_ai.gui import resources as rsc
from importlib import resources as rc
from PIL import Image, ImageTk
import customtkinter as ctk
import tkinter as tk


class StartWindow(WindowABC):
    """
    Implements the app starting window
    """

    def __init__(self, mediator):
        super().__init__(size=(400, 400), resizeable=False, mediator=mediator)
        self._background = self._set_background()
        self._bg_label = tk.Label(master=self._window, image=self._background)
        self._buttons_font = ctk.CTkFont(family="Console", size=16, weight="bold")
        self._exit_button = self._ExitButton(master=self._window, font=self._buttons_font, text='Exit',
                                             text_color='white',
                                             width=100, height=20, bg_color='#008be5', corner_radius=20,
                                             border_color='white', border_width=2)
        self._start_button = self._NextWinButton(master=self._window, font=self._buttons_font, text='Start',
                                                 text_color='white', width=100, height=20, bg_color='#008be5',
                                                 corner_radius=20, border_color='white', border_width=2,
                                                 mediator=mediator,
                                                 top_level=self, command=self._mediator.main_menu)
        self._bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self._start_button.place(x=140, y=290)
        self._exit_button.place(x=140, y=330)

    def _set_background(self) -> ImageTk:
        """
        Converts a background image to be displayed at the window
        :return:
        """
        raw_image = Image.open(str(rc.files(rsc).joinpath('start_bg.png')))
        resized_image = raw_image.resize((self._window.winfo_width(), self._window.winfo_height()), Image.LANCZOS)
        image = ImageTk.PhotoImage(resized_image)
        return image

    class _ExitButton(ButtonABC):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def _click_event(self):
            self.winfo_toplevel().destroy()
            quit()
