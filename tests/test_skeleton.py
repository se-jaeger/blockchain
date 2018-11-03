#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from blockchain.skeleton import fib

__author__ = "Sebastian Jäger"
__copyright__ = "Sebastian Jäger"
__license__ = "apache"


def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)
