# This module contains a IO class to write and read object instances

# Author: Álvaro Torralba
# Date: 22/06/2023
# Version: 0.0.1

from snake_ai.neural.nn import NN
import pickle
import os


class IO:
    @staticmethod
    def save(path: str, name: str, obj: object) -> int:
        """
        Saves an object instance as a binary file
        :param path: path where to save the object
        :param name: output file name
        :param obj: object instance to be saved
        :return:
        """
        with open(os.path.join(path, name), 'wb') as file:
            pickle.dump(obj, file)
        return 0

    @staticmethod
    def load(file_path: str) -> NN | None:
        """
        Loads and object
        :param file_path: absolute file path
        :return: object instance
        """
        path = os.path.normpath(file_path)
        with open(path, 'rb') as file:
            try:
                obj = pickle.load(file)
            except Exception:
                return None
        if isinstance(obj, NN):
            return obj
        else:
            return None
