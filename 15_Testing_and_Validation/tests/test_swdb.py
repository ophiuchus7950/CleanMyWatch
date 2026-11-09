#!/usr/bin/env python3
"""Unit tests for swdb.py"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SWDB = os.path.join(REPO_ROOT, "14_Automation_and_Scripting", "tools", "swdb.py")
DATA_DIR = os.path.join(REPO_ROOT, "08_Package_Database", "data")
PROFILE_DIR = os.path.join(REPO_ROOT, "13_Device_Specific_Profiles")


def run_swdb(args):
    cmd = [sys.executable, SWDB, "--data", DATA_DIR, "--profiles", PROFILE_DIR] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


class TestSwdbValidate(unittest.TestCase):
    def test_validate_all_datasets(self):
        code, out, err = run_swdb(["validate"])
        self.assertEqual(code, 0, f"validate failed: {err}\n{out}")
        self.assertIn("Valid: 4 dataset(s)", out)
        self.assertIn("207 package(s)", out)
        self.assertIn("4 profile(s)", out)

    def test_validate_individual_datasets(self):
        for dataset in ["discovery_galaxy_watch4", "knowledge_galaxy_watch",
                        "knowledge_google_wear_os", "knowledge_third_party_watch"]:
            code, out, err = run_swdb(["validate"])
            self.assertEqual(code, 0)

    def test_validate_detects_bad_profile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_dir = os.path.join(tmpdir, "bad")
            os.makedirs(bad_dir)
            with open(os.path.join(bad_dir, "profile.json"), "w",
                      encoding="utf-8") as f:
                json.dump({
                    "profile": "wrong_name",
                    "datasets": ["missing_dataset"],
                    "operation_map": {"SAFE_TO_REMOVE": "explode"},
                    "device_scope": [],
                    "software_scope": []
                }, f)
            code, out, err = run_swdb(["--profiles", tmpdir, "validate"])
            self.assertEqual(code, 1, f"bad profile should fail: {out}{err}")
            self.assertIn("does not match the directory", out)
            self.assertIn("missing_dataset", out)
            self.assertIn("not an operation", out)


class TestSwdbStats(unittest.TestCase):
    def test_stats(self):
        code, out, err = run_swdb(["stats"])
        self.assertEqual(code, 0, f"stats failed: {err}\n{out}")
        self.assertIn("discovery_galaxy_watch4", out)
        self.assertIn("knowledge_galaxy_watch", out)
        self.assertIn("knowledge_google_wear_os", out)
        self.assertIn("knowledge_third_party_watch", out)


class TestSwdbQuery(unittest.TestCase):
    def test_query_known_package(self):
        code, out, err = run_swdb(["query", "com.samsung.android.watch.compass"])
        self.assertEqual(code, 0, f"query failed: {err}\n{out}")
        self.assertIn("SAFE_TO_REMOVE", out)

    def test_query_unknown_package(self):
        code, out, err = run_swdb(["query", "com.unknown.package"])
        self.assertEqual(code, 1, "unknown package should return 1")
        self.assertIn("Unknown package", out)


class TestSwdbPackages(unittest.TestCase):
    def test_packages_list(self):
        code, out, err = run_swdb(["packages"])
        self.assertEqual(code, 0, f"packages failed: {err}\n{out}")
        self.assertIn("com.samsung.android.watch.compass", out)

    def test_packages_filter_risk(self):
        code, out, err = run_swdb(["packages", "--risk", "SAFE_TO_REMOVE"])
        self.assertEqual(code, 0, f"packages filter failed: {err}\n{out}")
        for line in out.strip().splitlines():
            if line and not line.startswith("#"):
                self.assertIn("SAFE_TO_REMOVE", line)

    def test_packages_filter_dataset(self):
        code, out, err = run_swdb(["packages", "--dataset", "knowledge_galaxy_watch"])
        self.assertEqual(code, 0, f"packages dataset filter failed: {err}\n{out}")
        self.assertIn("knowledge_galaxy_watch", out)


class TestSwdbProtected(unittest.TestCase):
    def test_protected_userdictionary_exception(self):
        # userdictionary should NOT be protected (CORE_OK exception)
        code, out, err = run_swdb(["query", "com.android.providers.userdictionary"])
        self.assertEqual(code, 0)
        self.assertNotIn("PROTECTED CORE", out)

    def test_protected_core_packages(self):
        # Core packages like android, gms, shell should be protected
        for pkg in ["android", "com.android.shell", "com.google.android.gms"]:
            code, out, err = run_swdb(["query", pkg])
            self.assertEqual(code, 0, f"query {pkg} failed: {err}\n{out}")
            self.assertIn("PROTECTED CORE", out, f"{pkg} should be protected")


class TestSwdbPlan(unittest.TestCase):
    def test_plan_gw4_excludes_unverified_scope(self):
        # Every verified debloat entry is scoped to Galaxy Watch 6/7.
        # The GW4 profile must not borrow that evidence.
        code, out, err = run_swdb(["plan", "--profile", "samsung_galaxy_watch4"])
        self.assertEqual(code, 0, f"plan failed: {err}\n{out}")
        commands = [line for line in out.splitlines()
                    if line.startswith("pm ")]
        self.assertEqual(commands, [])
        self.assertIn("outside the profile device scope", out)

    def test_plan_gw6_7_includes_third_party(self):
        code, out, err = run_swdb(["plan", "--profile", "samsung_galaxy_watch6_7"])
        self.assertEqual(code, 0, f"plan failed: {err}\n{out}")
        self.assertIn("com.samsung.android.watch.compass", out)
        self.assertIn("com.samsung.android.bixby.agent", out)
        self.assertIn("com.microsoft.office.outlook", out)
        self.assertIn("com.samsung.android.wear.calculator", out)

    def test_plan_gw6_7_restore(self):
        code, out, err = run_swdb(
            ["plan", "--profile", "samsung_galaxy_watch6_7", "--op", "restore"])
        self.assertEqual(code, 0, f"plan restore failed: {err}\n{out}")
        self.assertIn("pm install-existing --user 0", out)

    def test_plan_watch8_guard_profile_is_empty(self):
        code, out, err = run_swdb(["plan", "--profile", "samsung_galaxy_watch8"])
        self.assertEqual(code, 0, f"plan failed: {err}\n{out}")
        commands = [line for line in out.splitlines()
                    if line.startswith("pm ")]
        self.assertEqual(commands, [])

    def test_plan_google_core_empty(self):
        code, out, err = run_swdb(["plan", "--profile", "google_core"])
        self.assertEqual(code, 0, f"google_core plan failed: {err}\n{out}")
        # Should have no commands (empty operation_map)
        lines = [l for l in out.splitlines() if l.strip() and not l.startswith("#")]
        self.assertEqual(len(lines), 0)

    def test_plan_missing_profile(self):
        code, out, err = run_swdb(["plan", "--profile", "nonexistent"])
        self.assertEqual(code, 2, "missing profile should return 2")
        self.assertIn("refused: profile", err + out)


class TestSwdbMatch(unittest.TestCase):
    def test_match_with_known_dump(self):
        # Create a temporary dump file with some known packages
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("package:com.samsung.android.watch.compass\n")
            f.write("package:com.android.shell\n")
            f.write("package:com.unknown.package\n")
            f.write("com.google.android.gms\n")
            dump_path = f.name
        try:
            code, out, err = run_swdb(["match", dump_path])
            self.assertEqual(code, 0, f"match failed: {err}\n{out}")
            self.assertIn("Protected core", out)
            self.assertIn("com.android.shell", out)
            self.assertIn("com.google.android.gms", out)
            self.assertIn("Not in the database", out)
            self.assertIn("com.unknown.package", out)
        finally:
            os.unlink(dump_path)


class TestSwdbExport(unittest.TestCase):
    def test_export_csv(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            csv_path = f.name
        try:
            code, out, err = run_swdb(["export", csv_path])
            self.assertEqual(code, 0, f"export failed: {err}\n{out}")
            self.assertIn("Wrote", out)
            with open(csv_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            self.assertGreater(len(lines), 1)  # header + data
            self.assertIn("package,dataset,risk", lines[0])
        finally:
            if os.path.exists(csv_path):
                os.unlink(csv_path)


if __name__ == "__main__":
    unittest.main()
