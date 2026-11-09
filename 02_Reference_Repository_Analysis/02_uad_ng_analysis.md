# Universal Android Debloater Next Generation — Reference Repository Analysis

> Analysis date: 2026-11-09.
> Reference repository: `reference/universal-android-debloater-next-generation` (UAD-ng).
> Method: read-only static analysis of the source code. See section 13.

---

## 1. Purpose

This analysis extracts the package-management methodology of UAD-ng.
A new smartwatch repository will adapt this methodology. It will not copy UAD-ng code.
The source lives at `reference/universal-android-debloater-next-generation`.
The project license is GPL-3.0. The workspace version is `1.3.1`.
UAD-ng is a Rust workspace. It debloats Android system packages over ADB.
It gives every package a removal-risk label. It backs up device state. It restores that state later.

## 2. Reference Repository Overview

The workspace members live under `crates/`. The root `Cargo.toml` pins edition `2024`.

| Crate | Binary | Role |
|---|---|---|
| `uad-core` | library | ADB wrapper, package-list sync, state machine, config, backup, update checks |
| `uad-cli` | `uad` | command-line interface; subcommands and interactive REPL |
| `uad-gui` | `uad-ng` | desktop GUI on `iced 0.14`; not part of this study beyond shared warnings |

Artifact types:

- Two desktop binaries: `uad` (CLI) and `uad-ng` (GUI).
- One shared library crate: `uad-core`.
- One data asset: `resources/assets/uad_lists.json` (about 1.7 MB).
- Per-device backups: JSON files with package state.
- One config file: `config.toml`.
- Shell-completion scripts, a usage example (`crates/uad-cli/examples/usage.sh`), and a self-updater.

## 3. Architecture

`uad-core` exposes these modules: `adb`, `config`, `save`, `sync`, `uad_lists`, `update`, `utils`.
`lib.rs` builds two global paths: `CONFIG_DIR` and `CACHE_DIR`.
Each path is `{base}/uad`. The base comes from `dirs::config_dir()` or `dirs::cache_dir()`.

Key modules and identifiers:

| Module | Key items | Role |
|---|---|---|
| `adb.rs` | `ACommand`, `ShellCommand`, `PmCommand`, `PackageId`, `PmListPacksFlag`, `UserInfo` | typed wrappers around the `adb` CLI; parses `pm` output |
| `sync.rs` | `Phone`, `User`, `CorePackage`, `AdbError`, `apply_pkg_state_commands`, `request_builder`, `get_devices_list`, `get_package_state`, `attempt_fallback`, `run_adb_shell_action`, `make_friendly_error_message` | device model, state changes, verification, fallback |
| `uad_lists.rs` | `Package`, `PackageHashMap`, `UadList`, `PackageState`, `Removal`, `load_debloat_lists`, `LIST_FNAME`, `DATA` | list schema, enums, remote sync with cache fallback |
| `utils.rs` | `fetch_packages`, `matches_search`, `truncate_description`, `export_packages`, `export_selection`, `setup_uad_dir` | builds current package inventory; misc helpers |
| `config.rs` | `Config`, `GeneralSettings`, `DeviceSettings`, `BackupSettings` | TOML config, per-device settings |
| `save.rs` | `PhoneBackup`, `UserBackup`, `BackupPackage`, `RestoreResult`, `backup_phone`, `restore_backup` | backup and restore of package state |
| `update.rs` | `Release`, `ReleaseAsset`, `SelfUpdateState`, `SelfUpdateStatus`, `get_latest_release`, `BIN_NAME` | self-update machinery (feature `self-update`) |

Core structs, with fields:

```rust
pub struct Phone   { pub model: String, pub android_sdk: u8, pub user_list: Vec<User>, pub adb_id: String }
pub struct User    { pub id: u16, pub index: usize, pub protected: bool }
pub struct CorePackage { pub name: String, pub description: String,
                         pub removal: Removal, pub state: PackageState, pub list: UadList }
pub struct PackageRow  { name, description, removal, state, list, selected: bool, current: bool } // GUI layer
```

`CorePackage {name, description, removal, state, list}` is the pivot.
The CLI, the GUI, and the backup files all share this shape.
`PackageState` has variants `All`, `Enabled`, `Uninstalled`, `Disabled`. The default is `Enabled`.
`Removal` has variants `Recommended`, `Advanced`, `Expert`, `Unsafe`, `Unlisted`, `All`. The default is `Recommended`.
`PackageState::opposite(disable: bool)` picks the inverse state.
`Enabled` maps to `Disabled` or `Uninstalled`. `Disabled` and `Uninstalled` both map to `Enabled`.

## 4. ADB Integration

### 4.1 The 1-to-1 contract

`adb.rs` states the design rule in its module docs.
Every wrapper method maps 1-to-1 to one ADB CLI command.
The wrappers add no magic, no custom commands, and no command chaining.
This avoids two problems: non-atomic operations, and drifting semantics.
The docs ask maintainers to extend the typed API instead of calling raw `Command`.

Structure of the wrapper stack:

- `ACommand(std::process::Command)` — the host `adb` binary.
  - `ACommand::new()`, `ACommand::shell(device_serial)`, `ACommand::devices()`, `ACommand::version()`, private `run()`.
  - An empty serial omits `-s`. ADB then picks the default device.
  - On Windows, `run()` sets `creation_flags(0x0800_0000)`. This is `CREATE_NO_WINDOW`.
- `ShellCommand(ACommand)` — adds `adb shell` commands: `pm()`, `getprop(key)`, `reboot()`, `raw(action)`.
- `PmCommand(ShellCommand)` — adds `pm list packages -s ...` and `pm list users`.
- `PackageId(Rc<str>)` — validates package names per Android manifest rules, or accepts `"android"`.

`run()` also fixes an ADB quirk. Some errors arrive on stdout, not stderr.
The code uses `let err = if stdout.is_empty() { stderr } else { stdout };`.
`to_trimmed_utf8()` converts output with lossy UTF-8. Some OEMs emit non-UTF-8 bytes.

### 4.2 Full command inventory — 21 distinct commands

| # | Command (verbatim) | Count | Reason |
|---|---|---|---|
| 1 | `adb devices` | 1 wrapper; 2 run sites | device discovery; retry loop then requires status `device` |
| 2 | `adb version` | 1 | About view display; format check only in debug builds |
| 3 | `adb shell getprop ro.product.model` | 1 | device model (`get_device_model`) |
| 4 | `adb shell getprop ro.product.brand` | 1 | device brand (`get_device_brand`) |
| 5 | `adb shell getprop ro.build.version.sdk` | 1 (+1 GUI reuse) | API level (`get_android_sdk`); a value of `0` means failure |
| 6 | `adb shell reboot` | 1 | GUI "Reboot" button |
| 7 | `pm list packages -s` | 1 of 11 `list_packages_sys` sites | baseline scope: system packages only |
| 8 | `pm list packages -s -e` | serves 11 sites | enabled packages |
| 9 | `pm list packages -s -d` | serves 11 sites | disabled packages |
| 10 | `pm list packages -s -u` | serves 11 sites | include uninstalled; doc note: "`-u`, not to be confused with `-a`" |
| 11 | `pm list users` | 1 | user list; parses `UserInfo{<id>:<name>:<flags>}[ running]` |
| 12 | `pm enable` | 1 | `Disabled` to `Enabled` |
| 13 | `cmd package install-existing` | 1 | `Uninstalled` to `Enabled` on SDK 23+ |
| 14 | `pm unhide` | 1 | restore path on SDK 21/22 |
| 15 | `pm unblock` | 1 | restore path on SDK 19/20 |
| 16 | `pm clear` | const `PM_CLEAR_PACK`; 4 roles | kills app data; joins hide/block/unblock/disable sequences |
| 17 | `pm disable-user` | 1 | enable-to-disable, SDK 23+ |
| 18 | `am force-stop` | 1 | stops the process as step 2 of the disable trio |
| 19 | `pm uninstall` | 1 | uninstall on SDK 23+ |
| 20 | `pm hide` | 1 | uninstall path on SDK 21/22 |
| 21 | `pm block` | 1 | uninstall path on SDK 19/20; needs root on older devices |

Eleven call sites use `list_packages_sys`:
`is_protected_user` (1), `get_package_state` (3), `fetch_packages` (3), CLI `list_packages` (1),
`display_package_list` (2), REPL `handle_list_command` (1).

### 4.3 Absent commands

The codebase issues no `adb pair`, no `adb connect`, no `tcpip`, and no mDNS scan.
Wireless devices appear only if the host ADB session already knows them.
The codebase also issues no `pm path`, no `dumpsys`, no `settings`, and no `adb kill-server`.
The project wiki confirms the last gap intentionally: the app never runs `adb kill-server`.

## 5. Package List Format

### 5.1 `uad_lists.json` schema

The file lives at `resources/assets/uad_lists.json`. The binary embeds it via `include_str!`.
The package name is the JSON object key. No separate `package` field exists.
Each entry has exactly six fields:

```json
{
  "com.example.app": {
    "list": "Oem",
    "description": "What the app does.\nSafe to remove if you use another one.",
    "dependencies": [],
    "neededBy": [],
    "labels": [],
    "removal": "Recommended"
  }
}
```

Facts about the file:

- The file holds about 5400 top-level entries.
- `list` ∈ `Aosp`, `Carrier`, `Google`, `Misc`, `Oem`, `Pending`, `Unlisted` (type `UadList`).
- `removal` ∈ `Recommended`, `Advanced`, `Expert`, `Unsafe` (the string `Unlisted` never appears in the file).
- `dependencies` and `neededBy` are reciprocal arrays of package names.
  Example: `com.huawei.meetime` depends on `com.huawei.hwvoipservice`; the reverse list mirrors it.
- `labels` is a string array. The code deserializes it but never reads it.
- No `bodies`, `rem_app`, `protection_level`, `required`, or `references` keys exist in this snapshot.
- Removal counts: `Recommended` 3021, `Advanced` 1160, `Expert` 923, `Unsafe` 298, `Unlisted` 0.

### 5.2 Removal category definitions

The wiki page `wiki/Debloat-Lists` carries the categories. The code only stores the enum names.
Quotes below are verbatim from that page (fetched 2026-11-09):

> - `Recommended` — "Any package that's safe to uninstall ... and/or apps available through whatever app-store is built-in (G Play, Samsung Galaxy Store, etc...). Despite being "safe to remove", you should review them anyways, as different people have different needs and preferences."
> - `Advanced` — "Breaks obscure or minor parts of functionality, overlays, or apps that aren't easily enabled/installed through Settings/Google Play. This category is also used for apps that are useful (default keyboard/gallery/launcher/music app.) but that can easily be replaced by a better alternative."
> - `Expert` — "Breaks widespread and/or important functionality, but nothing important to the basic operation of the operating system. Removing an `Expert` package *should not* boot-loop the device (unless mentioned in the description) but we can't guarantee it 100%."
> - `Unsafe` — "Can break vital parts of the operating system or is illegal to remove in your country (e.g. emergency alerts, or SAR certification law in EU). Removing an `Unsafe` package have an extremely high risk of boot-looping your device."
- `Unlisted` — the wiki page does not define this label. The code defines it by default.
  `fetch_packages()` assigns `removal = Removal::Unlisted` to any package missing from the lists.
  It also assigns the description `[No description]: CONTRIBUTION WELCOMED` and `list = UadList::Unlisted`.

### 5.3 List sync chain

`load_debloat_lists(remote: bool)` builds a three-layer chain:

1. Remote fetch. `ureq::get("https://raw.githubusercontent.com/Universal-Debloater-Alliance/universal-android-debloater/main/resources/assets/uad_lists.json")`.
   Retries 60 times at 1 second. The response body is capped at 8 MiB (`limit(1 << (3 + 10 + 10))`).
2. Cache file. The fetched text is written to `{CACHE_DIR}/uad_lists.json`.
3. Embedded fallback. The constant `DATA` is a compile-time snapshot via `include_str!`.

Failure reports differ by layer: `UadListState::Done` (remote), `Err(list)` with local data (cache),
and `UadListState::Failed` in the GUI. The state display computes a relative age
with `format_diff_time_from_now()`: "Done (last was N min(s)/hour(s)/day(s) ago)".

## 6. Package State Model

### 6.1 State derivation

`fetch_packages()` derives every package state from three list queries.

- Superset: `pm list packages -s -u`.
- Enabled set: `pm list packages -s -e`.
- Disabled set: `pm list packages -s -d`.

Per-package rule, in code order:
membership in the enabled set gives `Enabled`; membership in the disabled set gives `Disabled`;
otherwise the state is `Uninstalled`. A package present only in the `-u` superset is thus "uninstalled".
`get_package_state()` repeats this triple test for one package. It returns `None` when no test matches.
The one-package variant feeds verification and the REPL.

### 6.2 Transition matrix

`apply_pkg_state_commands(package, wanted_state, selected_user, phone)` returns a command vector.
The table rows bundle the SDK branches.

| Wanted ↓ / Current → | `Enabled` | `Disabled` | `Uninstalled` |
|---|---|---|---|
| `Uninstalled` | SDK ≥ 23: `["pm uninstall"]` · SDK 21/22: `["pm hide", "pm clear"]` · SDK ≤ 20: `["pm block", "pm clear"]` | same branches as `Enabled` | no commands |
| `Disabled` | `supports_disabling` true: `["pm disable-user", "am force-stop", "pm clear"]`; else empty | no commands | same branch as `Enabled`→`Disabled` |
| `Enabled` | no commands | `["pm enable"]` | SDK ≥ 23: `["cmd package install-existing"]` · SDK 21/22: `["pm unhide"]` · SDK 19/20: `["pm unblock", "pm clear"]` |

Capability gates:

- `supports_disabling(dev)` returns `dev.android_sdk >= 23` (Marshmallow 6.0).
- `supports_multi_user(dev)` returns `dev.android_sdk >= 21`. "true isn't reliable, you can only trust false".
- SDK below 19 hits `unreachable!("already prevented by the GUI")`.

### 6.3 The disable trio

Disabling an app runs three commands in sequence:
`pm disable-user`, then `am force-stop`, then `pm clear`.
The pair `pm clear` + `am force-stop` kills the process and drops its data.
The wiki copy reinforces the intent: "In many cases, it's better to disable a package instead of uninstalling it".

### 6.4 Ordering contract

The comment in `sync.rs` states the rule:
"ALWAYS PUT THE COMMAND THAT CHANGES THE PACKAGE STATE FIRST!"
The state-changer runs first. Cleanup commands (`am force-stop`, `pm clear`) run after it.

### 6.5 Command assembly

`request_builder(commands, package, user) -> Vec<String>` assembles final strings.
It appends ` --user {id}` only when `supports_multi_user(phone)` is true.
With `user_flag(None)` it appends nothing, not a bare ` --user 0`.
It rejects invalid names: `error!("request_builder: refusing invalid package name: {package:?}")`.
The comment calls this fail-closed defense-in-depth against shell injection.

## 7. Safety System

### 7.1 Expert mode gate for `Unsafe`

The GUI row widget `PackageRow` disables both the checkbox and the action button when:

```rust
self.removal != Removal::Unsafe
    || self.state != PackageState::Enabled
    || settings.general.expert_mode
```

The gate text: `Allow to uninstall packages marked as "unsafe" (I KNOW WHAT I AM DOING)`.
The warning under it: `Most unsafe packages are known to bootloop the device if removed.`
The gate also blocks restore of an `Unsafe` package from the `Enabled` state.
The CLI is weaker. `process_package_state_change` only prints
`⚠ WARNING: This package is marked as UNSAFE to remove!` and then continues.

### 7.2 Uninstall or disable — the per-device choice

`DeviceSettings.disable_mode` is a per-device toggle. Its default seed is `supports_disabling(phone)`.
So SDK 23+ devices start with disable mode on. The GUI also offers `multi_user_mode`.
An `Unavailable` button links to the wiki FAQ when the device cannot disable packages.

### 7.3 Verify → fallback loop

The CLI `execute_with_fallback()` and the GUI `on_verify_and_fallback` follow one shape:

1. Run each command through `run_adb_shell_action()`.
2. Re-derive the state with `verify_package_state()`.
3. On mismatch, call `attempt_fallback()`.
4. On success, call `detect_cross_user_behavior()` and warn about OEM-copied changes.

`attempt_fallback` covers three cases:

- Wanted uninstall, found `Enabled` → disable instead. Result string: "disabled package instead of uninstalling".
- Wanted disable, found `Enabled` → uninstall instead, then re-verify. Result: "uninstalled package instead of disabling".
- Wanted enable, found `Disabled` → uninstall, then `install-existing` (reinstall), then verify.

Other mismatches return `Err("No fallback available for wanted state {..} and actual state {..}")`.
CLI glyphs mark outcomes: `✓` (ran), `✗` (failed), `⚠` (state mismatch), `↻` (fallback), `ℹ` (cross-user note).

### 7.4 OEM-translated error table

`make_friendly_error_message()` matches substrings in device output:

| Match | Explanation |
|---|---|
| `DELETE_FAILED_USER_RESTRICTED` | "restricted by the device manufacturer (Samsung Knox or similar)"; tip: disable instead |
| `NOT_INSTALLED_FOR_USER` | "may be installed for a different user profile or work profile" |
| `Shell cannot change component state for null` | "Invalid package: Empty package name detected" |
| `Permission denied`, `INSTALL_FAILED_PERMISSION_MODEL_DOWNGRADE` | "may require root access or the package is protected by the system" |
| `DELETE_FAILED_DEVICE_POLICY_MANAGER` | "managed by device policy (MDM/EMM)"; tip: contact the IT administrator |

Any output containing `Error` or `Failure` routes into this translator.
All other output falls back to `"{action} -> {error_output}"`.
`run_adb_shell_action` is the single funnel for all state-changing commands.

### 7.5 Other guardrails

- `request_builder` validates the name at the sink; malformed names emit no command.
- The inventory scope is system packages only (`-s`). Third-party packages (`-3`) never appear.
- `is_protected_user()` hides users whose package list fails. The GUI explains work profiles:
  "ADB is not authorized to access this user!" plus a Secure Folder note.
- `multi_user_mode` excludes `User.protected` users from bulk operations.
- A no-op guard skips work when `current_state == target_state`: "Already in target state, skipping".
- The CLI `--dry-run` flag prints "Would run: {cmd}" per command and performs nothing.
- The boot gate: `initial_load()` runs `adb devices`. On failure the GUI shows
  "ADB is not installed on your system, install ADB and relaunch application." with a wiki link.
- Device absence raises `NO_DEVICES_FOUND`:
  "No devices found. Make sure ADB is installed and devices are connected."
- The wiki states the hard limit: "System apps cannot truly be uninstalled without root".

## 8. Backup and Restore

`save.rs` writes JSON, not TOML. The TOML file holds only config and per-device toggles.

```rust
pub struct PhoneBackup { pub device_id: String, pub users: Vec<UserBackup> }
pub struct UserBackup  { pub id: u16, pub packages: Vec<CorePackage> }
```

Layout:

```
{Config.general.backup_folder}/{device_id}/%Y-%m-%d_%H-%M-%S.json
```

The default backup folder is `{CACHE_DIR}/backups`. The user can change it.
`backup_phone()` serializes every package of every user with `serde_json::to_string_pretty`.
Each stored `CorePackage` keeps `name`, `description`, `removal`, `state`, and `list`.

Restore path, `restore_backup()`:

- For each backed-up user, find the live user index. Fail with "user {id} doesn't exist" if absent.
- For each backed-up package, reuse the live `CorePackage` metadata.
  Missing packages are skipped with a warning; the count lands in `RestoreResult.skipped_count`.
- Regenerate commands toward the recorded state with `apply_pkg_state_commands(core_pkg, backup_package.state, ...)`.
- Append one empty sentinel `BackupPackage` when any commands exist.

Restore status strings: "Restore completed successfully", "Device state is already restored",
and "Device is not connected" (when `get_android_sdk` returns 0).
A CSV export also exists: `export_packages()` writes `uninstalled_packages_%Y%m%d.csv`
with header `["Package Name", "Description"]` for the `Uninstalled` subset.

## 9. Command Line Interface

The binary is `uad`. Clap drives parsing. [tokio::main] wraps the entry point.

| Subcommand | Alias | Flags & args | Function | Purpose |
|---|---|---|---|---|
| `devices` | — | — | `list_devices()` | list devices with model, serial, SDK, users |
| `list` | `ls` | `-d,--device`, `-s,--state`, `-r,--removal`, `-l,--list`, `-q,--search`, `--user` | `list_packages()` | filtered package table |
| `uninstall` | `rm` | pos. packages, `--device`, `--user`, `--dry-run` | `change_package_state(...)` | set `PackageState::Uninstalled` |
| `enable` | `restore` | same as uninstall | `change_package_state(...)` | set `PackageState::Enabled` |
| `disable` | — | same as uninstall | `change_package_state(...)` | set `PackageState::Disabled` |
| `info` | — | `package`, `--device`, `--user` | `show_package_info()` | list metadata plus device state |
| `update` | — | — | `update_lists()` | refresh lists from remote |
| `completions` | — | positional `Shell` | `generate_completions()` | write completion script to stdout |
| `repl` | `shell` | `--device`, `--user` | `repl_mode()` | interactive `rustyline` session |

Defaults: `--user` is `0`; `--device` omitted selects the first device, with a warning on multiples.
REPL commands: `help`, `exit`/`quit`, `list [-s state] [-q term]`, `info <pkg>`,
`uninstall|rm`, `enable|restore`, `disable`, `device`, `clear`.
REPL history lives at `{CACHE_DIR}/cli_history.txt`.

`--dry-run` behavior: it prints "DRY RUN - No changes will be made", then "Would run: {cmd}" per command,
and closes with "Dry run completed. No changes were made."
The example flow in `crates/uad-cli/examples/usage.sh`:

```sh
uad devices
uad list --state enabled | head -20
uad list --search google | head -10
uad info com.google.android.gms
uad uninstall com.example.package --dry-run
uad repl
```

CLI output macros `println_or_exit!` and `print_or_exit!` ignore broken-pipe errors, so piping into `head` is safe.

## 10. Support Range and Limitations

Support range, per the wiki and the code:

- The wiki claims: "Wide version range support, all the way back to Android 4".
- Android 4 is SDK 19 (KitKat). The code branches confirm: SDK ≥ 23 gives full parity;
  SDK 21/22 uses `pm hide`/`pm unhide`; SDK 19/20 uses `pm block`/`pm unblock`.
- The GUI prevents devices below SDK 19.
- `adb version` output is displayed, but no numeric ADB minimum is asserted anywhere.
  The app checks for adb presence at runtime instead.

Watch-relevant limitations:

- The whole device model is mobile-phone-shaped: `pm list users`, work-profile protection probes,
  cross-user detection, and multi-user bookkeeping. A watch does not need any of this.
- No wireless-pairing code exists. A watch repo must add its own `adb pair` / `adb connect` flow.
- The GUI layer is large (~4000 lines) and built on `iced`. It does not transfer.
- The bundled list catalog serves phones and tablets. It has no watch-specific entries.
- OEM-quickness, not watch-quickness: the fallback matrix targets phone OEM quirks.

## 11. Adaptation to the Smartwatch Repository

| # | Transferable item | What transfers | Mapping to the watch project |
|---|---|---|---|
| 1 | Typed command builder | `ACommand` → `ShellCommand` → `PmCommand` stack; 1-to-1 method↔command rule | Model watch ADB flows with the same layering and `#[must_use]` builders |
| 2 | `PackageId` validation | Package-name grammar, `"android"` special case, warn-and-skip parsing | Reuse grammar verbatim; validate every watch package name before use |
| 3 | State triple-derivation | `-u` superset minus `-e`/`-d` membership in `fetch_packages()` | Identical logic; watches run Android Wear (SDK 30+), so the superset test stays valid |
| 4 | Transition matrix | `apply_pkg_state_commands` wanted×current branching; state-changer-first ordering | Watch supports the SDK≥23 row only; port the matrix shape and the ordering contract |
| 5 | Expert gate | `PackageRow` unsafe-gating expression plus expert-mode copy | Gate `Unsafe` watch packages (e.g. heart-rate services) behind an opt-in toggle |
| 6 | Error translation | `make_friendly_error_message` token table | Copy the token table; add watch OEM tokens and sensor-service failures |
| 7 | Verify → fallback loop | `attempt_fallback` three cases + `detect_cross_user_behavior` notifications | Keep the loop; drop the multi-user parts, keep the uninstall↔disable swap cases |
| 8 | Fail-closed assembly | `request_builder` name validation at the command sink | Reuse as-is; it is device-agnostic |
| 9 | List JSON schema | Six fields, name-as-key, `removal` ranking, reciprocal `dependencies`/`neededBy` | Adopt for a watch catalog; pick watch-shaped `list` buckets (e.g. `Aosp`, `Google`, `Wear`, `Oem`) |
| 10 | Removal labels | `Recommended`, `Advanced`, `Expert`, `Unsafe`, `Unlisted` defaults | Same five labels; add watch-specific descriptions |
| 11 | Three-layer list sync | Remote URL fetch with retries, 8 MiB cap, cache file, `include_str!` snapshot | Same chain for a watch list; smaller file, shorter retry budget |
| 12 | Backup layout | `{backup_folder}/{device_id}/{timestamp}.json` with `PhoneBackup`/`UserBackup` | Works unchanged; watches add a serial key the same way |
| 13 | Restore regeneration | Rebuild command vectors toward recorded state; skip missing packages | Direct port; `cmd package install-existing` restores watch packages identically |
| 14 | Windows spawn hygiene | `creation_flags(0x0800_0000)` (`CREATE_NO_WINDOW`) + broken-pipe-safe output macros | Copy into the watch CLI for console-less Windows launches |
| 15 | Retry discipline | `retry(Fixed::from_millis(...).take(...))` on device probes and fetches; SDK-0 sentinel | Same pattern for dock/changing watch connection states |

Also reusable: the config precedent (`config.toml` with per-device upsert and auto-reset of defaults),
the CSV/selection exports, `truncate_description` and `matches_search` helpers,
and the concrete path plan: config under `dirs::config_dir()/uad`, cache and logs under `dirs::cache_dir()/uad`.

## 12. Non-Transferable Components

- GUI internals. `uad-gui` is built on `iced 0.14`: `views/list.rs` (~1500 lines), custom `theme.rs`/`style.rs`,
  icomoon icon font, `rfd` folder picker, `dark-light` theme detection, and the iced `Task` fan-out pipeline.
енов None of this fits a new CLI-first watch repo.
- Self-update machinery. `update.rs` swaps binaries (tar.gz extraction, `chmod 0o755`, rename dance,
  `--self-update-temp` re-launch), pins hardcoded asset names (`uad-ng-windows.exe`, `uad-ng-linux`, ...),
  and retries renames for 28 seconds to beat virus scanners. This is release-pipeline-specific.
- Multi-user phone assumptions. `pm list users`, `User.protected`, per-user package pages,
  cross-user OEM detection, and "Secure Folder" copy. Wear OS is effectively single-user.
- The 1.67 MB phone catalog. `resources/assets/uad_lists.json` holds ≈5400 phone entries.
  The schema transfers; the data does not.
- The CLI taxonomy. `--list oem` provenance filters and phone removal wording are tuned to phones.
  A watch tool needs watch-relevant buckets and defaults.

## 13. Limitations of This Analysis

- This analysis rests on static code reading. No physical device was attached. No ADB session ran.
- The analysis covers the snapshot at reference commit state as of 2026-11-09.
- Three wiki pages (Home, Usage, Debloat-Lists) supplemented the repository. Wiki text lives outside the repo,
  so it can drift from code. The category quotes came from the wiki fetch of 2026-11-09.
- The `Unlisted` definition has no wiki anchor. The analysis derives it from code defaults.
- File-size and entry counts came from text scans; they may differ by a few units from exact parser totals.
- Line counts are approximate (measured with PowerShell line counting).

END OF ANALYSIS.
