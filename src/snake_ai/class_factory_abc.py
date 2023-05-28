# This module contains the interface and common methods for creating factories

# Author: Álvaro Torralba
# Date: 17/05/2023
# Version: 0.0.1

from inspect import getmembers, isclass, isabstract
from abc import ABC, abstractmethod
import types


class FactoryABS(ABC):

    """
    This class is meant to be a factory for classes implementations of the same family
    """
    def __init__(self, module: types.ModuleType):
        """
        Constructor
        :param module: module where to load classes from
        """
        self._module = module
        self._classes = {}
        self._load_classes()

    def _load_classes(self) -> None:
        """
        Loads all the classes that are imported to the namespace with __init__.py at the module
        :return:
        """
        classes = getmembers(self._module, lambda m: isclass(m) and not isabstract(m))
        for name, _type in classes:
            self._classes[name] = _type

    @abstractmethod
    def get_instance(self, *args):
        """
        This method must provide the parameters and logic to instantiate any of the objects of the factory family
        :param args:
        :return:
        """
        pass
