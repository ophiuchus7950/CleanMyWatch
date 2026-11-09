# Disable Procedure

## 1 Purpose

Disable a package for the current user without removing it.

## 2 Scope

Applies to packages classified `SAFE_TO_DISABLE`.

## 3 Requirements

- Baseline state recorded (`sw.py record`)
- Package not in protected core set
- `--yes` confirmation flag

## 4 Procedure

### Single Package

```bash
python 14_Automation_and_Scripting/tools/sw.py disable com.example.package --yes
```

### Batch (via profile)

```bash
python 14_Automation_and_Scripting/tools/sw.py apply --profile samsung_galaxy_watch6_7 --yes
```

## 5 Command Executed

```bash
pm disable-user --user 0 <package>
```

One command per ADB shell call.

## 6 Verification

After the command, the tool re-reads the enabled/disabled sets:

```bash
pm list packages -s -e --user 0
pm list packages -s -d --user 0
```

The target package must appear in the disabled set. If not, the tool prints `READ-BACK FAILED` and exits 1 with:

> Stop here. Do not run the command in a loop.

## 7 Reversibility

Disable is fully reversible:

```bash
pm enable --user 0 <package>
```

No data loss. The package remains installed.

## 8 Safety Information

- Protected packages are refused before the command runs
- Read-back verification is mandatory
- Do not retry on verification failure — investigate the watch state first
