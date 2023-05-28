# This module contains the base class for creating functions factories, by creating those inside a class

# Author: Álvaro Torralba
# Date: 28/05/2023
# Version: 0.0.1

from inspect import getmembers, isfunction, isclass
import types


class FunctionFactory:
    """
    This class is meant to return a function by providing its name to a getter method
    """
    def __init__(self, globals: dict, module_name: str):
        """
        Constructor
        :param globals: current global symbols table
        :param module_name: module name where the functions are defined inside a class
        """
        self._functions = self._map_functions(globals, module_name)

    def _map_functions(self, globals, module_name):
        """
        Maps all the classes implemented in the module
        :return:
        """
        functions = {}
        classes = []
        # Map classes in the module
        for name, obj in globals.items():
            if isclass(obj) and obj.__module__ == module_name and obj.__name__.startswith('_'):
                classes.append(obj)

        # Map functions of each class
        for obj in classes:
            members = getmembers(obj)
            class_functions = {name.lower(): value for name, value in members if isfunction(value) and not name.startswith('_')}
            functions[obj.__name__[1:].lower()] = class_functions

        return functions

    def get_function(self, type: str, func: str) -> types.FunctionType:
        """
        Produces a function instance
        :param type: function type
        :param func: function name
        :return: function
        """
        if type in self._functions.keys():
            if func in self._functions[type].keys():
                return self._functions[type][func]
            else:
                raise ValueError(f"No implementation found for '{func}' of the type '{type}'. "
                                 f"Functions available {list(self._functions[type].keys())}")
        else:
            raise ValueError(f"No implementation found for functions of the type '{type}'."
                             f" Available types {list(self._functions.keys())}")
