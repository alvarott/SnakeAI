# This module is intended to contain all the custom data structures necessary for the interactions of the GUI

# Author: Álvaro Torralba
# Date: 30/07/2023
# Version: 0.0.1

from dataclasses import dataclass, field


@dataclass
class NeuralConfig:
    """
    Data class to hold neural network configuration choices
    """
    hidden_init: list[str] = field(default_factory=lambda: ['Xavier Glorot', 'He', 'LeCun'])
    hidden_act: list[str] = field(default_factory=lambda: ['ReLu', 'TanH', 'Softmax', 'Sigmoid'])
    output_init: list[str] = field(default_factory=lambda: ['Xavier Glorot', 'He', 'LeCun'])
    output_act: list[str] = field(default_factory=lambda: ['ReLu', 'TanH', 'Softmax', 'Sigmoid'])
    bias_init: list[str] = field(default_factory=lambda: ['Zero', 'Xavier Glorot', 'He', 'LeCun'])


@dataclass
class GeneralConfig:
    """
    Data class to hold vision configuration choices
    """
    vision: list[str] = field(default_factory=lambda: ['Binary', 'Real'])
    training_grid_size: dict[str, tuple[int, int]] = field(default_factory=lambda: {'10x10': (10, 10),
                                                                                    '15x15': (15, 15),
                                                                                    '20x20': (20, 20),
                                                                                    '25x25': (25, 25)})


@dataclass
class FileConfig:
    """
    Data class to hold supported files configuration choices
    """

    def __init__(self):
        self.model_file: list[tuple[str, str]] = [("model files(*.nn)", "*.nn")]
        self.population_file: list[tuple[str, str]] = [("population files(*.pop)", "*.pop"), ("all files (*.*)", "*.*")]
        self.stats_file: list[tuple[str, str]] = [("model files (*.sts)", "*.sts"), ("all files (*.*)", "*.*")]


@dataclass
class GeneticConfig:
    """
    Data class to hold genetic algorithm configuration choices
    """

    def __init__(self):
        self.alpha: str = '\u03B1'
        self.eta: str = '\u03B7'
        self.sigma: str = '\u03C3'
        self.selection: list[str] = ['Roulette Wheel', 'Stochastic', 'Tournament']
        self.crossover: dict[str, str] = {'W Arithmetic': self.alpha, 'SP Arithmetic': self.alpha, 'SBX': self.eta,
                                          'Uniform': ''}
        self.mutation: dict[str, str] = {'Gaussian': self.sigma}
        self.replacement: list[str] = ['Fitness-Based', 'Generational']
        self.hyperparams_range: dict[str, tuple[int, int]] = {self.alpha: (0, 1, 0.01),
                                                              self.eta: (0, 500, 1),
                                                              self.sigma: (0, 1, 0.01)}
        self.params_name: dict[str, str] = {'sp_arithmetic': 'alpha', 'whole_arithmetic': 'alpha', 'sbx': 'eta',
                                            'tournament': 'tournament_size', 'gaussian': 'sigma'}


@dataclass
class Colors:
    """
    Dataclass to hold the colors used along the GUI
    """
    active_text: str = '#dce4ee'
    inactive_text: str = '#5d5f61'
    bg_grey = '#2b2b2b'
    entry_grey: str = '#4a4a4a'
    dark_grey = '#2b2b2b'
    active_text_entry: str = '#dce4ee'
    inactive_text_entry: str = '#999999'
    error: str = 'red'
    blue_text = '#1f6aa5'
    init_blue = '#003462'
    init_bg_blue = '#008be5'
    init_white = '#ffffff'


class DropDownMapping:
    """
    Dataclass used for mapping the names displayed inside the GUI a then translation to function parameters
    """
    def __init__(self):
        self.mapping = {'binary': 'Binary', 'real': 'Real', 'glorot': 'Xavier Glorot', 'he': 'He', 'lecun': 'LeCun',
                        'relu': 'ReLu', 'tanh': 'TanH', 'softmax': 'Softmax', 'sigmoid': 'Sigmoid', 'zero': 'Zero',
                        'roulette_wheel': 'Roulette Wheel', 'stochastic': 'Stochastic', 'tournament': 'Tournament',
                        'whole_arithmetic': 'W Arithmetic', 'sp_arithmetic': 'SP Arithmetic', 'sbx': 'SBX',
                        'uniform': 'Uniform', 'alpha': '\u03B1', 'eta': '\u03B7', 'gaussian': 'Gaussian',
                        'sigma': '\u03C3', 'fitness_based': 'Fitness-Based', 'generational': 'Generational',
                        (10, 10): '10x10', (15, 15): '15x15', (20, 20): '20x20', (25, 25): '25x25'}


class GAShortNames:
    """
    Dataclass used to translate the parameters to an abbreviated form for fitting inside the training window
    """
    def __init__(self):
        self.names_map = {'roulette_wheel': 'RW', 'stochastic': 'stochastic', 'tournament': 'tournament',
                          'whole_arithmetic': 'WA', 'sp_arithmetic': 'SPA', 'sbx': 'SBX',
                          'uniform': 'uniform', 'gaussian': 'gauss', 'fitness_based': 'fitness_based',
                          'generational': 'generational'}
        self.params_map = {'whole_arithmetic': '\u03B1', 'sp_arithmetic': '\u03B1', 'sbx': '\u03B7',
                           'uniform': '', 'gaussian': '\u03C3'}
