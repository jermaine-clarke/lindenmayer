#  ---------------------------------------------------------------------------------------------------------------------
#  test_alphabet.py
#  Copyright (c) 2024. Jermaine Clarke
#  All rights reserved.
#  ---------------------------------------------------------------------------------------------------------------------
from unittest import TestCase, skip
from core import Alphabet, Symbol

class TestAlphabet(TestCase):

    def setUp(self):
        self.alphabet = Alphabet()

    def test_init(self):
        temp = Alphabet()
        self.assertEqual(len(temp), 0, 'empty alphabet should have a length of zero.')
        self.assertFalse(temp.is_final, 'alphabet modifiable on init failure.')

    def test_add(self):
        temp = Symbol('p', 'person', ['height', 'weight'])
        self.alphabet.add('a')
        self.assertEqual(len(self.alphabet), 1, "add-as-glyph failed to increase length.")
        self.alphabet.add('b', param_names=['length', 'angle'], name='bend')
        self.assertEqual(len(self.alphabet), 2, "add-as-forwarding failed to increase length.")
        self.alphabet.add(temp)
        self.assertEqual(len(self.alphabet), 3, "add-as-object failed to increase length.")

        self.assertTrue('a' in self.alphabet, 'symbol added-as-glyph failed membership test.')
        self.assertTrue('bend' in self.alphabet, 'symbol added-by-forward-construction failed membership test.')
        self.assertTrue(temp in self.alphabet, 'symbol added-as-object failed membership test.')


    @skip('Test stub.')
    def test_drop(self):
        self.fail()

    def test_contains(self):
        temp = Symbol('p', 'person', ['height', 'weight'])
        nm = Symbol('t')
        self.alphabet.add('a')
        self.alphabet.add('b', param_names=['length', 'angle'], name='bend')
        self.alphabet.add(temp)

        self.assertTrue(temp in self.alphabet, 'membership-by-object test failed.')
        self.assertTrue('a' in self.alphabet, 'membership-by-glyph test failed.')
        self.assertTrue('bend' in self.alphabet, 'membership-by-name failed.')
        self.assertFalse('c' in self.alphabet, 'non-membership-by-glyph test failed.')
        self.assertFalse('corn' in self.alphabet, 'non-membership-by-name test failed.')
        self.assertFalse(nm in self.alphabet, 'non-membership-by-object test failed.')

    def test_length(self):
        self.alphabet.add('a')
        self.assertEqual(len(self.alphabet), 1, "'add' does not increase length.")
        self.alphabet.add('b')
        self.assertEqual(len(self.alphabet), 2, "'add' does not increase length.")
        self.alphabet.drop('a')
        self.assertEqual(len(self.alphabet), 1, "'drop' does not increase length.")

    def test_subsetof(self):
        temp = Alphabet()
        temp.add('a')
        temp.add('b')
        temp.add('c')
        self.alphabet.add('a')
        self.assertTrue(self.alphabet <= temp, 'claimed a proper subset is not a subset.')
        self.assertFalse(temp <= self.alphabet, 'claimed a proper superset is a subset.')
        self.alphabet.add('b')
        self.alphabet.add('c')
        self.assertTrue(self.alphabet <= temp, 'claimed an identical set is not a subset.')
        self.assertTrue(temp <= self.alphabet, 'claimed an identical set is not a subset.')
        self.assertTrue(self.alphabet <= self.alphabet, 'claimed a set is not its own subset.')
        self.assertTrue(temp <= temp, 'claimed a set is not its own subset.')


    def test_proper_subsetof(self):
        temp = Alphabet()
        temp.add('a')
        temp.add('b')
        temp.add('c')
        self.alphabet.add('a')
        self.assertTrue(self.alphabet < temp, 'claimed a proper subset is not a proper subset.')
        self.assertFalse(temp < self.alphabet, 'claimed a proper superset is a proper subset.')
        self.alphabet.add('b')
        self.alphabet.add('c')
        self.assertFalse(self.alphabet < temp, 'claimed an identical set is a proper superset.')
        self.assertFalse(temp < self.alphabet, 'claimed an identical set is a proper superset.')
        self.assertFalse(self.alphabet < self.alphabet, 'claimed a set is its own proper superset.')
        self.assertFalse(temp < temp, 'claimed a set is its own proper superset.')


    def test_supersetof(self):
            temp = Alphabet()
            temp.add('a')
            temp.add('b')
            temp.add('c')
            self.alphabet.add('a')
            self.assertFalse(self.alphabet >= temp, 'claimed a proper subset is a superset')
            self.assertTrue(temp >= self.alphabet, 'claimed a proper superset is not a superset')
            self.alphabet.add('b')
            self.alphabet.add('c')
            self.assertTrue(self.alphabet >= temp, 'claimed an identical set is not a superset.')
            self.assertTrue(temp >= self.alphabet, 'claimed an identical set is not a superset.')
            self.assertTrue(self.alphabet >= self.alphabet, 'claimed a set is not its own superset.')
            self.assertTrue(temp >= temp, 'claimed a set is not its own superset.')

    def test_proper_supersetof(self):
        temp = Alphabet()
        temp.add('a')
        temp.add('b')
        temp.add('c')
        self.alphabet.add('a')
        self.assertFalse(self.alphabet > temp, 'claimed a proper subset is a proper superset')
        self.assertTrue(temp > self.alphabet, 'claimed a proper superset is not a proper superset')
        self.alphabet.add('b')
        self.alphabet.add('c')
        self.assertFalse(self.alphabet > temp, 'claimed an identical set is a proper superset.')
        self.assertFalse(temp > self.alphabet, 'claimed an identical set is a proper superset.')
        self.assertFalse(self.alphabet > self.alphabet, 'claimed a set is its own superset.')
        self.assertFalse(temp > temp, 'claimed a set is its own superset.')

    def test_intersection(self):
        temp = Alphabet()
        temp.add('a')
        temp.add('b')
        temp.add('c')
        self.alphabet.add('a')
        inter = self.alphabet & temp
        self.assertEqual(len(inter), 1, 'incorrect size of intersection')
        self.assertTrue('a' in inter, 'expected symbol in intersection not found!')
        self.assertFalse('b' in inter, 'unexpected symbol found in intersection.')
        self.assertFalse('c' in inter, 'unexpected symbol found in intersection.')

        self.alphabet.add('b')
        inter = self.alphabet & temp
        self.assertEqual(len(inter), 2, 'incorrect size of intersection')
        self.assertTrue('a' in inter, 'expected symbol in intersection not found!')
        self.assertTrue('b' in inter, 'expected symbol not found in intersection.')
        self.assertFalse('c' in inter, 'unexpected symbol found in intersection.')

    def test_union(self):
        temp = Alphabet()
        temp.add('a')
        temp.add('b')
        temp.add('c')
        self.alphabet.add('a')
        self.alphabet.add('b')
        self.alphabet.add('d')
        union = self.alphabet | temp
        self.assertEqual(len(union), 4, 'incorrect size of union')
        self.assertTrue('a' in union, 'expected symbol not found in union.')
        self.assertTrue('b' in union, 'expected symbol not found in union.')
        self.assertTrue('c' in union, 'expected symbol not found in union.')
        self.assertTrue('d' in union, 'expected symbol not found in union.')
        self.assertFalse('e' in union, 'unexpected symbol found in intersection.')

    def test_disjoint(self):
        temp = Alphabet()
        temp.add('a')
        self.alphabet.add('d')
        self.assertTrue(temp.isdisjoint(self.alphabet), 'expected alphabets to be disjoint.')
        self.assertFalse(temp.isdisjoint(temp), 'expected an alphabet is not disjoint from itself.')
        temp.add('d')
        self.assertFalse(temp.isdisjoint(self.alphabet), 'expected alphabets to not be disjoint.')

    def test_get(self):
        temp = Symbol('a', 'avenue', ['length', 'angle'])
        self.alphabet.add(temp)
        self.alphabet.add('b', name='bisection')

        res = self.alphabet.get(temp.glyph)
        self.assertEqual(res.glyph, temp.glyph)
        self.assertEqual(res.name, temp.name)
        self.assertEqual(res.size, temp.size)
        self.assertEqual(res.params, temp.params)

        res = self.alphabet.get('bisection')
        self.assertEqual(res.glyph, 'b')
        self.assertEqual(res.name, 'bisection')
        self.assertEqual(res.size, 0)
        self.assertEqual(res.params, tuple())

    @skip('Functionality not yet implemented.')
    def test_iter(self):
        self.fail()

