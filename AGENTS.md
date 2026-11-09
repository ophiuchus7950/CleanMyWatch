# AGENTS.md

## Job Routing

| You are asked to | Follow |
|------------------|--------|
| Clean up a watch | 11_Debloating_Procedures/01_preparation.md → 02_disable_procedure.md / 03_uninstall_procedure.md / 04_batch_procedures.md |
| Restore a watch | 12_Restoration_and_Recovery/01_restoration_procedure.md |
| Check drift after OTA | 16_Troubleshooting/01_troubleshooting.md (drift section) |
| Add a device profile | 13_Device_Specific_Profiles/README.md + CONTRIBUTING.md |
| Add package data | CONTRIBUTING.md §8 |
| Change the repo | This file (repo map below) |

## Repo Map

| Path | Purpose |
|------|---------|
| `01_Project_Overview/` | Project overview (ASD-STE100) |
| `02_Reference_Repository_Analysis/` | Analysis of 3 reference repos (read-only) |
| `03_Platform_Architecture/` | Wear OS + non-Android platform docs |
| `04_Device_Compatibility/` | Supported devices + decision rules |
| `05_Device_Identification/` | Device identification procedure |
| `06_ADB_Integration/` | ADB setup, pairing, command reference |
| `07_Package_Discovery/` | Package enumeration procedure |
| `08_Package_Database/` | Database schema + JSON data files |
| `09_Package_Classification/` | Risk levels + evidence labels |
| `10_Safety_and_Dependencies/` | Protected core + failure evidence |
| `11_Debloating_Procedures/` | Preparation, disable, uninstall, batch |
| `12_Restoration_and_Recovery/` | Restore + recovery procedures |
| `13_Device_Specific_Profiles/` | Device profiles (profile.json) |
| `14_Automation_and_Scripting/tools/` | `swdb.py`, `sw.py`, `ste_check.py` |
| `15_Testing_and_Validation/tests/` | Unit tests |
| `16_Troubleshooting/` | Symptom → cause → fix |
| `17_Technical_Documentation/` | Documentation standards |
| `18_ASD_STE100_Terminology/` | Approved terms, writing rules, checker limits |
| `19_References/` | All external source URLs |
| `20_Change_History/` | Version history |
| `reference/` | Read-only reference repos (NEVER MODIFY) |

## Hard Rules

1. Never modify `reference/` — read-only analysis sources
2. Evidence first — no classification without source + testing status
3. SAFE_TO_* requires PARTIALLY_VERIFIED+ — enforced by `swdb.py validate`
4. First record wins — `sw.py record` refuses overwrite
5. Protected core never targeted — enforced by `is_protected()` in both tools
6. One shell call per command — no chaining in `sw.py`
7. Read-back verification mandatory — `sw.py` exits 1 on mismatch
8. `--yes` required for mutations — no silent destructive operations
9. STE compliance — `ste_check.py` must pass (no banned words)
10. Tests must pass — `python3 -m unittest ...` before PR
11. Profile scope is enforced — plans skip entries outside the profile scope; `apply` refuses a watch outside `device_match` or `software_scope`

## Before PR Checklist

- [ ] `python3 14_Automation_and_Scripting/tools/swdb.py validate` passes
- [ ] `python3 -m unittest 15_Testing_and_Validation.tests.test_swdb 15_Testing_and_Validation.tests.test_sw -v` passes
- [ ] `python3 14_Automation_and_Scripting/tools/ste_check.py <changed_docs>` passes (no errors)
- [ ] No files in `reference/` modified
- [ ] New packages have evidence + testing status
- [ ] Abbreviations defined on first use in docs
