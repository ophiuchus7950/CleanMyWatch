# Recovery Procedures

## 1 Purpose

Handle failure scenarios when debloating causes device instability.

## 2 Boot Failure: "No android system found"

**Cause**: Disabling critical system packages (e.g., `com.samsung.android.app.routines` + `com.samsung.android.smartgesture` batch).

**Recovery**:
1. The watch shows "No android system found" in recovery mode
2. Factory reset from recovery menu (volume + power buttons)
3. Re-pair watch with phone
4. Packages restored to factory state

**Prevention**: The protected core set includes known boot-critical packages. Never override protected refusals.

## 3 Battery Drain After Debloat

**Cause**: Removing sync clusters (`com.samsung.android.scloud`, `com.samsung.android.app.contacts`, messaging) causes dependent services to retry in loops.

**Recovery**:
1. Run `python 14_Automation_and_Scripting/tools/sw.py restore --record <record> --yes`
2. If record unavailable, factory reset

**Prevention**: These packages are classified `NOT_RECOMMENDED` or `DO_NOT_REMOVE` in the database.

## 4 OTA Updates Restore Debloated Packages

**Cause**: System OTA updates re-install or re-enable packages that were debloated.

**Recovery**:
1. Re-run the debloat profile after OTA
2. Use `python 14_Automation_and_Scripting/tools/swdb.py drift <dump> --profile <id>` to detect drift

**Note**: This is expected behaviour. The debloat is for the current user only and does not persist across system image updates.

## 5 Factory Reset Implications

A factory reset:
- Removes all user data
- Restores all system packages to factory state
- Requires re-pairing with phone
- Requires re-enabling wireless debugging

## 5 Re-flash via Factory Images

For Pixel Watch devices, factory images are available at:
https://developers.google.com/android/images-watch

For Samsung, use Samsung Smart Switch or service center.

## 6 ADB Connection Recovery

| Symptom | Fix |
|---------|-----|
| `unauthorized` | Accept USB debugging prompt on watch |
| `offline` / connection refused | Re-pair: `adb pair`, then `adb connect` |
| `device` but shell fails | Restart ADB server: `adb kill-server && adb start-server` |
| Wireless ADB disconnects | Disable/enable wireless debugging on watch; check Wi-Fi |

## 7 Limitations

- No lab recovery validation performed in this project
- Recovery procedures based on community reports only
- Factory reset is the ultimate recovery for boot failures
