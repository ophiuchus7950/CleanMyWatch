#!/usr/bin/env python3
"""swdb.py - package database and profile tool for the smartwatch
debloating knowledge system.

Usage:
  python tools/swdb.py validate [--data DIR]
  python tools/swdb.py stats [--data DIR]
  python tools/swdb.py query PACKAGE [--data DIR]
  python tools/swdb.py packages [--data DIR] [--risk LEVEL] [--dataset ID]
  python tools/swdb.py match DUMP_FILE [--data DIR]
  python tools/swdb.py drift DUMP_FILE --profile ID [--profiles DIR] [--data DIR]
  python tools/swdb.py plan --profile ID [--profiles DIR] [--data DIR]
      [--op disable|restore]

Exit codes:
  0  the command ran
  1  the command ran and found a problem
  2  the command refused before it did anything

The tool reads only files. It never talks to a device. See
11_Debloating_Procedures and 14_Automation_and_Scripting/tool_guide.md.

Dataset and profile directories default to this repository:
  08_Package_Database/data
  13_Device_Specific_Profiles
"""

import argparse
import csv
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DATA_DIR = os.path.join(
    REPO_ROOT, "08_Package_Database", "data")
DEFAULT_PROFILE_DIR = os.path.join(
    REPO_ROOT, "13_Device_Specific_Profiles")

RISKS = (
    "SAFE_TO_REMOVE", "SAFE_TO_DISABLE", "ADVANCED_USERS_ONLY",
    "NOT_RECOMMENDED", "DO_NOT_REMOVE", "UNKNOWN")
STATUSES = ("VERIFIED", "PARTIALLY_VERIFIED", "UNVERIFIED", "UNKNOWN")
SOURCE_TYPES = ("community", "manufacturer", "code_analysis", "dump",
                "assessment", "unverified")
OPS = {"disable": "disable", "uninstall_keep_apk": "uninstall_keep_apk",
       "uninstall_purge_data": "uninstall_purge_data", "none": "none"}
STRONG_RISKS = ("SAFE_TO_REMOVE", "SAFE_TO_DISABLE")

PACKAGE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z0-9_]+)+$")

# Protected core set. The smartwatch adaptation of the CleanMyTV CORE_RE
# idea (02_Reference_Repository_Analysis). The rules are a functional
# record of 10_Safety_and_Dependencies/01_safety_analysis.md.
PROTECTED_PREFIXES = (
    "com.sec.", "com.sem.", "com.skms.", "com.ims.",
    "com.samsung.hidden.", "com.samsung.knox.", "com.wssyncmldm",
    "com.monotype.", "com.sk.", "com.samsung.sec.",
    "com.samsung.packageinstalleroverlay",
    "com.samsung.android.wearable.knox",
    "com.samsung.android.watch.watchface.emergency",
    "com.github.")
PROTECTED_EXACT = frozenset((
    "android",
    "com.android.shell", "com.android.phone", "com.android.settings",
    "com.android.systemui", "com.android.bluetooth", "com.android.vending",
    "com.android.sdksandbox", "com.android.location.fused",
    "com.google.android.gms", "com.google.android.gsf",
    "com.google.android.packageinstaller",
    "com.google.android.permissioncontroller",
    "com.google.android.ext.services", "com.google.android.ext.shared",
    "com.google.android.partnersetup", "com.google.android.tts",
    "com.google.android.apps.wearable.systemui",
    "com.google.android.apps.wearable.settings",
    "com.google.android.wearable.app",
    "com.google.android.wearable.healthservices",
    "com.google.android.wearable.batteryservices",
    "com.google.android.wearable.ambient",
    "com.google.android.wearable.frameworkpackagestubs",
    "com.google.android.wearable.overlay.home.merlot",
    "com.google.android.clockwork.oemsetup",
    "com.google.android.clockworkicons",
    "com.android.wearable.resources",
    "com.samsung.android.wearable.sysui",
    "com.samsung.android.wearable.setupwizard",
    "com.samsung.android.clientconnection",
    "com.samsung.android.networkstack",
    "com.samsung.android.app.telephonyui",
    "com.samsung.android.incallui",
    "com.samsung.android.app.routines",
    "com.samsung.android.smartgesture",
    "com.samsung.android.honeyboard",
    "com.samsung.android.watch.safety_assistance",
    "com.samsung.android.providers.contacts",
    "com.samsung.wear.contacts.sync",
    "com.samsung.android.app.esimkeystring",
    "com.samsung.euicc", "com.samsung.euicc.wmservice",
    "com.sec.android.app.samsungapps",
    "com.sec.imsservice",
    "com.wssyncmldm",
))
# CleanMyTV CORE_OK idea, adapted: removed-for-evidence providers.
PROTECTED_OK = frozenset(("com.android.providers.userdictionary",))


def is_protected(name):
    """Return True when the package sits in the protected core set."""
    if name in PROTECTED_OK:
        return False
    if name in PROTECTED_EXACT:
        return True
    for prefix in PROTECTED_PREFIXES:
        if name.startswith(prefix):
            return True
    if name.startswith("com.android.providers.") and name != \
            "com.android.providers.userdictionary":
        return True
    return False


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def data_files(data_dir):
    """Return sorted ((dataset id), path) tuples for all data files."""
    if not os.path.isdir(data_dir):
        return []
    out = []
    for name in sorted(os.listdir(data_dir)):
        if name.endswith(".json"):
            out.append((name[:-5], os.path.join(data_dir, name)))
    return out


def entry_with_defaults(dataset, entry):
    """Fill dataset-level defaults into one entry."""
    filled = dict(entry)
    for src, dst in (("default_risk", "risk"),
                     ("default_reversible", "reversible"),
                     ("default_restore_command", "restore_command"),
                     ("default_device_scope", "device_scope"),
                     ("default_software_scope", "software_scope")):
        if dst not in filled and src in dataset:
            filled[dst] = dataset[src]
    if "evidence" not in filled and "default_evidence" in dataset:
        filled["evidence"] = dict(dataset["default_evidence"])
    return filled


def check_entry(dataset_id, name, entry):
    """Return a list of problem strings for one entry."""
    problems = []
    fields = ("package", "app_name", "manufacturer", "category",
              "description", "dependencies", "needed_by", "risk",
              "reversible", "restore_command", "device_scope",
              "software_scope", "evidence")
    for field in fields:
        if field not in entry:
            problems.append("%s/%s: missing field %s" %
                            (dataset_id, name, field))
    if problems:
        return problems
    pkg = entry["package"]
    # Special case: "android" is the root system package (single component)
    if pkg != "android" and not PACKAGE_RE.match(pkg):
        problems.append("%s/%s: package name fails the format rule" %
                        (dataset_id, name))
        return problems
    if not PACKAGE_RE.match(name) and name != "android":
        problems.append("%s: JSON key %r is not a package name" %
                        (dataset_id, name))
    if pkg != name:
        problems.append("%s: JSON key %r does not match field package %r"
                        % (dataset_id, name, pkg))
    if entry["risk"] not in RISKS:
        problems.append("%s/%s: unknown risk %r" % (dataset_id, name,
                                                    entry["risk"]))
    if not isinstance(entry["dependencies"], list) or not isinstance(
            entry["needed_by"], list):
        problems.append("%s/%s: dependencies and needed_by are arrays" %
                        (dataset_id, name))
    for label in ("device_scope", "software_scope"):
        if not entry[label]:
            problems.append("%s/%s: %s is empty" % (dataset_id, name,
                                                    label))
    ev = entry["evidence"]
    for field in ("source", "source_type", "device_model", "firmware",
                  "testing_status", "verified_date", "side_effects"):
        if field not in ev:
            problems.append("%s/%s: evidence missing %s" %
                            (dataset_id, name, field))
            return problems
    if ev["source_type"] not in SOURCE_TYPES:
        problems.append("%s/%s: unknown source_type %r" %
                        (dataset_id, name, ev["source_type"]))
    if ev["testing_status"] not in STATUSES:
        problems.append("%s/%s: unknown testing_status %r" %
                        (dataset_id, name, ev["testing_status"]))
    if ev["source_type"] in (None, "assessment") and not ev.get("source"):
        if not ev.get("side_effects"):
            problems.append(
                "%s/%s: assessment entries need reasoning in "
                "side_effects" % (dataset_id, name))
    if entry["risk"] in STRONG_RISKS:
        if ev["testing_status"] in ("UNVERIFIED", "UNKNOWN"):
            problems.append(
                "%s/%s: risk %s needs PARTIALLY_VERIFIED or stronger, "
                "found %s" % (dataset_id, name, entry["risk"],
                              ev["testing_status"]))
        if not ev.get("source"):
            problems.append("%s/%s: risk %s needs a source" %
                            (dataset_id, name, entry["risk"]))
    return problems


def load_datasets(data_dir):
    """Load and validate all datasets. Returns (datasets, problems)."""
    problems = []
    datasets = []
    seen_ids = {}
    for path_id, path in data_files(data_dir):
        dataset = load_json(path)
        if dataset.get("schema") != "watchdb-1":
            problems.append("%s: schema is not watchdb-1" % path_id)
            continue
        dataset_id = dataset.get("dataset", path_id)
        if dataset_id in seen_ids:
            problems.append("%s: duplicate dataset id" % dataset_id)
        seen_ids[dataset_id] = path
        names = set()
        for name, entry in (dataset.get("packages") or {}).items():
            if name in names:
                problems.append("%s: duplicate package %r" %
                                (dataset_id, name))
            names.add(name)
            problems.extend(check_entry(dataset_id, name,
                                        entry_with_defaults(dataset,
                                                            entry)))
        datasets.append((dataset_id, dataset))
    return datasets, problems


def find_profile(profile_dir, profile_id):
    """Find a profile.json whose profile field matches profile_id."""
    if not os.path.isdir(profile_dir):
        return None
    for root, _dirs, files in os.walk(profile_dir):
        for fname in sorted(files):
            if fname != "profile.json":
                continue
            path = os.path.join(root, fname)
            data = load_json(path)
            if data.get("profile") == profile_id:
                return data
    return None


def check_profile(path, data, known_datasets):
    """Return a list of problem strings for one profile.json file."""
    problems = []
    profile_id = data.get("profile")
    if not profile_id:
        return ["%s: missing field profile" % path]
    folder = os.path.basename(os.path.dirname(path))
    if profile_id != folder:
        problems.append("%s: profile %r does not match the directory %r" %
                        (path, profile_id, folder))
    wanted = data.get("datasets")
    if wanted is None and data.get("dataset"):
        wanted = [data["dataset"]]
    if not isinstance(wanted, list) or not wanted:
        problems.append("%s: datasets must be a non-empty list" % path)
        wanted = []
    for dataset_id in wanted:
        if dataset_id not in known_datasets:
            problems.append("%s: dataset %r is not in the database" %
                            (path, dataset_id))
    op_map = data.get("operation_map")
    if not isinstance(op_map, dict):
        problems.append("%s: operation_map must be an object" % path)
        op_map = {}
    for risk, op in op_map.items():
        if risk not in RISKS:
            problems.append("%s: operation_map key %r is not a risk level" %
                            (path, risk))
        if op not in OPS:
            problems.append("%s: operation_map value %r is not an operation" %
                            (path, op))
    excluded = data.get("excluded")
    if excluded is not None and not isinstance(excluded, list):
        problems.append("%s: excluded must be a list" % path)
        excluded = []
    for name in excluded or []:
        if not isinstance(name, str) or not PACKAGE_RE.match(name):
            problems.append("%s: excluded value %r is not a package name" %
                            (path, name))
    for label in ("device_scope", "software_scope"):
        value = data.get(label)
        if not isinstance(value, list):
            problems.append("%s: %s must be a list" % (path, label))
        elif not value and op_map:
            problems.append("%s: %s is empty but operation_map is not" %
                            (path, label))
    matches = data.get("device_match")
    if matches is not None and not isinstance(matches, list):
        problems.append("%s: device_match must be a list" % path)
    elif op_map and not matches:
        problems.append("%s: device_match needs at least one model prefix "
                        "when operation_map is not empty" % path)
    else:
        for pattern in matches or []:
            if not isinstance(pattern, str) or not pattern.strip():
                problems.append("%s: device_match value %r is not a model "
                                "prefix" % (path, pattern))
    return problems


def load_profiles(profile_dir, known_datasets):
    """Return (profiles, problems) for every profile.json in profile_dir."""
    profiles = []
    problems = []
    if not os.path.isdir(profile_dir):
        return profiles, ["profiles: directory %r is not found" %
                          profile_dir]
    for root, _dirs, files in os.walk(profile_dir):
        for fname in sorted(files):
            if fname != "profile.json":
                continue
            path = os.path.join(root, fname)
            rel = os.path.relpath(path, os.path.dirname(profile_dir))
            try:
                data = load_json(path)
            except (ValueError, OSError) as exc:
                problems.append("%s: cannot read the file: %s" % (rel, exc))
                continue
            problems.extend(check_profile(rel, data, known_datasets))
            profiles.append(data)
    return profiles, problems


def entry_in_scope(entry, device_scope, software_scope):
    """Return (True, "") when an entry matches the profile scope.

    An empty profile scope matches every entry. An entry with an empty
    scope list is not filtered.
    """
    if device_scope:
        entry_devices = set(entry.get("device_scope") or [])
        if entry_devices and not (entry_devices & device_scope):
            return False, "outside the profile device scope"
    if software_scope:
        entry_software = set(entry.get("software_scope") or [])
        if entry_software and not (entry_software & software_scope):
            return False, "outside the profile software scope"
    return True, ""


def plan_commands(profile, datasets, op_direction):
    """Return (commands, skipped) for one profile.

    op_direction is "disable" for the forward plan, "restore" for the
    undo plan. Commands are printed for this repository's procedures.
    Entries outside the profile device or software scope are skipped.
    """
    wanted_ids = profile.get("datasets") or [profile["dataset"]]
    selected = []
    for wanted_dataset in wanted_ids:
        hit = None
        for dataset_id, dataset in datasets:
            if dataset_id == wanted_dataset:
                hit = dataset
        if hit is None:
            raise SystemExit("refused: dataset %r not found" %
                             wanted_dataset)
        selected.append(hit)
    op_map = profile.get("operation_map", {})
    excluded = set(profile.get("excluded", []))
    device_scope = set(profile.get("device_scope") or [])
    software_scope = set(profile.get("software_scope") or [])
    commands = []
    skipped = []
    for sel in selected:
        for name, raw in sorted((sel.get("packages") or {}).items()):
            entry = entry_with_defaults(sel, raw)
            risk = entry["risk"]
            op = op_map.get(risk, "none")
            if op not in OPS:
                skipped.append((name, "unknown operation %r" % op))
                continue
            if op == "none" or name in excluded:
                continue
            in_scope, reason = entry_in_scope(
                entry, device_scope, software_scope)
            if not in_scope:
                skipped.append((name, reason))
                continue
            if is_protected(name):
                skipped.append((name, "protected core package"))
                continue
            if op_direction == "disable":
                if op == "disable":
                    commands.append("pm disable-user --user 0 %s" % name)
                elif op == "uninstall_keep_apk":
                    commands.append("pm uninstall -k --user 0 %s" % name)
                elif op == "uninstall_purge_data":
                    commands.append("pm uninstall --user 0 %s" % name)
            else:
                if op == "disable":
                    commands.append("pm enable --user 0 %s" % name)
                else:
                    commands.append(
                        "pm install-existing --user 0 %s" % name)
    return commands, skipped


def read_dump(path):
    """Read a pm list packages dump file. Return list of package names."""
    names = []
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith("package:"):
                line = line[len("package:"):]
            line = line.split()[0] if not PACKAGE_RE.match(line) else line
            if PACKAGE_RE.match(line):
                names.append(line)
            else:
                # tolerate trailing comments and annotations
                token = line.split()[0] if line.split() else ""
                if PACKAGE_RE.match(token):
                    names.append(token)
    return names


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="swdb", description="package database tool")
    parser.add_argument("--data", default=DEFAULT_DATA_DIR)
    parser.add_argument("--profiles", default=DEFAULT_PROFILE_DIR)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate")
    sub.add_parser("stats")
    query = sub.add_parser("query")
    query.add_argument("package")
    packages = sub.add_parser("packages")
    packages.add_argument("--risk")
    packages.add_argument("--dataset")
    match = sub.add_parser("match")
    match.add_argument("dump_file")
    match.add_argument("--dataset")
    drift = sub.add_parser("drift")
    drift.add_argument("dump_file")
    drift.add_argument("--profile", required=True)
    plan = sub.add_parser("plan")
    plan.add_argument("--profile", required=True)
    plan.add_argument("--op", choices=("disable", "restore"),
                      default="disable")
    batch = sub.add_parser("export")
    batch.add_argument("path")
    args = parser.parse_args(argv)

    datasets, problems = load_datasets(args.data)
    known_datasets = {dataset_id for dataset_id, _dataset in datasets}
    profiles, profile_problems = load_profiles(args.profiles, known_datasets)
    problems = problems + profile_problems
    if problems and args.cmd != "validate":
        for problem in problems:
            sys.stderr.write("warning: %s\n" % problem)
    if problems and args.cmd == "validate":
        for problem in sorted(problems):
            print("PROBLEM: " + problem)
        print("Invalid: %d problem(s)" % len(problems))
        return 1
    if args.cmd == "validate":
        print("Valid: %d dataset(s), %d package(s), %d profile(s)." %
              (len(datasets),
               sum(len(d[1].get("packages", [])) for d in datasets),
               len(profiles)))
        return 0
    if args.cmd == "stats":
        for dataset_id, dataset in datasets:
            counts = {}
            for raw in (dataset.get("packages") or {}).values():
                risk = entry_with_defaults(dataset, raw)["risk"]
                counts[risk] = counts.get(risk, 0) + 1
            print("%-32s entries=%-4d %s" %
                  (dataset_id, len(dataset.get("packages") or {}),
                   " ".join("%s=%d" % kv for kv in sorted(
                       counts.items()))))
        return 0
    if args.cmd == "query":
        hits = []
        for dataset_id, dataset in datasets:
            if args.package in (dataset.get("packages") or {}):
                entry = entry_with_defaults(
                    dataset, dataset["packages"][args.package])
                hits.append((dataset_id, entry))
        if not hits:
            print("Unknown package: %s" % args.package)
            return 1
        prot = " (PROTECTED CORE)" if is_protected(args.package) else ""
        for dataset_id, entry in hits:
            ev = entry["evidence"]
            print("-- %s%s" % (dataset_id, prot))
            print("  risk: %s" % entry["risk"])
            print("  category: %s" % entry["category"])
            print("  device_scope: %s" % ", ".join(entry["device_scope"]))
            print("  software_scope: %s" %
                  ", ".join(entry["software_scope"]))
            print("  source_type: %s  testing_status: %s" %
                  (ev["source_type"], ev["testing_status"]))
            print("  side_effects: %s" % ev["side_effects"])
            print("  description: %s" %
                  entry["description"].replace("\n", " "))
        return 0
    if args.cmd == "packages":
        for dataset_id, dataset in datasets:
            if args.dataset and dataset_id != args.dataset:
                continue
            for name, raw in sorted((dataset.get("packages")
                                     or {}).items()):
                entry = entry_with_defaults(dataset, raw)
                if args.risk and entry["risk"] != args.risk:
                    continue
                flag = "!" if is_protected(name) else " "
                print("%s %-28s %-55s %s" %
                      (flag, dataset_id, name, entry["risk"]))
        return 0
    if args.cmd == "match":
        names = read_dump(args.dump_file)
        unknown, protected = [], []
        risk_by_name = {}
        for dataset_id, dataset in datasets:
            for name, raw in (dataset.get("packages") or {}).items():
                entry = entry_with_defaults(dataset, raw)
                if name not in risk_by_name or \
                        risk_by_name[name][0] == "UNKNOWN":
                    risk_by_name[name] = (entry["risk"], dataset_id)
        for name in names:
            if is_protected(name):
                protected.append(name)
            elif name not in risk_by_name:
                unknown.append(name)
        print("Read %d package name(s)." % len(names))
        if protected:
            print("Protected core (%d):" % len(protected))
            for name in protected:
                print("  %s" % name)
        if unknown:
            print("Not in the database (%d):" % len(unknown))
            for name in unknown:
                print("  %s" % name)
        print("Known entries: %d." %
              (len(names) - len(unknown) - len(protected)))
        return 0
    if args.cmd == "drift":
        profile = find_profile(args.profiles, args.profile)
        if profile is None:
            print("refused: profile %r not found" % args.profile)
            return 2
        forward, skipped = plan_commands(profile, datasets, "disable")
        names_in_dump = set(read_dump(args.dump_file))
        present_plans = [c for c in forward if c.split()[-1]
                         in names_in_dump]
        after_restore, _ = plan_commands(profile, datasets, "restore")
        print("Profile %s. Planned %d operation(s)."
              % (args.profile, len(forward)))
        print("Dump contains %d of the planned target package(s)."
              % len(present_plans))
        planned_targets = {c.split()[-1]: c for c in forward}
        drifted = []
        for command in sorted(planned_targets.values()):
            target = command.split()[-1]
            if target in names_in_dump:
                op = planned_targets[target]
                if op.startswith("pm disable-user"):
                    drifted.append("still enabled (plan: disable): %s"
                                   % target)
                else:
                    drifted.append("still installed (plan: remove): %s"
                                   % target)
        if drifted:
            print("Drift detected: %d" % len(drifted))
            for line in drifted:
                print("  %s" % line)
            return 1
        print("No drift between plan and dump.")
        return 0
    if args.cmd == "plan":
        profile = find_profile(args.profiles, args.profile)
        if profile is None:
            print("refused: profile %r not found" % args.profile)
            return 2
        commands, skipped = plan_commands(profile, datasets, args.op)
        print("# plan for profile %s op=%s" % (args.profile, args.op))
        print("# one command per line. Use one shell call each.")
        for command in commands:
            print(command)
        for name, reason in skipped:
            print("# skipped %s (%s)" % (name, reason))
        return 0
    if args.cmd == "export":
        with open(args.path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(("package", "dataset", "risk",
                             "manufacturer", "category", "source_type",
                             "testing_status"))
            count = 0
            for dataset_id, dataset in datasets:
                for name, raw in sorted((dataset.get("packages")
                                         or {}).items()):
                    entry = entry_with_defaults(dataset, raw)
                    ev = entry["evidence"]
                    writer.writerow((name, dataset_id, entry["risk"],
                                     entry["manufacturer"],
                                     entry["category"],
                                     ev["source_type"],
                                     ev["testing_status"]))
                    count += 1
        print("Wrote %d row(s) to %s" % (count, args.path))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
