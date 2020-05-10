#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Dummy conftest.py for pycard.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    https://pytest.org/latest/plugins.html
"""
import pytest

import pycard.model as pm


@pytest.fixture
def rummy():
    g = pm.Game()
    g.initialize(d=pm.Deck(), num_players=2)
    [d], remainder = g.stock.deal(10, 1)
    g.stock = remainder
    g.discard = d
    return g


@pytest.fixture
def rummy_shuffle():
    g = pm.Game()
    g.initialize()
    return g
