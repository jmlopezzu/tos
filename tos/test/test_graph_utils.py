# -*- coding: utf-8 -*-

"""
Simple graph utility tests.
"""

import tos.graph.utils as utils
from tos.graph.utils import extract_edge_relations
from tos.graph.utils import detect_duplicate_labels

from tos.interpreters import IsiInterpreter


def test_extract_edge_relations():
    isi_interpreter = IsiInterpreter()
    handler = open('sample_data/isi.txt', 'r')
    entries = isi_interpreter.parse_file(handler)[:10]
    relations = extract_edge_relations(entries, isi_interpreter)
    for entry in entries:
        label = isi_interpreter.get_entry_label(entry)
        for reference in isi_interpreter.get_referenced_labels(entry):
            assert (label, reference) in relations


def test_detect_duplicate_labels():
    import jellyfish

    isi_interpreter = IsiInterpreter()
    handler = open('sample_data/isi.txt', 'r')
    entries = isi_interpreter.parse_file(handler)[:10]
    labels = isi_interpreter.get_label_list(entries)
    duplicates = detect_duplicate_labels(labels)

    for dup, original in duplicates.items():
        assert jellyfish.jaro_winkler(original, dup) > 0.96


def test_detect_duplicate_labels_lower_threshold():
    import jellyfish

    labels = [
        'apple',
        'aphel',
        'aphil'
    ]
    duplicates = detect_duplicate_labels(labels, threshold=0.7)

    for dup, original in duplicates.items():
        assert jellyfish.jaro_winkler(original, dup) > 0.7


def test_detect_duplicate_labels_inverted():
    import jellyfish

    labels = [
        'apple',
        'aphel',
        'aphil'
    ]
    duplicates = detect_duplicate_labels(
        labels,
        threshold=2,
        similarity=jellyfish.levenshtein_distance,
        inverted=True)

    for dup, original in duplicates.items():
        assert jellyfish.levenshtein_distance(original, dup) < 2


def test_patch_list():
    items = [
        'Alpha',
        'Beta',
        'Gamma'
    ]
    patched = utils.patch_list(items, {'Alpha': 'Beta'})
    assert not 'Alpha' in patched
    assert 'Beta' in patched
    assert 'Gamma' in patched


def test_patch_tuple_list():
    items = zip(list('abcd'), list('fghi'))
    patch = {'a': 'z', 'h': 'w'}
    patched = utils.patch_tuple_list(items, patch)
    assert ('z', 'f') in patched
    assert ('c', 'w') in patched
