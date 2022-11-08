# -*- coding: utf-8 -*-

"""
Isi Plain Text Interpreter
--------------------------

Specializes the class :class:`~tos.interpreters.interpreter.BaseInterpreter`
to interpret the isi web of knowledge plain text file format.

"""

import re
from collections import OrderedDict

from .interpreter import BaseInterpreter


class IsiInterpreter(BaseInterpreter):

    """docstring for IsiInterpter"""

    def __init__(self):
        super(IsiInterpreter, self).__init__()
        self.entry_separator = '\nER\n\n'
        self.head_line = re.compile(r'(?P<head>[A-Z0-9]{2})\s(?P<line>.+)')

    def split_entries(self, txt):
        """This function splits text into single entries

        :param txt: Text to split
        :type txt: str
        :returns: list of strings containing each entry
        :rtype: list
        """
        return txt.split(self.entry_separator)[:-1]

    def parse_entry(self, txt):
        """Parses an individual entry and returns a structured dict

        :param txt: An individual entry
        :type txt: str
        :returns: a dictionary containg metadata
        :rtype: dict
        """
        lines = txt.split('\n')
        data = OrderedDict()
        section = "UNKW"

        for line, next in zip(lines, lines[1:] + ['']):
            # Split etries took care of this
            # if line == 'EF':
            #     break

            match_line = self.head_line.match(line)
            match_next = self.head_line.match(next)
            if match_line is not None:
                section = match_line.group('head')
                if match_next is not None or next == '':
                    data[section] = match_line.group('line')
                else:
                    data[section] = [match_line.group('line')]
            else:
                if section in data:
                    data[section].append(line.strip())
                else:
                    data[section] = [line.strip()]

        return data

    def get_entry_label(self, entry):
        """Returns and entry label acording to its metadata

        :param dict entry: Entry to be labeled
        :returns: Entry's label
        :rtype: str
        """
        from string import punctuation

        label_parts = []

        mask = dict(zip(list(punctuation), [None] * len(punctuation)))
        clear = lambda s: s.translate(mask)

        if isinstance(entry['AU'], str):
            author = entry['AU']
        else:
            author = entry['AU'][0]

        first_name = author.split(', ')[0]
        last_name = author.split(', ')[-1]

        label_parts.append(first_name + ' ' + clear(last_name))
        label_parts.append(entry.get('PY', ''))
        label_parts.append(entry.get('J9', ''))
        label_parts.append('V' + entry.get('VL', ''))
        if 'BP' in entry:
            label_parts.append('P' + entry['BP'])
        elif 'AR' in entry:
            label_parts.append('p' + entry['AR'].upper())
        if 'DI' in entry:
            label_parts.append('DOI ' + entry['DI'])

        return ', '.join(label_parts)

    def get_referenced_labels(self, entry):
        """Returns the references of an entry translated to labels

        :param dict entry: Entry to extract the references from
        :returns: Entry's reference list as labels
        :rtype: list
        """
        if 'CR' in entry:
            references = entry['CR']
            if isinstance(references, str):
                return [references, ]
            else:
                return references
        else:
            return []
