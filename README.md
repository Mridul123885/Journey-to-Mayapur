# The Journey — Milwaukee to Mayapur — Capacitor project

This folder turns the existing web app (`www/index.html`) into a real installable
Android and iOS app using [Capacitor](https://capacitorjs.com/). The app code
itself is unchanged — Capacitor just wraps it in a native shell and gives it
access to real device features, most importantly **local notifications that
fire even when the app is closed**.

The `www/index.html` file already contains logic to detect whether it's
running inside the native app (`window.Capacitor`) or in a plain browser, and
uses true OS-level scheduled notifications in the app, falling back to
browser notifications (tab must stay open) when just viewed as a website.

## What you need before starting

- **Node.js** (v18 or newer) — https://nodejs.org
- **For Android:** Android Studio — https://developer.android.com/studio
- **For iOS:** a Mac with Xcode installed (Apple does not allow iOS builds on
  Windows/Linux)
- A **Google Play developer account** ($25 one-time) if you want to publish
  on Android
- An **Apple Developer account** ($99/year) if you want to publish on iOS

## 1. Install dependencies

Open a terminal in this folder (the one with `package.json`) and run:

```bash
npm install
```

## 2. Add the native platforms

```bash
npx cap add android
npx cap add ios
```

(Skip whichever platform you don't need. You can add the other one later the
same way.)

## 3. Sync the web app into the native projects

Run this every time you change `www/index.html`:

```bash
npx cap sync
```

## 4. Open and run in the native IDE

Android:
```bash
npx cap open android
```
This opens Android Studio. Press the ▶ Run button to install it on an
emulator or a connected phone.

iOS:
```bash
npx cap open ios
```
This opens Xcode. Select a simulator or your connected iPhone and press ▶.

## 5. App icon and splash screen

Capacitor uses the `@capacitor/assets` tool to generate all required icon
sizes from one source image. From this folder:

```bash
npm install @capacitor/assets --save-dev
```

Then put a 1024×1024 PNG icon at `assets/icon.png` and a 2732×2732 splash
image at `assets/splash.png`, and run:

```bash
npx capacitor-assets generate
```

## 6. Testing local notifications

The reminder toggle inside the app (Japa tab → Chanting Reminders) now calls
`LocalNotifications.schedule()` with daily repeating triggers at 10:00 AM,
3:00 PM, and 8:30 PM when running inside the native app. Turn it on once from
inside the installed app on a real device — the OS will keep firing it daily
even after you close the app, with no server required.

Note: iOS and some Android manufacturers (Xiaomi, Huawei, OnePlus, etc.)
aggressively kill background processes to save battery. If notifications
stop arriving, the user may need to disable battery optimization for the app
in their phone settings — this is an OS-level setting, not something the app
can fully control.

## 7. Publishing

**Android (Google Play):**
1. In Android Studio: `Build → Generate Signed Bundle / APK`
2. Create a keystore (keep it safe — you need the same one for every future
   update)
3. Upload the generated `.aab` file to the Google Play Console
4. Fill in store listing details (screenshots, description, privacy policy
   URL) and submit for review

**iOS (App Store):**
1. In Xcode: set your Apple Developer team under Signing & Capabilities
2. `Product → Archive`
3. Use the Organizer window to upload the archive to App Store Connect
4. Fill in store listing details and submit for review

## Updating the app later

Whenever you want to change anything in the app itself, edit
`www/index.html` (or ask Claude to regenerate it), then run:

```bash
npx cap sync
```

and rebuild/re-run from Android Studio or Xcode as in step 4.

## About the embedded media

`www/index.html` has the photos and background music embedded directly as
base64 data, so it's a single self-contained file — no separate asset
folder to manage or lose track of.
