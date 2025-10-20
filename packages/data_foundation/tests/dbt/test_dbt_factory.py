import unittest

# from unittest.mock import patch


class TestFactory(unittest.TestCase): ...

class TestBuildDefinitions(TestFactory): ...
class TestGetAssets(TestFactory): ...

if __name__ == "__main__":
    unittest.main()