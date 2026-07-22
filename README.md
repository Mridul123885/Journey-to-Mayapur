# The Journey — Milwaukee to Mayapur (Capacitor 6, GitHub Actions only)

Complete Capacitor 6 Android project. Builds entirely on GitHub's servers —
no Android Studio needed anywhere.

## 🔧 Critical fix in this update: reminders were never actually being saved

Every setting in this app — including the reminder toggles — was being
persisted through `window.storage`, an API that only exists inside
Claude.ai's own artifact preview sandbox. **It does not exist in a real
packaged Android app.** Every read/write silently failed there, so:

- The reminder toggle always read back as "off" on the next launch,
  regardless of what the user had set
- The app's own startup code then saw "off" and actively **cancelled** any
  native alarms that were still working
- This is what looked like "reminders stop when the app is minimized or
  closed, and the setting is lost" — the app was quietly undoing its own
  reminders on every launch

**Fix:** all persistence now goes through `@capacitor/preferences`, the
official Capacitor plugin backed by real native `SharedPreferences` storage
on Android, which genuinely survives app close, reopen, and device restart.
This affects every saved setting in the app, not just reminders — japa
progress, quotes, game state, everything was subject to the same bug and is
now fixed the same way.

The JavaScript `setInterval`-based notification polling has also been
removed entirely. Scheduling now goes exclusively through
`@capacitor/local-notifications`' native `AlarmManager`-backed scheduling.

## ⚠️ Before you push: install Git LFS

`www/assets/models/modelToUsed.glb` is **107 MB**, which is over GitHub's
**100 MB hard file-size limit**. A normal `git add`/`git push` of this repo
**will be rejected**. This repo already includes a `.gitattributes` file
that routes `*.glb` through Git LFS, and the workflow already checks out
with `lfs: true` — you just need Git LFS installed locally before your
first commit:

```bash
# macOS
brew install git-lfs
# Windows
choco install git-lfs
# Ubuntu/Debian
sudo apt install git-lfs

git lfs install
git add .gitattributes
git add -A
git commit -m "Initial commit"
git push
```

If a push is ever rejected for a file over 100MB, it means Git LFS wasn't
installed/initialized before you ran `git add` on that file — remove it
from git history, run `git lfs install`, and re-add it.

**Also worth knowing:** the two 3D models total ~126 MB, and go straight
into the installed app package. That's a genuinely large app for a mobile
download — most Play Store apps are a fraction of this size. If load times
or app size become a problem, the fix is compressing the `.glb` files (Draco
or Meshopt compression via a tool like `gltf-transform` or `gltfpack`, run
on your own machine) before they go into `www/assets/models/`. That wasn't
possible to do in the environment that assembled this repo, so the models
are included at their original size.

## What's new in this update

### 1. Chanting Reminders — reliability fix
Reminders now:
- Use **deterministic notification IDs**, so re-scheduling never creates
  duplicates — it cleanly replaces the pending alarm instead.
- Are **re-applied on every app launch** if the toggle is on. That's what
  makes "stays enabled until you turn it off" actually hold up in practice —
  even if something cleared the OS-level alarm (an app update, for
  example), the next time the app opens it's silently re-armed.
- Play your uploaded chanting sound (`chant_reminder.mp3`), bundled as a
  real Android notification sound resource
  (`android/app/src/main/res/raw/`).

### 2. Mangal Arati Reminders (new)
Four daily reminders — 3:30, 4:00, 4:30, 5:00 AM — each with one of your
three uploaded sounds (cycled across the four slots). Own toggle, own
persistent settings, same reliable scheduling approach as above.

### 3. Event Reminders (new)
Every Ekadashi/observance in the app is automatically scheduled to notify
at 3:30 AM local time on the day itself. IDs are derived from the date
itself, so old/changed dates are cleanly replaced rather than duplicated.

### 4. How background reliability actually works here
All three reminder types use `@capacitor/local-notifications`, scheduled
through Android's `AlarmManager` — an OS-level mechanism that fires whether
the app is open, minimized, or the phone is locked. The plugin also
registers its own boot-completion receiver (enabled by the
`RECEIVE_BOOT_COMPLETED` permission already in the manifest), which is what
lets scheduled alarms survive a device restart. One honest caveat: some
Android manufacturers (Xiaomi, OnePlus, Huawei, etc.) apply aggressive
battery-optimization that can still kill background alarms regardless of
what any app does — if that happens, the user needs to exempt the app from
battery optimization in their phone's system settings. That's an OS-level
control no app can fully override.

### 5. New game: Sacred Gau Seva in Sri Vrindavan
A second, separate game — a new card in the Play tab, below Chapter 13.
- Your two uploaded 3D models are used directly: `modelToUsed.glb` as the
  cow(s) in the goshala, `Bridge01.glb` placed over a river as scenery.
- 10 stages, each at least 60 seconds, difficulty rising through more
  cows, faster need-decay, and fewer hearts, plus two added mechanics
  from Stage 4 (guiding a wandering cow home) and Stage 7 (protecting the
  herd from a warned danger).
- **Stage 10 is endless** — no finish line. Leave whenever you want via the
  back button, and your time survived is banked as stars and coins.
- Core loop: three need meters (Hunger, Thirst, Cleanliness) drain over
  time; tap Feed 🌿 / Water 💧 / Brush 🧽 to keep them up. Let one hit zero
  and you lose a heart; lose all hearts and the stage ends.
- Rewards: stars (1–3 per stage), coins, and badges at stages 3, 6, and 10
  ("Gentle Hands", "Protector of the Herd", "Vrindavan Sevak").
- Your uploaded background music (`gauseva_music.mp3`) plays through every
  stage, with its own mute toggle.

This game needs an internet connection **the first time it's opened in a
session**, to fetch the 3D model loader library from a CDN
(`GLTFLoader.js` — this one script isn't bundled locally). Once that's
loaded, the actual 3D models are local files inside the app and don't need
network access again that session.

## Project layout

```
package.json                        Capacitor 6.x, pinned to exact versions
capacitor.config.json               App ID, name, plugin config
www/index.html                      The app
www/assets/models/                  modelToUsed.glb, Bridge01.glb (Git LFS)
www/assets/sounds/                  chant_reminder.mp3, mangal_1/2/3.mp3, gauseva_music.mp3
www/assets/icons/                   gauseva_icon.png
android/                            Full pre-generated Android project
  app/release.keystore              Signing key (see caveat below)
  app/src/main/res/raw/             Same notification sound files, as Android resources
.github/workflows/android-build.yml Build pipeline
```

## How the workflow builds it

1. Checks out the repo (with Git LFS files)
2. Installs JDK 21 (Temurin) and Node.js 20
3. Installs the Android SDK command-line tools (no Android Studio)
4. `npm install` — reads the exact pinned `@capacitor/android` version from
   `package.json`, never `@latest`
5. `npx cap sync android` — copies `www/` and the plugin list into the
   Android project
6. Installs Gradle 8.7 directly (no `gradlew` wrapper needed)
7. `gradle :app:assembleRelease` → signed, installable `app-release.apk`
8. `gradle :app:bundleRelease` → signed `app-release.aab`
9. Both uploaded as workflow artifacts

## About the signing key — read this before publishing

`android/app/release.keystore` is committed with password
`journeyMayapur2026` (alias `journeykey`) so every build is signed and
installable with zero setup. Before publishing to Google Play, generate
your own private keystore, store it as GitHub Secrets, and update the
workflow's env values accordingly:

1. `keytool -genkeypair -v -keystore my-release.keystore -alias mykey -keyalg RSA -keysize 2048 -validity 10000`
2. Base64-encode it, add as repo secrets: `KEYSTORE_BASE64`,
   `KEYSTORE_PASSWORD`, `KEY_ALIAS`, `KEY_PASSWORD`
3. Add a step before the build steps: `echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 -d > android/app/release.keystore`
4. Point `CI_KEYSTORE_PASSWORD`/`CI_KEY_ALIAS`/`CI_KEY_PASSWORD` at those
   secrets instead of the hardcoded values
5. Delete the committed keystore and keep using the same private key for
   every future update (or enroll in Google Play App Signing)

## Testing on a device

Download `app-release.apk` from the workflow run's Artifacts section,
transfer to an Android phone, and install it directly (enable "install from
this source" the first time). Turn on all three reminder toggles from
inside the installed app and leave the phone alone for a day to confirm
delivery — that's the only real way to verify OS-level background
notification behavior, and it could not be tested from the environment that
assembled this repo (no network access, no Android device).

## Updating the app

Edit `www/index.html` (or ask Claude to regenerate it), commit, push — the
workflow rebuilds both artifacts automatically.
