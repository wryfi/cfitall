import os
import unittest

from cfitall.config import ConfigManager


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        super().setUp()
        os.environ["CFITALL__GLOBAL__NAME"] = "cfitall"
        os.environ["CFITALL__GLOBAL__PATH"] = "/Users/wryfi,/Users/wryfi/tmp"
        os.environ["CFITALL__FOO__BANG"] = "WHAMMY!"
        os.environ["CFITALL__ONELIST"] = "onething"
        os.environ["CFITALL__CSV"] = "onething,twothing"
        os.environ["CFITALL__JSONISH_LIST"] = "[onething,twothing]"
        os.environ["CFITALL__JSONISH_LIST_WHITESPACE"] = "[onething, twothing]"

    def tearDown(self):
        super().tearDown()
        for key, value in os.environ.items():
            if key.startswith("CFITALL"):
                del os.environ[key]

    def test_create_object(self):
        _cf = ConfigManager("cfitall")

    def test_environment_variables(self):
        cf = ConfigManager("cfitall")
        self.assertEqual(cf.get("global.name"), "cfitall")
        self.assertEqual(
            cf.get("global.path", list), ["/Users/wryfi", "/Users/wryfi/tmp"]
        )
        self.assertEqual(cf.get("foo.bang"), "WHAMMY!")

    def test_config_file(self):
        cf = ConfigManager("cfitall")
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
        cf = ConfigManager("cfitall")
        cf.set_default("global.authors", ["michael scott", "jim halpert"])
        self.assertEqual(
            cf.get("global.authors", list), ["michael scott", "jim halpert"]
        )
        cf.add_config_path(os.path.dirname(os.path.abspath(__file__)))
        cf.read_config()
        self.assertEqual(cf.get("global.authors", list), ["john doe", "jane deer"])
        os.environ["CFITALL__GLOBAL__AUTHORS"] = "holly flax,robert california"
        self.assertEqual(
            cf.get("global.authors", list), ["holly flax", "robert california"]
        )
        cf.set("global.authors", ["dwight schrute", "pam beesly"])
        self.assertEqual(
            cf.get("global.authors", list), ["dwight schrute", "pam beesly"]
        )

    def test_env_bool(self):
        cf = ConfigManager("cfitall")
        os.environ["CFITALL__TEST__BOOLEAN__TRUE"] = "true"
        os.environ["CFITALL__TEST__BOOLEAN__FALSE"] = "False"
        os.environ[
            "CFITALL__TEST__BOOLEAN__LIST"
        ] = "true,false,True,this,False,is,nice"
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
        cf = ConfigManager("cfitall")
        cf.set_default("test.list.withcommas", ["flenderson, toby", "martin, angela"])
        self.assertEqual(
            cf.get("test.list.withcommas"), ["flenderson, toby", "martin, angela"]
        )
        os.environ["CFITALL__TEST__LIST"] = "hello,world,melting"
        self.assertEqual(cf.get("test.list"), ["hello", "world", "melting"])
        cf.env_value_split = False
        self.assertEqual(cf.get("test.list"), "hello,world,melting")

    def test_space_list(self):
        cf = ConfigManager("cfitall")
        cf.set_default("test.list.withspaces", ["flenderson, toby", "martin, angela"])
        self.assertEqual(
            cf.get("test.list.withcommas"), ["flenderson, toby", "martin, angela"]
        )
        os.environ[
            "CFITALL__TEST__LIST"
        ] = "hello world    melting	 antarctica   broadway"
        cf.env_value_split_space = True
        self.assertEqual(
            cf.get("test.list"), ["hello", "world", "melting", "antarctica", "broadway"]
        )
        cf.env_value_split_space = False
        self.assertEqual(
            cf.get("test.list"), "hello world    melting	 antarctica   broadway"
        )

    def test_different_keys_same_value(self):
        cf = ConfigManager("cfitall")
        cf.set_default("test.string", "hello, world")
        cf.set_default("test.string_2", "hello, world")
        self.assertEqual(cf.get("test.string"), cf.get("test.string_2"))

    def test_single_element_list_env_var(self):
       cf = ConfigManager("cfitall")
       self.assertEqual(cf.get("onelist", list), ["onething"])

if __name__ == "__main__":
    unittest.main()
