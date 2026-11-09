# Restoration Procedure

## 1 Purpose

Restore packages to their pre-debloat state using a recorded state file.

## 2 Scope

Applies to any previously recorded state file (`sw-record-*.json`).

## 3 Requirements

- State record file from a previous `record` or `apply` operation
- Watch connected via ADB
- `--yes` confirmation flag

## 4 Procedure

```bash
python 14_Automation_and_Scripting/tools/sw.py restore --record sw-record-<serial-sha1-8>.json --yes
```

The tool:
1. Loads the state record
2. For each package in `disabled[]`: runs `pm enable --user 0 <pkg>`
3. For each package in `uninstalled_for_user[]`: runs `pm install-existing --user 0 <pkg>`
6. Verifies via read-back

## 5 Warning

> Packages that were already disabled or uninstalled before the record are restored to that state too.

This means if a package was already disabled by the user before the baseline record, it will be re-enabled during restore.

## 6 Data Loss Note

- `uninstall-keep` (`-k`): data preserved, `pm install-existing` restores fully
- `uninstall-purge` (no `-k`): user data deleted, `pm install-existing` restores APK only

## 7 Verification

Read-back checks that restored packages are in the enabled set.

## 8 Safety Information

- Restore only works with a valid state record
- No automatic backup of the current state before restore
- Run `record` before restore if you want to preserve the current state
