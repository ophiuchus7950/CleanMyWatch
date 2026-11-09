# Preparation Procedure

## 1 Purpose

Prepare the watch and computer for a debloating operation.

## 2 Scope

Applies to all debloating operations (disable, uninstall, batch).

## 3 Requirements

- ADB 30.0.0+ installed
- Python 3.10+
- Watch paired via wireless debugging
- Computer and watch on same Wi-Fi, AP isolation off
- Watch battery > 30%

## 4 Procedure

1. **Verify ADB connection**
   ```bash
   adb devices
   # One device with state "device"
   ```

2. **Identify the watch**
   ```bash
   python 14_Automation_and_Scripting/tools/sw.py identify
   # Confirms brand, model, SDK, Wear OS label
   ```

3. **Record baseline state (CRITICAL)**
   ```bash
   python 14_Automation_and_Scripting/tools/sw.py record
   # Creates sw-record-<serial-sha1-8>.json
   # First record wins — refuses to overwrite
   ```

4. **Review the plan**
   ```bash
   python 14_Automation_and_Scripting/tools/swdb.py plan --profile samsung_galaxy_watch6_7
   # Shows commands that will run
   ```

## 5 Expected Result

- Device identified and connected
- Baseline state recorded
- Plan reviewed and understood

## 6 Safety Information

- Never skip the record step — it enables full restore
- The record captures enabled, disabled, and uninstalled-for-user packages
- Protected core packages are never targeted
- If `record` refuses (file exists), the previous record is kept

## 7 Troubleshooting

- `no connected device` — pair and connect the watch first
- `several devices are connected` — set `SW_SERIAL`
- `record exists already` — first record wins; use `--out` for a new path
