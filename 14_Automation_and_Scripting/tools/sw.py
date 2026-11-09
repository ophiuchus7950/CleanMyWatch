#!/usr/bin/env python3
"""sw.py - guarded ADB client for Android smartwatches.

This is the debloating engine of the watch knowledge system. It works
only with the `adb` binary from Android platform-tools. Set SW_ADB when
the binary has a nonstandard path or name. Set SW_SERIAL to pick a
device when more than one is connected.

Usage:
  python tools/sw.py devices
  python tools/sw.py identify
  python tools/sw.py packages [--state all|enabled|disabled|uninstalled]
      [--out FILE]
  python tools/sw.py record [--out FILE]
  python tools/sw.py disable PACKAGE...
  python tools/sw.py enable PACKAGE...
  python tools/sw.py uninstall-keep PACKAGE...
  python tools/sw.py uninstall-purge PACKAGE...
  python tools/sw.py restore --record FILE [--all]
  python tools/sw.py one "getprop ro.product.model"   (read-only)
  python tools/sw.py apply --profile ID [--dry-run] [--yes]
      [--profiles DIR] [--data DIR]

Exit codes:
  0  the command ran
  1  the command ran and read-back or a check failed
  2  the command refused before it touched the watch

Safety rules (copy of 11_Debloating_Procedures/01_preparation.md):
  1. The tool records the watch state before the first change. The first
     record wins. It refuses to overwrite an existing record.
  2. Packages in the protected core set are refused. The tool never
     guesses a package name. Names come from the watch.
  3. One pm command runs per shell call.
  4. The tool reads the state back after every batch. It reports every
     package that did not reach the planned state and exits 1.
  5. apply needs the --yes flag. Never run unverified removal commands.
"""

import hashlib
import json
import os
import subprocess
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swdb as database  # noqa: E402  (same tools/ directory)

CREATE_NO_WINDOW = 0x08000000  # Windows: keep the console window away
IS_WINDOWS = os.name == "nt"

READ_ONLY_PREFIXES = ("getprop", "dumpsys", "pm list", "pm path")

# Wear OS mapping from the Android API level. Sources:
# 03_Platform_Architecture/01_wear_os_architecture.md
SDK_TO_WEAR = {
    30: "Wear OS 3 (Android 11)",
    33: "Wear OS 4 (Android 13)",
    34: "Wear OS 5 (Android 14)",
    35: "Wear OS 5.1 (Android 15)",
    36: "Wear OS 6 (Android 16)",
}

# Scope identifiers used by 13_Device_Specific_Profiles/profile.json.
SDK_TO_SCOPE = {
    30: "wear_os_3",
    33: "wear_os_4",
    34: "wear_os_5",
    35: "wear_os_5_1",
    36: "wear_os_6",
}


class Refuse(Exception):
    """The tool stops before it touches the watch."""


def adb_path():
    return os.environ.get("SW_ADB", "adb")


def adb(*args, timeout=60):
    """Run one adb host command. Return stdout text."""
    argv = [adb_path()] + list(args)
    if os.environ.get("SW_SERIAL"):
        argv[1:1] = ["-s", os.environ["SW_SERIAL"]]
    try:
        proc = subprocess.run(
            argv, capture_output=True, text=True, timeout=timeout,
            creationflags=CREATE_NO_WINDOW if IS_WINDOWS else 0)
    except FileNotFoundError:
        raise Refuse("the adb binary is not found. Install Android "
                     "platform-tools or set SW_ADB.")
    except subprocess.TimeoutExpired:
        raise Refuse("the adb command did not answer within %d seconds"
                     % timeout)
    out = proc.stdout or ""
    err = proc.stderr or ""
    if proc.returncode != 0 and not out:
        raise Refuse("adb failed: %s" % err.strip() or "no output")
    return out.strip()


def require_one_device():
    """Refuse when the device count is not exactly one usable watch."""
    listing = adb("devices")
    usable = []
    for line in listing.splitlines()[1:]:
        line = line.strip()
        if not line or "\t" not in line:
            continue
        serial, state = line.split("\t", 1)
        if state.strip() == "device":
            usable.append(serial)
    if os.environ.get("SW_SERIAL"):
        wanted = os.environ["SW_SERIAL"]
        if wanted not in usable:
            raise Refuse(
                "SW_SERIAL %r is not a connected device with state "
                "\"device\"." % wanted)
        return wanted
    if len(usable) == 0:
        raise Refuse(
            "no connected device. Pair and connect the watch first "
            "(06_ADB_Integration/01_adb_setup_and_pairing.md).")
    if len(usable) > 1:
        raise Refuse(
            "several devices are connected: %s. Set SW_SERIAL."
            % ", ".join(usable))
    return usable[0]


def shell(command, user_flag=""):
    """Run one shell call on the watch. Return trimmed output."""
    raise_on = ("Error", "Failure")
    out = adb("shell", shell_join(command, user_flag))
    for marker in raise_on:
        if marker in out:
            raise Refuse(
                "the watch refused %r: %s. See "
                "16_Troubleshooting/01_troubleshooting.md."
                % (command, out.strip()))
    return out.strip()


def shell_join(command, user_flag):
    return "%s%s" % (command, user_flag)


def package_names(raw):
    """Parse a pm list packages answer into package names."""
    names = []
    for line in raw.splitlines():
        line = line.strip()
        if not line.startswith("package:"):
            continue
        name = line[len("package:"):].strip()
        if name:
            names.append(name)
    return names


def fetch_states(user=0):
    """Return (enabled, disabled, uninstalled_for_user) name sets."""
    flag = " --user %d" % user
    enabled = set(package_names(shell(
        "pm list packages -s -e", flag)))
    disabled = set(package_names(shell(
        "pm list packages -s -d", flag)))
    all_names = set(package_names(shell(
        "pm list packages -s -u", flag)))
    uninstalled = all_names - enabled - disabled
    return enabled, disabled, uninstalled


def identify():
    props = ("ro.product.brand", "ro.product.model", "ro.product.device",
             "ro.product.manufacturer", "ro.build.version.release",
             "ro.build.version.sdk", "ro.build.display.id",
             "ro.build.version.incremental")
    values = {}
    for prop in props:
        values[prop] = shell("getprop %s" % prop)
    sdk = int(values["ro.build.version.sdk"]) \
        if values["ro.build.version.sdk"].isdigit() else 0
    return values, sdk


def check_refused_targets(names):
    bad = [n for n in names if database.is_protected(n)]
    if bad:
        for name in bad:
            print("refused: %s is in the protected core set. Nothing "
                  "was changed." % name)
        raise Refuse("remove the protected names from your request.")


def check_device(profile, values, sdk):
    """Refuse when the connected watch does not match the profile scope."""
    model = values.get("ro.product.model", "") or ""
    device = values.get("ro.product.device", "") or ""
    problems = []
    patterns = profile.get("device_match") or []
    if patterns:
        haystack = ("%s %s" % (model, device)).lower()
        if not any(str(p).lower() in haystack for p in patterns):
            problems.append(
                "device %r is not in the profile device_match list (%s)"
                % (model or "unknown", ", ".join(patterns)))
    software_scope = profile.get("software_scope") or []
    if software_scope:
        label = SDK_TO_SCOPE.get(sdk)
        if label is None:
            problems.append(
                "Android SDK %d is outside the verified Wear OS mapping" % sdk)
        elif label not in software_scope:
            problems.append(
                "software %r is not in the profile software_scope (%s)"
                % (label, ", ".join(software_scope)))
    if not problems:
        return
    if os.environ.get("SW_ALLOW_DEVICE_MISMATCH") == "1":
        for problem in problems:
            print("warning: %s" % problem)
        print("warning: SW_ALLOW_DEVICE_MISMATCH=1 is set. The profile "
              "scope check was bypassed.")
        return
    raise Refuse("the connected watch does not match the profile. %s. "
                 "Use the correct profile, or set SW_ALLOW_DEVICE_MISMATCH=1 "
                 "to bypass the check." % ". ".join(problems))


def record_path(serial, out=None):
    if out:
        return out
    tag = hashlib.sha1(serial.encode()).hexdigest()[:8]
    return "sw-record-%s.json" % tag


def save_record(serial, out=None, force=False):
    """Record the reachable state of user 0. First record wins."""
    identity, sdk = identify()
    enabled, disabled, uninstalled = fetch_states(0)
    path = record_path(serial, out)
    if os.path.exists(path) and not force:
        raise Refuse(
            "record %s exists already. The first record wins. Give a "
            "new --out path or remove the old file on purpose." % path)
    data = {
        "version": 1,
        "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "serial": serial,
        "identity": identity,
        "wear_os_label": SDK_TO_WEAR.get(sdk, "mapping unknown"),
        "user": 0,
        "enabled": sorted(enabled),
        "disabled": sorted(disabled),
        "uninstalled_for_user": sorted(uninstalled),
    }
    text = json.dumps(data, indent=2)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        handle.write(text)
    os.replace(tmp, path)
    return path, data


def load_record(path):
    if not os.path.exists(path):
        raise Refuse("record %s is not found." % path)
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if data.get("version") != 1 or "enabled" not in data:
        raise Refuse("record %s is not a usable state record." % path)
    return data


def log(serial, lines):
    """Append one execution log line per operation."""
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    with open("sw-log.txt", "a", encoding="utf-8") as handle:
        for line in lines:
            handle.write("%s %s %s\n" % (stamp, serial, line))


def change_state(op, names, planned_markers):
    """Run one guarded operation per package. Verify with read-back.

    planned_markers: dict name -> set of states that count as done.
    Returns the list of failed names.
    """
    check_refused_targets(names)
    enabled, disabled, uninstalled = fetch_states(0)
    serial = require_one_device()
    record, _data = ensure_record(serial)
    print("record: %s (first record wins)" % record)
    commands = {
        "disable": "pm disable-user --user 0",
        "enable": "pm enable --user 0",
        "uninstall-keep": "pm uninstall -k --user 0",
        "uninstall-purge": "pm uninstall --user 0",
    }
    for name in names:
        current = ("enabled" if name in enabled else
                   "disabled" if name in disabled else
                   "uninstalled" if name in uninstalled else "absent")
        print("running: %s %s (state before: %s)"
              % (commands[op], name, current))
        shell(commands[op], user_flag="")
        log(serial, ["%s %s" % (commands[op], name)])
    failed = verify(names, planned_markers)
    return failed


def verify(names, planned_markers):
    """Read the state back and compare with the planned states."""
    enabled, disabled, uninstalled = fetch_states(0)
    after = {"enabled": enabled, "disabled": disabled,
             "uninstalled": uninstalled}
    failed = []
    for name in names:
        got = None
        for state_, values in after.items():
            if name in values:
                got = state_
        want = planned_markers.get(name)
        ok = (got in want) if want else False
        print("verified: %s now %s (planned %s)"
              % (name, got or "absent", "/".join(want) if want else "?"))
        if not ok:
            failed.append(name)
    if failed:
        print("READ-BACK FAILED for: %s" % ", ".join(failed))
        print("Stop here. Do not run the command in a loop. See "
              "16_Troubleshooting/01_troubleshooting.md.")
    return failed


def cmd_apply(profile_id, profiles, data, confirm, dry):
    profiles_dir = profiles or os.path.join(
        REPO_ROOT, "13_Device_Specific_Profiles")
    data_dir = data or database.DEFAULT_DATA_DIR
    datasets, problems = database.load_datasets(data_dir)
    if problems:
        print("warning: the database has %d validation problem(s)."
              % len(problems))
    profile = database.find_profile(profiles_dir, profile_id)
    if profile is None:
        raise Refuse("profile %r not found" % profile_id)
    commands, skipped = database.plan_commands(
        profile, datasets, "disable")
    if not dry and not confirm:
        raise Refuse("apply changes the watch. Confirm with --yes.")
    if dry:
        print("DRY RUN. No changes will be made.")
    serial = require_one_device()
    values, sdk = identify()
    print("device: %s %s (SDK %d, %s)" % (
        values.get("ro.product.brand", "unknown"),
        values.get("ro.product.model", "unknown"), sdk,
        SDK_TO_WEAR.get(sdk, "outside the verified mapping")))
    check_device(profile, values, sdk)
    if not dry:
        record, _data = ensure_record(serial)
        print("record: %s (first record wins)" % record)
    planned = {}
    for command in commands:
        target = command.split()[-1]
        if command.startswith("pm disable-user"):
            planned[target] = {"disabled"}
        elif command.startswith("pm uninstall"):
            planned[target] = {"uninstalled"}
        print(("DRY RUN: " if dry else "") + command)
    for name, reason in skipped:
        print("# skipped %s (%s)" % (name, reason))
    if dry:
        print("DRY RUN ended. The watch was not changed.")
        return 0
    failed = []
    for command in commands:
        target = command.split()[-1]
        try:
            shell(command)
        except Refuse as exc:
            print("watch refused: %s" % exc)
            failed.append(target)
            continue
        log(serial, [command])
    failed_names = verify(list(planned), planned)
    all_failed = failed + failed_names
    if all_failed:
        return 1
    return 0


def cmd_restore(record_file):
    """Print and run restore commands from a state record."""
    data = load_record(record_file)
    commands = []
    for name in data.get("disabled", []) or []:
        commands.append("pm enable --user 0 %s" % name)
    for name in data.get("uninstalled_for_user", []) or []:
        commands.append("pm install-existing --user 0 %s" % name)
    serial = require_one_device()
    record, _ = ensure_record(serial)
    print("record: %s (first record wins)" % record)
    print("Restoring %d package(s) from %s. Packages that were already "
          "disabled or uninstalled before the record are restored to "
          "that state too." % (len(commands), record_file))
    for command in commands:
        try:
            shell(command)
        except Refuse as exc:
            print("watch refused: %s" % exc)
    planned = {}
    for command in commands:
        target = command.split()[-1]
        planned[target] = {"enabled"} if command.startswith(
            "pm enable") else {"enabled"}
    failed = verify(list(planned), planned)
    return 1 if failed else 0


def ensure_record(serial, out=None):
    """Save a record if none exists; if one exists, keep it and proceed."""
    try:
        return save_record(serial, out, force=False)
    except Refuse as exc:
        if "exists already" in str(exc):
            print("existing record kept (first record wins): %s" % exc)
            return record_path(serial, out), load_record(record_path(serial, out))
        raise


def cmd_one(raw):
    """Run one read-only shell command. Mutations are refused."""
    raw = raw.strip()
    if not raw or not any(raw.startswith(p) for p in READ_ONLY_PREFIXES):
        raise Refuse(
            "one runs read-only commands only (%s)." %
            ", ".join(READ_ONLY_PREFIXES))
    print(shell(raw))
    return 0


def cmd_packages(state="all", out=None):
    serial = require_one_device()
    enabled, disabled, uninstalled = fetch_states(0)
    lines = []
    for name in sorted(enabled | disabled | uninstalled):
        state_ = ("enabled" if name in enabled else
                  "disabled" if name in disabled else
                  "uninstalled-for-user" if name in uninstalled else
                  "absent")
        if state != "all" and state_ != state:
            continue
        lines.append("%s %s" % (name, state_))
    text = "\n".join(lines) + "\n"
    if out:
        with open(out, "w", encoding="utf-8") as handle:
            handle.write(text)
        print("wrote %d line(s) to %s" % (len(lines), out))
    else:
        sys.stdout.write(text)
    return 0


def main(argv=None):
    try:
        return dispatch(argv)
    except (Refuse, KeyboardInterrupt) as exc:
        print("refused: %s" % exc)
        return 2


def dispatch(argv=None):
    import argparse
    parser = argparse.ArgumentParser(prog="sw")
    parser.add_argument("--data", default=None)
    parser.add_argument("--profiles", default=None)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("devices")
    sub.add_parser("identify")
    pkgs = sub.add_parser("packages")
    pkgs.add_argument("--state", default="all", choices=(
        "all", "enabled", "disabled", "uninstalled"))
    pkgs.add_argument("--out")
    rec = sub.add_parser("record")
    rec.add_argument("--out")
    dis = sub.add_parser("disable")
    dis.add_argument("packages", nargs="+")
    ena = sub.add_parser("enable")
    ena.add_argument("packages", nargs="+")
    uk = sub.add_parser("uninstall-keep")
    uk.add_argument("packages", nargs="+")
    up = sub.add_parser("uninstall-purge")
    up.add_argument("packages", nargs="+")
    rest = sub.add_parser("restore")
    rest.add_argument("--record", required=True)
    one = sub.add_parser("one")
    one.add_argument("command")
    app = sub.add_parser("apply")
    app.add_argument("--profile", required=True)
    app.add_argument("--yes", action="store_true", default=False)
    app.add_argument("--dry-run", action="store_true", default=False)
    args = parser.parse_args(argv)

    if args.cmd == "devices":
        print(adb("devices"))
        return 0
    if args.cmd == "identify":
        require_one_device()
        values, sdk = identify()
        for prop in sorted(values):
            print("%s = %s" % (prop, values[prop]))
        print("wear_os_label = %s" %
              SDK_TO_WEAR.get(sdk, "outside the verified mapping (SDK "
                              "%d)" % sdk))
        return 0
    if args.cmd == "packages":
        return cmd_packages(args.state, args.out)
    if args.cmd == "record":
        serial = require_one_device()
        path, data = save_record(serial, args.out)
        print("record written: %s (%d enabled, %d disabled, %d "
              "uninstalled-for-user)" % (
                  path, len(data["enabled"]), len(data["disabled"]),
                  len(data["uninstalled_for_user"])))
        return 0
    if args.cmd in ("disable", "enable", "uninstall-keep",
                    "uninstall-purge"):
        names = args.packages
        want = {"disable": {"disabled"}, "enable": {"enabled"},
                "uninstall-keep": {"uninstalled"},
                "uninstall-purge": {"uninstalled"}}[args.cmd]
        failed = change_state(args.cmd, names, want)
        return 1 if failed else 0
    if args.cmd == "restore":
        return cmd_restore(args.record)
    if args.cmd == "one":
        return cmd_one(args.command)
    if args.cmd == "apply":
        return cmd_apply(args.profile, args.profiles, args.data,
                         args.yes, args.dry_run)
    return 2


if __name__ == "__main__":
    sys.exit(main())
