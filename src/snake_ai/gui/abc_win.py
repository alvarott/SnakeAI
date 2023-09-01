# This module contains the base class for app windows


# Author: Álvaro Torralba
# Date: 21/06/2023
# Version: 0.0.1
from snake_ai.gui import resources as rsc
from importlib import resources as rc
from snake_ai.gui.abc_button import ButtonABC
from types import FunctionType
import customtkinter as ctk
from typing import Any
from abc import ABC


class WindowABC(ABC):
    """
    Window base class
    """
    def __init__(self, size: tuple[int, int], resizeable: bool, mediator, title: str = 'SnakeAI',
                 top_level: ctk.CTk = None, theme: str = 'dark', anchor_prev: str | None = None):
        """
        Constructor
        :param size: window size in pixels
        :param resizeable: sets if the window can be resized or not
        :param mediator: reference to the mediator class
        :param title: window title
        :param top_level: references to the parent window
        :param theme: selected theme
        :param anchor_prev: flag to set the position of the new window relative to the parent one supported values
                            [topleft, center]
        """
        self._v_anchor = ['topleft', 'center', None]
        if anchor_prev not in self._v_anchor:
            raise ValueError(f'Value {anchor_prev} is not a supported value a anchor_prev,'
                             f' supported_values {self._v_anchor}')
        ctk.set_appearance_mode(theme)
        if top_level is None:
            self._window = ctk.CTk()
        else:
            self._window = ctk.CTkToplevel(top_level)
            self._window.attributes('-alpha', 10)
            self._window.protocol("WM_DELETE_WINDOW", self._closing_button_event)
        self._window.after(230, lambda: self._window.iconbitmap(str(rc.files(rsc).joinpath('app_icon.ico'))))
        self._anchor = anchor_prev
        self._root = top_level
        self._mediator = mediator
        self._width = size[0]
        self._height = size[1]
        self._center_window()
        self._window.resizable(resizeable, resizeable)
        self._window.title(title)
        self._buttons_font = ctk.CTkFont(family="Console", size=16, weight="bold")
        self._title_font = ctk.CTkFont(family="Console", size=20, weight="bold")

    @property
    def window(self):
        return self._window

    def _center_window(self) -> None:
        """
        Places the window at the center of the screen
        :return:
        """
        screen_width = self._window.winfo_screenwidth()
        screen_height = self._window.winfo_screenheight()
        if self._anchor is None:
            center = (screen_width // 2, screen_height // 2)
            x_position = center[0] - (self._width // 2)
            y_position = center[1] - (self._height // 2)
            self._window.geometry(f'{self._width}x{self._height}+{x_position}+{y_position}')
        else:
            self.center_to_current(anchor=self._anchor, parent=self._root)

    def center_to_current(self, anchor: str, parent: ctk.CTk) -> None:
        """
        Centers the window at the same point that the previous window was located
        :param parent: previous window
        :param anchor: flag to position the window
        :return:
        """
        if anchor not in self._v_anchor:
            raise ValueError(f'{anchor} is not a supported value. Supported values {self._v_anchor}')
        if anchor == 'center':
            parent_width = parent.winfo_width()
            parent_height = parent.winfo_height()
            parent_x = parent.winfo_x()
            parent_y = parent.winfo_y()
            x_position = ((parent_width / 2) + parent_x) - self._width / 2
            y_position = ((parent_height / 2) + parent_y) - self._height / 2
            self._window.geometry(f'{self._width}x{self._height}+{int(x_position)}+{int(y_position)}')
        else:
            self._window.geometry(f'{self._width}x{self._height}+{parent.winfo_x()}+{parent.winfo_y()}')

    def set_layout(self, columns: int, columns_weight: int, rows: int, rows_weights: int, uniform: str) -> None:
        """
        Creates a grid layout for the window
        :param columns: number of columns
        :param columns_weight: width of the columns
        :param rows: number of rows
        :param rows_weights: width of the rows
        :param uniform: string used by tkinter to maintain the ratio
        :return:
        """
        for i in range(columns):
            self._window.columnconfigure(index=i, weight=columns_weight, uniform=uniform)
        for j in range(rows):
            self._window.rowconfigure(index=j, weight=rows_weights, uniform=uniform)

    def _closing_button_event(self):
        """
        Defines the behavior if the user presses the SO window closing button
        :return:
        """
        self._mediator.exit()

    class _NextWinButton(ButtonABC):
        """
        Defines a custom button class to be used inside the windows
        """
        def __init__(self, command: FunctionType | Any, **kwargs):
            super().__init__(**kwargs)
            self.command = command

        def _click_event(self):
            self.command()
