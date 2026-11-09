# Universal Android Pre-installed Lists — Reference Repository Analysis

Analysis date: 2026-11-09.
Reference path: `reference\universal-android-preinstalled-lists` (read-only). Cross-check: UAD-ng at `reference\universal-android-debloater-next-generation` (read-only).
Method: I read all three repo files, plus the UAD-ng ingest file `crates/uad-core/src/uad_lists.rs`.
I scanned the live data file `resources/assets/uad_lists.json`. I fetched two UAD-ng wiki pages and the upstream README for cross-checks.

## 1. Purpose

This repo is a data-methodology reference for our smartwatch package database.

It shows how a community stores, formats, and governs a package-knowledge dataset.
Our smartwatch tool will consume a similar database. We copy the conventions, not the phone content.

Facts about the reference repo:

- Path: `reference\universal-android-preinstalled-lists`. Licence: GNU LGPL v3 (29 June 2007). Commit history: `f164e3a switch to LGPL3`.
- The repo is scaffolding. It contains three files: `README.md` (26 lines), `LICENSE`, and `.editorconfig`.
- It has one branch (`main`), ten commits, and no tags.
- It holds no package data yet. The UAD-ng repo currently carries the data.
- The latest commit merges PR #2 (`editconf`), which added `.editorconfig`.

Note: this reference repo describes the methodology. The UAD-ng repo carries the data.

## 2. Reference Repository Overview

The README declares the goal (line 2, verbatim):

> The set of all known [built-in](https://en.wikipedia.org/wiki/Pre-installed_software) [Android](https://www.android.com/) packages, with:
> - descriptions
> - source/authors
> - removal recommendations
> - dependency declarations

The README adds (line 8): `Will be used primarily by [UAD-NG]`.

The name has a rationale (README §Name, verbatim quotes, compressed):
"Universal" covers many devices. "Android" excludes a general pack database. "Pre-installed" means not all is bloat.
"Lists" (plural) points to split files.

The repo exists because the community split the lists out of the UAD-ng app repo (README §Why):

> This repo was created in response to [this](...universal-android-debloater-next-generation/discussions/646), and because we (the org members) have "voted" (not formally) and agreed that it had to be done.

The README gives three split reasons (verbatim bullets):

- `Better issue/PR management and organization`
- `Versioning: more predictable "API" for 3rd-party consumers (such as [Canta])`
- `Multi-list support`

Lesson: separate data from code when third parties will consume the data. Use discussions for naming, and issues and PRs for data.

## 3. Package Entry Format

The entry syntax is not in the README. The canonical spec lives in the UAD-ng wiki page `How-to-contribute`.
The wiki page states the source of truth (verbatim):

> The UAD-ng list is a JSON (we're [reconsidering that](discussions/608)) that can be found [here] (for now) and [here] (future).

The wiki page specifies a package entry. Quote, verbatim:

> A package is defined like this:

```json
"com.google.mainline.telemetry": {
    "list": "Google",
    "description": "First line of the a description\nThis is a new line",
    "dependencies": null,
    "neededBy": null,
    "labels": null,
    "removal": "Unsafe"
},
```

Field meanings (as the wiki defines them):

- Package name: the JSON key. It is the full Android package name, for example `com.google.mainline.telemetry`.
- `list`: the origin bucket. Allowed values: `Google`, `Misc` (miscellaneous), `Oem`, `Aosp`, `Pending`, `Carrier` (ISP).
- `description`: free text. Newline characters separate sentences. The first line identifies the app.
- `dependencies`: package names this package requires. The wiki says: `Only the **absolutely-required** deps are listed.`
- `neededBy`: the reverse-dependency list. The wiki calls it redundant and `might be removed`.
- `labels`: free tags. The wiki says: `Will be removed in a future version`.
- `removal`: the risk category. Allowed values: `Recommended`, `Advanced`, `Expert`, `Unsafe`.

Three schema gaps matter for our design:

- No dedicated app-name field. The first description line supplies the identity.
- No restore-command field. An early pipe-separated format had a `Fix` field. The JSON schema dropped it.
- No per-device field. Device context stays in description prose, or later in per-vendor files.

Data shape from the live file: top level is one JSON object. Keys are package names. Values are entry objects.
Size: 1.6 MB, about 5402 entries. Most entries set `dependencies`, `neededBy`, and `labels` to empty arrays, not `null`.
UAD-ng parses with Serde under `#[serde(rename_all = "camelCase")]`. The Rust field `needed_by` maps to JSON key `neededBy`.

## 4. Description Conventions

### 4.1 The triplet template

Most clean entries follow a three-line grammar.
Line 1 identifies the app. Line 2 says when removal is safe. Line 3 names the loss.

Verbatim example from the live JSON (`org.lineageos.aperture`):

```text
"LineageOS Camera App.\nSafe to remove if you've replaced it with another app.\nOtherwise there will be no camera app on your device."
```

The same triplet appears for browser, calendar, and gallery packages. It fills the "Safe to remove" and "Keep" roles; the schema has no boolean for either.

Other safe-phrasing variants (verbatim): `"Safe to remove if you don't need it or have replaced it with another app."`, `"Can be safely removed if you don't need/use it."` (Pixel Watch package `com.google.android.wearable.pixel.aspen`), and `"Removing it just removes the Dolby Atmos feature and its app. Safe to remove if you don't need it."`

### 4.2 Conditional-safety phrasing

Safety depends on state, not only on the package. Verbatim sample: `"Only safe to remove if you have removed gms."`
The project does not auto-remove dependents. The wiki says dependencies are advisory. Conditional sentences carry the real removal logic.

### 4.3 Breakage wording

Removal effects name concrete symptoms (verbatim): `"removing may cause a bootloop."` (`android.ext.shared`), `"Not safe to remove; could break Updater UI on devices with WitAqua ROMs."`, and `"Totally not safe to remove, it's as important as 'android'"`.

### 4.4 ALL-CAPS warning blocks with legality rationale

Safety-critical entries use a capitals warning block. Abbreviated verbatim sample: `"!!! WARNING !!! DO NOT DELETE THIS PACKAGE, EVEN IF YOU ENABLED REMOVAL OF UNSAFE PACKAGES. THIS PACKAGE WON'T BOOTLOOP YOUR DEVICE ..."` and `"...removing this package might violate the SAR (Specific Absorption Rate) law in EU."`
The entry mixes health risk, network instability, and legal violation. The `Unsafe` definition also cites legality (section 5).

### 4.5 Version notes and per-device notes

The schema has no version field and no device field. Sentences carry both (verbatim):
`"Introduced in Android 13."` and `"Introduced in Android 14(com.google.android.federatedcompute Introduced in Android 13)."`
Descriptions also cite official Android docs, for example `https://source.android.com/docs/core/ota/modular-system/ondevicepersonalization`.
Device-scope samples: `"a framework package that powers all the system UI on ZTE, Nubia, Axon & Blade devices"`, `"found on Lenovo devices mostly"`, `"AOSPA's Dolby Atmos App on custom ROMs for Xiaomi phones"`.

### 4.6 Relations and syntax negatives (verified by grep in the live JSON)

Reverse-dependency lists are sparse. Example: `"dependencies": ["com.felicanetworks.mfc"]`, `"neededBy": ["com.felicanetworks.mfw.a.boot", "com.felicanetworks.mfm.main"]`.
Carrier-provisioned Felica and NTT docomo packs use these lists. The field is otherwise rare.

Syntax negatives found:

- No dependency arrows in descriptions. Relations live only in `dependencies` and `neededBy`.
- No federated-app marker. "Federated" appears only as plain words in two package descriptions.
- No multi-page naming, for example `sys.2|`. None was found.
- `labels` is empty in every scanned entry. The wiki plans to remove the field.
- Descriptions sometimes self-correct (verbatim): `"There's no such package as com.google.android.wifi.resources, but only com.android.wifi.resources."` Correcting prose is part of the culture.

## 5. Category Definitions

Two independent dimensions classify each package: sourcing list and removal category.

### 5.1 The origin (list) buckets

From the ingest enum `UadList` (verbatim order): `Aosp, Carrier, Google, Misc, Oem, Pending, Unlisted`, plus a synthetic filter `All`.
The wiki `Debloat-Lists` page summarizes vendors: "GFAM (Google/Facebook/Amazon/Microsoft), AOSP, Manufacturers (OEMs), Cellular carriers, Qualcomm / Mediatek / Miscellaneous".
Coverage tracking uses per-OEM checklists (Asus, Xiaomi, Samsung, ZTE, and 20 more) and a per-country carrier table (France, USA, Germany, UK, Italy, Japan).
Pixel rule-of-thumb (wiki, verbatim): `If an app is a Pixel-exclusive, list should be Oem not Google (this is just a rule-of-thumb, not strict). Google is more appropriate for Gapps that might be installed on any device.`

### 5.2 The removal categories — verbatim definitions

From the UAD-ng wiki page `Debloat-Lists`, section "Removal definitions":

> - `Recommended` -- Any package that's safe to uninstall ([this will change]), and/or apps available through whatever app-store is built-in (G Play, Samsung Galaxy Store, etc...). Despite being "safe to remove", you should review them anyways, as different people have different needs and preferences.
> - `Advanced` -- Breaks obscure or minor parts of functionality, [overlays], or apps that aren't easily enabled/installed through Settings/Google Play. This category is also used for apps that are useful (default keyboard/gallery/launcher/music app.) but that can easily be replaced by a better alternative. This removal-type might be merged with `Expert` in the future.
> - `Expert` -- Breaks widespread and/or important functionality, but nothing important to the basic operation of the operating system. Removing an `Expert` package *should not* boot-loop the device (unless mentioned in the description) but we can't guarantee it 100%.
> - `Unsafe` -- Can break vital parts of the operating system or is illegal to remove in your country (e.g. emergency alerts, or SAR certification law in EU). Removing an `Unsafe` package have an extremely high risk of boot-looping your device.

`Unlisted` has no definition on that page. The wiki `How-to-contribute` page gives its operational definition:

> All non-documented packages can be displayed by selecting the **unlisted** filter.

So `Unlisted` means: present in the dataset, not yet documented.
Note the calibration language. Each definition names the failure level, the restore cost, and a legal clause.

### 5.3 Distribution in the live data (counted on 2026-11-09)

Counts: Recommended 3021, Advanced 1160, Expert 923, Unsafe 298, Unlisted 0. Total: about 5402 entries.
Interpretation: most entries are safe or replaceable. Critical entries are few. App filters compute the Unlisted set at runtime, so the baked zero is expected.

## 6. Data Distribution and Consumption

### 6.1 How UAD-ng ingests the list

File: `crates/uad-core/src/uad_lists.rs`. Verbatim constants:

```rust
pub const LIST_FNAME: &str = "uad_lists.json";
pub static DATA: &str = include_str!("../../../resources/assets/uad_lists.json");
```

The ingest builds one URL. Verbatim (line breaks in the Rust source fold the string):

```rust
"https://raw.githubusercontent.com\
    /Universal-Debloater-Alliance\
    /universal-android-debloater\
    /main\
    /resources\
    /assets\
    /{LIST_FNAME}"
```

Note the quirk: the remote URL still points to the old repo `universal-android-debloater`, not `-next-generation`, and not `universal-android-preinstalled-lists`.

Fetch policy (verbatim pieces of code):

```rust
retry(Fixed::from_millis(1000).take(60), || { ... })
let text = data.body_mut().with_config().limit(1 << (3 + 10 + 10)) // 8 MiB cap
fs::write(cached_uad_lists.clone(), &text)
serde_json::from_str(&text)
```

The fallback chain is:

1. Fetch remote. Retry up to 60 times at 1 s intervals.
2. On failure, read the cache file `CACHE_DIR/uad_lists.json`.
3. If no cache file, parse the snapshot `DATA` compiled into the binary. Each successful fetch writes to the cache; then parsing yields `PackageHashMap`.

### 6.2 The parsed record

Verbatim struct:

```rust
#[derive(Deserialize, Debug, Clone, PartialEq, Hash, Eq)]
#[serde(rename_all = "camelCase")]
pub struct Package {
    pub list: UadList,
    pub description: String,
    dependencies: Vec<String>,
    needed_by: Vec<String>,
    labels: Vec<String>,
    pub removal: Removal,
}
```

The `Removal` enum matches the five categories plus a synthetic `All`. The UAD-ng README promises only `GET` requests to GitHub for the list and update checks.

### 6.3 Contributor verification toolkit

The wiki documents how contributors gather evidence:

- Decompile APKs with Jadx (recommended), Apktool, or Bytecode Viewer.
- Locate a package with `adb shell pm path com.test`. Strip the `package:` prefix. Fetch the APK with `adb pull /odm/overlay/test.apk`.
- Inspect with SD Maid v2 "Apps checker", AppManager, APK Studio, or logcat readers.
- Query online services such as Pithus.

## 7. Contribution Discipline

### 7.1 Issue labels and templates

UAD-ng labels issues automatically by template (from CONTRIBUTING.md):

- `package::addition` — "Add new package(s)".
- `package::breakage` — "Debloat issue report". `package::documentation` — "Update apps description or recommendation".
- These three feed the "Packages/apps" section of auto-generated release notes (`.github/release.yml`).

### 7.2 The mass-automation disclosure rule

CONTRIBUTING.md requires disclosure of automated bulk edits. Verbatim rule: `You must specify what automation you used.` It covers `sed`, `jq`, and also AI: `And it also applies to AI, *especially* LLMs.`

The guide demands a reproduction command, for example a `sed -i` command plus a `git diff <commit>` proof. It warns about collateral damage (the "Scunthorpe problem"). Quote, verbatim:

> Since AI is non-deterministic, the version number is optional, but it's helpful to know how "intelligent" it is. AI edits are non-reproducible, so "verification scripts" are useless.

Lesson: data patches must attach their commands. AI edits need extra care and manual review.

### 7.3 Branching and commit messages

- Trunk-based development. One trunk branch: `main` (or `master`). Short-lived branches: `feature/*`, `hotfix/*`, `deps/*`.
- Package work branches use scheme `[issue number][issue title]`.
- Commit messages follow Conventional Commits, and authors close issues with closing keywords.

### 7.4 File-format hygiene

From `.editorconfig` of the reference repo:

- Charset: UTF-8. Line endings: LF. Indent style: tab, indent size 4. Trailing whitespace trimmed.
- JSON files get no final newline (`insert_final_newline = false`).

From the git history: authors use Conventional Commits (`docs(README):`, `chore:`), and each PR carries one focused change.

## 8. Findings for a Smartwatch Database

1. Reuse the schema shape. Keep the flat JSON map keyed by package name, with the six fields above.
2. Simplify the schema early. The `labels` field and the `neededBy` reverse-list carry deprecated weight in UAD-ng. Keep `dependencies` only, or mark `neededBy` as experimental.
3. Adopt the description grammar on day one. Give each entry an identity line plus a loss line at minimum. Add a `safe-if` line when replacement matters.
4. Add evidence-first policy to entries. Require version notes like "Introduced in Wear OS 4". Require command-level disclosure for mass edits, as UAD-ng does.
5. Select LGPL-3.0 for the data repo, and keep app code in a separate repo. LGPL keeps the data free for third parties without triggering licence spread.
6. Name buckets after origin, not after device model, for example `Aosp`, `Google`, `Oem`, `Wear-companion`. Track device coverage with checklist pages, not with fields.
7. Drop the cellphone-specific bucket. Watches have no carrier provisioning. The `Carrier` taxonomy adds no watch content.
8. Recalibrate the removal categories for smartwatch OS-criticality. Bootloop boundaries shift when storage is 16 to 32 GB and battery capacity is small. Small-looking watch apps can still sit at a category boundary. Re-derive each Expert/Unsafe boundary, and test removals on a watch.

## 9. Non-Transferable Components

- The `Carrier` bucket and per-carrier tables. No cellphone carrier taxonomy makes sense for a watch.
- The phone-criticality calibration itself. Expert/Unsafe boundary definitions encode phone boot-sequence needs and SAR law; copy them only as a starting point.
- The wired-ADB verification loop (`adb shell pm path`, `adb pull`, USB). Watch evidence-gathering must use ADB-over-WiFi or companion-app steps.
- The `labels` field and the `neededBy` reverse-list. UAD-ng already plans to drop them; a fresh smartwatch schema should not inherit deprecated weight.

## 10. Limitations of This Analysis

- The reference repo is scaffolding. Its README has no syntax spec; the spec lives in the UAD-ng wiki, outside the repo. Format is under reconsideration (discussion 608).
- Counts come from a snapshot of the baked JSON asset in UAD-ng, not from an online live feed. They are approximate and dated.
- Data location may change again. The remote ingest URL points to another repo path than the data repo itself.
- Wiki content is mutable. Category definitions may already differ upstream since this analysis (2026-11-09).

END OF ANALYSIS.
