# Contributing

## 1 Purpose

This document defines contribution rules for the project.

## 2 Evidence-First Principle

Every package classification must have evidence:
- Source (URL or reference ID from `19_References/01_references.md`)
- Source type: community / manufacturer / code_analysis / dump / assessment / unverified
- Testing status: VERIFIED / PARTIALLY_VERIFIED / UNVERIFIED / UNKNOWN
- SAFE_TO_REMOVE and SAFE_TO_DISABLE require PARTIALLY_VERIFIED or stronger
- DO_NOT_REMOVE requires verified failure evidence or safety function

## 3 Automation Disclosure

Mass edits via scripts, LLM, or automated tools must be disclosed in the PR:
- Exact commands used (`sed`, `jq`, `python` script, etc.)
- Before/after diff
- Verification steps run

AI-generated edits without reproducible commands are not accepted.

## 4 Reference Repository Protection

Never modify files in `reference/`:
- `reference/cleanyourtv/`
- `reference/universal-android-debloater-next-generation/`
- `reference/universal-android-preinstalled-lists/`

These are read-only analysis sources.

## 5 Documentation Rules

- All docs must pass `python3 14_Automation_and_Scripting/tools/ste_check.py <path>` (no banned words)
- Follow ASD-STE100 structure (12 sections for procedures)
- Define abbreviations on first use
- Use approved terminology from `18_ASD_STE100_Terminology/01_approved_terminology.md`

## 6 Pre-Commit Checks

Run before submitting PR:

```bash
# Validate database
python3 14_Automation_and_Scripting/tools/swdb.py validate

# Run tests
python3 -m unittest 15_Testing_and_Validation.tests.test_swdb 15_Testing_and_Validation.tests.test_sw -v

# Check STE compliance
python3 14_Automation_and_Scripting/tools/ste_check.py 09_Package_Classification 10_Safety_and_Dependencies 11_Debloating_Procedures 12_Restoration_and_Recovery 16_Troubleshooting
```

## 7 Adding a New Device Profile

1. Create directory under `13_Device_Specific_Profiles/<profile_id>/`
2. Add `profile.json` with:
   - `profile` (matches directory name)
   - `datasets` (list of dataset IDs)
   - `operation_map` (risk → operation)
   - `device_scope`, `software_scope`
   - `description`
3. Run `python3 14_Automation_and_Scripting/tools/swdb.py validate`
4. Update `13_Device_Specific_Profiles/README.md`

## 8 Adding Package Data

1. Edit the appropriate dataset JSON in `08_Package_Database/data/`
2. Ensure all required fields present
3. Run `python3 14_Automation_and_Scripting/tools/swdb.py validate`
4. Evidence must be traceable to a source in `19_References/01_references.md`

## 9 Code Style

- Python: standard library only, no external dependencies
- Type hints optional but encouraged
- Functions documented with docstrings
- Exit codes: 0 = success, 1 = problem found, 2 = refused
