# ADB Command Reference

## 1 Purpose

This document lists the verified ADB commands used by the debloating system.

## 2 Verified Commands

### Identification and State

| Command | Purpose |
|---------|---------|
| `adb devices` | List connected devices |
| `adb -s <serial> shell getprop ro.product.brand` | Get brand |
| `adb -s <serial> shell getprop ro.product.model` | Get model |
| `adb -s <serial> shell getprop ro.build.version.sdk` | Get API level |
| `adb -s <serial> shell getprop ro.build.display.id` | Get build fingerprint |

### Package Enumeration

| Command | Purpose |
|---------|---------|
| `pm list packages -s` | All system packages |
| `pm list packages -s -e --user 0` | Enabled system packages |
| `pm list packages -s -d --user 0` | Disabled system packages |
| `pm list packages -s -u --user 0` | All including uninstalled-for-user |

### State Changes

| Command | Purpose | Reversibility |
|---------|---------|---------------|
| `pm disable-user --user 0 <pkg>` | Disable package | `pm enable --user 0 <pkg>` |
| `pm enable --user 0 <pkg>` | Enable package | — |
| `pm uninstall -k --user 0 <pkg>` | Uninstall, keep APK + data | `pm install-existing --user 0 <pkg>` |
| `pm uninstall --user 0 <pkg>` | Uninstall, delete data | `pm install-existing --user 0 <pkg>` (data lost) |
| `pm install-existing --user 0 <pkg>` | Restore uninstalled system package | — |

### APK Extraction

| Command | Purpose |
|---------|---------|
| `pm path <pkg>` | Get APK path on device |
| `adb pull <path> <name>.apk` | Copy APK to computer |

### App Installation

| Command | Purpose |
|---------|---------|
| `adb install --user 0 <apk>` | Side-load APK for current user |

## 3 Forbidden Commands

| Command | Reason |
|---------|--------|
| `pm uninstall <pkg>` (no `--user`) | Requires root, affects all users |
| `pm disable <pkg>` (no `--user`) | Requires root, affects all users |
| `adb root` / `adb shell su` | Root not used in this system |
| Chained commands (`cmd1 && cmd2`) | Silent failure risk — one shell call per command |
| Blind `--user N` switching | Use `--user 0` only; multi-user not verified on watches |

## 4 Command Execution Rules

1. **One command per shell call** — `sw.py` runs each `pm` command in a separate `adb shell` invocation
2. **Read-back verification** — After every batch, `pm list packages -e --user 0` is compared to the plan
3. **Protected refusal** — Protected core packages are checked before any command runs
4. **Explicit confirmation** — `--yes` flag required for any state-changing operation
