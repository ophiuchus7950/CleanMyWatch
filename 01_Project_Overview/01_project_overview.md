# Project Overview

## 1 Purpose

This document describes the Universal Smartwatch Debloating and Package Knowledge System. The system helps users identify, analyse, classify, disable, and restore pre-installed applications on Android-based smartwatches.

## 2 Scope

The system covers Wear OS 3 through 6 devices including Samsung Galaxy Watch series, Google Pixel Watch series, and other Android-based watch implementations. Non-Android platforms (watchOS, Tizen, Garmin, Fitbit, Zepp OS, LiteOS) are documented for compatibility reference only. No debloating procedures apply to non-Android platforms.

## 3 Requirements

- ADB version 30.0.0 or newer
- Python 3.10 or newer (standard library only)
- Wear OS device with wireless debugging enabled
- Computer on the same Wi-Fi network as the watch (AP isolation off)

## 4 Definitions

| Term | Meaning |
|------|---------|
| package | Android application package identified by reverse-DNS name |
| debloat | Disable or uninstall a package for the current user only |
| restore | Return a package to its pre-debloat state |
| protected core | Package set that must never be targeted |
| risk level | Classification from SAFE_TO_REMOVE to DO_NOT_REMOVE |

## 5 System Description

The system has three main components:

1. **Package Database** (`08_Package_Database/`) — structured JSON datasets with package metadata, risk classifications, and evidence
2. **Debloating Engine** (`14_Automation_and_Scripting/tools/sw.py`) — ADB client that records state, applies operations, and verifies results
3. **Planning Tool** (`14_Automation_and_Scripting/tools/swdb.py`) — offline database validator and operation planner

Device-specific profiles (`13_Device_Specific_Profiles/`) map database datasets to watch models and define which risk levels map to which operations.

## 6 Operating Conditions

- Watch must be paired via ADB wireless debugging (pairing code flow)
- Exactly one watch connected to ADB at a time
- Battery above 30% recommended
- Wireless ADB left on drains battery; disable after use

## 7 Safety Information

- Never run unverified removal commands
- Always record state before the first change (first record wins)
- Protected core packages are refused automatically
- Read-back verification runs after every batch
- Stop on verification failure — do not retry in a loop
- OTA updates may restore debloated packages

## 8 Procedures

See `11_Debloating_Procedures/` for preparation, disable, uninstall, and batch procedures. See `12_Restoration_and_Recovery/` for restore and recovery.

## 9 Expected Result

A watch with user-selected packages disabled or uninstalled (for current user only), with a verified record enabling full restore.

## 10 Verification

Run `python 14_Automation_and_Scripting/tools/swdb.py validate` to validate the database. Run `python 14_Automation_and_Scripting/tools/sw.py identify` to confirm device connection. Run `python 14_Automation_and_Scripting/tools/swdb.py drift <dump> --profile <id>` to check for post-OTA drift.

## 11 Troubleshooting

See `16_Troubleshooting/01_troubleshooting.md`.

## 12 References

See `19_References/01_references.md`.
