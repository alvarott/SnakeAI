# This module contains the base class for panels
import math
import os.path

# Author: Álvaro Torralba
# Date: 22/06/2023
# Version: 0.0.1

from snake_ai.gui.abc_button import ButtonABC
from snake_ai.IO import IO
from snake_ai.gui.abc_panel import PanelABC
from tkinter import filedialog
import customtkinter as ctk




class SpinBoxPanel(PanelABC):
    TYPES = ['double', 'int']

    def __init__(self, master: ctk.CTk, text: str, lower_limit: float, upper_limit: float, small_step: float,
                 large_step: float, width: int, height: int, num_type: str):
        if num_type not in SpinBoxPanel.TYPES:
            raise ValueError(f'{num_type} not a supported type for Spin Box Panel')
        if lower_limit >= upper_limit:
            raise ValueError('lower_limit must be lower than upper_limit')
        if num_type == 'int':
            self._low = math.floor(lower_limit)
            self._up = math.ceil(upper_limit)
            self._s_step = math.floor(small_step)
            self._l_step = math.ceil(large_step)
            self._init_value = ((self._up - self._low) // 2) + self._low
        else:
            self._low = lower_limit
            self._up = upper_limit
            self._s_step = small_step
            self._l_step = large_step
            self._init_value = ((self._up - self._low) / 2) + self._low
        super().__init__(master=master,
                         variable=ctk.DoubleVar(value=self._init_value) if num_type == 'double'
                         else ctk.IntVar(value=self._init_value),
                         width=width, height=height)
        self._set_layout()
        # Variables
        self._label_var = ctk.StringVar(value=str(self._init_value))
        # Fonts
        self._big_buttons = ctk.CTkFont(family="Console", size=16, weight="bold")
        self._small_buttons = ctk.CTkFont(family="Console", size=13, weight="bold")
        # Buttons
        self._s_add = self._AdditionButton(master=self, variable=self._variable, text='+', addition=self._s_step,
                                           label_variable=self._label_var, upper_limit=self._up,
                                           lower_limit=self._low, font=self._small_buttons)
        self._l_add = self._AdditionButton(master=self, variable=self._variable, text='+', addition=self._l_step,
                                           label_variable=self._label_var, upper_limit=self._up,
                                           lower_limit=self._low, font=self._big_buttons)
        self._s_sub = self._AdditionButton(master=self, variable=self._variable, text='-', addition=self._s_step * -1,
                                           label_variable=self._label_var, upper_limit=self._up,
                                           lower_limit=self._low, font=self._small_buttons)
        self._l_sub = self._AdditionButton(master=self, variable=self._variable, text='-', addition=self._l_step * -1,
                                           label_variable=self._label_var, upper_limit=self._up,
                                           lower_limit=self._low, font=self._big_buttons)
        # Labels
        self._name = ctk.CTkLabel(master=self, text=text, font=self._text)
        self._number = ctk.CTkLabel(master=self, textvariable=self._label_var, font=self._small_buttons)
        # Placement
        self._name.grid(row=0, column=0, columnspan=3, sticky='w', padx=2)
        self._l_add.grid(row=0, column=3, sticky='news', padx=2, pady=5)
        self._s_add.grid(row=0, column=4, sticky='news', padx=2, pady=5)
        self._number.grid(row=0, column=5)
        self._s_sub.grid(row=0, column=6, sticky='news', padx=2, pady=5)
        self._l_sub.grid(row=0, column=7, sticky='news', padx=2, pady=3)

    def _set_layout(self):
        self.configure(fg_color='transparent')
        self.grid_propagate(False)
        self.rowconfigure(index=0, weight=1, uniform='s')
        for i in range(8):
            self.columnconfigure(index=i, weight=1, uniform='s')

    class _AdditionButton(ButtonABC):
        def __init__(self, addition: float, label_variable: ctk.StringVar, upper_limit: float, lower_limit: float,
                     **kwargs):
            super().__init__(**kwargs)
            self._step = addition
            self._label = label_variable
            self._low = lower_limit
            self._up = upper_limit

        def _click_event(self):
            next_value = round(self.value + self._step, 2)
            if self._low <= next_value <= self._up:
                self.value = next_value
                self._label.set(str(round(self.value, 2)))


class SegmentedPanel(PanelABC):
    def __init__(self, master: ctk.CTk, text: str, options: list[str], width: int, height: int):
        super().__init__(master=master, variable=ctk.StringVar(value=options[0]), width=width, height=height)
        self._set_layout()
        # Labels
        self._title = ctk.CTkLabel(master=self, text=text, font=self._text)
        # Buttons
        self._multi_button = ctk.CTkSegmentedButton(master=self, variable=self._variable, values=options,
                                                    font=self._text)
        # Placement
        self._title.grid(row=0, column=0, padx=2, pady=2)
        self._multi_button.grid(row=1, column=0, sticky='news', padx=2, pady=2)

    def _set_layout(self):
        self.grid_propagate(False)
        for j in range(2):
            self.rowconfigure(index=j, weight=1, uniform='s')
        self.columnconfigure(index=0, weight=1, uniform='s')


class DropDownPanel(PanelABC):
    def __init__(self, master: ctk.CTk, text: str, options: list[str], width: int, height: int):
        super().__init__(master=master, variable=ctk.StringVar(value=options[0]), width=width, height=height)
        self._set_layout()
        # Fonts
        self._drop_down_font = ctk.CTkFont(family="Console", size=12)
        # Labels
        self._title = ctk.CTkLabel(master=self, text=text, font=self._text)
        # Buttons
        self._multi_button = ctk.CTkOptionMenu(master=self, variable=self._variable, values=options, font=self._text,
                                               dropdown_font=self._drop_down_font, button_color='#444',
                                               button_hover_color='#333', dropdown_fg_color='#666', fg_color='#4a4a4a')
        # Placement
        self._title.grid(row=0, column=0, padx=5, pady=2, sticky='w')
        self._multi_button.grid(row=1, column=0, sticky='news', padx=2, pady=2)

    def _set_layout(self):
        self.configure(fg_color='transparent')
        self.grid_propagate(False)
        for j in range(2):
            self.rowconfigure(index=j, weight=1, uniform='s')
        self.columnconfigure(index=0, weight=1, uniform='s')


class IOFile(PanelABC):
    def __init__(self, master: ctk.CTk, text: str, width: int, height: int):
        from importlib import resources as rc
        from snake_ai.snake import resources as rsc
        super().__init__(master=master,
                         variable=ctk.StringVar(value=str(rc.files(rsc).joinpath(f'default_controller/default_controller.nn'))),
                         width=width, height=height)
        self._set_layout()
        # Variables
        self._file_text_var = ctk.StringVar()
        self._file_error = ctk.StringVar()
        # Fonts
        self._error_font = ctk.CTkFont(family='Console', size=12)
        # Inner Frame
        self._frame1 = ctk.CTkFrame(master=self)
        self._frame1.rowconfigure(index=0, weight=1, uniform='i')
        self._frame1.columnconfigure(index=0, weight=3, uniform='i')
        self._frame1.columnconfigure(index=1, weight=1, uniform='i')
        self._frame2 = ctk.CTkFrame(master=self._frame1, corner_radius=0)
        # Labels
        self._title = ctk.CTkLabel(master=self, text=text, font=self._text)
        self._file = ctk.CTkLabel(master=self._frame2, textvariable=self._file_text_var, anchor='w', font=self._text)
        # Buttons
        self._browse_button = self._DialogButton(master=self._frame1, variable=self._variable,
                                                 label_var=self._file_text_var, text='Browse', font=self._text,
                                                 label_error=self._file_error)
        # Placement
        self._frame1.grid(row=1, column=0, sticky='news', padx=4, pady=2)
        self._title.grid(row=0, column=0, padx=5, pady=2, sticky='ws')
        self._frame2.grid(row=0, column=0, sticky='news', padx=5, pady=5)
        self._file.pack(fill='both', expand=True)
        self._browse_button.grid(row=0, column=1, sticky='news', padx=5, pady=5)

    @property
    def error_var(self):
        return self._file_error

    def _set_layout(self):
        self.configure(fg_color='transparent')
        self.grid_propagate(False)
        for j in range(2):
            self.rowconfigure(index=j, weight=1, uniform='s')
        self.columnconfigure(index=0, weight=1, uniform='s')

    class _DialogButton(ButtonABC):
        def __init__(self, label_var: ctk.StringVar, label_error: ctk.StringVar, **kwargs):
            super().__init__(**kwargs)
            self._default = str(self.value)
            self._label = label_var
            self._label.set(os.path.basename(self._default))
            self._error = label_error

        def _click_event(self):
            path = filedialog.askopenfilename(initialdir="/", title="Select model",
                                              filetypes=(("model files (*.nn)", "*.nn"), ("all files (*.*)", "*.*")))
            if path != '':
                if IO.load(path) is None:
                    self._error.set('The file selected does not contain a supported model')
                    self.value = ''
                    self._label.set('')
                else:
                    self._error.set('')
                    self.value = path
                    self._label.set(os.path.basename(self.value))
            else:
                self.value = self._default
                self._label.set(os.path.basename(self.value))
                self._error.set('')
