#  ---------------------------------------------------------------------------------------------------------------------
#  test_core.py
#  Copyright (c) 2024. Jermaine Clarke
#  All rights reserved.
#  ---------------------------------------------------------------------------------------------------------------------
from unittest import TestCase, skip
from src.core import Symbol

class TestSymbols(TestCase):

    def setUp(self):
        self.sym0 = Symbol('a', 'symbol1', ['budget', 'distance'])

    @skip('Test being developed.')
    def test_regex(self):
        self.assertEquals(self.sym0.regex, '')