# -*- coding: utf-8 -*-

"""
Simple tests for the Interpreter class.
"""

from __future__ import print_function
from __future__ import unicode_literals

from tos.interpreters import interpreter
import pytest


def test_abstract():
    with pytest.raises(TypeError):
        interpreter.BaseInterpreter()
