# Uninstall Procedure

## 1 Purpose

Uninstall a package for the current user, optionally keeping the APK and data.

## 2 Scope

Applies to packages classified `SAFE_TO_REMOVE`.

## 3 Requirements

- Baseline state recorded
- Package not in protected core set
- `--yes` confirmation flag

## 4 Procedure

### Keep APK and Data (Default for SAFE_TO_REMOVE)

```bash
python 14_Automation_and_Scripting/tools/sw.py uninstall-keep com.example.package --yes
```

Command executed:

```bash
pm uninstall -k --user 0 <package>
```

The `-k` flag keeps the APK on the system partition and preserves user data. Restore with `pm install-existing --user 0 <package>`.

### Purge Data

```bash
python 14_Automation_and_Scripting/tools/sw.py uninstall-purge com.example.package --yes
```

Command executed:

```bash
pm uninstall --user 0 <package>
```

Without `-k`, user data is deleted. `pm install-existing` restores the APK but data is permanently lost.

## 5 Verification

Read-back checks the uninstalled-for-user set:

```bash
pm list packages -s -u --user 0
```

Target must appear in the uninstalled set (absent from enabled and disabled).

## 6 Reversibility

| Operation | Restore Command | Data Preserved |
|-----------|-----------------|----------------|
| `uninstall-keep` | `pm install-existing --user 0 <pkg>` | Yes |
| `uninstall-purge` | `pm install-existing --user 0 <pkg>` | No — data lost |

## 7 Safety Information

- `uninstall-purge` requires explicit user acceptance of data loss
- Default for `SAFE_TO_REMOVE` is `uninstall-keep` (`-k` flag)
- Protected packages are refused
- Read-back verification is mandatory
