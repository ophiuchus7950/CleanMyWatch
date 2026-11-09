# Automation and Scripting Tool Guide

This directory contains three Python tools for the smartwatch debloating knowledge system:

- `swdb.py` — Package database and profile tool (offline, file-only)
- `sw.py` — Watch ADB client (device operations)
- `ste_check.py` — ASD-STE100 documentation checker

All tools use only the Python standard library.

---

## swdb.py — Package Database Tool

**Purpose:** Validate, query, and plan operations on the package database without a device connection.

### Environment

No environment variables required.

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Command ran successfully |
| 1 | Command ran and found a problem (validation failure, unknown package, drift detected) |
| 2 | Command refused before doing anything (missing profile, missing dataset, invalid arguments) |

### Commands

#### `validate`
```bash
python 14_Automation_and_Scripting/tools/swdb.py validate [--data DIR]
```
Loads all datasets from `DIR` (default: `08_Package_Database/data`) and all profiles from `--profiles DIR` (default: `13_Device_Specific_Profiles`). Validates schema, package format, risk levels, evidence fields, profile fields, and cross-references. Prints problem list and summary. Exit 1 on any problem.

#### `stats`
```bash
python 14_Automation_and_Scripting/tools/swdb.py stats [--data DIR]
```
Prints per-dataset entry counts and risk-level breakdowns.

#### `query PACKAGE`
```bash
python 14_Automation_and_Scripting/tools/swdb.py query com.example.package [--data DIR]
```
Shows all dataset entries matching the package name, with risk, category, scopes, evidence, and description.

#### `packages`
```bash
python 14_Automation_and_Scripting/tools/swdb.py packages [--data DIR] [--risk LEVEL] [--dataset ID]
```
Lists all packages, optionally filtered by risk level or dataset. Protected core packages are marked with `!`.

#### `match DUMP_FILE`
```bash
python 14_Automation_and_Scripting/tools/swdb.py match dump.txt [--data DIR] [--dataset ID]
```
Reads a `pm list packages` dump file (one package per line, `package:` prefix tolerated) and reports:
- Protected core packages found in the dump
- Packages not in any dataset (unknown)
- Known entry count

#### `drift DUMP_FILE --profile ID`
```bash
python 14_Automation_and_Scripting/tools/swdb.py drift dump.txt --profile samsung_galaxy_watch6_7 [--profiles DIR] [--data DIR]
```
Compares the planned disable operations for a profile against a device dump. Reports packages that are still enabled/installed on the device (drift). Exit 1 if drift detected.

#### `plan --profile ID [--op disable|restore]`
```bash
python 14_Automation_and_Scripting/tools/swdb.py plan --profile samsung_galaxy_watch6_7 [--op disable]
```
Prints the ADB commands for the profile's operation map. One command per line, intended for one shell call each. Skipped packages (protected, excluded, outside the profile scope, no operation mapped) are listed as comments.

#### `export PATH`
```bash
python 14_Automation_and_Scripting/tools/swdb.py export packages.csv [--data DIR]
```
Exports all packages to CSV with columns: package, dataset, risk, manufacturer, category, source_type, testing_status.

---

## sw.py — Watch ADB Client

**Purpose:** Connect to a Wear OS watch via ADB, identify it, record its package state, and apply debloating operations from a profile.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SW_ADB` | `adb` | Path to the ADB binary. |
| `SW_SERIAL` | (none) | If set, use this ADB serial instead of auto-detecting a single device. |
| `SW_ALLOW_DEVICE_MISMATCH` | (none) | Set to `1` to bypass the profile device and software scope check. The tool prints a warning. Use only with a verified reason. |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Command ran successfully |
| 1 | Command ran but verification failed (READ-BACK FAILED) |
| 2 | Command refused before doing anything (no device, multiple devices, protected target, missing --yes, etc.) |

### Prerequisites

1. **ADB ≥ 30.0.0** (required for pairing code flow on Wear OS 3+).
2. **Wireless debugging enabled on the watch** (Developer options → Wireless debugging → Pair with pairing code).
3. **Watch and computer on the same Wi-Fi network**, AP/client isolation OFF.
4. **ADB pairing completed**: `adb pair <ip:port>` then `adb connect <ip:port>`.

### Device Identification

The watch must appear as exactly one device in `adb devices` (status `device`). If multiple devices are connected, set `SW_SERIAL` to the watch's serial.

```bash
# Auto-detect
python 14_Automation_and_Scripting/tools/sw.py identify

# Or specify serial
SW_SERIAL=192.168.1.100:5555 python 14_Automation_and_Scripting/tools/sw.py identify
```

Output includes brand, model, device codename, Android SDK, and Wear OS label (W3–W6).

### Record Package State (Backup)

**Always run this before any debloating operation.**

```bash
python 14_Automation_and_Scripting/tools/sw.py record [--out PATH]
```

Creates `sw-record-<serial-sha1-8>.json` containing:
- `version: 1`
- `created` (ISO timestamp)
- `serial`
- `identity` (brand, model, device, manufacturer)
- `wear_os_label` (W3/W4/W5/W5.1/W6)
- `user: 0`
- `enabled[]`, `disabled[]`, `uninstalled_for_user[]` package lists

**First record wins:** If a record for this serial already exists, the tool refuses to overwrite it (exit 2). This protects the pre-debloat state. Use `--out` to write to a different path if needed.

### List Packages

```bash
python 14_Automation_and_Scripting/tools/sw.py packages [--state enabled|disabled|uninstalled] [--out PATH]
```

Enumerates packages on the watch (system packages only, `pm list packages -s`). Output mirrors the record structure.

### Apply Profile (Debloat)

```bash
python 14_Automation_and_Scripting/tools/sw.py apply --profile samsung_galaxy_watch6_7 --yes [--dry-run]
```

1. Identifies the connected watch.
2. **Checks the profile scope.** Refuses when `ro.product.model` or `ro.product.device` is not in the profile `device_match` list, or when the Wear OS version is not in `software_scope`. Set `SW_ALLOW_DEVICE_MISMATCH=1` to bypass with a warning.
3. Loads the profile and its datasets, and plans commands (risk → operation map, profile scope filter).
4. **Records package state first** (refuses if record exists — first record wins).
5. For each command: refuses protected core packages, runs **one `pm` command per ADB shell call** (no chaining).
6. **Verifies (READ-BACK):** Re-fetches enabled/disabled/uninstalled sets and diffs against the plan.
   - If any target package did not change state: prints `READ-BACK FAILED` table and exits 1 with message: `Stop here. Do not run the command in a loop.`
7. On success: prints verification table, exits 0.

**`--dry-run`** prints the commands that would run (lines prefixed `DRY RUN:`) and `DRY RUN. No changes will be made.` It prints the device identity and runs the profile scope check, but it does not touch the watch. It still requires `--yes` (this is intentional: dry-run is a preview of a confirmed operation).

**Profile scope in plans:** `swdb.py plan` skips an entry when its `device_scope` or `software_scope` does not intersect the profile scope. In release 1.0 every verified debloat entry is scoped to Galaxy Watch 6/7. The `samsung_galaxy_watch4` profile therefore prints only skip comments.

### Restore from Record

```bash
python 14_Automation_and_Scripting/tools/sw.py restore --record sw-record-<serial-sha1-8>.json [--yes]
```

Restores the package state recorded in the given record file:
- For each package in `disabled[]`: runs `pm enable --user 0 <pkg>`
- For each package in `uninstalled_for_user[]`: runs `pm install-existing --user 0 <pkg>`

**Warning:** Packages that were already disabled by the user before the record was taken will be re-enabled too. Data for packages uninstalled *without* `-k` (purge data) is not restored by `install-existing` — only the APK is reinstated.

### Single Command (Read-Only)

```bash
python 14_Automation_and_Scripting/tools/sw.py one "getprop ro.build.version.sdk"
```

Runs a single read-only ADB shell command. Allowed prefixes:
- `getprop`
- `dumpsys`
- `pm list`
- `pm path`

Any other command is refused (exit 2). No state recording or verification is performed.

### Manual Disable/Enable/Uninstall

```bash
# Disable a package
python 14_Automation_and_Scripting/tools/sw.py disable com.example.package --yes

# Enable a package
python 14_Automation_and_Scripting/tools/sw.py enable com.example.package --yes

# Uninstall keeping APK and data (-k)
python 14_Automation_and_Scripting/tools/sw.py uninstall-keep com.example.package --yes

# Uninstall and purge data (no -k)
python 14_Automation_and_Scripting/tools/sw.py uninstall-purge com.example.package --yes
```

Each command:
1. Refuses if the package is in the protected core set.
2. Records state first (first-record-wins).
3. Runs the single `pm` command.
4. Verifies via READ-BACK.
5. Exits 1 on verification failure with `Stop here. Do not run the command in a loop.`

---

## Divergence Notes

### Disable vs. UAD Trio

UAD-ng's disable sequence is three commands:
```
pm disable-user --user N <pkg>
am force-stop --user N <pkg>
pm clear --user N <pkg>
```

**This project deliberately uses only `pm disable-user --user 0 <pkg>`.**

Rationale: The three-command sequence clears app data and stops the process, which is appropriate for a "disable and clean" operation on phones. For watches, we prefer to **preserve user data** so that re-enabling (`pm enable`) restores the app to its exact prior state. The single `pm disable-user` is sufficient to stop the package from running and is fully reversible without data loss.

### Restore of Purged-Data Packages

If a package was uninstalled with `uninstall-purge` (no `-k`), `pm install-existing` restores the APK but **user data is permanently lost**. This is documented in the `restore` command warning. The profile operation map should use `uninstall_keep_apk` (maps to `pm uninstall -k`) for `SAFE_TO_REMOVE` by default.

### No Launcher/Home Surface Management

CleanMyTV manages the Android TV home activity via `cmd package set-home-activity`. Wear OS does not expose a user-replaceable home surface in the same way (watchface selection is a system setting, comanaged by the companion app). No equivalent operation is implemented.

### Record First, Then Act

Both `swdb.py plan` and `sw.py apply` use the same plan function and the same profile scope filter. Only `sw.py apply` records the device state, and it records state before the first change.

---

## Workflow Example

```bash
# 1. Pair and connect (one-time)
adb pair 192.168.1.100:5555
adb connect 192.168.1.100:5555

# 2. Identify the watch
python 14_Automation_and_Scripting/tools/sw.py identify

# 3. Record baseline state (CRITICAL)
python 14_Automation_and_Scripting/tools/sw.py record

# 4. Preview the plan
python 14_Automation_and_Scripting/tools/swdb.py plan --profile samsung_galaxy_watch6_7

# 5. Apply with confirmation
python 14_Automation_and_Scripting/tools/sw.py apply --profile samsung_galaxy_watch6_7 --yes

# 6. If something goes wrong, restore
python 14_Automation_and_Scripting/tools/sw.py restore --record sw-record-<serial-sha1-8>.json --yes

# 7. Check for drift after OTA updates
python 14_Automation_and_Scripting/tools/sw.py packages --out current_dump.txt
python 14_Automation_and_Scripting/tools/swdb.py drift current_dump.txt --profile samsung_galaxy_watch6_7
```

---

## Safety Rules (Enforced by Tools)

1. **Protected core packages are never targeted** — `swdb.py` and `sw.py` both check `is_protected()` before any operation.
2. **One `pm` command per shell call** — No command chaining (`;` or `&&`). Each operation is a separate ADB call.
3. **READ-BACK verification** — After every batch, the device state is re-read and compared to the plan. Mismatch = hard stop.
4. **First record wins** — The baseline record is never overwritten. Subsequent runs in the same session print "existing record kept" and continue.
5. **Explicit `--yes` required** — No destructive operation runs without `--yes`. Dry-run also requires `--yes` (confirmed preview).
6. **No root, no `pm uninstall` without `-k` by default** — System APKs stay on the system partition. `uninstall_purge_data` exists but is not the default for `SAFE_TO_REMOVE`.
