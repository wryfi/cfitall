import decimal
import os
import unittest

from cfitall.registry import ConfigurationRegistry
from cfitall.providers import EnvironmentProvider, FilesystemProvider


class TestConfigRegistry(unittest.TestCase):
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

    def test_create_registry_default(self):
        cf = ConfigurationRegistry("test")
        self.assertEqual(cf.name, "test")
        self.assertEqual(cf.values["defaults"], {})
        self.assertEqual(cf.values["super"], {})
        self.assertEqual(cf.providers.ordering, ["filesystem", "environment"])
        if home := os.getenv("HOME"):
            self.assertEqual(
                cf.providers.filesystem.path,
                [
                    os.path.join(home, ".local", "etc", "test"),
                    os.path.join("/etc", "test"),
                ],
            )
        else:
            self.assertEqual(cf.providers.filesystem.path, os.path.join("/etc", "test"))
        self.assertEqual(
            {"defaults": {}, "filesystem": {}, "environment": {}, "super": {}}, cf.all
        )

    def test_config_keys(self):
        cf = ConfigurationRegistry("cfitall")
        cf.set_default("hello", "nurse")
        cf.set("goodbye.cruel", "world")
        self.assertEqual(
            cf.config_keys,
            ["foo.bang", "global.name", "global.path", "goodbye.cruel", "hello"],
        )

    def test_comma_list(self):
        cf = ConfigurationRegistry("cfitall")
        cf.set_default("test.list.withcommas", ["flenderson, toby", "martin, angela"])
        self.assertEqual(
            cf.get("test.list.withcommas"), ["flenderson, toby", "martin, angela"]
        )

    def test_config_order(self):
        cf = ConfigurationRegistry("cfitall")
        cf.set_default("global.authors", ["michael scott", "jim halpert"])
        self.assertEqual(
            cf.get_list("global.authors"), ["michael scott", "jim halpert"]
        )
        cf.providers.filesystem.path.append(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "yaml")
        ),
        cf.update()
        self.assertEqual(cf.get_list("global.authors"), ["john doe", "jane deer"])
        os.environ["CFITALL__GLOBAL__AUTHORS"] = "[holly flax,robert california]"
        self.assertEqual(
            cf.get_list("global.authors"), ["holly flax", "robert california"]
        )
        cf.set("global.authors", ["dwight schrute", "pam beesly"])
        self.assertEqual(
            cf.get_list("global.authors"), ["dwight schrute", "pam beesly"]
        )

    def test_different_keys_same_value(self):
        cf = ConfigurationRegistry("cfitall")
        cf.set_default("test.string", "hello, world")
        cf.set_default("test.string_2", "hello, world")
        self.assertEqual(cf.get("test.string"), cf.get("test.string_2"))

    def test_env_vars_list(self):
        cf = ConfigurationRegistry("cfitall")
        cf.set_default("hello", "nurse")
        cf.set("goodbye.cruel", "nurse ratched")
        self.assertEqual(
            cf.env_vars,
            [
                "CFITALL__FOO__BANG",
                "CFITALL__GLOBAL__NAME",
                "CFITALL__GLOBAL__PATH",
                "CFITALL__GOODBYE__CRUEL",
                "CFITALL__HELLO",
            ],
        )

    def test_get(self):
        cf = ConfigurationRegistry("cfitall")
        cf.set_default("test.bool", True)
        cf.set_default("test.decimal", decimal.Decimal(123.45))
        cf.set_default("test.float", 101.5)
        cf.set_default("test.integer", 42)
        self.assertEqual(type(cf.get("test.bool")), bool)
        self.assertEqual(type(cf.get("test.decimal")), decimal.Decimal)
        self.assertEqual(type(cf.get("test.float")), float)
        self.assertEqual(type(cf.get("test.integer")), int)
        self.assertEqual(type(cf.get("global.path")), list)
        self.assertEqual(type(cf.get("global.name")), str)

    def test_get_bool(self):
        cf = ConfigurationRegistry("test")
        cf.set_default("bool.true", True)
        cf.set_default("bool.false", False)
        cf.set_default("bool.int.true", 1)
        cf.set_default("bool.int.false", 0)
        self.assertTrue(cf.get_bool("bool.true"))
        self.assertFalse(cf.get_bool("bool.false"))
        self.assertEqual(type(cf.get_bool("bool.int.true")), bool)
        self.assertTrue(cf.get_bool("bool.int.true"))
        self.assertEqual(type(cf.get_bool("bool.int.false")), bool)
        self.assertFalse(cf.get_bool("bool.int.false"))

    def test_get_decimal(self):
        cf = ConfigurationRegistry("cfitall")
        cf.set_default("decimal.string", "3.14159")
        cf.set_default("decimal.int", 5)
        cf.set_default("decimal.float", 1 / 255.0)
        cf.set_default("decimal.letters", "asdf")
        self.assertEqual(cf.get_decimal("decimal.string"), decimal.Decimal("3.14159"))
        self.assertEqual(cf.get_decimal("decimal.int"), decimal.Decimal(5))
        self.assertEqual(
            cf.get_decimal("decimal.float"),
            decimal.Decimal(0.00392156862745098033773416545955114997923374176025390625),
        )
        with self.assertRaises(decimal.InvalidOperation):
            cf.get_decimal("decimal.letters")
        with self.assertRaises(ValueError):
            cf.get_decimal("global.path")

    def test_get_int(self):
        cf = ConfigurationRegistry("cfitall")
        cf.set_default("int.bool.false", False)
        cf.set_default("int.bool.true", True)
        cf.set_default("int.float", 3.14159)
        cf.set_default("int.int", 5)
        cf.set_default("int.letters", "asdf")
        cf.set_default("int.string", "3.14159")
        self.assertEqual(cf.get_int("int.bool.false"), 0)
        self.assertEqual(cf.get_int("int.bool.true"), 1)
        self.assertEqual(cf.get_int("int.float"), 3)
        self.assertEqual(cf.get_int("int.int"), 5)
        with self.assertRaises(ValueError):
            cf.get_int("int.string")
        with self.assertRaises(ValueError):
            cf.get_int("int.letters")
        with self.assertRaises(TypeError):
            cf.get_int("global.path")

    def test_get_list(self):
        cf = ConfigurationRegistry("cfitall")
        cf.set_default("csv.string", "hello, world")
        self.assertEqual(cf.get_list("csv.string"), ["hello", "world"])
        self.assertEqual(
            cf.get_list("csv.string", csv=False),
            ["h", "e", "l", "l", "o", ",", " ", "w", "o", "r", "l", "d"],
        )
        self.assertEqual(
            cf.get_list("global.path"), ["/Users/wryfi", "/Users/wryfi/tmp"]
        )

    def test_get_string(self):
        cf = ConfigurationRegistry("cfitall")
        cf.set_default("string.bool", True)
        cf.set_default("string.decimal", decimal.Decimal("1.5"))
        cf.set_default("string.float", 1 / 3)
        cf.set_default("string.int", 42)
        self.assertEqual(cf.get_string("string.bool"), "True")
        self.assertEqual(cf.get_string("string.decimal"), "1.5")
        self.assertEqual(cf.get_string("string.float"), "0.3333333333333333")
        self.assertEqual(cf.get_string("string.int"), "42")
        self.assertEqual(cf.get_string("global.name"), "cfitall")
        self.assertEqual(
            cf.get_string("global.path"), "['/Users/wryfi', '/Users/wryfi/tmp']"
        )

    def test_set(self):
        cf = ConfigurationRegistry("test")
        cf.set("foo.bar", 42)
        self.assertEqual(cf.values["super"]["foo"]["bar"], 42)
        cf.set_default("foo.bar", 420)
        self.assertEqual(cf.get("foo.bar"), 42)

    def test_set_default(self):
        cf = ConfigurationRegistry("test")
        cf.set_default("foo.bar", 42)
        self.assertEqual(cf.values["defaults"]["foo"]["bar"], 42)
        self.assertEqual(cf.get("foo.bar"), 42)

    def test_providers_empty_list(self):
        cf = ConfigurationRegistry("cfitall", providers=[])
        with self.assertRaises(KeyError):
            _ = cf.values["environment"]
        with self.assertRaises(KeyError):
            _ = cf.values["filesystem"]
        with self.assertRaises(AttributeError):
            _ = cf.providers.filesystem
        with self.assertRaises(AttributeError):
            _ = cf.providers.environment
        self.assertEqual(cf.providers.ordering, [])
        self.assertIsNone(cf.get("global.name"))
        self.assertIsNone(cf.get("foo.bar"))

    def test_providers_env_only(self):
        cf = ConfigurationRegistry(
            "cfitall", providers=[EnvironmentProvider("cfitall")]
        )
        with self.assertRaises(KeyError):
            _ = cf.values["filesystem"]
        with self.assertRaises(AttributeError):
            _ = cf.providers.filesystem
        self.assertEqual(cf.providers.ordering, ["environment"])
        self.assertEqual(cf.get("global.name"), "cfitall")
        self.assertIsNone(cf.get("foo.bar"))

    def test_providers_filesystem_only(self):
        cf = ConfigurationRegistry(
            "cfitall",
            providers=[
                FilesystemProvider(
                    [os.path.join(os.path.dirname(os.path.abspath(__file__)), "yaml")],
                    "cfitall",
                )
            ],
        )
        cf.update()
        with self.assertRaises(KeyError):
            _ = cf.values["environment"]
        with self.assertRaises(AttributeError):
            _ = cf.providers.environment
        self.assertEqual(cf.providers.ordering, ["filesystem"])
        self.assertEqual(cf.get("global.name"), "cfityaml")
        self.assertEqual(cf.get("foo.bar"), "baz")
        self.assertIsNone(cf.get("foo.bang"))

    def test_providers_env_extra(self):
        cf = ConfigurationRegistry("cfitall")
        cf.providers.register(EnvironmentProvider("extra", provider_name="env_extra"))
        os.environ["CFITALL__STUFF"] = "cfitall_stuff"
        os.environ["EXTRA__STUFF"] = "extra_stuff"
        self.assertEqual(cf.get("stuff"), "extra_stuff")

    def test_providers_filesystem_extra(self):
        cf = ConfigurationRegistry("cfitall")
        cf.providers.register(
            FilesystemProvider(
                [os.path.join(os.path.dirname(os.path.abspath(__file__)), "yaml")],
                "extra",
                provider_name="filesystem_extra",
            ),
        )
        cf.providers.filesystem.path.append(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "yaml")
        ),
        cf.update()
        os.environ["EXTRA__STUFF"] = "extra_env"
        self.assertEqual(cf.get("stuff"), "extra_yaml")
        self.assertEqual(cf.get("foo.bar"), "baz")
        self.assertEqual(cf.get("foo.bang"), "WHAMMY!")


if __name__ == "__main__":
    unittest.main()
