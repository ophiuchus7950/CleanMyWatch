# Device-Specific Profiles

Each subdirectory under `13_Device_Specific_Profiles/` contains a `profile.json` file that defines how the package database maps to a specific device or device family.

## Profile Schema

```json
{
  "profile": "string",
  "datasets": ["string", ...],
  "operation_map": {
    "SAFE_TO_REMOVE": "uninstall_keep_apk",
    "SAFE_TO_DISABLE": "disable"
  },
  "excluded": ["package.name", ...],
  "device_scope": ["string", ...],
  "software_scope": ["string", ...],
  "device_match": ["SM-R87", ...],
  "description": "string"
}
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `profile` | Yes | Unique identifier for this profile. Must match the directory name. |
| `datasets` | Yes* | List of dataset IDs from `08_Package_Database/data/` to apply. Exactly one of `datasets` or `dataset` must be present. |
| `dataset` | Yes* | Legacy single-dataset field. Kept for backward compatibility; `datasets` takes precedence. |
| `operation_map` | Yes | Maps risk classifications to operations. Allowed operations: `disable`, `uninstall_keep_apk`, `uninstall_purge_data`, `none`. Risk levels not listed default to `none`. |
| `excluded` | No | Package names to skip even if their risk maps to an operation. |
| `device_scope` | Yes* | List of device identifiers this profile applies to (e.g., `galaxy_watch4`, `galaxy_watch6`). Entry scope filters the plan. Must not be empty when `operation_map` is not empty. |
| `software_scope` | Yes* | List of software version identifiers (e.g., `wear_os_3`, `wear_os_4`). Entry scope filters the plan. Must not be empty when `operation_map` is not empty. |
| `device_match` | Yes* | Model prefixes matched against `ro.product.model` and `ro.product.device` (e.g., `SM-R87`). `sw.py apply` refuses a connected watch that matches no prefix. Must not be empty when `operation_map` is not empty. |
| `description` | No | Human-readable description of the profile. |

\* Required unless `operation_map` is empty. An empty operation map makes the profile a guard profile.

### Operation Map Values

| Value | ADB Command (forward) | ADB Command (restore) | Notes |
|-------|----------------------|----------------------|-------|
| `disable` | `pm disable-user --user 0 <pkg>` | `pm enable --user 0 <pkg>` | Reversible, keeps data |
| `uninstall_keep_apk` | `pm uninstall -k --user 0 <pkg>` | `pm install-existing --user 0 <pkg>` | Keeps APK on system partition, keeps data |
| `uninstall_purge_data` | `pm uninstall --user 0 <pkg>` | `pm install-existing --user 0 <pkg>` | Removes user data; restore re-installs APK but data is lost |
| `none` | (no operation) | (no operation) | Default for unlisted risks |

### Risk Levels

The risk levels are defined in `09_Package_Classification/01_classification_methodology.md`:

1. `SAFE_TO_REMOVE` — Safe to uninstall with `-k` flag (keeps data, reversible via `install-existing`)
2. `SAFE_TO_DISABLE` — Safe to disable, reversible via `pm enable`
3. `ADVANCED_USERS_ONLY` — Requires advanced knowledge, may break minor functionality
4. `NOT_RECOMMENDED` — Known negative side effects (battery drain, feature loss)
5. `DO_NOT_REMOVE` — Critical for device operation, boot failure risk
6. `UNKNOWN` — Insufficient evidence to classify

### Profiles in This Repository

| Profile | Datasets | Purpose |
|---------|----------|---------|
| `samsung_galaxy_watch4` | knowledge_galaxy_watch, knowledge_google_wear_os, knowledge_third_party_watch | Guard profile. All verified debloat entries are scoped to Watch 6/7, so the plan has no commands. |
| `samsung_galaxy_watch6_7` | knowledge_galaxy_watch, knowledge_google_wear_os, knowledge_third_party_watch | Galaxy Watch 6/7 series debloating |
| `samsung_galaxy_watch8` | knowledge_galaxy_watch, knowledge_google_wear_os, knowledge_third_party_watch | Guard profile for Galaxy Watch 8 (SM-L330). No verified evidence, no operations. |
| `google_core` | knowledge_google_wear_os | Guard profile — no operations, identifies protected Google core packages |

### Scope Enforcement

`swdb.py plan` skips an entry when its `device_scope` or `software_scope` does not intersect the profile scope. `sw.py apply` also reads the connected watch identity and refuses when the model does not match `device_match`, or when the Wear OS version is not in `software_scope`. Set `SW_ALLOW_DEVICE_MISMATCH=1` to bypass that check with a warning.

### Usage

```bash
# Validate all profiles and datasets
python 14_Automation_and_Scripting/tools/swdb.py validate

# Show plan for Galaxy Watch 6/7
python 14_Automation_and_Scripting/tools/swdb.py plan --profile samsung_galaxy_watch6_7

# Show restore plan
python 14_Automation_and_Scripting/tools/swdb.py plan --profile samsung_galaxy_watch6_7 --op restore

# Check drift against a device dump
python 14_Automation_and_Scripting/tools/swdb.py drift dump.txt --profile samsung_galaxy_watch6_7
```

### Adding a New Profile

1. Create a new directory under `13_Device_Specific_Profiles/` named after the profile ID.
2. Create `profile.json` following the schema above. Add verified model prefixes to `device_match`.
3. Ensure all referenced datasets exist in `08_Package_Database/data/`.
4. Run `python 14_Automation_and_Scripting/tools/swdb.py validate` to verify.
5. Document the profile in this README.
