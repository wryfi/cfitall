import os
import unittest

from cfitall.providers import EnvironmentProvider


class EnvironmentProviderTests(unittest.TestCase):
    def setUp(self):
        os.environ["CFITALL__GLOBAL__NAME"] = "cfitall"
        os.environ["CFITALL__GLOBAL__PATH"] = "[/Users/wryfi, /Users/wryfi/tmp]"
        os.environ["CFITALL__FOO__BANG"] = "WHAMMY!"
        os.environ["CFITALL__MAGIC__ENABLE"] = "true"
        os.environ["CFITALL__BOOL_LIST"] = "[true, false, false, true]"
        os.environ[
            "CFITALL__SPACE_LIST"
        ] = "[one two \t\t three \t four             five six]"
        super().setUp()

    def tearDown(self):
        for key, value in os.environ.items():
            if key.startswith("CFITALL__"):
                del os.environ[key]
        super().tearDown()

    def test_dict(self):
        provider = EnvironmentProvider("cfitall")
        self.assertEqual(
            {
                "global": {
                    "name": "cfitall",
                    "path": ["/Users/wryfi", "/Users/wryfi/tmp"],
                },
                "foo": {"bang": "WHAMMY!"},
                "magic": {"enable": True},
                "bool_list": [True, False, False, True],
                "space_list": ["one two \t\t three \t four             five six"],
            },
            provider.dict,
        )

    def test_read_variable(self):
        provider = EnvironmentProvider("cfitall")
        self.assertEqual(provider.dict["global"]["name"], "cfitall")
        self.assertEqual(
            provider.dict["global"]["path"], ["/Users/wryfi", "/Users/wryfi/tmp"]
        )
        self.assertEqual(provider.dict["foo"]["bang"], "WHAMMY!")

    def test_cast_bool(self):
        provider = EnvironmentProvider("cfitall")
        self.assertTrue(provider.dict["magic"]["enable"])

    def test_cast_bool_disabled(self):
        provider = EnvironmentProvider("cfitall", cast_bool=False)
        self.assertEqual("true", provider.dict["magic"]["enable"])

    def test_cast_bool_list(self):
        provider = EnvironmentProvider("cfitall")
        self.assertEqual([True, False, False, True], provider.dict["bool_list"])

    def test_cast_bool_disabled_list(self):
        provider = EnvironmentProvider("cfitall", cast_bool=False)
        self.assertEqual(["true", "false", "false", "true"], provider.dict["bool_list"])

    def test_list_whitespace(self):
        provider = EnvironmentProvider("cfitall", value_separator=r"\s+")
        self.assertEqual(
            ["one", "two", "three", "four", "five", "six"], provider.dict["space_list"]
        )

    def test_single_element_list(self):
        os.environ["CFITALL__ONELIST"] = "[onething]"
        provider = EnvironmentProvider("cfitall")
        self.assertEqual(provider.dict["onelist"], ["onething"])

    def test_list_trailing_comma(self):
        os.environ["CFITALL__EXTRA_COMMAS"] = "[,onething,,twothing,]"
        provider = EnvironmentProvider("cfitall")
        self.assertEqual(provider.dict["extra_commas"], ["onething", "twothing"])

    def test_update(self):
        provider = EnvironmentProvider("cfitall")
        self.assertTrue(provider.update())
