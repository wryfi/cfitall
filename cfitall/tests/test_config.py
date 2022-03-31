import os
import unittest

from cfitall.registry import ConfigurationRegistry


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        super().setUp()
        os.environ["CFITALL__GLOBAL__NAME"] = "cfitall"
        os.environ["CFITALL__GLOBAL__PATH"] = "[/Users/wryfi, /Users/wryfi/tmp]"
        os.environ["CFITALL__FOO__BANG"] = "WHAMMY!"

    def tearDown(self):
        super().tearDown()
        for key, value in os.environ.items():
            if key.startswith("CFITALL"):
                del os.environ[key]

    def test_create_object(self):
        _cf = ConfigurationRegistry("cfitall")

    def test_environment_read_variables(self):
        cf = ConfigurationRegistry("cfitall")
        self.assertEqual(cf.get("global.name"), "cfitall")
        self.assertEqual(
            cf.get("global.path", list), ["/Users/wryfi", "/Users/wryfi/tmp"]
        )
        self.assertEqual(cf.get("foo.bang"), "WHAMMY!")

    def test_read_config_file(self):
        cf = ConfigurationRegistry("cfitall")
        cf.add_config_path(os.path.dirname(os.path.abspath(__file__)))
        cf.read_config()
        self.assertEqual(cf.get("global.name"), "cfitall")
        self.assertEqual(
            cf.get("global.path", list), ["/Users/wryfi", "/Users/wryfi/tmp"]
        )
        self.assertEqual(cf.get("foo.bang"), "WHAMMY!")
        self.assertEqual(cf.get("global.authors", list), ["john doe", "jane deer"])
        self.assertEqual(
            cf.get("search", list), ["/Users/wryfi/foo", "/Users/wryfi/bar"]
        )
        self.assertEqual(cf.get("foo.bar"), "baz")

    def test_config_order(self):
        cf = ConfigurationRegistry("cfitall")
        cf.set_default("global.authors", ["michael scott", "jim halpert"])
        self.assertEqual(
            cf.get("global.authors", list), ["michael scott", "jim halpert"]
        )
        cf.add_config_path(os.path.dirname(os.path.abspath(__file__)))
        cf.read_config()
        self.assertEqual(cf.get("global.authors", list), ["john doe", "jane deer"])
        os.environ["CFITALL__GLOBAL__AUTHORS"] = "[holly flax,robert california]"
        self.assertEqual(
            cf.get("global.authors", list), ["holly flax", "robert california"]
        )
        cf.set("global.authors", ["dwight schrute", "pam beesly"])
        self.assertEqual(
            cf.get("global.authors", list), ["dwight schrute", "pam beesly"]
        )

    def test_environment_booleans(self):
        cf = ConfigurationRegistry("cfitall")
        os.environ["CFITALL__TEST__BOOLEAN__TRUE"] = "true"
        os.environ["CFITALL__TEST__BOOLEAN__FALSE"] = "False"
        os.environ[
            "CFITALL__TEST__BOOLEAN__LIST"
        ] = "[true,false,True,this,False,is,nice]"
        self.assertEqual(cf.get("test.boolean.true"), True)
        self.assertEqual(cf.get("test.boolean.false"), False)
        self.assertEqual(
            cf.get("test.boolean.list"),
            [True, False, True, "this", False, "is", "nice"],
        )
        cf.env_bool = False
        self.assertEqual(cf.get("test.boolean.true"), "true")
        self.assertEqual(cf.get("test.boolean.false"), "False")
        self.assertEqual(
            cf.get("test.boolean.list"),
            ["true", "false", "True", "this", "False", "is", "nice"],
        )

    def test_comma_list(self):
        cf = ConfigurationRegistry("cfitall")
        cf.set_default("test.list.withcommas", ["flenderson, toby", "martin, angela"])
        self.assertEqual(
            cf.get("test.list.withcommas"), ["flenderson, toby", "martin, angela"]
        )
        os.environ["CFITALL__TEST__LIST"] = "[hello, world, melting]"
        self.assertEqual(cf.get("test.list"), ["hello", "world", "melting"])
        cf.env_value_split = False
        self.assertEqual(cf.get("test.list"), "[hello, world, melting]")

    def test_space_list(self):
        cf = ConfigurationRegistry("cfitall")
        os.environ[
            "CFITALL__TEST__LIST"
        ] = "[hello world    melting	 antarctica   broadway]"
        cf.env_value_separator = r"\s+"
        self.assertEqual(
            cf.get("test.list"), ["hello", "world", "melting", "antarctica", "broadway"]
        )
        cf.env_value_split = False
        self.assertEqual(
            cf.get("test.list"), "[hello world    melting	 antarctica   broadway]"
        )

    def test_different_keys_same_value(self):
        cf = ConfigurationRegistry("cfitall")
        cf.set_default("test.string", "hello, world")
        cf.set_default("test.string_2", "hello, world")
        self.assertEqual(cf.get("test.string"), cf.get("test.string_2"))

    def test_environment_single_element_list(self):
        os.environ["CFITALL__ONELIST"] = "[onething]"
        cf = ConfigurationRegistry("cfitall")
        self.assertEqual(cf.get("onelist", list), ["onething"])

    def test_environment_list_trailing_comma(self):
        os.environ["CFITALL__EXTRA_COMMAS"] = "[,onething,,twothing,]"
        cf = ConfigurationRegistry("cfitall")
        self.assertEqual(cf.get("extra_commas", list), ["onething", "twothing"])


if __name__ == "__main__":
    unittest.main()
