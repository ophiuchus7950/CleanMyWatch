# Package Classification Methodology

## 1. Purpose

This document defines how the repository classifies packages. Every
package entry in `08_Package_Database/data/` uses these rules. The rules
give one meaning to each risk level. The rules make classifications
traceable to evidence.

## 2. Scope

The methodology applies to Android-based smartwatches with a working
Android package manager. Compare the platform compatibility matrix in
`03_Platform_Architecture/03_platform_compatibility_matrix.md`. Packages
on platforms without a package manager get no classification.

## 3. Requirements

1. Classify a package only when evidence exists.
2. Never classify a package as safe without sufficient evidence.
3. Record the evidence source, device model, and software scope for
   every classification.
4. Prefer the lowest-risk classification when evidence is incomplete.
5. Use the evidence labels in
   `09_Package_Classification/02_evidence_labels.md`.

## 4. Risk Classification Levels

| Level | Meaning | Typical use |
|---|---|---|
| `SAFE_TO_REMOVE` | Community or manufacturer evidence shows removal without device failure. The function is optional or replaceable. | Standalone utility apps: timer, stopwatch, compass |
| `SAFE_TO_DISABLE` | Community or manufacturer evidence shows disabling without device failure. The function stays installed and can return without restore commands. | Voice assistant services, transfer services |
| `ADVANCED_USERS_ONLY` | Removal or disabling can break a minor or major function. Users must accept data loss, conditional operation, or manual recovery. | Keyboard, health app with stored data, device-transfer tools |
| `NOT_RECOMMENDED` | No verified benefit, or verified reports show negative effects such as battery drain or function loss. | Backup and sync cluster, media controller |
| `DO_NOT_REMOVE` | Evidence or function analysis shows device failure, safety impact, or core system role. | System UI, Bluetooth, health sensor services, payment |
| `UNKNOWN` | Insufficient evidence. Function not established or not tested. | Most function-unknown infrastructure components |

## 5. Decision Procedure

Classify each package in order. Stop at the first rule that matches.

1. **Core system.** The package name is in the protected core set
   (`10_Safety_and_Dependencies/01_safety_analysis.md`). Classify
   `DO_NOT_REMOVE`.
2. **Verified failure evidence.** A community or manufacturer source
   reports device failure from removal or disabling. Classify
   `DO_NOT_REMOVE`.
3. **Verified safety function.** The package carries an emergency,
   safety, security, authentication, or payment function (module E list
   in `10_Safety_and_Dependencies/01_safety_analysis.md`). Classify
   `DO_NOT_REMOVE` or `NOT_RECOMMENDED`, never lower.
4. **Verified removal evidence.** A source reports removal or disabling
   without device failure. Classify from the observed operation:
   - Removing replaced or deleted app data. `ADVANCED_USERS_ONLY` when
     the data loss matters (health data, paired settings).
   - `SAFE_TO_REMOVE` when the function is optional.
   - `SAFE_TO_DISABLE` when the source disables instead of removing.
5. **Verified negative side effects.** A source reports problems after
   removal, for example battery drain or retry loops, but not device
   failure. Classify `NOT_RECOMMENDED`.
6. **Function analysis.** The package supports an essential device
   function from the module E list. Classify `NOT_RECOMMENDED` or
   `ADVANCED_USERS_ONLY`.
7. **No sufficient evidence.** Classify `UNKNOWN`.

## 6. Reversibility Rules

| Operation | What it changes | Reversibility |
|---|---|---|
| `pm disable-user --user 0` | Component state for the user | `pm enable --user 0` restores the same installation. Highest preference. |
| `pm uninstall -k --user 0` | Hidden for the user; APK and data stay | `pm install-existing --user 0` restores. Preference when data must stay. |
| `pm uninstall --user 0` | Hidden for the user; app data is deleted | `pm install-existing --user 0` restores the app. Stored data are lost. Use only when the user accepts data loss. |
| `pm uninstall --user 0` on a removable (non-system) package | Complete removal for the user | Reinstall from the watch Play Store or `adb install`. |

Rule: prefer disable. Use uninstall with `-k` when data must stay. Use
plain uninstall only for optional packages without important data.

Classifications of `SAFE_TO_REMOVE` assume the `-k` form unless the
database entry says the opposite.

## 7. Device and Software Scope

Every classification is scoped:

1. `device_scope` — device models or codenames with the evidence.
2. `software_scope` — OS family or version range with the evidence.

Never extend a `SAFE_TO_REMOVE` classification to an unnamed device or
software version. Mark the entry `UNKNOWN` for new scopes until a source
exists. Package names can differ between manufacturers and OS versions.
Do not assume identical names.

## 8. Conditional Classifications

Some packages are safe only under a condition. Record the condition in
the entry `description` and `evidence.side_effects`. Example:
`com.samsung.android.shealthmonitor` is removable only when no Samsung
phone is used with the watch. Conditional packages are
`ADVANCED_USERS_ONLY`. The user must read the condition.

## 9. Verification Requirements

A database check rejects:

1. `SAFE_TO_REMOVE` or `SAFE_TO_DISABLE` entries without a non-empty
   `evidence.source`.
2. Entries with missing required schema fields. See
   `08_Package_Database/01_database_schema.md`.
3. Entries whose `testing_status` is weaker than the risk level
   requires. `SAFE_TO_REMOVE` and `SAFE_TO_DISABLE` need
   `PARTIALLY_VERIFIED` or stronger.

## 10. Limitations

1. Evidence in release 1.0 comes from community reports. No laboratory
   verification exists yet.
2. Community evidence does not prove behaviour on all firmware builds.
3. Users must verify their device model and software version before
   they apply any procedure.

## 11. References

1. `09_Package_Classification/02_evidence_labels.md` — evidence labels.
2. `08_Package_Database/01_database_schema.md` — schema fields.
3. `10_Safety_and_Dependencies/01_safety_analysis.md` — protected set.
4. Source reports in `19_References/01_references.md`.

END OF DOCUMENT.
