# -*- coding: utf-8 -*-

"""
Simple tests for the Interpreter class.
"""

from __future__ import print_function
from __future__ import unicode_literals

from tos.interpreters.isitxt import IsiInterpreter
# import pytest
# from pprint import pprint


def check_entry(entry):
    assert('AU' in entry)
    assert('PY' in entry)
    assert('J9' in entry)
    assert('VL' in entry)
    assert('BP' in entry or 'AR' in entry)
    # Sometimes there is no DOI specially for older articles
    # assert('DI' in entry)


def test_split_entries():
    isi_interpreter = IsiInterpreter()
    entries = isi_interpreter.split_entries('a\nER\n\nb\nER\n\nEF')
    assert(entries == ['a', 'b'])


def test_split_etries_data():
    isi_interpreter = IsiInterpreter()
    data = open('sample_data/isi.txt', 'r').read()
    assert(len(isi_interpreter.split_entries(data)) == 77)


def test_parse_entry():
    isi_interpreter = IsiInterpreter()
    data = open('sample_data/isi.txt', 'r').read()
    entries = isi_interpreter.split_entries(data)
    for entry in map(isi_interpreter.parse_entry, entries):
        check_entry(entry)


def test_parse():
    isi_interpreter = IsiInterpreter()
    data = open('sample_data/isi.txt', 'r').read()
    entries = isi_interpreter.parse(data)
    for entry in entries:
        check_entry(entry)


def test_parse_file():
    isi_interpreter = IsiInterpreter()
    handler = open('sample_data/isi.txt', 'r')
    entries = isi_interpreter.parse_file(handler)
    for entry in entries:
        check_entry(entry)


def test_parse_parse_file_coherence():
    isi_interpreter = IsiInterpreter()
    data = open('sample_data/isi.txt', 'r').read()
    handler = open('sample_data/isi.txt', 'r')
    assert(isi_interpreter.parse(data) == isi_interpreter.parse_file(handler))


def test_get_entry_label():
    isi_interpreter = IsiInterpreter()
    handler = open('sample_data/isi.txt', 'r')
    entries = isi_interpreter.parse_file(handler)

    cases = [
        (0, 'Pereira SI, 2014, FOOD CHEM, V154, P291, '
            'DOI 10.1016/j.foodchem.2014.01.019'),
        (1, 'Medina-Cleghorn D, 2014, ACS CHEM BIOL, V9, P423, '
            'DOI 10.1021/cb400796c'),
        (11, 'de Bekker C, 2013, PLOS ONE, V8, pE70609, '
            'DOI 10.1371/journal.pone.0070609'),
        (65, 'Toyo\'oka T, 2008, J CHROMATOGR SCI, V46, P233')
    ]

    for index, value in cases:
        assert(isi_interpreter.get_entry_label(entries[index]) == value)


def test_get_referenced_labels():
    isi_interpreter = IsiInterpreter()
    handler = open('sample_data/isi.txt', 'r')
    entries = isi_interpreter.parse_file(handler)

    cases = [
        (5, [
            'Begum G, 2004, AQUAT TOXICOL, V66, P83, '
            'DOI 10.1016/j.aquatox.2003.08.002',
            'Hu Ze-Ping, 2012, J Proteome Res, V11, P5903, '
            'DOI 10.1021/pr300666p',
            'Liang SH, 2009, COMP BIOCHEM PHYS C, V149, P349, '
            'DOI 10.1016/j.cbpc.2008.09.004',
        ]),
        (6, [
            'Cappellin L, 2012, METABOLOMICS, V8, P761, '
            'DOI 10.1007/s11306-012-0405-9',
            'Frolov A, 2013, J AGR FOOD CHEM, V61, P1219, '
            'DOI 10.1021/jf3042648',
            'Laursen KH, 2011, J AGR FOOD CHEM, V59, P4385, '
            'DOI 10.1021/jf104928r',
        ])
    ]

    for index, values in cases:
        references = isi_interpreter.get_referenced_labels(entries[index])
        for value in values:
            assert(value in references)


def test_get_referenced_labels_unique_cite():
    isi_interpreter = IsiInterpreter()
    handler = open('test/test_data/artificial_isi.txt', 'r')
    entries = isi_interpreter.parse_file(handler)

    cases = [
        (0, [
            'Abu-Reidah IM, 2013, J CHROMATOGR A, V1313, '
            'P212, DOI 10.1016/j.chroma.2013.07.020'
        ]),
    ]

    for index, values in cases:
        references = isi_interpreter.get_referenced_labels(entries[index])
        assert(not isinstance(references, str))
        for value in values:
            assert(value in references)


def test_get_referenced_labels_inconsistent():
    isi_interpreter = IsiInterpreter()
    entries = isi_interpreter.parse('a\nER\n\nb\nER\n\nEF')
    assert(isi_interpreter.get_referenced_labels(entries[0]) == [])


def test_get_label_list():
    isi_interpreter = IsiInterpreter()
    handler = open('sample_data/isi.txt', 'r')
    entries = isi_interpreter.parse_file(handler)[0:1]
    labels = [
        'Pereira SI, 2014, FOOD CHEM, V154, P291, '
        'DOI 10.1016/j.foodchem.2014.01.019',
        'Abu-Reidah IM, 2013, J CHROMATOGR A, V1313, P212, '
        'DOI 10.1016/j.chroma.2013.07.020',
        'Ashraf M, 2007, ENVIRON EXP BOT, V59, P206, '
        'DOI 10.1016/j.envexpbot.2005.12.006',
        'Beni C, 2011, BIOL TRACE ELEM RES, V143, P518, '
        'DOI 10.1007/s12011-010-8862-3',
        'Bernillon S, 2013, METABOLOMICS, V9, P57, '
        'DOI 10.1007/s11306-012-0429-1',
        'Blasco B, 2013, J AGR FOOD CHEM, V61, P2591, '
        'DOI 10.1021/jf303917n',
        'Capitani D., 2012, J AGR FOOD CHEM, V61, P1718',
        'Dias M. C., 2014, PHOTOSYNTET IN PRESS',
        'Easton A, 2001, J BIOCHEM MOL TOXIC, V15, P15, '
        'DOI 10.1002/1099-0461(2001)15:1<15::AID-JBT2>3.0.CO;2-Z',
        'Hediji H, 2010, ECOTOX ENVIRON SAFE, V73, P1965, '
        'DOI 10.1016/j.ecoenv.2010.08.014',
        'Karmakar R, 2009, J AGR FOOD CHEM, V57, P6369, '
        'DOI 10.1021/jf9008394',
        'Kausch KD, 2012, AMINO ACIDS, V42, P843, '
        'DOI 10.1007/s00726-011-1000-5',
        'Kim J, 2013, FOOD CHEM, V137, P68, '
        'DOI 10.1016/j.foodchem.2012.10.012',
        'Lemon J, 2006, R NEWS, V6, P8',
        'Mannina L, 2012, PROG NUCL MAG RES SP, V66, P1, '
        'DOI 10.1016/j.pnmrs.2012.02.001',
        'Paro R, 2012, TOXICOL APPL PHARM, V260, P155, '
        'DOI 10.1016/j.taap.2012.02.005',
        'Perez EMS, 2010, FOOD CHEM, V122, P877, '
        'DOI 10.1016/j.foodchem.2010.03.003',
        'Picone G, 2011, J AGR FOOD CHEM, V59, P9271, '
        'DOI 10.1021/jf2020717',
        'R Core Team, 2012, R LANG ENV STAT COMP',
        'Shepherd LVT, 2011, BIOANALYSIS, V3, P1143, '
        'DOI 10.4155/BIO.11.61',
        'Silvente S, 2012, PLOS ONE, V7, '
        'DOI 10.1371/journal.pone.0038554',
        'Sobolev AP, 2010, J AGR FOOD CHEM, V58, P6928, '
        'DOI 10.1021/jf904439y',
        'Sobolev AP, 2007, J AGR FOOD CHEM, V55, P10827, '
        'DOI 10.1021/jf072437x',
        'Sobolev AP, 2010, NUTRIENTS, V2, P1, '
        'DOI [10.3390/nu20100001, 10.3390/nu2010001]',
        'Sobolev AP, 2005, MAGN RESON CHEM, V43, P625, '
        'DOI 10.1002/mrc.1618',
        'Son HS, 2009, J AGR FOOD CHEM, V57, P1481, '
        'DOI 10.1021/jf803388w',
        'Spraul M, 2009, MAGN RESON CHEM, V47, pS130, '
        'DOI 10.1002/mrc.2528',
        'Wishart DS, 2013, NUCLEIC ACIDS RES, V41, pD801, '
        'DOI 10.1093/nar/gks1065',
        'Zhang XT, 2011, J AGR FOOD CHEM, V59, P2672, '
        'DOI 10.1021/jf104335z',
        'Zhang XT, 2012, FOOD CHEM, V134, P1020, '
        'DOI 10.1016/j.foodchem.2012.02.218',
    ]
    assert(isi_interpreter.get_label_list(entries) == sorted(labels))

if __name__ == '__main__':
    test_split_etries_data()
    test_parse_parse_file_coherence()
