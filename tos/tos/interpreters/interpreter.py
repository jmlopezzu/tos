# -*- coding: utf-8 -*-

"""
Interpreter
-----------

Just contains the :class:`~tos.interpreters.interpreter.BaseInterpreter`
which is an intepreter abstract base class.

"""

from abc import ABCMeta
from abc import abstractmethod


class BaseInterpreter(object, metaclass=ABCMeta):

    """docstring for Interpreter"""

    # __metaclass__ = ABCMeta

    def parse_file(self, handler):
        """Proxy for parsing a file handler

        :param handler: hendler for the file to be parsed
        :type handler: file
        :returns: a list of dictionaries containing parsed metadata
        :rtype: list
        """
        return self.parse(handler.read())

    def parse(self, txt):
        """Parses a string with one or more records

        Load a string with multiple records, split them into
        entries and parse the entries.

        :param txt: text to be parsed
        :type txt: str
        :returns: a list of dictionaries containing parsed metadata
        :rtype: list
        """
        entries = self.split_entries(txt)
        return list(map(self.parse_entry, entries))

    @abstractmethod
    def split_entries(self, txt):
        """Abstract method that should split text into individual entries.
        """

    @abstractmethod
    def parse_entry(self, txt):
        """Abstract method that should parse an individual entry.
        """

    @abstractmethod
    def get_entry_label(self, entry):
        """Abstract method that should return an individual entry label.
        """

    @abstractmethod
    def get_referenced_labels(self, entry):
        """Abstract method that should get the referenced labels
        out of an entry's metadata.
        """

    def get_label_list(self, entries):
        """Computes a list of unique entry labels

        Returns a shorted listo of the unique entry labels.

        :param list entries: A list of dictionaries containing anotated data
        :returns: a list of unique labels
        :rtype: list
        """
        labels = []

        for entry in entries:
            labels.append(self.get_entry_label(entry))
            labels.extend(self.get_referenced_labels(entry))

        return sorted(list(set(labels)))
