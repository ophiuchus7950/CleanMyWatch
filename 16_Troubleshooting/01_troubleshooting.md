# Troubleshooting

## 1 Purpose

Symptom → cause → fix table for common issues.

## 2 ADB Connection Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `adb devices` shows `unauthorized` | Watch has not accepted debugging prompt | Accept prompt on watch; re-run `adb devices` |
| `adb devices` shows nothing | Watch not paired or Wi-Fi issue | Re-pair: `adb pair <ip:port>`, then `adb connect <ip:port>`; check AP isolation off |
| `adb connect` fails | Wrong IP/port or watch sleeping | Wake watch; verify IP in Developer options; retry |
| `adb shell` hangs | ADB server stuck | `adb kill-server && adb start-server` |

## 3 Tool Refusal Messages

| Refusal Message | Cause | Fix |
|-----------------|-------|-----|
| `no connected device` | No watch paired | Pair and connect the watch |
| `several devices are connected` | Multiple ADB devices | Set `SW_SERIAL=<serial>` |
| `SW_SERIAL ... is not a connected device` | Wrong serial | Run `adb devices` and use correct serial |
| `refused: <pkg> is in the protected core set` | Package in protected list | Do not target this package; remove from request |
| `record ... exists already. The first record wins` | Baseline record exists | Use `--out` for new path; or delete old record intentionally |
| `apply changes the watch. Confirm with --yes` | Missing `--yes` flag | Add `--yes` to confirm |
| `one runs read-only commands only` | Mutation command given to `one` | Use `disable`/`enable`/`uninstall-*` instead |

## 4 Operation Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| `READ-BACK FAILED for: <pkg>` | Package state did not change | Stop. Do not retry in a loop. Check watch manually: `pm list packages -e -d -u --user 0` |
| `watch refused: ... DELETE_FAILED_USER_RESTRICTED` | Samsung Knox blocks uninstall | Use `disable` instead of `uninstall` |
| `watch refused: ... DELETE_FAILED_DEVICE_POLICY_MANAGER` | MDM/EMM manages device | Contact IT admin; cannot debloat |
| `watch refused: ... NOT_INSTALLED_FOR_USER` | Package installed for different user | Check `pm list packages -u --user 0` |
| `watch refused: Permission denied` | Package protected by system | Cannot debloat this package |

## 5 Post-Debloat Issues

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Battery drain | Removed sync cluster (`scloud`, `contacts`, `messaging`) | Restore from record |
| Feature missing (alarms, health) | Removed `DO_NOT_REMOVE` package | Restore from record |
| Boot failure ("No android system found") | Removed `app.routines` + `smartgesture` batch | Factory reset from recovery |
| OTA re-installs packages | System update | Re-run debloat after OTA; check drift |

## 6 Package Name Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Unknown package` in query | Not in any dataset | Run `match` on a device dump to find it |
| `Protected core` but not in my list | Protected prefixes match | Check `is_protected()` in `swdb.py` |

## 7 Drift Detection

```bash
python 14_Automation_and_Scripting/tools/sw.py packages --out current.txt
python 14_Automation_and_Scripting/tools/swdb.py drift current.txt --profile samsung_galaxy_watch6_7
```

Exit 1 = drift detected (planned packages still present on device).

## 8 Limitations

- No lab recovery validation performed
- Community-reported failure modes only
- Factory reset is ultimate recovery for boot failure
