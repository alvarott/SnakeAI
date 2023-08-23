# This module contains the base class for panels

# Author: Álvaro Torralba
# Date: 22/06/2023
# Version: 0.0.1

from abc import ABC, abstractmethod
import snake_ai.gui._data as data
import customtkinter as ctk


class PanelABC(ABC, ctk.CTkFrame):
    def __init__(self, variable: ctk.Variable, **kwargs):
        """
        Constructor
        :param variable: tkinter variable associated with the panel
        :param kwargs: ctk.CTkFrame kwargs
        """
        super().__init__(**kwargs)
        self._color_data = data.Colors()
        self._variable = variable
        self._text = ctk.CTkFont(family="Console", size=12, weight="bold")

    @property
    def value_var(self) -> ctk.Variable:
        """
        Returns the variable that holds the panel value
        :return:
        """
        return self._variable

    @property
    def value(self):
        """
        Returns the actual value that the panel value variable holds
        :return:
        """
        return self._variable.get()

    @value.setter
    def value(self, new_value):
        self._variable.set(new_value)

    @abstractmethod
    def _set_layout(self):
        """
        Panel layout method setter
        :return:
        """
        pass

    def _flip_widgets(self, widgets: list, state: bool):
        """
        Provides a way to deactivate or activate a list of widgets
        :param widgets: list of widget to activate or deactivate
        :param state: flag to indicate if the widget should pass a disabled (false) or enabled state (true)
        :return:
        """
        for widget in widgets:
            if state:
                if isinstance(widget, ctk.CTkLabel):
                    widget.configure(text_color=self._color_data.inactive_text)
                else:
                    if isinstance(widget, ctk.CTkEntry):
                        widget.configure(text_color=self._color_data.inactive_text_entry)
                    widget.configure(state='disabled')
            else:
                if isinstance(widget, ctk.CTkLabel):
                    widget.configure(text_color=self._color_data.active_text)
                else:
                    if isinstance(widget, ctk.CTkEntry):
                        widget.configure(text_color=self._color_data.active_text_entry)
                    widget.configure(state='normal')
