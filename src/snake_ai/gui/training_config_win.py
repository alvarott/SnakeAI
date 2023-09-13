# This module contains the class that implements the GUI training configuration window

# Author: Álvaro Torralba
# Date: 1/08/2023
# Version: 0.0.1

from snake_ai.gui.panels import IOFile, DropDownPanel, TabMenu, ArrayEntry, NumericEntry, TextEntry
from snake_ai.gui._data import Colors
from snake_ai.gui.abc_win import WindowABC
from snake_ai.gui.abc_panel import PanelABC
from snake_ai.data import Population
from snake_ai.data import Folders
import snake_ai.gui._data as data
from tkinter import messagebox
import customtkinter as ctk
from snake_ai.IO import IO
import numpy as np
import os


class TrainingConfigWindow(WindowABC):
    """
    Implements the training configuration window
    """
    def __init__(self, top_level: ctk.CTk, mediator):
        super().__init__(size=(320, 400), resizeable=False, top_level=top_level, mediator=mediator,
                         anchor_prev='topleft')
        # Master Frames
        self._master_frame = ctk.CTkFrame(master=self.window)
        self._master_frame.rowconfigure(index=0, weight=9, uniform='i')
        self._master_frame.rowconfigure(index=1, weight=1, uniform='i')
        # Tab Frames
        self._tab = TabMenu(master=self._master_frame, tabs=['General', 'Neural Network', 'Genetic Algorithm'])
        # Subframes
        self._subframes = self._TGeneralPanel(master=self._tab, locking_win=self.window, width=300, height=390)
        # Buttons
        self._back_button = self._NextWinButton(master=self.window, text='Back',
                                                font=self._buttons_font,
                                                command=lambda: self._mediator.back_to_main(self.window),
                                                width=100, height=20, bg_color=Colors.dark_grey)
        self._next_button = self._NextWinButton(master=self.window, text='Next', font=self._buttons_font,
                                                command=self._next_behavior, bg_color=Colors.dark_grey,
                                                width=100, height=20)

        # Placements
        self._master_frame.pack(fill=ctk.BOTH, expand=True)
        self._tab.grid(column=0, row=0, sticky='news', padx=2, pady=2)
        self._subframes.grid(sticky='news', padx=2, pady=2)
        self._back_button.place(x=50, y=365)
        self._next_button.place(x=175, y=365)

    def clean(self) -> None:
        """
        If the training is stopped to tune some of the parameters it sets the selected previous population as the one
        under training
        :return:
        """
        self._subframes.set_population()

    def _next_behavior(self) -> None:
        """
        Next button behavior
        :return:
        """
        config, prev_population = self._subframes.check_launch()
        if config is not None:
            self._mediator.training_widow(config, prev_population)

    class _TGeneralPanel(PanelABC):
        """
        Implements the general configuration panel
        """
        def __init__(self, master: TabMenu | ctk.CTkFrame, locking_win: ctk.CTk, **kwargs):
            super().__init__(variable=ctk.StringVar(), master=master.tab('General'), **kwargs)
            self._set_layout()
            # Config data
            self._lock_win = locking_win
            self._general_data = data.GeneralConfig()
            self._file_data = data.FileConfig()
            self._color_data = data.Colors()
            self._pop_data = Population()
            self._mapping_in = data.DropDownMapping().mapping
            self._mapping_out = {value: key for key, value in self._mapping_in.items()}
            self._previous_pop_obj: dict | None = None
            # Controlled Widgets
            self._cwidgets_g1 = []
            self._cwidgets_g2 = []
            self.entries = {}
            self._neural = TrainingConfigWindow._TNeuralPanel(master=master.tab('Neural Network'),
                                                              width=300, height=390)
            self._add_entries(self._neural.entries)
            self._genetic = TrainingConfigWindow._TGeneticPanel(master=master.tab('Genetic Algorithm'),
                                                                width=300, height=390)
            self._add_entries(self._genetic.entries)
            # Font
            self._font = ctk.CTkFont(family='console', size=13)
            self._error_font = ctk.CTkFont(family='console', size=11)
            # Labels
            self._error_lb = ctk.CTkLabel(master=self, text_color='red', font=self._error_font, bg_color='transparent')
            self._model_lb = ctk.CTkLabel(master=self, text="  Model Name", font=self._font)
            self._gsize_lb = ctk.CTkLabel(master=self, text="  Game Size", font=self._font)
            self._cpu_lb = ctk.CTkLabel(master=self, text="  Cpu Cores", font=self._font)
            self._vision_lb = ctk.CTkLabel(master=self, text="  Vision", font=self._font)
            self._previous_lb = ctk.CTkLabel(master=self, text="  Previous Population", font=self._font)
            # Widgets
            self._model_w = TextEntry(master=self, label=self._model_lb)
            self._gsize_w = DropDownPanel(master=self, options=list(self._general_data.training_grid_size.keys()))
            self._cpu_w = NumericEntry(master=self, from_=1, to=os.cpu_count() - 2, step=1, type='int',
                                       label=self._cpu_lb)
            self._vision_w = DropDownPanel(master=self, options=self._general_data.vision)
            self._previous_bool_w = ctk.BooleanVar(value=False)
            self._previous_w = ctk.CTkCheckBox(master=self, border_width=1, text='', variable=self._previous_bool_w,
                                               command=self._check_behavior)
            self._dialog_w = IOFile(master=self, width=300, height=65, text='Select Existing Population',
                                    locking_window=locking_win,
                                    default_file_path=Folders.populations_folder + '/',
                                    file_types=self._file_data.population_file)
            self._dialog_w.title.configure(font=self._font)

            # Entries
            self.entries['model'] = self._model_w
            self.entries['game_size'] = self._gsize_w
            self.entries['cpu'] = self._cpu_w
            self.entries['vision'] = self._vision_w

            # Placements
            self._neural.grid(sticky='news', padx=2, pady=2)
            self._genetic.grid(sticky='news', padx=2, pady=2)
            self._model_lb.grid(column=0, row=1, sticky='w')
            self._gsize_lb.grid(column=0, row=2, sticky='w')
            self._cpu_lb.grid(column=0, row=3, sticky='w')
            self._vision_lb.grid(column=0, row=4, sticky='w')
            self._previous_lb.grid(column=0, row=5, sticky='w')
            self._error_lb.place(x=10, y=275)

            self._model_w.grid(column=1, row=1, sticky='w', padx=2, pady=2)
            self._gsize_w.grid(column=1, row=2, sticky='w', padx=2, pady=2)
            self._cpu_w.grid(column=1, row=3, sticky='w', padx=2, pady=2)
            self._vision_w.grid(column=1, row=4, sticky='w', padx=2, pady=2)
            self._previous_w.grid(column=1, row=5, sticky='w', padx=2, pady=2)
            self._dialog_w.grid(column=0, row=6, rowspan=2, columnspan=2, sticky='w', padx=2, pady=2)

            # Actions
            self._error_lb.configure(textvariable=self._dialog_w.error_var)
            self._cwidgets_g2.extend(self._dialog_w.cwidgets)
            self._cwidgets_g1.append(self._vision_lb)
            self._cwidgets_g1.append(self._vision_w)
            self._flip_widgets(self._cwidgets_g2, True)
            self._dialog_w.file_var.trace('w', self._set_prev_population)

        def set_population(self) -> None:
            """
            Resets the selected population
            :return:
            """
            self._dialog_w.file_var.set('')
            self._previous_w.deselect()
            self._check_behavior()

        def _check_behavior(self) -> None:
            """
            Implements the behavior of the check button that disabled the NN configuration or enables it
            :return:
            """
            if self._previous_bool_w.get():
                self._flip_widgets(self._cwidgets_g1, True)
                self._flip_widgets(self._cwidgets_g2, False)
                self._neural.switch(True)
            else:
                self._flip_widgets(self._cwidgets_g1, False)
                self._flip_widgets(self._cwidgets_g2, True)
                self._neural.switch(False)
                self._dialog_w.error_var.set('')
                self._dialog_w.file_var.set('')

        def _set_layout(self) -> None:
            self.grid_propagate(False)
            self.rowconfigure(index=0, weight=1, uniform='s')
            for j in range(1, 10):
                self.rowconfigure(index=j, weight=2, uniform='s')
            self.rowconfigure(index=10, weight=1, uniform='s')
            for i in range(2):
                self.columnconfigure(index=i, weight=1, uniform='s')

        def _set_prev_population(self, *args) -> None:
            """
            Used when a previous population is used to check the instances loaded are correct
            :param args:
            :return:
            """
            self._previous_pop_obj = None
            if self._dialog_w.file_var.get() == "":
                return
            if os.path.isfile(self._dialog_w.value):
                try:
                    prev_population = IO.load(self._dialog_w.value, dict)
                    names = list(prev_population.keys())
                    pop_struct = vars(self._pop_data)
                    # Check if the instance conserve the original structure
                    for name, value in prev_population.items():
                        if name in names:
                            if type(prev_population[name]) == pop_struct[name][1]:
                                continue
                            else:
                                raise ValueError()
                        else:
                            raise ValueError()
                    # Check hidden layers config values
                    for value in prev_population['hidden']:
                        if not isinstance(value, int) or value > 100 or value < 1:
                            raise ValueError
                    # Check that individuals NN codification is coherent with the layers
                    layers = [22] + prev_population['hidden'] + [3]
                    length = 0
                    for i in range(1, len(layers)):
                        length += layers[i] * layers[i - 1]
                        if prev_population['bias']:
                            length += layers[i]
                    for id, nn in prev_population['population'].items():
                        if not isinstance(id, int) or not isinstance(nn, np.ndarray) or length != len(nn):
                            raise ValueError()
                    self._dialog_w.error_var.set('')
                    self._propagate_settings(prev_population)
                    self._previous_pop_obj = prev_population['population']
                except Exception:
                    self._dialog_w.error_var.set('The selected file does not contain a supported file type')
                    messagebox.showerror('File type error',
                                         'The selected file does not contain a supported file type or '
                                         'it is corrupted',
                                         parent=self._lock_win)
            else:
                if not os.path.exists(self._dialog_w.value):
                    self._dialog_w.error_var.set('The selected file has vanished')
                    messagebox.showerror('File not found',
                                         'The selected file has vanished from the specified path',
                                         parent=self._lock_win)
                else:
                    self._dialog_w.error_var.set('')

        def _propagate_settings(self, settings: dict) -> None:
            """
            Propagates de previous population settings to the GUI
            :param settings: previous population settings
            :return:
            """
            for item in settings.items():
                if isinstance(item[1], list):
                    self.entries[item[0]].set(','.join([str(num) for num in item[1]]))
                elif item[0] == 'population':
                    self.entries[item[0]].set(len(item[1]))
                elif isinstance(item[1], bool):
                    self.entries[item[0]].set(item[1])
                else:
                    self.entries[item[0]].set(self._mapping_in[item[1]])

        def _add_entries(self, entries: dict[str, ctk.CTkEntry]) -> None:
            """
            Adds entries to the general dictionary
            :param entries: entries dict
            :return:
            """
            self.entries |= entries

        def check_launch(self) -> tuple:
            """
            Checks if all setting are being correctly configured
            :return: the selected configuration and the previous population instance if any
            """
            unfilled = []
            final_values = {}
            if self._previous_bool_w.get() == 1 and self._dialog_w.file_var.get() == '':
                messagebox.showerror('Missing fields', 'No previous population selected',
                                     parent=self._lock_win)
                return None, None
            for entry in self.entries.items():
                # Check keyboard entries
                if isinstance(entry[1], ctk.CTkEntry):
                    value = entry[1].get()
                    if entry[1].cget('state') == 'normal':
                        if value == '' or value == '.':
                            unfilled.append(entry[1])
                            continue
                    if '_param' in entry[0]:
                        final_values[entry[0]] = (entry[1].value, entry[1].cget('state'))
                    else:
                        final_values[entry[0]] = entry[1].value
                # Check dropdown entries
                elif isinstance(entry[1], DropDownPanel):
                    final_values[entry[0]] = self._mapping_out[entry[1].get()]
                else:
                    final_values[entry[0]] = entry[1].get()
            if len(unfilled) > 0:
                for entry in unfilled:
                    entry.set_error_color()
                messagebox.showerror('Missing fields', 'Please fill all the required fields',
                                     parent=self._lock_win)
                return None, None
            else:
                return final_values, self._previous_pop_obj

    class _TNeuralPanel(PanelABC):
        """
        Implements the neural network configuration panel
        """
        def __init__(self, master: ctk.CTk | ctk.CTkFrame, **kwargs):
            super().__init__(variable=ctk.StringVar(), master=master, **kwargs)
            self._set_layout()
            # Data
            self._neural_data = data.NeuralConfig()
            self._color_data = data.Colors()
            # Controlled Widgets
            self._cwidgets_g1 = []
            self._cwidgets_g2 = []
            self.entries = {}
            # Font
            self._font = ctk.CTkFont(family='console', size=13)
            # Labels
            self._hiddenl_lb = ctk.CTkLabel(master=self, text="  Hidden Layers", font=self._font)
            self._hiddeni_lb = ctk.CTkLabel(master=self, text="  Hidden Initialization", font=self._font)
            self._hiddena_lb = ctk.CTkLabel(master=self, text="  Hidden Activation", font=self._font)
            self._outputi_lb = ctk.CTkLabel(master=self, text="  Output Initialization", font=self._font)
            self._outputa_lb = ctk.CTkLabel(master=self, text="  Output Activation", font=self._font)
            self._bias_lb = ctk.CTkLabel(master=self, text="  Bias", font=self._font)
            self._biasi_lb = ctk.CTkLabel(master=self, text="  Bias Initialization", font=self._font)
            # Widgets
            self._hiddenl_w = ArrayEntry(master=self, label=self._hiddenl_lb)
            self._hiddeni_w = DropDownPanel(master=self, options=self._neural_data.hidden_init)
            self._hiddena_w = DropDownPanel(master=self, options=self._neural_data.hidden_act)
            self._outputi_w = DropDownPanel(master=self, options=self._neural_data.output_init)
            self._outputa_w = DropDownPanel(master=self, options=self._neural_data.output_act)
            self._bias_bool_w = ctk.BooleanVar(value=False)
            self._bias_w = ctk.CTkCheckBox(master=self, border_width=1, text='', variable=self._bias_bool_w,
                                           command=self._check_behavior)
            self._biasi_w = DropDownPanel(master=self, options=self._neural_data.bias_init)

            # Placements
            self._hiddenl_lb.grid(column=0, row=1, sticky='w')
            self._hiddeni_lb.grid(column=0, row=2, sticky='w')
            self._hiddena_lb.grid(column=0, row=3, sticky='w')
            self._outputi_lb.grid(column=0, row=4, sticky='w')
            self._outputa_lb.grid(column=0, row=5, sticky='w')
            self._bias_lb.grid(column=0, row=6, sticky='w')
            self._biasi_lb.grid(column=0, row=7, sticky='w')

            self._hiddenl_w.grid(column=1, row=1, sticky='w', padx=2, pady=2)
            self._hiddeni_w.grid(column=1, row=2, sticky='w', padx=2, pady=2)
            self._hiddena_w.grid(column=1, row=3, sticky='w', padx=2, pady=2)
            self._outputi_w.grid(column=1, row=4, sticky='w', padx=2, pady=2)
            self._outputa_w.grid(column=1, row=5, sticky='w', padx=2, pady=2)
            self._bias_w.grid(column=1, row=6, sticky='w', padx=2, pady=2)
            self._biasi_w.grid(column=1, row=7, sticky='w', padx=2, pady=2)

            # Entries
            self.entries['hidden'] = self._hiddenl_w
            self.entries['hidden_init'] = self._hiddeni_w
            self.entries['hidden_act'] = self._hiddena_w
            self.entries['output_init'] = self._outputi_w
            self.entries['output_act'] = self._outputa_w
            self.entries['bias'] = self._bias_bool_w
            self.entries['bias_init'] = self._biasi_w

            # Actions
            self._cwidgets_g1.append(self._hiddenl_lb)
            self._cwidgets_g1.append(self._hiddeni_lb)
            self._cwidgets_g1.append(self._hiddena_lb)
            self._cwidgets_g1.append(self._outputi_lb)
            self._cwidgets_g1.append(self._outputa_lb)
            self._cwidgets_g1.append(self._bias_lb)
            self._cwidgets_g1.append(self._biasi_lb)
            self._cwidgets_g2.append(self._biasi_lb)
            self._cwidgets_g1.append(self._hiddenl_w)
            self._cwidgets_g1.append(self._hiddena_w)
            self._cwidgets_g1.append(self._hiddeni_w)
            self._cwidgets_g1.append(self._outputi_w)
            self._cwidgets_g1.append(self._outputa_w)
            self._cwidgets_g1.append(self._bias_w)
            self._cwidgets_g1.append(self._biasi_w)
            self._cwidgets_g2.append(self._biasi_w)
            self._check_behavior()

        def switch(self, activate: bool) -> None:
            """
            Deactivates the panel widgets
            :param activate:
            :return:
            """
            self._flip_widgets(self._cwidgets_g1, activate)
            if not activate:
                self._check_behavior()

        def _check_behavior(self) -> None:
            """
            Checkbox bias behavior method
            :return:
            """
            if self._bias_bool_w.get():
                self._flip_widgets(self._cwidgets_g2, False)
            else:
                self._flip_widgets(self._cwidgets_g2, True)

        def _set_layout(self) -> None:
            self.grid_propagate(False)
            self.rowconfigure(index=0, weight=1, uniform='s')
            for j in range(1, 10):
                self.rowconfigure(index=j, weight=2, uniform='s')
            self.rowconfigure(index=10, weight=1, uniform='s')
            for i in range(2):
                self.columnconfigure(index=i, weight=1, uniform='s')

    class _TGeneticPanel(PanelABC):
        """
        Implements the GA configuration panel
        """
        def __init__(self, master: ctk.CTk | ctk.CTkFrame, **kwargs):
            super().__init__(variable=ctk.StringVar(), master=master, **kwargs)
            self._set_layout()
            # Data
            self._genetic_data = data.GeneticConfig()
            self._color_data = data.Colors()
            # Controlled Widgets
            self._cwidgets_g1 = []
            self._cwidgets_g2 = []
            self.entries = {}
            # Font
            self._font = ctk.CTkFont(family='console', size=13)
            # Labels
            self._population_lb = ctk.CTkLabel(master=self, text="  Population", font=self._font)
            self._selection_lb = ctk.CTkLabel(master=self, text="  Selection", font=self._font)
            self._tournament_lb = ctk.CTkLabel(master=self, text="     Tournament Size", font=self._font)
            self._crossover_lb = ctk.CTkLabel(master=self, text="  Crossover", font=self._font)
            self._cross_param_lb = ctk.CTkLabel(master=self, font=self._font)
            self._cross_rate_lb = ctk.CTkLabel(master=self, text="     Crossover Rate", font=self._font)
            self._mutation_lb = ctk.CTkLabel(master=self, text="  Mutation", font=self._font)
            self._mut_rate_lb = ctk.CTkLabel(master=self, text="     Mutation Rate", font=self._font)
            self._mut_param_lb = ctk.CTkLabel(master=self, font=self._font)
            self._replacement_lb = ctk.CTkLabel(master=self, text="  Replacement", font=self._font)
            self._offspring_lb = ctk.CTkLabel(master=self, text="     Offspring", font=self._font)
            # Widgets
            self._population_w = NumericEntry(master=self, from_=1, to=1000, step=10, type='int',
                                              label=self._population_lb)
            self._selection_w = DropDownPanel(master=self, options=self._genetic_data.selection,
                                              command=self._select_behavior,
                                              mouse_wheel_func=self._select_behavior)
            self._tournament_w = NumericEntry(master=self, from_=1, to=250, step=10, type='int',
                                              label=self._tournament_lb)
            self._crossover_w = DropDownPanel(master=self, options=list(self._genetic_data.crossover.keys()),
                                              command=self._crossover_behavior,
                                              mouse_wheel_func=self._crossover_behavior)
            self._cross_rate_w = NumericEntry(master=self, from_=0, to=1, step=0.01, type='float',
                                              label=self._cross_rate_lb)
            self._cross_param_w = NumericEntry(master=self, from_=0, to=1, step=0.01, type='float',
                                               label=self._cross_param_lb)
            self._mutation_w = DropDownPanel(master=self, options=list(self._genetic_data.mutation.keys()),
                                             command=self._mutation_behavior,
                                             mouse_wheel_func=self._mutation_behavior)
            self._mut_rate_w = NumericEntry(master=self, from_=0, to=1, step=0.01, type='float',
                                            label=self._mut_rate_lb)
            self._mut_param_w = NumericEntry(master=self, from_=0, to=1, step=0.01, type='float',
                                             label=self._mut_param_lb)
            self._replacement_w = DropDownPanel(master=self, options=self._genetic_data.replacement,
                                                command=self._replacement_behavior,
                                                mouse_wheel_func=self._replacement_behavior)
            self._offspring_w = NumericEntry(master=self, from_=1, to=250, step=10, type='int',
                                             label=self._offspring_lb)

            # Entries
            self.entries['population'] = self._population_w
            self.entries['selection'] = self._selection_w
            self.entries['selection_param'] = self._tournament_w
            self.entries['crossover'] = self._crossover_w
            self.entries['crossover_param'] = self._cross_param_w
            self.entries['crossover_rate'] = self._cross_rate_w
            self.entries['mutation'] = self._mutation_w
            self.entries['mutation_param'] = self._mut_param_w
            self.entries['mutation_rate'] = self._mut_rate_w
            self.entries['replacement'] = self._replacement_w
            self.entries['offspring'] = self._offspring_w

            # Placements
            self._population_lb.grid(column=0, row=1, sticky='w')
            self._selection_lb.grid(column=0, row=2, sticky='w')
            self._tournament_lb.grid(column=0, row=3, sticky='w')
            self._crossover_lb.grid(column=0, row=4, sticky='w')
            self._cross_param_lb.grid(column=0, row=5, sticky='w')
            self._cross_rate_lb.grid(column=0, row=6, sticky='w')
            self._mutation_lb.grid(column=0, row=7, sticky='w')
            self._mut_param_lb.grid(column=0, row=8, sticky='w')
            self._mut_rate_lb.grid(column=0, row=9, sticky='w')
            self._replacement_lb.grid(column=0, row=10, sticky='w')
            self._offspring_lb.grid(column=0, row=11, sticky='w')

            self._population_w.grid(column=1, row=1, sticky='w', padx=2, pady=2)
            self._selection_w.grid(column=1, row=2, sticky='w', padx=2, pady=2)
            self._tournament_w.grid(column=1, row=3, sticky='w', padx=2, pady=2)
            self._crossover_w.grid(column=1, row=4, sticky='w', padx=2, pady=2)
            self._cross_param_w.grid(column=1, row=5, sticky='w', padx=2, pady=2)
            self._cross_rate_w.grid(column=1, row=6, sticky='w', padx=2, pady=2)
            self._mutation_w.grid(column=1, row=7, sticky='w', padx=2, pady=2)
            self._mut_param_w.grid(column=1, row=8, sticky='w', padx=2, pady=2)
            self._mut_rate_w.grid(column=1, row=9, sticky='w', padx=2, pady=2)
            self._replacement_w.grid(column=1, row=10, sticky='w', padx=2, pady=2)
            self._offspring_w.grid(column=1, row=11, sticky='w', padx=2, pady=2)

            # Actions
            self._population_w.set('500')
            self._offspring_w.set('250')
            self._tournament_w.delete(0, len(self._tournament_w.get()))
            self._tournament_w.insert(0, '2')
            self._select_behavior()
            self._crossover_behavior()
            self._mutation_behavior()
            self._replacement_behavior()
            self._population_w.bind('<Leave>', self._leave_event)
            self._tournament_w.bind('<Leave>', self._leave_event)
            self._population_w.bind('<MouseWheel>', self._population_behavior)
            vcmd = (self.register(self._population_behavior), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
            self._population_w.configure(validate='key', validatecommand=vcmd)

        def _leave_event(self, event) -> None:
            """
            Set the entries to a valid minimum value
            :param event:  leave mouse event
            :return:
            """
            if self._population_w.value < 2:
                self._population_w.set('2')
            if self._tournament_w.value < 2:
                self._tournament_w.set('2')
            self._offspring_w.set_to(self._population_w.value)
            self._tournament_w.set_to(self._population_w.value)

        def _set_layout(self) -> None:
            self.grid_propagate(False)
            self.rowconfigure(index=0, weight=1, uniform='s')
            for j in range(1, 17):
                self.rowconfigure(index=j, weight=2, uniform='s')
            self.rowconfigure(index=12, weight=1, uniform='s')
            for i in range(2):
                self.columnconfigure(index=i, weight=1, uniform='s')

        def _select_behavior(self, *args) -> None:
            """
             Selection dropdown panel behavior
             :param args:
             :return:
             """
            if self._selection_w.get() == 'Tournament':
                self._flip_widgets([self._tournament_lb, self._tournament_w], False)
            else:
                self._flip_widgets([self._tournament_lb, self._tournament_w], True)

        def _crossover_behavior(self, *args) -> None:
            """
            Crossover dropdown panel behavior
            :param args:
            :return:
            """
            option = self._crossover_w.get()
            parameter = self._genetic_data.crossover[option]
            self._cross_param_lb.configure(text=f"     {parameter}")
            if parameter == '':
                self._flip_widgets([self._cross_param_w], True)
            else:
                self._flip_widgets([self._cross_param_w], False)
                self._cross_param_w.set_from(self._genetic_data.hyperparams_range[parameter][0])
                self._cross_param_w.set_to(self._genetic_data.hyperparams_range[parameter][1])
                self._cross_param_w.set_step(self._genetic_data.hyperparams_range[parameter][2])

        def _mutation_behavior(self, *args) -> None:
            """
            Mutation dropdown panel behavior
            :param args:
            :return:
            """
            option = self._mutation_w.get()
            parameter = self._genetic_data.mutation[option]
            self._mut_param_lb.configure(text=f"     {parameter}")
            if parameter == '':
                self._flip_widgets([self._mut_param_w], True)
            else:
                self._flip_widgets([self._mut_param_w], False)
                self._mut_param_w.set_from(self._genetic_data.hyperparams_range[parameter][0])
                self._mut_param_w.set_to(self._genetic_data.hyperparams_range[parameter][1])
                self._mut_param_w.set_step(self._genetic_data.hyperparams_range[parameter][2])

        def _replacement_behavior(self, *args) -> None:
            """
            Replacement dropdown panel behavior
            :param args:
            :return:
            """
            if self._replacement_w.get() == 'Generational':
                self._flip_widgets([self._offspring_lb, self._offspring_w], True)
            else:
                self._flip_widgets([self._offspring_lb, self._offspring_w], False)

        def _population_behavior(self, *args, **kwargs) -> bool:
            """
            Limits the offspring and tournament entries according to the population
            :param args:
            :param kwargs:
            :return:
            """
            try:
                if len(args) > 1:
                    population = int(args[2])
                else:
                    population = int(self._population_w.get())
                self._offspring_w.set_to(population)
                self._tournament_w.set_to(population)
                return True
            except:
                return True
