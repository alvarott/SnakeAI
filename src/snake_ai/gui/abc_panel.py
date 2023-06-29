# This module contains the base class for panels

# Author: Álvaro Torralba
# Date: 22/06/2023
# Version: 0.0.1

from abc import ABC, abstractmethod
import customtkinter as ctk


class PanelABC(ABC,ctk.CTkFrame):
    def __init__(self, variable: ctk.Variable, **kwargs):
        super().__init__(**kwargs)
        self._variable = variable
        self._text = ctk.CTkFont(family="Console", size=12, weight="bold")

    @property
    def value(self):
        return self._variable.get()

    @value.setter
    def value(self, new_value):
        self._variable.set(new_value)

    def disable_panel(self):
        for widget in self.winfo_children():
            widget.configure(state="disabled")

    @abstractmethod
    def _set_layout(self):
        pass