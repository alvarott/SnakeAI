# This module contains the base class for buttons

# Author: Álvaro Torralba
# Date: 21/06/2023
# Version: 0.0.1

from abc import ABC, abstractmethod
import customtkinter as ctk


class ButtonABC(ABC, ctk.CTkButton):
    """
    Buttons base class extend the CTKButton class
    """
    def __init__(self, variable: ctk.Variable = None, mediator=None, top_level=None, **kwargs):
        """
        Constructor
        :param variable: value holder if any
        :param kwargs: configuration parameters for the base class CTkButton
        """
        super().__init__(**kwargs)
        self._variable = variable
        self.mediator = mediator
        self.top = top_level
        self.configure(command=self._click_event)

    @property
    def value(self) -> None | int | float | bool | str:
        """
        Returns the value held by the variable associated with the button if any
        :return:
        """
        return None if self._variable is None else self._variable.get()

    @value.setter
    def value(self, new_value) -> None :
        if self._variable is not None:
            self._variable.set(new_value)

    @abstractmethod
    def _click_event(self, *args, **kwargs) -> None:
        """
        This method defines the behavior of the button when it is pressed
        :param args: any positional parameter needed
        :param kwargs: any key-value parameter needed
        :return:
        """
        pass
