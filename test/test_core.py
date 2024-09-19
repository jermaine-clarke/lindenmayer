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
        self.sym1 = Symbol('p', 'person', ['name', 'age', 'nationality'])
        self.sym2 = Symbol('q')

    def test_regex(self):
        self.assertEqual(self.sym0.regex, '^a\(\s*(?P<budget>\w+),\s*(?P<distance>\w+)\)')
        self.assertEqual(self.sym1.regex, '^p\(\s*(?P<name>\w+),\s*(?P<age>\w+),\s*(?P<nationality>\w+)\)')
        self.assertEqual(self.sym2.regex, '^q')

    def test_attributes(self):
        self.assertEqual(self.sym0.name, 'symbol1', 'name does not match')
        self.assertEqual(self.sym0.size, 2, 'parameter count is incorrect.')
        self.assertEqual(self.sym0.glyph, 'a', 'incorrect glyph')
        self.assertEqual(self.sym1.name, 'person', 'name does not match')
        self.assertEqual(self.sym1.size, 3, 'parameter count is incorrect.')
        self.assertEqual(self.sym1.glyph, 'p', 'incorrect glyph')
        self.assertEqual(self.sym2.name, 'q', 'name does not match')
        self.assertEqual(self.sym2.size, 0, 'parameter count is incorrect.')
        self.assertEqual(self.sym2.glyph, 'q', 'incorrect glyph')

    @skip('Not yet implemented.')
    def test_rulesets(self):
        self.fail()