# Common data structures to different modules

# Author: Álvaro Torralba
# Date: 05/08/2023
# Version: 0.0.1


from dataclasses import dataclass
import os


@dataclass
class Population:
    """
    Population common possible params
    """
    vision: tuple[str, type] = ('vision', str)
    hidden: tuple[str, type] = ('hidden', list)
    hidden_init: tuple[str, type] = ('hidden_init', str)
    hidden_act: tuple[str, type] = ('hidden_act', str)
    output_init: tuple[str, type] = ('output_init', str)
    output_act: tuple[str, type] = ('output_act', str)
    bias: tuple[str, type] = ('bias', bool)
    bias_init: tuple[str, type] = ('bias_init', str)
    population: tuple[str, type] = ('population', dict)


@dataclass
class Folders:
    """
    Common used folders
    """
    data_folder = os.path.join(os.getcwd(), 'SnakeAI_data')
    statistics_folder = os.path.join(data_folder, 'statistics')
    models_folder = os.path.join(data_folder, 'models')
    populations_folder = os.path.join(data_folder, 'populations')
