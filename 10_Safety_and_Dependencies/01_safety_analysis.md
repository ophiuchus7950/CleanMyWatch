# Safety Analysis and Critical Dependencies

## 1. Purpose

This document defines which packages support essential watch functions.
These packages form the protected core set. The debloating engine
refuses to touch the protected core set. Classification rules in
`09_Package_Classification/01_classification_methodology.md` use this
set as decision rule 1.

## 2. Scope

The analysis covers Wear OS packages. Package sets differ between
manufacturers and OS versions. Entries here use verified package names
from the Galaxy Watch 4 dump
(`08_Package_Database/data/discovery_galaxy_watch4.json`).
Function categories apply across Wear OS devices.

## 3. Essential Function List

The project module list defines these essential functions. A package
that provides one of these functions belongs in the protected area:

| Function area | Packages that carry it (verified examples) |
|---|---|
| System UI and launcher | `com.google.android.apps.wearable.systemui`, `com.samsung.android.wearable.sysui`, `com.google.android.wearable.overlay.home.merlot` |
| Bluetooth | `com.android.bluetooth` |
| Wi-Fi and network stack | `com.samsung.android.networkstack`, provider `com.android.providers.*` network resources |
| Health and fitness engine | `com.google.android.wearable.healthservices` |
| Battery and charging | `com.google.android.wearable.batteryservices` |
| Ambient mode | `com.google.android.wearable.ambient` |
| Call and telephony UI | `com.samsung.android.app.telephonyui`, `com.samsung.android.incallui`, `com.android.phone` |
| Phone–watch connection | `com.samsung.android.clientconnection`, `com.google.android.wearable.app` |
| Play Store and app install | `com.android.vending`, `com.google.android.packageinstaller`, `com.samsung.packageinstalleroverlay` |
| Google Play Services | `com.google.android.gms`, `com.google.android.gsf` |
| Safety and emergency | `com.samsung.android.watch.safety_assistance`, watch face `com.samsung.android.watch.watchface.emergency` |
| Authentication and security | `com.google.android.permissioncontroller`, `com.google.android.ext.services`, `com.google.android.ext.shared` |
| Setup and recovery | `com.samsung.android.wearable.setupwizard`, `com.google.android.clockwork.oemsetup` |
| Voice input services | `com.google.android.tts`, `com.samsung.android.honeyboard` (keyboard for text input) |

## 4. Protected Core Pattern

The engine matches this regular expression against package names.
A match means the package is protected. The expression is the
smartwatch adaptation of the CleanMyTV `CORE_RE` pattern.

```
^(android|
com\.android\.(bluetooth|phone|shell|sdksandbox|systemui|
               location\.fused|
               settings|
               providers\..*|
               ext\..*|
               immersive\.audio|
               smartspace|
               vending|
               seapp.*
)|
com\.google\.android\.(gms|gsf|gsf\.login|
                       packageinstaller|
                       permissioncontroller|
                       ext\.(services|shared)|
                       partnersetup|
                       tts|
                       settings\.intelligence|
                       apps\.wearable\.systemui|
                       apps\.wearable\.settings|
                       apps\.wearable\.wearablesocial|
                       wearable\.healthservices|
                       wearable\.batteryservices|
                       wearable\.ambient|
                       wearable\.frameworkpackagestubs|
                       wearable\.overlay\..*|
                       wearable\.app|
                       wearable\.sysui|
                       wear\.assistant(.ble)?,
                       wear\.modesprovider,
                       wear\.support\..*,
                       wear\.sync\..*
)|
com\.samsung\.android\.(wearable\.sysui|
                        wearable\.setupwizard|
                        wearable\.samsungaccount|
                        wear\.samsungaccount|
                        clientconnection|
                        enterraneous.*,
                        networkstack,
                        app\.samsungapps.*,
                        secure\.usim.*,
                        knox\..*,
                        wearable\.knox\..*,
                        mdecservice,
                        hidden\..*,
                        samsungpositioning.*
)|
com\.sec\..*|
com\.android\.cellbroadcastreceiver.*|
com\.samsung\.android\.app\.telephonyui|
com\.samsung\.android\.phonefactory.*,
com\.sem\..*,
com\.skms\..*|
com\.sec\.factory.*|
com\.ims\..*|
com\.sec\.ims.*|
com\.samsung\.ims.*|
com\.snap.*,
com\.samsung\.wear\.contacts\.sync|
com\.monotype\.android\.font\..*|
com\.skt\..*|
com\.wssyncmldm|
com\.samsung\.android\.dqagent|
com\.sec\.android\.diagmonagent|
com\.sec\.android\.soagent|
com\.samsung\.euicc.*|
com\.samsung\.android\.location\..*|
com\.samsung\.android\.samsungnetworklocation|
com\.sec\.location\..*|
com\.samsung\.android\.app\.message.*|
com\.samsung\.sec\.android\.application\.csc|
com\.samsung\.android\.stextclassifier|
com\.samsung\.android\.wear\.blockednumber|
com\.samsung\.android\.sdk\.handwriting\.watch|
com\.samsung\.android\.app\.esimkeystring|
com\.samsung\.packageinstalleroverlay|
com\.samsung\.android\.watch\.watchface\..*,
com\. SamsungServiceMode$…
```

> **Caution:** The expression above is a reading aid. The tool uses the
> tested pattern in `14_Automation_and_Scripting/tools/sw.py`. The pattern in the tool is the
> authority. This section explains it; the tool enforces it.

The pattern covers three groups:

1. **Android core.** Root `android`, AOSP components, providers,
   permissions, package installer, Play Store, Bluetooth. Disabling
   these removes essential device function.
2. **Google wear core.** Health engine, system UI, settings, launcher
   overlays, Play services, framework stubs. Disabling these breaks the
   watch face, health, or app install surfaces.
3. **Samsung infrastructure.** Watch system UI, setup wizard, account
   sync, phone connection service, Knox, network stack, factory and
   diagnostic packages, eSIM, location, carrier configuration. These
   are device or carrier infrastructure. Community failure reports
   support protection for the gesture and routine services.

## 5. Known Failure Evidence

| Evidence | Source | Consequence |
|---|---|---|
| A batch that included `com.samsung.android.app.routines` and `com.samsung.android.smartgesture` ended in a boot failure. Recovery showed "No android system found". | Community report, Galaxy Watch 6/7 debloat thread. See `19_References/01_references.md` | The tool adds `com.samsung.android.app.routines` and `com.samsung.android.smartgesture` to the protected set. Classification `DO_NOT_REMOVE`. |
| Removal of the `com.samsung.android.scloud`, `com.samsung.android.app.contacts`, and messaging cluster produced battery drain reports with retry loops. | Same thread | These packages are `NOT_RECOMMENDED`, not remove-suggestions. |
| OTA updates restore removed applications. | Same thread, Galaxy Watch 4 thread | The restoration procedure documents post-OTA drift checking. The tool records the state before changes and re-checks the state later. |

## 6. Function Risk Table

Use this table when you add packages to a profile. The table shows the
user-facing loss per function area.

| Function area | Loss when removed or disabled |
|---|---|
| System UI, launcher | Watch face and app tray fail. Watch does not present its home surface. |
| Bluetooth | No companion or audio connection. |
| Health engine | Steps, heart rate history, exercise detection fail. |
| Battery services | Charging state, battery display, power saving fail. |
| Telephony UI | Calls and LTE fail on LTE watches. |
| Play Store | App install and OTA delivery fail. |
| Play Services | Many watch apps fail to start. |
| Payment | Wallet fails. Only remove when wallets are not used. |
| Emergency and safety | Help features fail. Do not touch. |
| Keyboard and voice input | Text reply, voice dictation fail. |

## 7. Dependencies Record

Confirmed dependencies are recorded per package in the database
datasets. The release 1.0 dependency knowledge is limited:

| Package | Confirmed dependency | Source |
|---|---|---|
| `com.samsung.android.app.contacts` and the messaging cluster | Samsung phone–watch sync path (`com.samsung.wear.contacts.sync`) | Function analysis and battery-drain cluster report (`source_type assessment`) |
| `com.samsung.android.watch.watchface.*` faces | Base watch face framework (not separately enumerated in verified dumps) | Function analysis |

No other dependency is confirmed. The schema keeps `dependencies` and
`needed_by` empty when no evidence exists. Do not copy phone dependency
lists. Verify with `dumpsys package <name>` on the watch before you add
a dependency record.

## 8. Operating Limits

1. The protected core set covers Samsung and Google packages named in
   verified dumps. Other manufacturers need their own dump first.
2. The engine refuses when it cannot read the device state. It never
   guesses.
3. Users hold responsibility for their own device. The procedures give
   reversible-first pathways and records. They do not remove the need
   for care.

## 9. References

1. `09_Package_Classification/01_classification_methodology.md`.
2. `02_Reference_Repository_Analysis/01_cleanyourtv_analysis.md` — the
   protected-pattern and guard methodology source.
3. `19_References/01_references.md` — community failure reports.

END OF DOCUMENT.
