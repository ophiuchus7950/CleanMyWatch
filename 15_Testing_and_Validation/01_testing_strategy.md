# Testing and Validation Strategy

## 1. Purpose

This document describes the validation layers for the project.
The tools are in `14_Automation_and_Scripting/tools/`.
The tests are in `15_Testing_and_Validation/tests/`.
Continuous integration (CI) runs the same layers on each push and
pull request.

## 2. Validation Layers

### 2.1 Database Validation

Tool `14_Automation_and_Scripting/tools/swdb.py validate` checks each
dataset and each profile. It rejects these conditions:
- A missing required field.
- A duplicate package name in one dataset.
- A `SAFE_TO_REMOVE` or `SAFE_TO_DISABLE` entry with a testing status
  below `PARTIALLY_VERIFIED`.
- A profile that names a missing dataset.
- A profile that uses an unknown operation.

The expected result for release 1.0 is
`Valid: 4 dataset(s), 207 package(s), 4 profile(s).`

### 2.2 Unit Tests

Run the tests from the test directory:

```bash
cd 15_Testing_and_Validation/tests
python3 -m unittest test_swdb test_sw -v
```

The suite has 37 tests. The tests do not need a watch.

`test_swdb.py` starts `swdb.py` as a subprocess against the real data
and profile directories. It covers validation, query, match, plan,
stats, export, and the protected package list.

`test_sw.py` imports `sw.py` as a module. It replaces
`subprocess.run` with a fake Android Debug Bridge (ADB) result. It
covers device detection, record paths, state changes, dry runs,
profile scope refusals, and protected package refusals.

### 2.3 Documentation Check

Tool `14_Automation_and_Scripting/tools/ste_check.py` checks the
ASD-STE100 subset. A banned word is a hard error. A long sentence or a
semicolon is a warning.

```bash
python3 14_Automation_and_Scripting/tools/ste_check.py [0-9][0-9]_* README.md AGENTS.md CONTRIBUTING.md SESSION_SUMMARY.md
```

The limits of the checker are in
`18_ASD_STE100_Terminology/03_checker_limitations.md`.

## 3. Continuous Integration

The workflow `.github/workflows/validate.yml` runs on each push and
pull request. It uses Python 3.12. It runs the three validation
layers above. A pull request must not fail this workflow.

## 4. Device Testing

The unit tests use a fake ADB. They do not prove behavior on a real
watch. Each package entry has a `testing_status` field. The values are
defined in `09_Package_Classification/02_evidence_labels.md`. Device
evidence must come from a real watch.

## 5. Limits

- Automated tests do not test the boot sequence, the radio, or the
  sensors. A user must test these functions on a device.
- The documentation checker is a subset of ASD-STE100. It does not
  replace a full review.

END OF DOCUMENT.
