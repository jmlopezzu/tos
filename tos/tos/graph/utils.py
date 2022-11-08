# -*- coding: utf-8 -*-

"""
Graph Utilities
---------------

This module encapsulates several utilities aiming to extract a
directed graph from an entry list possibli comming form a
:class:`~tos.interpreters.interpreter.BaseInterpreter` subclass.

"""

import jellyfish


def extract_edge_relations(entries, interpreter):
    """Returns an edge list for the given entries

    It uses the `interpreter` to compute the label, and the referenced
    labels for each entry using the especialized method
    :meth:`~tos.interpreters.interpreter.BaseInterpreter.get_entry_label`
    and
    :meth:`~tos.interpreters.interpreter.BaseInterpreter.get_referenced_labels`
    respectively.

    :param list entries: List of entries
    :param interpreter: BaseInterpreter to get the labels and referenced labels
    :type interpreter: :class:`~tos.interpreters.interpreter.BaseInterpreter`
    :returns: Edge list of the form `[(label_source, label_target), ...]`
    :rtype: list
    """
    edges = []

    for entry in entries:
        label = interpreter.get_entry_label(entry)
        references = interpreter.get_referenced_labels(entry)
        edges.extend(zip([label] * len(references), references))

    return edges


def detect_duplicate_labels(labels,
                            similarity=jellyfish.jaro_winkler,
                            shared_first_letters=2,
                            threshold=0.96,
                            inverted=False):
    """Detects duplicate strings in a list

    Detects duplicate strings comparing every pair of strings that
    share the same characters up to `shared_first_leters`
    and returns a dictionary with patching information to reduce
    the list to unique labels.

    :param list labels: Labels to be compared
    :param function similarity: Similarity function
    :param int shared_first_letters: Only labels that share this ammount
        of characters at the beggining will be compared.
    :param float threshold: Two strings with `similarity`
        greater than this will be considered duplicates
    :param bool inverted: If `True` strings with `similarity`
        lower than `threshold` will be considered duplicates
    :returns: Duplicate map
    :rtype: dict
    """
    sorted_labels = sorted(labels)
    num_labels = len(sorted_labels)
    duplicates = dict()

    if inverted:
        comp = lambda x, y: x < y
    else:
        comp = lambda x, y: x > y

    for i in range(num_labels):
        label = duplicates.get(sorted_labels[i], sorted_labels[i])
        start_letters = label[:shared_first_letters]

        for j in range(i + 1, num_labels):
            other = sorted_labels[j]

            if not other.startswith(start_letters):
                break

            sim = similarity(label, other)

            if comp(sim, threshold):
                duplicates[other] = label

    return duplicates


def patch_list(items, patch):
    """
    Patches a list given a dictionary where the key is the element to
    be changed and the value is the element to be patched to.

    :param list items: items to be patched
    :param dict patch: patch dictionary
    :returns: Patched list
    :rtype: list
    """
    return list(map(patch.get, items, items))


def patch_tuple_list(items, patch):
    """
    Patches a list of tuples given a dictionary where the key is the element to
    be changed and the value is the element to be patched to.

    :param list items: items to be patched
    :param dict patch: patch dictionary
    :returns: Patched list
    :rtype: list
    """
    keys, values = zip(*items)
    keys = patch_list(keys, patch)
    values = patch_list(values, patch)
    return list(zip(keys, values))
