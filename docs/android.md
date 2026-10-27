# KFW on Android

The Android edition is a complete port of the game, not a reduced remake. The original
`kf_lib` Python code runs inside the app through Chaquopy; a native Java/Android Views
layer replaces the terminal with touch controls. English and Russian content, hot-seat
play, AI players, encounters, stories, tournaments, fights, accomplishments and the
existing save format all use the same implementation as the desktop game.

## Requirements and compatibility

- Android 7.0 (API 24) or newer; the app targets Android 15 (API 35).
- `arm64-v8a` for current devices and `x86_64` for emulators. 32-bit builds are not
  included.
- No network connection, Google Play services or storage permission is required to play.
- Build machine: JDK 17, Python 3.13 on `PATH`, Android SDK Platform 35 and Build Tools
  35.0.0. Android Studio is optional.
- Pinned build components: Gradle 8.11.1 (wrapper included), Android Gradle Plugin 8.9.2,
  Chaquopy 17.1.0, embedded CPython 3.13.

## Building an APK

Set `ANDROID_HOME` (and `ANDROID_SDK_ROOT` if your tools use it), or create the untracked
`android/local.properties` file with an absolute `sdk.dir=/path/to/sdk` line. Then run:

```bash
cd android
./gradlew assembleDebug
```

The installable, debug-signed APK is written to
`android/app/build/outputs/apk/debug/app-debug.apk`. Install it on a connected device with
developer mode and USB debugging enabled:

```bash
$ANDROID_HOME/platform-tools/adb install -r app/build/outputs/apk/debug/app-debug.apk
```

For an unsigned release package:

```bash
cd android
./gradlew clean assembleRelease
```

`app-release-unsigned.apk` is in `app/build/outputs/apk/release/`. Sign it with your own
upload key before distribution; no release private key is stored in this repository. Debug
and release packages have the same application ID, so installing one replaces the other.
Export saves first. Release builds exclude `python_debug/` and its self-test module.

The Gradle `Sync` tasks copy the canonical desktop sources and data into a clean generated
source tree on every build. Edit `kf_lib/`, `moves/`, `quotes/` and `locale/` in their normal
locations, not files under `app/build/generated/`. No manual copy step is needed.

## Playing

- **New game** follows the original setup: any mix of human and AI players, co-op and
  hot-seat play, standard or generated styles, custom world settings and autosave.
- **Continue** loads the newest valid save. **Load game** offers all valid saves, newest
  first. **Watch an AI game** runs four visible Smart AI players; their pauses use the same
  Continue button as human play.
- Game menus become touch buttons with their real labels. Scroll the bottom panel for
  more moves or actions. The optional Back button closes weak menus such as the post-fight
  menu.
- Text and numeric answers use the Android keyboard. A hardware keyboard also works for
  menu keys; use Shift for the uppercase State commands. A key that is not on the menu
  is ignored and the menu buttons stay.
- The console keeps the original ANSI colors and monospace ASCII art. Scroll vertically
  for history and horizontally for wide tables/art. A− / A+ changes text size and remembers
  it. Long transcripts are capped at 400,000 characters to bound memory use.
- **State** in the day menu opens character information and the original Save / Load /
  Save and Quit commands. Returning to the title with the Android Back button or the ‹
  button asks for confirmation because it discards progress after the last save.
- Rotation, moving the app to the background, connecting a keyboard and changing the
  system font size, bold text or language do not restart the running game (a new system
  font size reaches the console on the next game). As with
  any mobile app, the operating system may eventually reclaim a background process;
  autosave or manual saves protect progress.
- The language button restarts the app to apply English or Russian before any game content
  is imported. Restarting from the title does not erase saves.

## Saves, import and export

Saves are stored in the app-private `files/save/` directory and use the desktop JSON
`.txt` format without conversion. Existing JSON saves work on desktop and Android. The
legacy executable-Python loader is also available for old KFW saves. **Only import legacy
saves from trusted sources: their original format contains executable Python code.**

Use **Import save** and **Export save** to copy files through Android's Storage Access
Framework. No broad storage permission is requested. Imports are validated, limited to
20 MiB, restricted to safe `.txt` filenames and never overwrite an existing file: a numeric
suffix is added instead. Files that are not recognizable KFW saves are rejected.

Manual, automatic, game-over and emergency saves persist across app updates. Android cloud
backup and device transfer include the `save/` directory when the device permits it.
Uninstalling the app or using **Clear data** deletes its saves; export anything you need
first.

After a game error, the app writes `errors.txt` and `debug.txt` and tries to create
`emergency_save.txt`. The error dialog returns to the title, where the emergency save can
be loaded and exported. Python diagnostics also go to Logcat.

## Architecture

- `android/python/kfw_android.py` owns the embedded runtime. It stages read-only `moves/`,
  `quotes/` and `locale/` into app-private HOME before importing any `kf_lib` module. This
  preserves the desktop cwd-relative resource loaders while keeping saves and logs out of
  upgrade-managed code directories. Before each new (not loaded) game it also restores the
  pristine default-style list, so a previous generated-style session cannot leak into the
  next one.
- `GameHost.java` is the blocking input/output bridge between the Python game thread and
  the Android main thread. Closing a host wakes pending input and unwinds the old session.
  A new session waits for the previous game thread in the background before installing
  any hooks, preventing rapid restart races without freezing the Android UI.
- `MainActivity.java` owns navigation, native widgets, save transfer and language changes.
- `ConsoleView.java` and `AnsiParser.java` render streaming ANSI output with bounded
  history, horizontal art scrolling and text-size controls.
- `SaveRepository.java` validates, lists, imports and exports saves, including canonical
  path checks and duplicate-name handling.
- The only changes to desktop UI code are optional frontend hooks in
  `kf_lib/ui/_frontend.py`: key input, clear-screen and presentation of the current menu.
  With no frontend installed, terminal behavior is unchanged.

## Verification

Run all commands from the repository root unless a command says otherwise:

```bash
.venv/bin/python -m pytest
python kfw.py --autoplay --silent-ending
cd android
./gradlew testDebugUnitTest lintDebug assembleDebugAndroidTest
```

With one booted emulator or connected device (and `adb` on `PATH`):

```bash
cd android
./gradlew connectedDebugAndroidTest
cd ..
.venv/bin/python android/scripts/ui_smoke.py \
  --adb "$ANDROID_HOME/platform-tools/adb" \
  --artifacts android/build/ui-smoke
```

The instrumentation suite executes localized resources, new game, interactive combat and
save/load in an isolated app-private HOME. The UIAutomator script drives the real native UI:
new game, a key outside the menu, keyboard input, background/resume, rotation, a system
font-size change, State/Save, title, Continue, a
deterministic NormalFight (launched through the game's Debug Menu) with manual move
selection, post-fight Back and another save. Screenshots
are written to the artifacts directory. Add `--reset` only on a disposable test device: it
explicitly clears all KFW app data before the run.

Local JDK, SDK, Gradle caches, AVDs and downloaded tools can live under
`android/.toolchain/`; that directory, `local.properties`, build outputs and APKs are
intentionally ignored by git.
