from mininterface import Mininterface, run
from mininterface._lib.form_dict import dataclass_to_tagdict
from mininterface.tag import Tag
from pydantic_configs import PydModel, PydNested, PydNestedRestraint
from shared import TestAbstract


class TestPydanticIntegration(TestAbstract):
    def test_basic(self):
        m = run(PydModel, interface=Mininterface)
        self.assertEqual("hello", m.env.name)

    def test_nested(self):
        m = run(PydNested, interface=Mininterface)
        self.assertEqual(-100, m.env.number)

        self.sys("--number", "-200")
        m = run(PydNested, interface=Mininterface)
        self.assertEqual(-200, m.env.number)
        self.assertEqual(4, m.env.inner.number)

    def test_config(self):
        m = run(PydNested, config_file="tests/pydantic.yaml", interface=Mininterface)
        self.assertEqual(100, m.env.number)
        self.assertEqual(0, m.env.inner.number)
        self.assertEqual("hello", m.env.inner.text)

    def test_nested_restraint(self):
        m = run(PydNestedRestraint, interface=Mininterface)
        self.assertEqual("hello", m.env.inner.name)

        f: Tag = dataclass_to_tagdict(m.env)["inner"]["name"]
        self.assertTrue(f.update("short"))
        self.assertEqual("Restrained name ", f.description)
        self.assertFalse(f.update("long words"))
        self.assertEqual("String should have at most 5 characters Restrained name ", f.description)
        self.assertTrue(f.update(""))
        self.assertEqual("Restrained name ", f.description)

    # NOTE
    # def test_run_ask_for_missing(self):
    #   Might be a mess. Seems that missing fields are working better
    #   when nested than directly.
