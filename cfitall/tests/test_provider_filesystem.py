import os
import unittest

from cfitall.providers import FilesystemProvider


class FilesystemProviderTests(unittest.TestCase):
    def test_init_empty_provider(self):
        provider = FilesystemProvider([], "test")
        self.assertEqual(provider.path, [])
        self.assertEqual(provider.prefix, "test")
        self.assertEqual(provider.provider_name, "filesystem")
        self.assertEqual(provider.dict, {})
        self.assertIsNone(provider.config_file)
        self.assertIsNone(provider.config_file_type)

    def test_set_config_file_json_first(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "json")
        provider = FilesystemProvider([json_path], "cfitall")
        provider._set_config_file()
        self.assertEqual(provider.config_file, os.path.join(json_path, "cfitall.json"))
        self.assertEqual(provider.config_file_type, "json")

    def test_set_config_file_multipath(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "json")
        yaml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yaml")
        provider = FilesystemProvider([yaml_path, json_path], "cfitall")
        provider._set_config_file()
        self.assertEqual(provider.config_file, os.path.join(yaml_path, "cfitall.yml"))
        self.assertEqual(provider.config_file_type, "yaml")

    def test_read_config_file_none(self):
        provider = FilesystemProvider([], "test")
        provider._read_config_file()
        self.assertEqual(provider.dict, {})

    def test_read_config_file_json(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "json")
        provider = FilesystemProvider([json_path], "cfitall")
        provider._set_config_file()
        self.assertEqual(provider.dict, {})
        provider._read_config_file()
        self.assertEqual(sorted(provider.dict.keys()), ["foo", "global", "search"])
        self.assertEqual(provider.dict["global"]["name"], "cfitjson")
        self.assertEqual(
            provider.dict["search"], ["/Users/wryfi/foo", "/Users/wryfi/bar"]
        )

    def test_read_config_file_yaml(self):
        yaml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yaml")
        provider = FilesystemProvider([yaml_path], "cfitall")
        provider._set_config_file()
        self.assertEqual(provider.dict, {})
        provider._read_config_file()
        self.assertEqual(
            sorted(provider.dict.keys()), ["foo", "global", "search", "stuff"]
        )
        self.assertEqual(provider.dict["global"]["name"], "cfityaml")
        self.assertEqual(provider.dict["foo"]["bar"], "baz")

    def test_update(self):
        yaml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yaml")
        provider = FilesystemProvider([yaml_path], "cfitall")
        self.assertEqual(provider.dict, {})
        self.assertTrue(provider.update())
        self.assertEqual(
            sorted(provider.dict.keys()), ["foo", "global", "search", "stuff"]
        )
        self.assertEqual(provider.dict["global"]["name"], "cfityaml")
        self.assertEqual(provider.dict["foo"]["bar"], "baz")
