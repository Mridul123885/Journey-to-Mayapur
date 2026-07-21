# The Journey — Milwaukee to Mayapur (Capacitor 6, GitHub Actions only)

This repo is a complete Capacitor 6 Android project that builds entirely on
GitHub's servers — you never need Android Studio installed anywhere.

## What's included

```
package.json                        Capacitor 6.x, pinned to exact versions
capacitor.config.json               App ID, name, plugin config
www/index.html                      The app itself (self-contained, includes photos/audio as base64)
android/                            A complete, pre-generated Android project
  app/release.keystore              A signing key, committed (see caveat below)
.github/workflows/android-build.yml The build pipeline
```

The `android/` folder is committed as a real, ready-to-build Gradle project —
not something GitHub has to generate fresh on every run with `npx cap add
android`. The workflow just runs `npx cap sync android`, which refreshes the
web assets and plugin list inside the existing project. This is more
reliable than regenerating the platform from scratch every build.

## How the workflow builds it

On every push to `main`/`master` (or manually via the *Run workflow* button):

1. Checks out the repo
2. Installs **JDK 21** (Temurin) and **Node.js 20**
3. Installs the Android SDK command-line tools (no Android Studio, no GUI)
4. Runs `npm install` — this reads the **exact pinned version** of
   `@capacitor/android` from `package.json` (`6.1.2`), never `@latest`
5. Runs `npx cap sync android` to copy `www/` and the plugin list into the
   Android project
6. Installs Gradle 8.7 directly (no `gradlew` wrapper needed — see note below)
7. Runs `gradle :app:assembleRelease` → produces a **signed, installable**
   `app-release.apk`
8. Runs `gradle :app:bundleRelease` → produces a **signed**
   `app-release.aab`
9. Uploads both as workflow artifacts you can download from the Actions run
   page

## Why there's no `gradlew`

Normal Capacitor projects include a `gradlew` wrapper script plus a binary
`gradle-wrapper.jar`. That jar is a compiled binary — not something safely
hand-written — so instead the workflow installs Gradle 8.7 directly via the
official `gradle/actions/setup-gradle` action and calls `gradle` on the
runner's PATH. Functionally identical result, one less binary file to trust.

If you also want to build locally on your own machine later, run this once
inside `android/`:
```bash
gradle wrapper --gradle-version 8.7
```
That generates a proper `gradlew` for local use. It's not needed for CI.

## About the signing key — read this before publishing

`android/app/release.keystore` is committed to this repo with the password
`journeyMayapur2026` (alias `journeykey`), and the workflow uses it to sign
every build automatically. This means:

- ✅ Every APK/AAB from every build is properly signed and installable —
  no "package appears to be invalid" error.
- ✅ Builds work immediately with zero configuration — just push.
- ⚠️ **The private key is sitting in your git history in plain sight.**
  That's fine for testing and sideloading, but it is not how you should
  ship something real. Anyone with repo access can extract and use it.

**Before publishing to Google Play**, replace this with a real private key
that only you hold:

1. Generate your own keystore once, locally:
   ```bash
   keytool -genkeypair -v -keystore my-release.keystore -alias mykey \
     -keyalg RSA -keysize 2048 -validity 10000
   ```
2. Base64-encode it and add these as **GitHub repo Secrets**
   (Settings → Secrets and variables → Actions):
   - `KEYSTORE_BASE64` (the base64 output of the file)
   - `KEYSTORE_PASSWORD`
   - `KEY_ALIAS`
   - `KEY_PASSWORD`
3. In the workflow, add a step before the build steps to decode it:
   ```yaml
   - name: Decode keystore
     run: echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 -d > android/app/release.keystore
   ```
4. Change the `CI_KEYSTORE_PASSWORD` / `CI_KEY_ALIAS` / `CI_KEY_PASSWORD`
   env values in the workflow to `${{ secrets.KEYSTORE_PASSWORD }}` etc.
5. Delete the committed `release.keystore` and remove the `.gitignore`
   note about it.
6. **Keep using the same key for every future update** — Google Play
   requires the same signing key across the app's lifetime (or Play App
   Signing, which is Google's managed alternative — recommended for new
   apps: enroll in Play App Signing when you first upload, and Google
   handles key security for you going forward).

## Publishing to Google Play

1. Create a Google Play Developer account ($25 one-time)
2. Create a new app in the Play Console
3. Upload `app-release.aab` (not the APK — Play requires the AAB format)
4. Fill in the store listing, content rating, privacy policy URL, etc.
5. Submit for review

## Installing the APK directly (sideloading, for testing)

Download `app-release.apk` from the workflow run's Artifacts section,
transfer it to an Android phone, and open it (you'll need to allow installs
from your file manager / browser the first time). This is useful for testing
before you're ready for a Play Store listing.

## A note on how this was built

This project was hand-assembled to match Capacitor 6's standard Android
project layout, since generating it required no internet access in this
environment. The Gradle files, manifest, and module structure follow the
same layout `npx cap add android` produces. GitHub Actions runners have full
internet access, so `npm install`, SDK downloads, and Gradle dependency
resolution will all work there even though they couldn't be live-tested here.
If the very first run surfaces a small Gradle error, it's almost always one
of two things:
- A dependency version that's shifted since this was written — check the
  Actions log for the exact package/version it can't resolve and adjust
  `package.json` or `variables.gradle` accordingly.
- The `@capacitor/local-notifications` version needing to be nudged to the
  nearest available `6.x` release if `6.1.0` has been superseded.

## Updating the app

Edit `www/index.html` (or ask Claude to regenerate it), commit, push — the
workflow rebuilds both artifacts automatically.
