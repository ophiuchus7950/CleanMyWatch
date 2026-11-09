# Package Database Schema

## 1. Purpose

This document defines the data schema for all files in
`08_Package_Database/data/`. The schema adapts the field set used by the
reference databases to smartwatch needs. Tool `14_Automation_and_Scripting/tools/swdb.py validate`
checks every data file against this schema.

## 2. File Structure

Each data file is a JSON object:

```json
{
  "schema": "watchdb-1",
  "dataset": "knowledge_galaxy_watch",
  "description": "Classified Samsung Galaxy Watch packages",
  "packages": {
    "<package name>": { }
  }
}
```

Field rules:

| Field | Requirement |
|---|---|
| `schema` | Always `watchdb-1`. |
| `dataset` | Unique file identifier, lower case with underscores. |
| `description` | One sentence about the file content. |
| `packages` | JSON object keyed by package name. Each value is one entry, see §3. |
| `default_evidence` | Optional evidence object applied to entries with no own `evidence` field. Used by dump-based discovery datasets. |
| `default_risk`, `default_reversible`, `default_restore_command`, `default_device_scope`, `default_software_scope` | Optional defaults applied to entries that omit the matching field. Discovery datasets use them to stay compact. |

Available datasets in release 1.0:

| Dataset | Content |
|---|---|
| `discovery_galaxy_watch4` | Verified full package dump, Samsung Galaxy Watch 4. Classification `UNKNOWN` for function-unknown entries. |
| `knowledge_galaxy_watch` | Classified Samsung Galaxy Watch packages with debloat evidence. |
| `knowledge_google_wear_os` | Classified Google and AOSP core Wear OS packages. |
| `knowledge_third_party_watch` | Classified pre-installed third-party packages seen on watches. |

## 3. Package Entry Fields

| Field | Type | Requirement |
|---|---|---|
| `package` | string | Android package name. Format `[A-Za-z_][A-Za-z0-9_]*(.[A-Za-z0-9_]+)+` with two or more components. |
| `app_name` | string \| null | User-visible name when known. `null` when not established. |
| `manufacturer` | string | Package owner: `Samsung`, `Google`, `AOSP`, `Microsoft`, or a real name. |
| `category` | string | Function category. See `07_Package_Discovery/01_package_discovery.md` category list. |
| `description` | string | First sentence: identity. Later sentences: conditions, loss effects. Use ASD-STE100. |
| `dependencies` | array | Package names required by this package. Only confirmed dependencies. Never speculative. |
| `needed_by` | array | Confirmed packages that require this package. Optional reverse view. |
| `risk` | string | One of the six levels in `09_Package_Classification/01_classification_methodology.md`. |
| `reversible` | boolean | `true` when a restore command exists for the typical operation. |
| `restore_command` | string \| null | The restore command pattern with `{package}` placeholder, for example `pm enable --user 0 {package}`. |
| `device_scope` | array | Device models or codenames with evidence. Every entry field is scoped. |
| `software_scope` | array | OS or firmware scope with evidence, for example `wear_os_4` or `one_ui_watch_5`. |
| `evidence` | object | See §4. Required. |

## 4. Evidence Object

| Field | Type | Requirement |
|---|---|---|
| `source` | string \| null | URL or document path. `null` only when `source_type` is `assessment` with a model below. |
| `source_type` | string | One of `community`, `manufacturer`, `code_analysis`, `dump`, `assessment`, `unverified`. |
| `device_model` | string | Device model string with the evidence, for example `Galaxy Watch 4`. |
| `firmware` | string \| null | Firmware or OS string of the source, when known. |
| `testing_status` | string | One of `VERIFIED`, `PARTIALLY_VERIFIED`, `UNVERIFIED`, `UNKNOWN`. |
| `verified_date` | string \| null | ISO date of the recorded evidence, when known. |
| `side_effects` | string | Known or suspected side effects. Empty string means none were recorded. Never invent effects. |

Rules:

1. `assessment` entries state the reasoning basis in `side_effects`.
2. `dump` entries set `device_model` to the dumped model.
3. `UNVERIFIED` sources cannot support `SAFE_TO_REMOVE` or
   `SAFE_TO_DISABLE`.

## 5. Dataset Separation Rules

1. Discovery datasets (`dump` evidence, classification `UNKNOWN` or
   observation only) record what a device has installed.
2. Knowledge datasets carry classification and evidence.
3. A package can appear in a discovery dataset and a knowledge dataset.
   A package must not appear twice inside one dataset.
4. Data transformations go one direction: discovery → knowledge. Each
   knowledge entry cites its basis.
5. An entry applies to a profile only when its `device_scope` and
   `software_scope` intersect the profile scope. Keep both fields
   accurate. A profile plan never borrows evidence from another device.

## 6. Data Hygiene

1. JSON files use an indent of two spaces. Follow the contributor rules:
   no final newline spaces, sorted package keys inside each dataset.
2. Package names are the identity key. Record names exactly as printed
   by `pm list packages`.
3. Never add a package name that no recorded source shows.
4. Run `python 14_Automation_and_Scripting/tools/swdb.py validate` after every data edit.

## 7. Schema Limitations

1. The schema has no per-field device map. Scope is entry-level. This is
   sufficient for release 1.0 because verified evidence exists only for
   Samsung Galaxy Watch platforms.
2. Package version is recorded inside `evidence.firmware` as text when a
   source shows it. Component-level version tracking comes with the
   first per-build verification record.

## 8. References

1. `09_Package_Classification/01_classification_methodology.md`.
2. `09_Package_Classification/02_evidence_labels.md`.
3. `02_Reference_Repository_Analysis/03_preinstalled_lists_analysis.md`
   — the source schema this schema adapts.

END OF DOCUMENT.
