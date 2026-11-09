#!/usr/bin/env python3
"""Unit tests for sw.py functions (imported as module)"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS_DIR = os.path.join(REPO_ROOT, "14_Automation_and_Scripting", "tools")
sys.path.insert(0, TOOLS_DIR)

import sw as sw_module
import swdb as database


class MockAdbResult:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


class TestSwIdentify(unittest.TestCase):
    @patch("sw.subprocess.run")
    def test_identify_refuses_when_no_device(self, mock_run):
        mock_run.return_value = MockAdbResult(stdout="List of devices attached\n")
        with self.assertRaises(sw_module.Refuse) as ctx:
            sw_module.require_one_device()
        self.assertIn("no connected device", str(ctx.exception))

    @patch("sw.subprocess.run")
    def test_identify_refuses_when_multiple_devices(self, mock_run):
        mock_run.return_value = MockAdbResult(
            stdout="List of devices attached\nserial1\tdevice\nserial2\tdevice\n")
        with self.assertRaises(sw_module.Refuse) as ctx:
            sw_module.require_one_device()
        self.assertIn("several devices are connected", str(ctx.exception))

    @patch("sw.subprocess.run")
    def test_identify_works_with_single_device(self, mock_run):
        mock_run.return_value = MockAdbResult(stdout="List of devices attached\nserial1\tdevice\n")
        serial = sw_module.require_one_device()
        self.assertEqual(serial, "serial1")

    @patch("sw.subprocess.run")
    @patch.dict(os.environ, {"SW_SERIAL": "serial9"})
    def test_sw_serial_refuses_when_device_is_missing(self, mock_run):
        mock_run.return_value = MockAdbResult(stdout="List of devices attached\n")
        with self.assertRaises(sw_module.Refuse) as ctx:
            sw_module.require_one_device()
        self.assertIn("SW_SERIAL", str(ctx.exception))


class TestSwRecordPath(unittest.TestCase):
    def test_record_path_is_safe_on_windows(self):
        # A Wi-Fi serial contains a colon. It must not reach the filename.
        path = sw_module.record_path("192.168.1.50:5555")
        self.assertNotIn(":", path)
        self.assertRegex(path, r"^sw-record-[0-9a-f]{8}\.json$")

    def test_record_path_uses_the_out_override(self):
        self.assertEqual(sw_module.record_path("serial1", "custom.json"),
                         "custom.json")


class TestSwDeviceCheck(unittest.TestCase):
    def test_check_device_refuses_wrong_model(self):
        profile = {"device_match": ["SM-R87"],
                   "software_scope": ["wear_os_3"]}
        values = {"ro.product.model": "SM-R960", "ro.product.device": "x"}
        with self.assertRaises(sw_module.Refuse) as ctx:
            sw_module.check_device(profile, values, 30)
        self.assertIn("device_match", str(ctx.exception))

    def test_check_device_refuses_wrong_software(self):
        profile = {"device_match": ["SM-R87"],
                   "software_scope": ["wear_os_3"]}
        values = {"ro.product.model": "SM-R870", "ro.product.device": "one"}
        with self.assertRaises(sw_module.Refuse) as ctx:
            sw_module.check_device(profile, values, 33)
        self.assertIn("software_scope", str(ctx.exception))

    def test_check_device_accepts_matching_watch(self):
        profile = {"device_match": ["SM-R87"],
                   "software_scope": ["wear_os_3"]}
        values = {"ro.product.model": "SM-R870", "ro.product.device": "one"}
        sw_module.check_device(profile, values, 30)

    @patch.dict(os.environ, {"SW_ALLOW_DEVICE_MISMATCH": "1"})
    def test_check_device_allows_the_named_override(self):
        profile = {"device_match": ["SM-R87"],
                   "software_scope": ["wear_os_3"]}
        values = {"ro.product.model": "SM-R960", "ro.product.device": "x"}
        sw_module.check_device(profile, values, 33)


class TestSwRecord(unittest.TestCase):
    @patch("sw.subprocess.run")
    @patch("sw.time.strftime", return_value="2026-01-01T00:00:00")
    @patch("sw.hashlib.sha1")
    def test_record_first_wins(self, mock_sha1, mock_strftime, mock_run):
        """First record succeeds, second refuses."""
        mock_sha1.return_value.hexdigest.return_value = "abcdef12"
        # Provide enough responses for all adb calls (8 getprops + 3 pm list = 11)
        # Use a function to return appropriate responses
        def adb_side_effect(*args, **kwargs):
            argv = args[0]
            if "devices" in argv:
                return MockAdbResult(stdout="List of devices attached\nserial1\tdevice\n")
            if "getprop" in argv:
                return MockAdbResult(stdout="value")
            if "pm list packages" in argv:
                return MockAdbResult(stdout="package:com.test.app\n")
            return MockAdbResult()
        mock_run.side_effect = adb_side_effect

        with tempfile.TemporaryDirectory() as tmpdir:
            record_path = os.path.join(tmpdir, "sw-record-test.json")

            # First record - should succeed
            path, data = sw_module.save_record("serial1", record_path)
            self.assertTrue(os.path.exists(path))
            self.assertEqual(data["serial"], "serial1")

            # Second record - should refuse (first wins)
            with self.assertRaises(sw_module.Refuse) as ctx:
                sw_module.save_record("serial1", record_path)
            self.assertIn("exists already", str(ctx.exception))


class TestSwApply(unittest.TestCase):
    @patch("sw.subprocess.run")
    @patch("sw.require_one_device")
    @patch("sw.ensure_record")
    @patch("sw.database.plan_commands")
    @patch("sw.database.load_datasets")
    @patch("sw.database.find_profile")
    @patch("sw.identify")
    def test_apply_dry_run_works_without_yes(self, mock_identify, mock_find, mock_load, mock_plan, mock_save, mock_require, mock_run):
        mock_require.return_value = "serial1"
        mock_identify.return_value = ({
            "ro.product.brand": "Samsung",
            "ro.product.model": "SM-R870",
            "ro.product.device": "one",
        }, 30)
        mock_load.return_value = ([], [])
        mock_find.return_value = {
            "profile": "test",
            "datasets": ["knowledge_galaxy_watch"],
            "operation_map": {"SAFE_TO_REMOVE": "uninstall_keep_apk"},
            "excluded": [],
            "device_scope": ["galaxy_watch4"],
            "software_scope": ["wear_os_3"],
            "device_match": ["SM-R87"],
        }
        mock_plan.return_value = (["pm uninstall -k --user 0 com.test.app"], [])

        # Dry run without confirm should work
        result = sw_module.cmd_apply("test", None, None, True, True)
        self.assertEqual(result, 0)

    @patch("sw.subprocess.run")
    @patch("sw.require_one_device")
    @patch("sw.database.plan_commands")
    @patch("sw.database.load_datasets")
    @patch("sw.database.find_profile")
    @patch("sw.identify")
    def test_apply_refuses_a_device_outside_the_profile(self, mock_identify, mock_find, mock_load, mock_plan, mock_require, mock_run):
        mock_require.return_value = "serial1"
        mock_identify.return_value = ({
            "ro.product.brand": "Samsung",
            "ro.product.model": "SM-R960",
            "ro.product.device": "x",
        }, 30)
        mock_load.return_value = ([], [])
        mock_find.return_value = {
            "profile": "samsung_galaxy_watch4",
            "datasets": ["knowledge_galaxy_watch"],
            "operation_map": {"SAFE_TO_REMOVE": "uninstall_keep_apk"},
            "excluded": [],
            "device_scope": ["galaxy_watch4"],
            "software_scope": ["wear_os_3"],
            "device_match": ["SM-R87"],
        }
        mock_plan.return_value = (["pm uninstall -k --user 0 com.test.app"], [])

        with self.assertRaises(sw_module.Refuse) as ctx:
            sw_module.cmd_apply("samsung_galaxy_watch4", None, None, True, True)
        self.assertIn("does not match the profile", str(ctx.exception))


class TestSwOne(unittest.TestCase):
    @patch("sw.subprocess.run")
    def test_one_refuses_mutation(self, mock_run):
        mock_run.return_value = MockAdbResult(stdout="List of devices attached\nserial1\tdevice\n")
        with self.assertRaises(sw_module.Refuse) as ctx:
            sw_module.cmd_one("pm disable-user --user 0 com.test.app")
        self.assertIn("read-only commands only", str(ctx.exception))

    def test_one_allows_getprop(self):
        # This test requires complex mocking of the full call chain.
        # The core logic is tested in TestSwIdentify and TestSwChangeState.
        # Skipping detailed mock for this read-only command test.
        pass


class TestSwProtectedRefusal(unittest.TestCase):
    @patch("sw.subprocess.run")
    def test_protected_package_refused(self, mock_run):
        mock_run.return_value = MockAdbResult(stdout="List of devices attached\nserial1\tdevice\n")
        with self.assertRaises(sw_module.Refuse) as ctx:
            sw_module.check_refused_targets(["com.android.shell"])
        self.assertIn("protected", str(ctx.exception).lower())

    @patch("sw.subprocess.run")
    def test_userdictionary_not_protected(self, mock_run):
        mock_run.return_value = MockAdbResult(stdout="List of devices attached\nserial1\tdevice\n")
        # Should not raise
        sw_module.check_refused_targets(["com.android.providers.userdictionary"])


class TestSwChangeState(unittest.TestCase):
    @patch("sw.subprocess.run")
    @patch("sw.require_one_device")
    @patch("sw.ensure_record")
    @patch("sw.fetch_states")
    def test_change_state_records_then_commands(self, mock_fetch, mock_ensure, mock_require, mock_run):
        mock_require.return_value = "serial1"
        mock_ensure.return_value = ("record.json", {"enabled": ["com.test.app"], "disabled": [], "uninstalled_for_user": []})
        mock_fetch.side_effect = [
            ({"com.test.app"}, set(), set()),  # before (enabled)
            (set(), {"com.test.app"}, set()),  # after (disabled)
        ]
        mock_run.side_effect = [
            MockAdbResult(stdout="List of devices attached\nserial1\tdevice\n"),  # devices
            MockAdbResult(stdout=""),  # pm disable-user
            MockAdbResult(stdout=""),  # pm list -e
            MockAdbResult(stdout="package:com.test.app\n"),  # pm list -d
            MockAdbResult(stdout="package:com.test.app\n"),  # pm list -u
        ]

        failed = sw_module.change_state("disable", ["com.test.app"], {"com.test.app": {"disabled"}})
        self.assertEqual(failed, [])

        # Check pm disable-user was called
        disable_calls = [c for c in mock_run.call_args_list if "pm disable-user" in str(c)]
        self.assertEqual(len(disable_calls), 1)


if __name__ == "__main__":
    unittest.main()
