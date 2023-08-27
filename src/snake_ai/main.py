# This module contains the application main class


# Author: Álvaro Torralba
# Date: 22/08/2023
# Version: 0.0.1

from snake_ai.mediator import APPMediator
from snake_ai.snake import resources as rsc
from importlib import resources as rc
from snake_ai.data import Folders
import multiprocessing
import shutil
import os


class Main:
    """
    Application main class
    """
    @staticmethod
    def _setup() -> None:
        """
        Creates the folders structure necessary to execute the application
        :return:
        """
        folders = []
        # Folders
        folders.extend([Folders.statistics_folder, Folders.models_folder, Folders.populations_folder])
        # Create folders if they do not exist
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(name=folder, exist_ok=True)
        # Copy default controllers if it is necessary
        folder_path = str(rc.files(rsc).joinpath(f'default_controller'))
        with os.scandir(folder_path) as models:
            for model in models:
                if model.is_file() and not os.path.exists(os.path.join(Folders.models_folder, model.name)):
                    shutil.copy(os.path.join(folder_path, model.name), os.path.join(Folders.models_folder, model.name))

    @staticmethod
    def init():
        """
        Initiates the application
        :return:
        """
        Main._setup()
        mediator = APPMediator()
        mediator.start()

if __name__ == '__main__':
    multiprocessing.freeze_support()
    Main.init()
