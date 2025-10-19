import unittest

import dlt
from data_foundation.defs.dlthub.translator import CustomDagsterDltTranslator


class TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.translator = CustomDagsterDltTranslator()

        @dlt.resource(name="test.table_1")
        def resource_1():
            yield from [{"a":1}]
        cls.resource_1 = resource_1

        @dlt.resource(name="test.table_2", data_from=resource_1) # type: ignore
        def resource_2(data):
            yield from [{"a":1}]
        
        cls.resource_2 = resource_2

class TestGetDepsAssetKeys(TestCase):

    def test_get_deps_asset_key(self) -> None:
        deps_asset_key = self.translator.get_deps_asset_keys(self.resource_1)[0] # type: ignore
        self.assertEqual(deps_asset_key.parts, ("test", "src", "table_1"))

    def test_get_get_deps_asset_key_with_data_from_(self) -> None:
        deps_asset_key = self.translator.get_deps_asset_keys(self.resource_2)[0] # type: ignore
        self.assertEqual(deps_asset_key.parts, ("test", "raw", "table_1"))        

class TestGetAssetKey(TestCase):

    def test_get_asset_key(self) -> None:
        asset_key = self.translator.get_asset_key(self.resource_1)
        self.assertEqual(asset_key.parts, ("test", "raw", "table_1"))


class TestGetGroupName(TestCase):

    def test_get_group_name(self) -> None:
        group_name = self.translator.get_group_name(self.resource_1)
        self.assertEqual(group_name, "test")

class TestGetPartitionsDef(TestCase):
    ...

class TestGetAutomationCondition(TestCase):
    
    def test_get_automation_condition(self) -> None:
        condition = self.translator.get_automation_condition(self.resource_1)
        self.assertIs(condition, None)

class TestGetTags(TestCase):
    ...
