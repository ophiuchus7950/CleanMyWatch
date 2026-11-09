# CleanMyTV (cleanyourtv) — Reference Repository Analysis

Analysis date: 2026-11-09. This document records the analysis of the first reference
repository for a new smartwatch debloating project. It presents the repository model and
the verified command syntax with exact paths, keys, and identifiers.

## 1. Purpose

This document records the analysis of a reference repository. The new smartwatch project
will re-use the methods here. The analysed repository is CleanMyTV (project name
`cleanyourtv`). It sits at `reference/cleanyourtv`. The project cleans
Android TV devices over the network. It removes maker-added software. The licence is MIT.
The analysis read the repository only. The analysis changed nothing under `reference\`.

## 2. Reference Repository Overview

The project helps a computer control an Android TV. ADB is the Android Debug Bridge, the
standard debug protocol of Android. A package is one installable Android application with
a name such as `com.example.app`. A package name is one bundle of the app and its services.
The project disables packages for the main Android user. It never uninstalls.

Top-level layout:

| Entry | Purpose |
|---|---|
| `PROMPT.md` | The work order that a coding agent pastes and runs on the real TV. |
| `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` | The rulebook for coding agents; the last two import `AGENTS.md`. |
| `README.md` + 11 translations | The front page. Its tables are generated. |
| `examples/` | One folder per tested TV model. About 460 folders. |
| `docs/` | Troubleshooting, per-device notes, per-topic workflows. |
| `tools/` | The ADB client and the scripts. One shell script plus one PowerShell twin. |
| `themes/` | 28 theme folders; each has a `config.json` and a screenshot. |
| `addons/` | Separate small apps. They do not build into the launcher. |
| `launcher/` | One Android TV home app, package `com.gathin.tvhome`. |
| `tests/` | About 250 Python test files. They run without a device. |
| `.github/` | CI workflows, a review policy, and PR templates. |

Scale facts: about 460 device profile folders, about 250 test files, 28 themes, and tools
written in Python with bash and PowerShell twins. Every script states its usage in its
first lines. Complex tools have a `.md` guide beside them, such as `tools/trace.md`.

## 3. Device Optimisation Methodology

The workflow has ten stages. Each stage maps to one tool.

| Stage \| Stage Name | Tool | What it does |
|---|---|---|
| 1 Connect | `tools/tv.py` | Connects to the TV with TCP ADB. Uses `TV_HOST` and `TV_PORT`. |
| 2 Probe | `tools/tv.py --probe` | Prints model and build with `getprop` commands. |
| 3 Enumerate | `tools/tv.py 'pm list packages'` | Lists all packages and the disabled set. |
| 4 Classify | `PROMPT.md` + `tools/privacy.py` + `tools/match.py` | Sorts packages by purpose. Shows evidence, not verdicts. |
| 5 Record | `tools/recovery.py --save <list>` | Writes the pre-change state to `~/.cleanyourtv/`. |
| 6 Disable | `tools/disable.sh <list>` | Runs four safety gates, then batches `pm disable-user --user 0`. |
| 7 Verify | Read-back inside `disable.sh` + `tools/tv.py --screenshot` | Re-queries the enabled set. Captures the TV screen. |
| 8 Restore | `tools/restore.sh <list>` | Replays the recorded state through `tools/recovery.py --commands`. |
| 9 Drift-check | `tools/check.py <list> [--fix]` | Compares the TV against the list after a firmware update. |
| 10 Close | `tools/adb-closed.py <ip>` | Confirms the ADB port refuses connections. |

A debloat list is a text file of package names. Disable means one user loses the package,
and Android keeps the files. Install and Launcher stages use
`launcher/build-and-install.sh`. Theme push uses `tools/theme.sh`. One rule orders the
stages. The record stage must finish before the first disable command reaches the TV.
A failed record stops the run with the TV untouched.

## 4. ADB Integration

### 4.1 Transport

The default transport is pure Python. It uses the `adb_shell` package and class
`AdbDeviceTcp` over TCP port 5555. It does not need the `adb` binary. It signs the ADB
handshake with an RSA key in `tools/adbkey/`. It also offers the user's own key at
`~/.android/adbkey`, so the TV does not ask to allow the key twice.

### 4.2 Environment contract

| Variable | Meaning |
|---|---|
| `TV_HOST` | Required. The TV IP address, or `host:port`, or `[ipv6]:port`. |
| `TV_PORT` | Optional. Default `5555`. |
| `TV_ADB_BINARY` | Optional. Path to the Google `adb` binary. Selects the native backend. |

Invalid `TV_HOST` values are refused at import time. A value with `://` gets the message
"that is a URL, not the TV's address". A value with `/` gets "that is a path, not the
TV's address". These refusals use exit 2. They run before any socket opens.

### 4.3 Native backend

With `TV_ADB_BINARY` set, the tools shell out to the Google binary. Each command becomes
`adb -s <serial> shell -T -x <command>`. The serial is `host:port`. The wrapper first
checks `adb get-state` and answers `device` or stops. It never runs `adb tcpip`. It never
selects another connected device. Its `close()` leaves the shared ADB server alive. The
guide is `tools/native-adb.md`.

### 4.4 Exit codes

| Code | Meaning |
|---|---|
| 0 | The command ran. The TV's answer is in the output. |
| 1 | The TV ran something and it failed, or the answer got lost. |
| 2 | Refused before anything ran on the TV (bad flag, bad path, no `TV_HOST`). |

In batch mode the tool reads one command per line from stdin. It prints `$ <command>` and
then output. It skips blank lines and comments. A dropped connection mid-batch gives exit
1 and a message that names the command count: "the connection to the TV dropped while
running `<cmd>` (command N of this batch)... The TV may or may not have run it, and the
commands after it were not sent."

### 4.5 Key shell commands

| Command | Use | Used by |
|---|---|---|
| `pm list packages` | List installed packages. | Probe, classify, profiles. |
| `pm list packages -3` | List third-party packages only. | Device READMEs. |
| `pm list packages --user 0` | List packages installed for user 0. | Record. |
| `pm list packages -d --user 0` | List the disabled set. | Record, check. |
| `pm list packages -e --user 0` | List the enabled set. Read-back after every batch. | Disable, check. |
| `pm disable-user --user 0 <pkg>` | Turn the package off for user 0. One package per call. | Disable, fix. |
| `pm enable <pkg>` | Turn the package back on. Implies user 0. | Restore, fix. |
| `pm install -r /data/local/tmp/<apk>` | Sideload an APK. | Launcher install. |
| `cmd package install-existing <pkg>` | Reinstall a package that another guide removed for user 0. See the note below. | — |
| `pm uninstall -k --user 0 <pkg>` | Used by other guides, never by this repo. The tests cover its state effects. | — |
| `cmd package set-home-activity --user 0 <pkg/act>` | Set the default Home app. | Launcher install, restore. |
| `cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME` | Ask which app answers the Home key. | Home guard. |
| `cmd package query-activities --brief ...` | List all claimants of one intent. | Handlers guard. |
| `getprop ro.product.model` and `ro.build.version.sdk`, `ro.adb.secure`, `service.adb.tcp.port` | Read model, build, and ADB properties. | Probe, guards. |
| `dumpsys package <pkg>` | One package dump. Shows its own requested permissions. | TV-input guard. |
| `dumpsys wifi` | Show which app owns the saved Wi-Fi networks (`cname=` lines). | Wi-Fi guard. |
| `dumpsys activity` | Show the Home process on firmware without `cmd`. | Home guard fallback. |
| `settings get/put global <key>` | Read and set window animation scales. | Record, restore. |
| `input keyevent KEYCODE_<NAME>` | Inject a remote key, names only. | Screenshots. |
| `screencap -p /data/local/tmp/cleanyourtv-shot.png` | Capture, pull, verify PNG, then `rm`. | Verify. |
| `am start -W -a android.intent.action.MAIN -c android.intent.category.HOME -n <pkg>/.MainActivity` | Start and confirm an activity. | Launcher install. |
| `am force-stop <pkg>` | Stop a lingering process or reset key services. | Launcher install. |

Note on `cmd package install-existing`: the cleanyourtv scripts never uninstall and never
need this command. The repo's tests also treat `pm uninstall -k --user 0` output as a
package that is gone for user 0 only. Watch tools may need `cmd package install-existing`
because other watch guides do uninstall. CleanMyTV never uninstalls, so this command has
no caller in the repo.

### 4.6 Package name validation and user-0 rule

Every name that enters a device shell command passes one regex:

```
[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z0-9_]+)+     # tools/recovery.py PACKAGE_RE
```

The rule exists because package names are pasted into commands that the device shell runs.
Nothing that could carry shell syntax gets through. Key names for `input keyevent` pass a
second regex, `^[A-Z0-9_]+$`.

The user-0 rule: every command the tools send acts on user 0. `pm disable-user --user 0`
acts on user 0 only. `pm enable` with no user means user 0. Without `--user`, Android 14's
`pm` answers for all users and merges the answers. A package that only another user
disabled then reads as disabled for user 0. So all reads also use `pm list packages
--user 0` and `pm list packages -d --user 0`, with a fallback to the plain form only when
that `pm` errors on `--user`. This rule keeps the record and the read-back on user 0.

## 5. Device Profiles

`examples/` holds one folder per tested TV model. The folder name is lowercase with
hyphens, for example `examples/xiaomi-mi-box-s/`. Each folder holds:

| File | Required | Content |
|---|---|---|
| `debloat.txt` | Yes | The tested package list. |
| `tv.json` | Yes | This folder's row in the generated tables. |
| `README.md` | No | Free prose notes. Their package counts are tested against the list. |
| `config.json` | No | Dock and key config for the launcher on this device. |
| `debloat-<variant>.txt` | Rare | A second list, such as `debloat-keep-cast.txt`. |

### 5.1 debloat.txt format

The parser strips a BOM and CRLF line endings. It takes one package per line. It drops a
trailing `# note` after the name. It refuses the whole file if any entry fails the
package regex. The header is a comment block with the model, firmware, fingerprint, and
dated test notes. Three lines are a fixed part of the header. Sample lines from
`examples/xiaomi-mi-box-s/debloat.txt`:

```
# Apply:   TV_HOST=<box ip> tools/disable.sh examples/xiaomi-mi-box-s/debloat.txt
# Undo:    TV_HOST=<box ip> tools/restore.sh examples/xiaomi-mi-box-s/debloat.txt
# Everything is DISABLED, not uninstalled. Comment out any line you want to keep.
...
com.miui.tv.analytics                  # Mi analytics: reads logs and app usage
com.mitv.tvhome.atv                    # PatchWall
# com.amazon.amazonvideo.livingroom    # Prime Video  (commented = keep)
com.google.android.tvlauncher          # Stock Google TV launcher, replaced by launcher/
```

A commented-out line means "the tested set kept this on". The header notes record the
observed behaviour, for example "Survives a reboot: nothing is re-enabled at boot".

### 5.2 tv.json schema

`tv.json` has four required keys and one optional key.

```json
{
  "tv": "Xiaomi Mi Box S (MIBOX4, oneday), streaming box",
  "os": "Android TV 9",
  "brand": "Xiaomi",
  "notes": "PatchWall, Mi analytics, Alphonso ad tracking; 24 packages disabled"
}
```

| Key | Fills |
|---|---|
| `tv` | The device title in the table row. |
| `os` | The OS cell. |
| `brand` | The brand grid. Spell it exactly as the grid shows it. |
| `notes` | The notes cell. One Markdown line, links relative to `examples/`. |
| `readme_os` | Optional. A shorter OS cell for the two-column README table. |

`tools/gen_tables.py` generates every table and counter from all `tv.json` files. A list
PR adds one folder only. The generated blocks carry markers such as `<!-- tv-brands:start:
generated by tools/gen_tables.py from examples/*/tv.json; edit those, not this -->`.

### 5.3 config.json

The per-device launcher config uses these keys: `dock_apps` (package list, left to
right), `hidden_apps`, `live_tv_package`, `columns`, `rows_below_dock`, and `app_keys`
with entries shaped `"4062:com.netflix.ninja"`. Pushed with `tools/theme.sh`; no rebuild.

## 6. Package Classification and Safety

### 6.1 Taxonomy

`PROMPT.md` gives the agent this sort order: manufacturer telemetry and analytics;
manufacturer content and ad services; background services you probably do not need;
preloaded apps; streaming apps. Streaming apps, the voice assistant, casting, and the
firmware updater go behind one checklist question to the owner. The tools disable only
what the owner does not tick.

### 6.2 Protected core

`tools/disable.sh`, `disable.ps1`, and `tools/recovery.py` carry the same two patterns.
`tests/test_core_packages.py` keeps the three copies in step.

```
CORE_RE='^(android|android\.ext\.(services|shared)|com\.android\.sdksandbox|com\.android\.location\.fused|com\.android\.systemui|com\.android\.shell|com\.android\.phone|com\.android\.settings|com\.android\.tv\.settings|com\.(google\.)?android\.(permissioncontroller|packageinstaller|ext\.services|ext\.shared|modulemetadata)|com\.google\.android\.overlay\.modules.*|com\.android\.providers\..*|com\.cltv\.mal|com\.mediatek\.(tis|tv\.service|tv\.agent))$'

CORE_OK='^com\.android\.providers\.(calendar|contacts|userdictionary|blockednumber)$'
```

`CORE_RE` names the core and TV middleware packages. `CORE_OK` excludes four content
providers that tested lists turn off. The refusal text is exact:

> "refusing $LIST: it disables core Android or TV middleware packages, and without them
> the TV may not boot again (#884, #1578): ... Nothing was changed on the TV."

No switch overrides this check. `FORCE_HOME=1` and the other overrides do not apply here.

### 6.3 Four fail-closed runtime gates

Each gate checks the TV before it disables anything. If the check cannot read a state,
the gate skips the package and says why. Unknown never means proceed.

| Gate | Check | Skip condition | Override | What it prevents |
|---|---|---|---|---|
| Wi-Fi owner | `dumpsys wifi`, `grep -o 'cname=[^ ]*'` | The setup wizard `com.google.android.tungsten.setupwraith` owns the saved Wi-Fi, or the check cannot read it. | `FORCE_SETUPWRAITH=1` | Deleting the Wi-Fi network the TV is on. |
| HOME owner | `cmd package resolve-activity --brief ... -c android.intent.category.HOME`, fallback `dumpsys activity` (`mHomeProcess:`) | The list takes the app that owns Home, and no other enabled app answers Home. Setup wizards, settings apps, `*/FallbackHome`, and factory-test apps do not count. | `FORCE_HOME=1` | A TV with no Home app, and a crash loop. |
| TV-input | `dumpsys package <pkg>`; the package's own "requested permissions" block must contain `android.permission.TV_INPUT_HARDWARE` | The package drives the HDMI/AV/tuner inputs. Unreadable dumps mark the package `NOCHK`; a hung system marks it `HUNG`; both skip. | `TVINPUT_ALLOW=1` | Black HDMI inputs that only a full restore and a cold boot fix (#321). |
| Handlers | `cmd package query-activities --brief` for `ACTION_VIEW` with type `vnd.android.cursor.item/channel`, and for `android.settings.SETTINGS` | The package opens the inputs or opens Settings. | `HANDLERS_ALLOW=1` | Input tiles that do nothing. Losing the path back to Developer options. |

Each override set in the environment prints one note: "note: FORCE_HOME=1 is set; the
safety check it overrides stays off until it is cleared (unset FORCE_HOME)." The script
also warns when `getprop ro.adb.secure` is `0` or empty. Port 5555 then answers any
device on the network without an allow prompt.

### 6.4 Read-back verification

After the batch, the script does not trust the exit code. It fetches the enabled set and
diffs it against the list:

```
ENABLED=$(pm list packages -e --user 0)     # via tv.py
STILL_ON = listed packages still in ENABLED
```

The message reads: "Still enabled after this run, although the list disables them:". It
then tells what to do: run each disable once by hand, run the list once more after a
reboot, never in a loop. If every listed package stays enabled, the firmware refuses
`pm disable-user`. The run stops there and says so. The exit status is then 1.

### 6.5 Evidence and labels

`tools/privacy.py` prints what the firmware says about voice, ACR, and telemetry, with
the evidence for each candidate. Its stated limit: "It never claims a package is
listening." A hand-curated map gives the category `voice`, `acr`, `telemetry`, or
`unknown` with a note. Name-only matches stay out of the generated list unless the caller
passes `--include-low`. `tools/match.py` works offline. For each package it prints how
many tested lists disable it, how many keep it commented, and their most common note.
Core packages show as `never`. It ranks nothing.

The example READMEs carry their own evidence labels. Phrases like `reboot-checked` and
`not yet checked across a reboot` state the depth of each test. Header notes carry dated
per-unit reports, for example "Fifth unit (same PI.3933 build), 2026-10-25".

## 7. Restoration and Recovery

### 7.1 The record

`tools/recovery.py --save <list>` queries the TV and writes the record before the first
change. One record file per TV address and list lives in `~/.cleanyourtv/` with the name
`recovery-<ip>-<digest>.json`. `<ip>` is the LAN address the TV was reached at (a host
name also works). `<digest>` is the first 8 hex characters of the SHA-1 of the absolute
list path. The record schema:

```json
{
  "version": 1,
  "created": "<ISO timestamp with zone>",
  "host": "192.168.1.50",
  "list": "<absolute path of the debloat list>",
  "home": "<package/activity component>",
  "settings": {
    "window_animation_scale": "<value>",
    "transition_animation_scale": "<value>",
    "animator_duration_scale": "<value>"
  },
  "packages": {
    "<pkg>": "enabled",
    "<pkg>": "disabled",
    "<pkg>": "absent"
  }
}
```

Each package state is `enabled`, `disabled`, or `absent`. `disabled` or `absent` mean the
record already had it off, so restore leaves it alone.

### 7.2 First record wins and extend_record

A retry never overwrites the record. The first record is the only copy of the TV before
cleanup. `--save` on an existing record only extends it. `extend_record` adds names the
list gained since, with their state now, and sets a package recorded as `absent` that is
now installed and enabled to `enabled`. Writes are atomic: a temp file, `fsync`, then
`os.replace`. A record under another address that reads like this TV after cleanup gets a
warning, not a guess. The choice stays with the owner.

### 7.3 The undo batch

`recovery.py --commands <list> [stock launcher]` prints the undo batch for
`tools/tv.py --batch`. It needs no TV. It needs `TV_HOST` only to name the record. The
batch does this: for each state `enabled` it prints `pm enable <pkg>`. For other states
it prints one line to stderr, "leaving <name> alone (state when the record was taken)".
It replays Home with `cmd package set-home-activity --user 0 <component>`, except when
the recorded Home was the repo's own launcher, a chooser, a setup wizard, or absent. It
replays the three settings with `settings put global <key> <value>`, or
`settings delete global <key>` for `null`. It ends with `pm list packages -d`.

Without a record, the fallback batch enables every listed package, resets Home, and sets
the scales to `1.0`. The message says that packages already disabled before cleanup get
enabled too. It also names the records under other addresses.

### 7.4 The wrappers

`tools/restore.sh` validates the arguments, then pipes:

```
recovery.py --commands "$LIST" "$STOCK" | tv.py --batch
```

It refuses a dash-led word as the list or the stock package, and any third argument, with
exit 2 and the message "Nothing was sent to the TV". `restore.ps1` is the twin.
`launcher/build-and-install.sh` also has a rollback path. If Home does not land on the
new launcher, it re-enables the stock launcher, resets Home, and writes a recovery
command file with the exact remaining commands.

## 8. Testing Without Hardware

The test suite needs no device. CI builds the suite on GitHub runners. The main kinds:

| Test kind | Example files | What they assert |
|---|---|---|
| Fake-TV integration | `test_recovery_record.py`, `test_drift_check.py`, `test_privacy_audit.py` | The real `disable.sh`, `restore.sh`, `check.py` run against a fake TV script in a scratch repo. |
| Stubbed-transport unit tests | `test_tv_target.py` | `tools/tv.py` imports with mocked `adb_shell` modules. Assert `TV_HOST` and `TV_PORT` parsing and refusals without a socket. |
| Parity tests | `test_core_packages.py`, `test_recovery_home_not_a_launcher.py` | The shared regexes and word sets stay identical across `disable.sh`, `disable.ps1`, and `recovery.py`. |
| User-0 merge tests | `test_user0_package_state.py` | A fake answers `pm list packages` the way Android 14 merges two users. Restore must still enable what the owner had on. |
| List-format validators | `test_examples.py`, `test_example_list_count.py` | Each profile parses, and the README's "N packages" matches the actual list. |
| Doc-consistency tests | `test_documented_tool_commands.py`, `test_markdown_links.py`, `test_tv_py_flags_in_docs.py` | Documented commands parse as typed. Links and flags in docs stay real. |
| Launcher tests | `tests/` plus Gradle | Unit tests, lint with zero errors, and a release build. |

The CI jobs in `.github/workflows/ci.yml`:

- `lists-and-tools`: Python 3.12, a `tools/venv`, then `unittest discover -s tests -v`
  with `CLEANYOURTV_STRICT=1` on main.
- `tables`: `python3 tools/gen_tables.py --check` must match the generated README tables.
- `launcher`: Gradle `testReleaseUnitTest lintRelease assembleRelease`, then an APK size
  gate. The APK must stay under 589824 bytes. The error text: "the launcher targets
  1 GB TVs, keep it small".

Windows machines skip the suites that drive `tools/*.sh`. CI runs them on Linux. Only
launcher visual changes need a real-TV screenshot in the PR description.

## 9. User-Facing Documentation Style

The README follows this order: a decision table ("Start here"), a three-row "How it
works" table (back up, disable, install), a"Quick start" table written for a coding
agent, screenshots, the "Supported TVs" grid, a "Doing it by hand" section with a
copy-paste command block, a Tools table where every row is one tool contract, FAQ entries
in collapsed boxes, three emoji-tagged troubleshooting bullets, legal text, and the
licence.

`PROMPT.md` is the imperative work order. It uses sections: Connect / Back up first /
Debloat / Launcher / Verify. Every rule names its exact failure signature and fix. Two
quoted examples:

> "Run `pm` commands one per shell call, chained commands may silently stop after the
> first."

> "wait about 15 seconds before rebooting - Android writes package state to disk about
> ten seconds after a change (`WRITE_SETTINGS_DELAY`)"

`AGENTS.md` opens with a job-routing table ("You were asked to: Clean up a TV - follow
PROMPT.md exactly... Change this repo - read on"). It then states the not-negotiable
rules, a repo map, a change-routing table, and a hard-rules list ("No prebuilt APKs or
binaries... No uninstalling... No network in the launcher"). `CLAUDE.md` and `GEMINI.md`
are three-line files that import `AGENTS.md` with `@AGENTS.md`.

Complex tools have a `.md` guide beside them, for example `tools/trace.md`,
`tools/screendiff.md`, and `tools/native-adb.md`. Each guide carries: one line of
purpose, a setup command, the exact command block, an options table, an exit-status table
(`| Exit status | Printed | Meaning |`), and a "Rules" section.

The risk language is blunt and directional. One FAQ answer: "If the TV no longer starts
far enough for that, a factory reset from its recovery menu is usually the way back."
The docs never say "be careful". They name the toggle, port, command, and symptom.

## 10. Findings

What makes the methodology strong:

1. **Record before any change.** The undo file is written before the first
   `pm disable-user --user 0` reaches the TV. The first record always wins. A failed
   record stops the run with the device untouched.
2. **Read-back verification.** The scripts do not trust exit codes. After every batch
   they diff the enabled set against the list and report each target that stayed on.
3. **Fail-closed guards.** Four runtime gates skip packages when a state is unreadable.
   Unknown means skip, not proceed. Each skip message names the override and its cost.
4. **No uninstall, ever.** All applied state stays reversible with `pm enable`. Listing
   `pm uninstall` becomes a hard rule violation, at repo and agent level.
5. **Safety rules cite their incidents.** Refusal messages carry issue numbers such as
   #884 and #1578. Every rule names the event that created it, so agents learn why.
6. **Data-driven docs.** All tables and counters generate from `tv.json`. A device PR
   adds one folder and one JSON file. Generated blocks are marked and never edited by
   hand.
7. **A real exit-code contract.** 0 ran, 1 ran-and-failed, 2 never-reached holds across
   the whole toolset. Error messages answer in plain words at every failure point, at
   import, on connect, and mid-batch.
8. **Honest evidence tools.** `tools/privacy.py` reports evidence, never intent.
   `tools/match.py` prints consensus counts, never a verdict. The tools say what they
   cannot know.

## 11. Adaptation to the Smartwatch Repository

The smartwatch repo (`cleanmysmartwatch`) can map each of these ideas:

1. **Apply the user-0 rule.** What: all package queries and changes scope to user 0.
   How: add `--user 0` to every `pm list packages` and `pm disable-user` on the watch, as
   CleanMyTV does.
2. **Read-back verification.** What: after every batch, diff and re-enable targets.
   How: fetch `pm list packages -e --user 0` on the watch and compare with the watch
   profile list.
3. **Record before change.** What: a state record holds the watch before the first
   disable. How: write a `watch-state` record that maps packages to `enabled|disabled|absent`,
   and keep the first-record-wins rule and `extend_record` behaviour.
4. **Disable, never uninstall.** What: the watch profile only turns packages off.
   How: make `pm uninstall` a hard rule violation in the agent file, and use `pm enable`
   as the whole undo surface.
5. **Protected core set.** What: a `CORE_RE`-style regex names never-disable packages.
   How: build a watch set with systemui, keyguard, BT and Wi-Fi pairing services, the
   health/sensor stack, telephony, and Store; model the analog as a `CORE_RE` + `CORE_OK`
   pair.
6. **Fail-closed gates with named overrides.** What: each gate checks the watch, skips on
   unreadable state, and names one override variable. How: port the four gate shapes with
   sensor, screen, and BT health checks, and gate overrides such as `FORCE_*` variables.
7. **Device-specific profiles.** What: one folder per tested watch. How: a
   `watch/<brand-model>/` profile folder with the debloat.txt analogue and a
   `watch.json` schema with `tv`-like description, OS, brand, and notes keys.
8. **Apply in small batches.** What: batches keep failures local. How: do not bundle by
   category; screenshot/state-dump between batches, with issue-cited rewrite rules.
9. **Offline consensus matcher.** What: show how many profiles support each candidate.
   How: `match.py` reads a saved watch package list against the collection of profiles
   and marks core as never.
10. **Honest-evidence audit.** What: report what the firmware says, with evidence and no
    claims about intent. How: build a `privacy.py` analogue for use cases such as
    voice/health/work data profiles with a hard limit on `--include-low` name-only
    matches.
11. **Drift check after updates.** What: a check/fix pair compares with the applied list
    after firmware updates. How: keep the record; fix only when the profiles match state.
12. **Exit-code contract and lost-connection wording.** What: 0, 1, 2 carries the same
    meaning everywhere. How: on a mid-batch drop, print which command ran, which did not,
    and what to check next.
13. **Pure-Python transport with a binary fallback.** What: no locked platform tools as
    the base, with a native path for paired transports. How: reuse the `adb_shell`
    approach and the env contract behind a `WATCH_HOST`-style interface, keeping
    regex validation.
14. **Test without hardware.** What: fake-device tests, parity tests, doc tests. How:
    use fake watch harnesses and keep shared regexes in duplicate files identical.
15. **Generated tables and labels.** What: one JSON per device feeds a generated doc
    table. How: `gen_tables.py`-style generation over the watch profiles, and labels
    such as `reboot-checked`/`not yet checked across a reboot` in the profile notes.

## 12. Non-Transferable Components

1. **`launcher/` home app.** The TV launcher is a 572 KB App with a D-pad UI and a
   module-card protocol. A watch cannot replace its Home with a sideloaded launcher. The
   design philosophy (small, offline, no network permission) transfers. The code does not.
2. **Port-5555 ADB closing flow.** `tools/adb-closed.py`, the `ro.adb.secure` warning, and
   the wireless debugging checks assume plaintext TCP ADB on the LAN. Watches reach ADB
   over USB, Bluetooth, or companion apps. A watch repo needs its own close-out protocol
   with the same "only the tool saying closed counts" rule.
3. **TV-input and HDMI guards.** The `android.permission.TV_INPUT_HARDWARE` check and the
   passthrough channel intent checks exist in the TV framework. Watches have no HDMI.
   The pattern (ask the framework which app answers a critical intent before you disable
   it) transfers. The exact commands do not.
4. **The `cmd package` Home-activity machinery.** `cmd package set-home-activity`,
   `resolve-activity ... category.HOME`, and the crash-loop guards exist only on Android
   TV. A watch Home is a system component; a watch tool has other load-bearing services
   to guard.
5. **The themes and UX package.** 28 themes, wallpapers, screensavers, 31 languages.
   A watch cleanup project's value is health and battery hygiene, not a new UI. Keep from
   it only the config-without-rebuild idea, if a watch tool needs per-device overrides.

## 13. Limitations of This Analysis

This limit applies to all sections above:

1. **Date.** The analysis records the state of the repository copy on 2026-11-09. The
   repo moves fast; issue numbers and examples may change.
2. **Only static source.** The analysis read files. No device connected, and no commands
   ran on real hardware. All `pm`, `getprop`, `dumpsys`, and `cmd package` syntax comes
   from source code, docstrings, docs, and tests.
3. **No Wear OS coverage in the reference.** The reference repo tests only Android TV,
   Google TV, and Fire TV. `examples/` holds zero watch models. The watch protected set
   and the watch-specific failure modes need their own field data.
4. **Windows analysis host.** The analysis ran on Windows. The POSIX-shell suites that
   drive `tools/disable.sh` skipped the local shell; CI covers them. PowerShell twin
   testing on Windows went through dedicated test files, not a run.
5. **The ~460 profiles vary in depth.** Some lists state `reboot-checked`; others state
   `not yet checked across a reboot`. Re-use any exact list with care, not as a default.

END OF ANALYSIS.
