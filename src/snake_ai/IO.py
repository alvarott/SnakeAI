# This module contains a IO class to write and read object instances

# Author: Álvaro Torralba
# Date: 22/06/2023
# Version: 0.0.1

from typing import Type, Any
import hashlib
import pickle
import os


class IO:

    @staticmethod
    def _calculate_checksum(data: bytes):
        """
        Calculate the checksum of the data using the SHA-256 hash algorithm.
        """
        hash_object = hashlib.sha256(data)
        return hash_object.hexdigest()

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
            data = pickle.dumps(obj)
            checksum = IO._calculate_checksum(data)
            pickle.dump((checksum, data), file)
        return 0

    @staticmethod
    def load(file_path: str, obj_class: Type) -> Any | None:
        """
        Loads and object
        :param file_path: absolute file path
        :return: object instance
        """
        path = os.path.normpath(file_path)
        with open(path, 'rb') as file:
            try:
                checksum, obj = pickle.load(file)
                recalculated_checksum = IO._calculate_checksum(obj)
                # If the files is corrupted
                if checksum != recalculated_checksum:
                    return -1
            except Exception:
                return -2
        obj = pickle.loads(obj)
        if isinstance(obj, obj_class):
            return obj
        else:
            return -3