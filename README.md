# Watch Debloat Knowledge System

**A universal smartwatch debloating and package knowledge system.**

This repository helps users understand, classify, disable, and restore
pre-installed applications on Android-based smartwatches. It focuses on
Wear OS platforms. It documents platforms that do not support Android
package management, and it refuses to apply debloating operations there.

This project combines three proven methodologies:

| Methodology source | What this project adapts |
|---|---|
| CleanMyTV (Android TV) | Per-device profiles, state records, fail-closed safety gates, read-back verification |
| UAD Next Generation (Android phones) | Typed ADB command flows, package state model, package list format |
| Universal Android Pre-installed Lists | Package database schema, description grammar, evidence discipline |

The three reference repositories are analysed from a local, read-only
copy in `reference/`. The copies keep their original licences (MIT,
GPL-3.0, LGPL-3.0) and are not distributed with this repository. This
project never modifies their files.

## What this repository provides

1. **Reference analysis** (`02_Reference_Repository_Analysis/`) — analysis
   of each source repository, plus a comparative analysis with an
   adaptation decision for every feature.
2. **Platform architecture** (`03_Platform_Architecture/`) — Wear OS
   internals, non-Android platforms, and the platform compatibility matrix.
3. **Device compatibility** (`04_Device_Compatibility/`) — which devices
   are in scope and why other platforms are refused.
4. **Device identification** (`05_Device_Identification/`) — commands and
   interpretation rules for identifying a connected watch.
5. **ADB integration** (`06_ADB_Integration/`) — pairing, connection,
   and the verified command reference for watches.
6. **Package discovery** (`07_Package_Discovery/`) — how to enumerate
   packages and group them by function.
7. **Package database** (`08_Package_Database/`) — schema and data for
   verified Wear OS packages with risk classification and evidence.
8. **Classification methodology** (`09_Package_Classification/`) — risk
   levels, evidence labels, and the decision rules behind them.
9. **Safety and dependencies** (`10_Safety_and_Dependencies/`) — critical
   function analysis (Bluetooth, health sensors, payment, emergency).
10. **Debloating procedures** (`11_Debloating_Procedures/`) — disable,
    uninstall-for-current-user, and batch procedures with safety gates.
11. **Restoration and recovery** (`12_Restoration_and_Recovery/`) —
    restore commands, recovery records, and failure recovery.
12. **Device-specific profiles** (`13_Device_Specific_Profiles/`) —
    per-device profiles with documented software scope.
13. **Automation and scripting** (`14_Automation_and_Scripting/`) —
    working Python tools (`14_Automation_and_Scripting/tools/`) with no third-party dependencies.
14. **Testing and validation** (`15_Testing_and_Validation/`) — headless
    test suite plus the validation strategy.
15. **Troubleshooting** (`16_Troubleshooting/`) — symptom-indexed fixes.
16. **Technical documentation standards** (`17_Technical_Documentation/`).
17. **ASD-STE100 terminology** (`18_ASD_STE100_Terminology/`) — approved
    words, writing rules, and the STE checker configuration.
18. **References** (`19_References/`) — every cited source.
19. **Change history** (`20_Change_History/`).

## Quick start

1. Read the safety information first:
   see `11_Debloating_Procedures/01_preparation.md`.
2. Connect your watch with ADB:
   see `06_ADB_Integration/01_adb_setup_and_pairing.md`.
3. Identify your watch model:
   run `python3 14_Automation_and_Scripting/tools/sw.py identify`.
4. Enumerate packages:
   run `python3 14_Automation_and_Scripting/tools/sw.py packages --out packages.txt`.
5. Compare with the database:
   run `python3 14_Automation_and_Scripting/tools/swdb.py match packages.txt`.

> **Warning:** The debloating procedures change software component state
> on your watch. Wrong operations can stop the watch from starting
> correctly. Records made before the first change are the only reliable
> undo path. Read `11_Debloating_Procedures/01_preparation.md` and
> `12_Restoration_and_Recovery/01_restoration_procedure.md` before you
> change anything.

## Status and evidence policy

- Verified package evidence in release 1.0 covers **Samsung Galaxy Watch
  4** (143-package discovery dump, classifications `UNKNOWN`) and
  **Samsung Galaxy Watch 6/7** (community debloat evidence). See
  `08_Package_Database/`.
- Only the `samsung_galaxy_watch6_7` profile produces debloat operations.
  The `samsung_galaxy_watch4` and `samsung_galaxy_watch8` profiles are
  guard profiles until device-scoped removal evidence exists.
- Package names for other manufacturers are **not** in the database until
  a source package dump exists. See the evidence labels in
  `09_Package_Classification/02_evidence_labels.md`.
- Every recommendation carries: source, device model, software scope,
  testing status, and known side effects. See `08_Package_Database/01_database_schema.md`.

## Development and validation

The tools use only the Python standard library (Python 3.10 or newer).
Run these checks before a pull request:

```bash
python3 14_Automation_and_Scripting/tools/swdb.py validate
cd 15_Testing_and_Validation/tests
python3 -m unittest test_swdb test_sw -v
cd ../..
python3 14_Automation_and_Scripting/tools/ste_check.py [0-9][0-9]_* README.md AGENTS.md CONTRIBUTING.md SESSION_SUMMARY.md
```

GitHub Actions runs the same checks on each push and pull request.
The `reference/` directory is a local, read-only analysis source. It is
not tracked.

## Licence

MIT. See `LICENSE`. The reference repositories in `reference/` keep their
original licences (MIT, GPL-3.0, LGPL-3.0).

END OF DOCUMENT.
