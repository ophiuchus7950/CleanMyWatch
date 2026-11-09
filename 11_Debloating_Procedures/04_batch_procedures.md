# Batch Procedures

## 1 Purpose

Apply a debloating profile to disable or uninstall multiple packages in one operation.

## 2 Scope

Applies when using `sw.py apply --profile <id> --yes`.

## 3 Requirements

- Baseline state recorded (first record wins)
- Profile exists in `13_Device_Specific_Profiles/`
- `--yes` confirmation flag

## 4 Procedure

```bash
python 14_Automation_and_Scripting/tools/sw.py apply --profile samsung_galaxy_watch6_7 --yes
```

The tool:
1. Identifies the connected watch and refuses a profile mismatch
2. Loads the profile and its datasets
3. Plans commands via `swdb.py` (risk → operation map, profile scope filter)
4. Records baseline state (refuses if record exists)
5. Executes each command: one `pm` command per ADB shell call
6. Verifies via read-back after all commands

## 5 Dry Run

Preview without changes:

```bash
python 14_Automation_and_Scripting/tools/sw.py apply --profile samsung_galaxy_watch6_7 --dry-run --yes
```

Prints `DRY RUN: <command>` for each planned operation. Requires `--yes` even for dry run.

## 6 Verification

After the batch, the tool re-reads all three package states and compares to the plan. Any mismatch prints:

```
READ-BACK FAILED for: <package>, ...
Stop here. Do not run the command in a loop.
```

Exit code 1.

## 7 Skipped Packages

Packages are skipped (printed as comments) when:
- Risk level not in profile's `operation_map`
- Package in profile's `excluded` list
- Package outside the profile's `device_scope` or `software_scope`
- Package in protected core set

## 8 Safety Information

- One shell call per command — no chaining
- Protected packages never targeted
- Read-back verification mandatory
- First record wins — baseline state protected
