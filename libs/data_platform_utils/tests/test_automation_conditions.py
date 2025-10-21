import unittest

from dagster import AutomationCondition
from dagster._core.definitions.declarative_automation.operators import (
    AndAutomationCondition,
)

from data_platform_utils.automation_conditions import CustomAutomationCondition


class TestCustomAutomationCondition(unittest.TestCase):
    def test_manual_returns_none(self):
        self.assertIsNone(CustomAutomationCondition.manual())

    def test_missing_or_changed_returns_condition(self):
        cond = CustomAutomationCondition.missing_or_changed()
        self.assertIsInstance(cond, AutomationCondition)
        self.assertEqual(cond.label, "missing_or_changed")

    def test_eager_returns_condition(self):
        cond = CustomAutomationCondition.eager()
        self.assertIsInstance(cond, AndAutomationCondition)
        self.assertEqual(cond.label, "eager")

    def test_eager_with_deps_checks_returns_condition(self):
        cond = CustomAutomationCondition.eager_with_deps_checks()
        self.assertIsInstance(cond, AutomationCondition)

    def test_lazy_returns_condition(self):
        cond = CustomAutomationCondition.lazy()
        self.assertIsInstance(cond, AutomationCondition)
        self.assertEqual(cond.label, "lazy")

    def test_lazy_on_cron_returns_condition(self):
        cond = CustomAutomationCondition.lazy_on_cron("0 6 * * *", "UTC")
        self.assertIsInstance(cond, AutomationCondition)
        self.assertEqual(cond.label, "lazy_on_cron(0 6 * * *, UTC)")

    def test_lazy_on_cron_with_ignored_assets(self):
        cond = CustomAutomationCondition.lazy_on_cron("0 6 * * *", "UTC", [["a", "b"]])
        self.assertIsInstance(cond, AutomationCondition)

    def test_on_cron_returns_condition(self):
        cond = CustomAutomationCondition.on_cron("0 6 * * *", "UTC")
        self.assertIsInstance(cond, AndAutomationCondition)

    def test_on_cron_with_ignored_assets(self):
        cond = CustomAutomationCondition.on_cron("0 6 * * *", "UTC", [["x", "y"]])
        self.assertIsInstance(cond, AndAutomationCondition)

    def test_on_schedule_returns_condition(self):
        cond = CustomAutomationCondition.on_schedule("0 6 * * *", "utc")
        self.assertIsInstance(cond, AutomationCondition)
        self.assertEqual(cond.label, "on_schedule(0 6 * * *, utc)")

    def test_get_automation_condition_returns_callable(self):
        method = CustomAutomationCondition.get_automation_condition("eager")
        self.assertTrue(callable(method))

    def test_get_automation_condition_returns_none_for_invalid(self):
        method = CustomAutomationCondition.get_automation_condition(
            "nonexistent_condition")
        self.assertIsNone(method)


if __name__ == "__main__":
    unittest.main()
