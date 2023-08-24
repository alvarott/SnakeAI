# This module contains the base class for panels

# Author: Álvaro Torralba
# Date: 22/06/2023
# Version: 0.0.1

from snake_ai.gui.abc_button import ButtonABC
from snake_ai.gui.abc_panel import PanelABC
import snake_ai.gui._data as data
from tkinter import filedialog
from typing import Callable
import customtkinter as ctk
import os.path
import math
import re


class SpinBoxPanel(PanelABC):
    """
    Implements a custom spinbox
    """
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
    """
    Custom segmented panel
    """
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


class DropDownPanel(ctk.CTkOptionMenu):
    """
    Custom dropdown panel
    """
    def __init__(self, master: ctk.CTk | ctk.CTkFrame, options: list[str], mouse_wheel_func: Callable = None, **kwargs):
        # Fonts
        self._mouse_wheel_func = mouse_wheel_func
        self._font = ctk.CTkFont(family="Console", size=12)
        super().__init__(master=master, variable=ctk.StringVar(value=options[0]), values=options, font=self._font,
                         dropdown_font=self._font, button_color='#444',
                         button_hover_color='#333', dropdown_fg_color='#666', fg_color='#4a4a4a', **kwargs)
        self.bind("<MouseWheel>", self._mouse_wheel_event)
        self._values_list = options

    def _mouse_wheel_event(self, event):
        """
        Implements the behavior of the panel when the mouse wheel is used
        :param event: mouse wheel event
        :return:
        """
        if self.cget('state') != 'disabled':
            current_value = self.get()
            index = self._values_list.index(current_value)
            if event.delta < 0:
                if (index + 2) <= len(self._values_list):
                    self.set(self._values_list[index + 1])
            else:
                if (index - 1) >= 0:
                    self.set(self._values_list[index - 1])
        if self._mouse_wheel_func is not None:
            self._mouse_wheel_func()


class IOFile(PanelABC):
    """
    Implements a panel that allows to select a file
    """
    def __init__(self, master: ctk.CTk | ctk.CTkFrame, locking_window: ctk.CTk, text: str, width: int, height: int,
                 default_file_path: str, file_types: list[tuple[str, str]]):
        super().__init__(master=master,
                         variable=ctk.StringVar(value=default_file_path),
                         width=width, height=height)
        self._set_layout()
        self._cwidgets = []
        # Variables
        self._file_text_var = ctk.StringVar()
        self._file_error = ctk.StringVar()
        self._initial_path = ctk.StringVar(value=str(os.path.dirname(default_file_path)))
        # Fonts
        self._error_font = ctk.CTkFont(family='Console', size=12)
        # Inner Frame
        self._frame1 = ctk.CTkFrame(master=self)
        self._frame1.rowconfigure(index=0, weight=1, uniform='i')
        self._frame1.columnconfigure(index=0, weight=3, uniform='i')
        self._frame1.columnconfigure(index=1, weight=1, uniform='i')
        self._frame2 = ctk.CTkFrame(master=self._frame1, corner_radius=2, fg_color='#4a4a4a')
        # Labels
        self._title = ctk.CTkLabel(master=self, text=text, font=self._text)
        self._file = ctk.CTkLabel(master=self._frame2, textvariable=self._file_text_var, anchor='w', font=self._text)
        # Buttons
        self._browse_button = self._DialogButton(master=self._frame1, variable=self._variable,
                                                 label_var=self._file_text_var, text='Browse', font=self._text,
                                                 file_types=file_types, initial_path=self._initial_path,
                                                 locking_win=locking_window)
        # Placement
        self._frame1.grid(row=1, column=0, sticky='news', padx=4, pady=2)
        self._title.grid(row=0, column=0, padx=5, pady=2, sticky='ws')
        self._frame2.grid(row=0, column=0, sticky='news', padx=5, pady=5)
        self._file.pack(fill='both', expand=True)
        self._browse_button.grid(row=0, column=1, sticky='news', padx=5, pady=5)

        # Actions
        self._cwidgets.append(self._title)
        self._cwidgets.append(self._file)
        self._cwidgets.append(self._browse_button)

    @property
    def cwidgets(self):
        return self._cwidgets

    @property
    def file_var(self):
        return self._file_text_var

    @property
    def error_var(self):
        return self._file_error

    @property
    def title(self):
        return self._title

    def _set_layout(self):
        self.configure(fg_color='transparent')
        self.grid_propagate(False)
        for j in range(2):
            self.rowconfigure(index=j, weight=1, uniform='s')
        self.columnconfigure(index=0, weight=1, uniform='s')

    class _DialogButton(ButtonABC):
        def __init__(self, label_var: ctk.StringVar, file_types: list[tuple[str, str]], initial_path: ctk.StringVar,
                     locking_win: ctk.CTk, **kwargs):
            super().__init__(**kwargs)
            self._lock_win = locking_win
            self._default = str(self.value)
            self._file_types = file_types
            self._initial_path = initial_path
            self._label = label_var
            self._label.set(os.path.basename(self._default))

        def _click_event(self):
            path = filedialog.askopenfilename(initialdir=self._initial_path.get(), title="Select file",
                                              filetypes=self._file_types, parent=self._lock_win)
            if path != '':
                self.value = path
                self._label.set(os.path.basename(self.value))
                self._initial_path.set(os.path.dirname(path))
            else:
                self.value = self._default
                self._label.set(os.path.basename(self.value))
                self._initial_path.set(os.path.dirname(self.value))


class TabMenu(ctk.CTkTabview):
    """
    Custom TabMenu widget
    """
    def __init__(self, master: ctk.CTk | ctk.CTkFrame, tabs: list[str]):
        super().__init__(master=master)
        self._add_tabs(tabs)

    def _add_tabs(self, tabs: list[str]):
        for tab in tabs:
            self.add(tab)


class Entry(ctk.CTkEntry):
    """
    Custom Entry baseclass
    """
    def __init__(self, value: ctk.Variable, backup_value: ctk.Variable, label: ctk.CTkLabel, **kwargs):
        self._label = label
        self._value = value
        self._backup_value = backup_value
        self._colors = data.Colors()
        super().__init__(textvariable=self._value, fg_color=self._colors.entry_grey,
                         border_color=self._colors.entry_grey, **kwargs)
        self._value.trace('w', self._value_behavior)

    @property
    def value(self):
        return self._value.get()

    def set_error_color(self):
        self._label.configure(text_color=self._colors.error)

    def set_normal_color(self):
        if self.cget('state') == 'normal':
            self._label.configure(text_color=self._colors.active_text)

    def _value_behavior(self, *args):
        pass

    def set(self, new_entry: str):
        self._value.set(new_entry)


class NumericEntry(Entry):
    """
    Defines a custom numeric entry
    """
    def __init__(self, master: ctk.CTk | ctk.CTkFrame, from_: float | int, to: float | int, step: float | int,
                 type: str, label: ctk.CTkLabel, **kwargs):
        if step <= 0:
            raise ValueError("Step cannot be negative or zero")
        if type not in ['float', 'int']:
            raise ValueError(f'{type} is not supported data type')
        else:
            if type == 'float':
                self._cast = float
            else:
                self._cast = int
        self._type = type
        self._pattern = r'^(?:[1-9]\d*|0)?(?:\.\d*)?$' if self._type == 'float' else r'^(?:[1-9][0-9]*)?$'
        self._step: int | float
        self._from: int | float
        self._to: int | float
        self._value = ctk.StringVar(value='-1')
        self.set_from(from_)
        self.set_to(to)
        self.set_step(step)
        super().__init__(master=master, value=self._value, backup_value=ctk.StringVar(), label=label, **kwargs)
        self._value.set(f"{((self._from + self._to) / 2):.2f}" if self._type == 'float'
                        else f"{int((self._from + self._to) // 2)}")
        self._backup_value.set(self._value.get())
        self.bind("<MouseWheel>", self._mouse_wheel_event)

    @property
    def value(self):
        try:
            return self._cast(self._value.get())
        except Exception:
            return 0

    def set_from(self, from_: int | float):
        value = 0 if from_ < 0 else from_
        try:
            current = self.value
        except Exception:
            current = 0
        if value > current:
            self._value.set(str(self._cast(value)))
        self._from = value if self._type == 'float' else int(value)

    def set_to(self, to: int | float):
        if to < self._from:
            value = self._from
        elif to < 0:
            value = 0
        else:
            value = to
        try:
            current = self.value
        except Exception:
            current = 0
        if value < current:
            self._value.set(str(self._cast(value)))
        self._to = value if self._type == 'float' else int(value)

    def set_step(self, step: int | float):
        value = 1 if step < 0 else step
        self._step = value if self._type == 'float' else int(value)

    def _mouse_wheel_event(self, event):
        if self.cget('state') != 'disabled':
            current_value = 0 if self._value.get() == '' else self.value
            if event.delta > 0:
                next_value = current_value + self._step
            else:
                next_value = current_value - self._step
            if next_value > self._to:
                next_value = self._to
            elif next_value < self._from:
                next_value = self._from
            self._value.set(f"{next_value:.2f}" if self._type == 'float' else f"{next_value}")

    def _value_behavior(self, *args):
        floor = self._from if self._type == "int" else -0.0000000001
        input = self._value.get()
        if len(input) > 12:
            self._value.set(input[:-1])
        if not re.match(self._pattern, input):
            self._value.set(self._backup_value.get())
        else:
            self._backup_value.set(input)
        if self._value.get() != '' and self._value.get() != '.':
            if self.value >= self._to:
                self._value.set(f"{self._to:.2f}" if self._type == 'float' else f"{self._to}")
                self._backup_value.set(f"{self._to:.2f}" if self._type == 'float' else f"{self._to}")
            elif self.value <= floor:
                self._value.set(f"{self._from:.2f}" if self._type == 'float' else f"{self._from}")
                self._backup_value.set(f"{self._from:.2f}" if self._type == 'float' else f"{self._from}")
            self.set_normal_color()


class TextEntry(Entry):
    """
    Defines a custom text entry
    """
    def __init__(self, master: ctk.CTk | ctk.CTkFrame, label: ctk.CTkLabel, **kwargs):
        super().__init__(master=master, value=ctk.StringVar(), backup_value=ctk.StringVar(), label=label, **kwargs)

    def _value_behavior(self, *args):
        pattern = r'^[A-Za-z0-9_-]*$'
        input = self._value.get()
        if len(input) > 12:
            self._value.set(input[:-1])
        if not re.match(pattern, input):
            self._value.set(self._backup_value.get())
        else:
            self._backup_value.set(input)
        if len(self.value) > 0:
            self.set_normal_color()


class ArrayEntry(Entry):
    """
    Defines a custom array entry used for NN layers
    """
    def __init__(self, master: ctk.CTk | ctk.CTkFrame, label: ctk.CTkLabel, **kwargs):
        super().__init__(master=master, value=ctk.StringVar(), backup_value=ctk.StringVar(), label=label, **kwargs)

    @property
    def value(self):
        values = self._value.get().strip(',').split(',')
        try:
            values = [int(value) for value in values]
        except Exception:
            values = ""
        return values

    def _value_behavior(self, *args):
        pattern = r'(^(?:100|[1-9][0-9]?)(?:,(?:100|[1-9][0-9]?)(?=,|$))*(?:,)?)*$'
        input = self._value.get()
        counter = 0
        for char in input:
            if char == ',':
                counter += 1
        if counter > 10:
            self._value.set(self._backup_value.get())
            input = self._value.get()
        if not re.match(pattern, input):
            self._value.set(self._backup_value.get())
        else:
            self._backup_value.set(input)
        if len(self.value) > 0:
            self.set_normal_color()


class ProgressBar(ctk.CTkProgressBar):
    """
    Defines a custom progressbar
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # create the text item in the internal canvas
        self._canvas.create_text(0, 0, text=self._variable.get(), fill="white",
                                 font=('Console', 10), anchor="c", tags="progress_text")
        self.set(0)

    # override function to move the progress text at the center of the internal canvas
    def _update_dimensions_event(self, event):
        super()._update_dimensions_event(event)
        self._canvas.coords("progress_text", event.width / 2, event.height / 2)

    # override function to update the progress text whenever new value is set
    def set(self, val, **kwargs):
        super().set(val, **kwargs)
        self._canvas.itemconfigure("progress_text", text=f'Progress: {val * 100:.2f} %')
