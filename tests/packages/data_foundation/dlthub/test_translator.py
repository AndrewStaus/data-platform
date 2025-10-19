import unittest

import dagster as dg
from data_foundation.defs.dlthub.factory import Factory


class TestBuildExternalAsset(unittest.TestCase):

    def test_returns_asset_spec_when_data_from_missing(self) -> None:
        config = {
            "name": "public.users",
            "kinds": {"api"}
        }
        asset = Factory._build_external_asset(config)
        
        self.assertIsInstance(asset, dg.AssetSpec)
        if asset:
            print(asset.key.parts)
            self.assertEqual(asset.key.parts, ("public", "src", "users"))
            self.assertEqual(asset.kinds, {"api"})
            self.assertEqual(asset.group_name, "public")

    def test_returns_none_when_data_from_present(self) -> None:
        config = {
            "name": "public.users",
            "data_from": "another_source"
        }
        asset = Factory._build_external_asset(config)
        self.assertIsNone(asset)

    def test_handles_missing_kinds(self) -> None:
        config = {
            "name": "public.users"
        }
        asset = Factory._build_external_asset(config)

        self.assertIsInstance(asset, dg.AssetSpec)
        if asset:
            print(asset.key.parts)
            self.assertEqual(asset.key.parts, ("public", "src", "users"))
            self.assertEqual(asset.kinds, set())
            self.assertEqual(asset.group_name, "public")

    def test_raises_on_invalid_name_format(self) -> None:
        config = {
            "name": "invalidname"
        }
        with self.assertRaises(ValueError):
            Factory._build_external_asset(config)


if __name__ == "__main__":
    unittest.main()