# Evidence Labels

## 1. Purpose

This document defines the evidence labels for database entries. Every
entry records a `testing_status` label. The labels show how strong the
evidence is. Every procedure note uses the same labels.

## 2. Label Definitions

| Label | Meaning |
|---|---|
| `VERIFIED` | Tested on the specified device model and software version. The test result is recorded with a date and tester. |
| `PARTIALLY_VERIFIED` | Community or manufacturer evidence exists for the specified device model or software scope. The evidence has no controlled test record, or it covers a slightly different build. |
| `UNVERIFIED` | A claim exists without repeatable evidence. Do not use as the only basis for a safety decision. |
| `UNKNOWN` | No evidence was examined. |

## 3. Evidence Order

A claim moves up the scale only when new evidence supports it. A claim
stays at its level when evidence conflicts. When evidence conflicts,
the database keeps the more conservative risk level and records the
conflict in `evidence.side_effects`.

## 4. Source Types

| `source_type` | Meaning |
|---|---|
| `community` | Public user report or forum thread. Record the URL. |
| `manufacturer` | Document from the manufacturer. Record the URL. |
| `code_analysis` | Function derived from package name, manifest role, or framework analysis. Say so in `evidence.side_effects`. |
| `dump` | Direct package enumeration from a device. Record the device model. |
| `assessment` | Engineer reasoning based on combined evidence. Say so explicitly. |
| `unverified` | Claim without confirmable source. Treat as `UNKNOWN` data. |

## 5. Combination Rules

Risk level and testing status combine:

1. `SAFE_TO_REMOVE` and `SAFE_TO_DISABLE` need `PARTIALLY_VERIFIED` or
   stronger.
2. `ADVANCED_USERS_ONLY` needs at least `PARTIALLY_VERIFIED` for the
   risk reason, or an explicit function-analysis basis.
3. `DO_NOT_REMOVE` can cite `code_analysis` or `dump` evidence alone,
   because the decision protects the device, not the cleanup.
4. `UNKNOWN` matches any `testing_status`, including `UNKNOWN`.

## 6. Honesty Rules

1. Never invent a source, date, or device model.
2. Copy package names only from a recorded dump or source list.
3. Write "Function not established" when the function is not known.
4. Record negative results too. A report of battery drain is evidence
   and must stay in `side_effects`.
5. Put uncertain information in the limitations section, not in
   classification fields.

## 7. Verification

Tool `14_Automation_and_Scripting/tools/swdb.py validate` rejects entries that break rules 3, 4, 5
in `09_Package_Classification/01_classification_methodology.md` and the
combination rules above. Run it in CI. See
`15_Testing_and_Validation/01_testing_strategy.md`.

END OF DOCUMENT.
