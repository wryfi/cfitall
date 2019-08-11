import os
import unittest
from cfitall import utils


class TestAddKeys(unittest.TestCase):
    def test_add_keys_single(self):
        new_dict = utils.add_keys({}, ['foo'])
        self.assertEqual(new_dict, {'foo': None})

    def test_add_keys_single_with_value(self):
        new_dict = utils.add_keys({}, ['foo'], 'bar')
        self.assertEqual(new_dict, {'foo': 'bar'})

    def test_add_keys_nested(self):
        new_dict = utils.add_keys({}, ['foo', 'bar', 'baz'])
        self.assertEqual(new_dict, {'foo': {'bar': {'baz': None}}})

    def test_add_keys_nested_with_value(self):
        new_dict = utils.add_keys({}, ['foo', 'bar', 'baz'], 'bat')
        self.assertEqual(new_dict, {'foo': {'bar': {'baz': 'bat'}}})

    def test_add_keys_nested_with_value_and_dict(self):
        start_dict = {'asdf': {'1234': 'rewq'}}
        new_dict = utils.add_keys(start_dict, ['foo', 'bar', 'baz'], 'bat')
        self.assertEqual(new_dict, {
            'asdf': {'1234': 'rewq'},
            'foo': {'bar': {'baz': 'bat'}}
        })


class TestExpandFlatten(unittest.TestCase):
    def test_expand_flattened_path(self):
        expanded = utils.expand_flattened_path('asdf.fdsa.qwer.rewq', 'foo')
        self.assertEqual(expanded, {'asdf': {'fdsa': {'qwer': {'rewq': 'foo'}}}})

    def test_expand_flattened_dict(self):
        expanded = utils.expand_flattened_dict({'asdf.fdsa.qwer.rewq': 'foo'})
        self.assertEqual(expanded, {'asdf': {'fdsa': {'qwer': {'rewq': 'foo'}}}})

    def test_flatten_dict(self):
        flattened = utils.flatten_dict({'asdf': {'fdsa': {'qwer': {'rewq': 'foo'}}}})
        self.assertEqual(flattened, {'asdf.fdsa.qwer.rewq': 'foo'})


class TestExtractFindMerge(unittest.TestCase):
    def test_find_keys(self):
        keys = utils.find_keys({'asdf': {'fdsa': {'qwer': {'rewq': 'foo'}}}}, 'foo')
        self.assertEqual(keys, ['asdf', 'fdsa', 'qwer', 'rewq'])

    def test_extract_values(self):
        extracted = utils.extract_values({'asdf': {'fdsa': {'qwer': {'rewq': 'foo'}}}})
        self.assertEqual(extracted, ['foo'])

    def test_merge_dicts(self):
        srcdict = {'asdf': 'fdsa', 'qwer': {'werq': 'poiu'}}
        destdict = {'lkjh': 'zxcv', 'asdf': 1234}
        merged = utils.merge_dicts(srcdict, destdict)
        self.assertEqual(merged, {
            'asdf': 'fdsa',
            'qwer': {'werq': 'poiu'},
            'lkjh': 'zxcv'
        })


if __name__ == '__main__':
    unittest.main()
