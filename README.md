# The Journey — Milwaukee to Mayapur (Capacitor 6, GitHub Actions only)

Complete Capacitor 6 Android project. Builds entirely on GitHub's servers —
no Android Studio needed anywhere.

## 🎮 Gau Seva: critical point-collection bug fixed, obstacles added, stages 9-10 rebuilt as real endless runners

**The point-collection bug — root cause found and fixed.** Every falling
item was using a `click` event listener, and its position was updated
every 16ms via a separate `setInterval` disconnected from the browser's own
event/render timing. On touch devices, `click` is synthesized from
touch-start/touch-end with real latency, and a fast-moving target can shift
out from under the finger between those two events, so the tap silently
misses. **Fixed:** every falling item now uses `pointerdown` (registers
immediately, no synthesis delay) combined with `requestAnimationFrame`
motion (frame-synced, smooth, matches Screen refresh instead of an
independent timer), a `collected` guard flag so nothing can ever score
twice, and a real 56–60px padded hit box with `touch-action:none` instead
of a bare emoji character — noticeably easier for a child to tap
accurately.

**Falling speed cut by roughly 45% across the board**, then scaled back up
gradually as stages progress (Stage 1 starts near 48px/s; Stage 8 tops out
around 62px/s) — matching the requested "slow start, gradual increase"
curve.

**Every stage 1–8 now includes obstacles** (rocks, thorn bushes, mud,
broken pots, a monkey, crows, rolling logs) mixed in among the
collectibles. Tapping one ends the attempt and restarts the current stage.

**Stages redesigned to match the brief:**
- Stage 4 (Groom) and Stage 8/old-8 (Health Care) no longer use a tap-sequence
  — the required items (brush, soap, bucket, towel / medicine, bandage,
  blanket, food, water) now fall from above like every other stage.
- Stage 5 (Milk Collection) replaced the old rhythm-tap with falling milk
  buckets, pots, and bottles.
- Stage 6 (Decorate) and Stage 7 (Play with the Calf) are longer, with
  falling decorations/toys instead of a static picker.
- **Stage 9 — Devotional Running Adventure**: a real endless-runner, ~3
  minutes long, four escalating difficulty phases exactly as specified
  (0–30s easy, 30–60s medium, 60–120s hard, 120–180s very hard). Devotee
  Boy or Girl runs automatically across three lanes; move left/right (tap
  the arrow buttons or swipe) to dodge obstacles and collect devotional
  items. One obstacle touch restarts the stage. Scenery cycles between the
  game's three world backdrops through the run.
- **Stage 10 — Infinite Gau Seva Run**: true endless runner, no finish
  line, difficulty escalates continuously the longer you survive, a
  friendly cow runs alongside you. Ends only when you touch an obstacle —
  at which point that's a normal ending, not a failure, and your score is
  saved as a high score with a "🏆 New high score!" callout when beaten.

**Flower Collection mini-game** rebuilt with the same fixes: `pointerdown`
+ `requestAnimationFrame`, slower fall speed, a bigger hit box, and a
genuine petal-burst animation (several small petals fly outward and fade)
plus a short synthesized collection chime on every catch.

**On sound effects**: no new sound files were uploaded for collection
feedback, so rather than fabricate an audio asset, collection/fail sounds
are short tones synthesized live with the Web Audio API — a real,
functioning sound on every catch and every obstacle hit, without inventing
a file that doesn't exist.

## 🔔 Notifications weren't firing at all — three real, separate bugs found and fixed

The reminder toggle staying on was only the storage layer working; the
actual notification pipeline had three independent problems, any one of
which alone would cause exactly what was reported (toggle on, nothing ever
fires):

**1. Missing notification icon resource.** `capacitor.config.json` told the
plugin to use a small icon called `ic_stat_icon` — but that image file was
never actually created anywhere in the Android project. On Android, if the
small-icon resource a notification points to doesn't exist, the system can
fail to display the notification at all, silently. **Fixed:** generated a
real `ic_stat_icon.png` at all five required densities
(`android/app/src/main/res/drawable-{m,h,x,xx,xxx}hdpi/`).

**2. Invalid schedule format.** Every repeating reminder was scheduled with
`schedule: { on: {hour, minute}, every: 'day' }`. That combination isn't
the documented pattern for Capacitor's LocalNotifications plugin — daily
repetition at a fixed time is expressed with `on: {hour, minute}` **alone**;
adding `every: 'day'` on top of it isn't valid and could cause the native
`schedule()` call to fail. **Fixed:** removed `every` from every repeating
schedule.

**3. No notification channels — so no custom sound, and on some Android
versions no notification at all.** Android 8+ requires every notification
to belong to a channel, and a channel's sound is fixed at creation time —
the per-notification `sound` field is only honored if the channel doesn't
already define one. Since no channels were ever created, Android was
falling back to a default channel with no custom sound, and depending on
version behavior, could suppress the notification entirely. **Fixed:**
explicit `LocalNotifications.createChannel()` calls for six channels (one
per distinct sound needed — chanting, three separate Mangal Arati sounds,
events, and the new test channel), each notification now carries the
matching `channelId`.

**On top of the fix, every scheduling call is now wrapped in try/catch with
logging**, so a failure is never silent again — errors are visible both in
`console.log`/`console.error` and in an on-screen debug log inside the app
itself (Japa tab → Test & Debug), since a real user on a real phone can't
easily attach `adb logcat`.

### New: Test Reminder button
Japa tab → Test & Debug → **Send Test Reminder (10s)**. Schedules one
notification 10 seconds out on its own channel with the chanting sound,
and logs every step (permission status, channel creation, scheduled ID,
pending-notification count, delivery, and any error) to the on-screen debug
log. This is the fastest way to confirm the whole pipeline works on a given
device without waiting for a real scheduled time — press it, background the
app, and watch for the notification and the log update.

### What's still an honest, unresolved caveat
Android 12+ (API 31+) restricts exact alarms (`SCHEDULE_EXACT_ALARM`)
behind a special permission that in some cases requires the user to
manually approve it in system settings — this is not something the
LocalNotifications JS API can request directly, and if it's not granted,
Android may deliver a scheduled notification a little late (inexact) rather
than not at all; it should not cause total silence the way the three bugs
above did. If notifications now appear via the Test button but real
scheduled ones are consistently late, that's the next thing to check, in
the phone's own Settings → Apps → [this app] → Alarms & reminders.

## 🎮 Gau Seva gameplay redesign — no more repetitive stages

The old need-meter/hearts system is gone. Every stage now has its own
distinct mechanic, real scoring from zero, and no fail state:

- **Stage 1 — Feed the Cow**: tap falling grass before it lands
- **Stage 2 — Give Water**: tap falling water drops
- **Stage 3 — Clean the Shelter**: tap falling leaves/debris
- **Stage 4 — Groom the Cow**: ordered tap sequence (brush → wash → dry → garland)
- **Stage 5 — Milk Time**: rhythm-tap a moving marker into the golden zone
- **Stage 6 — Decorate the Cow**: pick decorations, rarer ones worth more points
- **Stage 7 — Play with the Calf**: tap feed/pet/play icons as they appear
- **Stage 8 — Cow Health Check**: ordered caring actions (medicine, thorn removal, herbal paste, blanket)
- **Stage 9 — Temple Offering**: collect fruits and flowers
- **Stage 10 — Grand Festival**: chains three earlier mechanics back-to-back as a finale

Every stage: starts at score 0, floating "+1"/"+5"/"+10" popups on every
successful tap, a live score bar instead of pre-filled hearts, a cow that
visibly bounces with a heart-burst when pleased, an end screen showing
stars (1–3), total score, a speed bonus, and a "Cow Happiness %", plus a
rotating short devotional message. There's no lose state — this rewards
gentleness and completion over speed pressure, per the brief.

The Flower Collection mini-game now has five flower tiers worth different
points (🌸1 / 🌼2 / 🌺3 / 💙5 / 🌻10, weighted so rare ones are rarer),
floating score popups on every catch, and a garland-fill celebration every
12 flowers.

The scene also now renders in two parallax layers (a soft-focus far layer
and a sharper near layer, each drifting independently) for a real 2.5D
depth feel instead of a single flat backdrop.

## 🎮 Gau Seva in Sri Vrindavan — rebuilt as a real 2D game

The previous 3D version (Three.js + two large `.glb` models) has been
**removed entirely** and replaced with a 2D game built from your uploaded
character/animal/NPC/scenery artwork. This also means:

- **No more Git LFS requirement.** The 126MB of 3D models is gone; the repo
  is now ~16MB total. Push it normally, no special setup needed.
- **No more CDN dependency for the game.** The old version needed to fetch
  a 3D model-loader library from a CDN on first open. The 2D version needs
  nothing external — every asset is a local image file.
- **Lighter and faster on real phones.** Sprite images load instantly
  compared to parsing a 107MB 3D model in a mobile WebView.

**What's in this build**, scoped honestly against the full brief (which
described a multi-year, studio-scale open-world game — 10 full worlds, RPG
progression, day/night/weather, a dozen-plus mini-games, a full
inventory/world-map UI). That exact scope isn't achievable in one build;
here's the real, working subset:

- **4 playable characters** — Devotee Boy, Devotee Girl, Young Krishna,
  Young Balarama — selectable before entering the game, shown with real
  idle/walk/celebrate art cropped from your sprite sheets.
- **3 connected areas** (not 10): Sacred Goshala, Flower Garden, Yamuna
  Riverside — each with its own backdrop art, unlocking as you progress.
- **10 stages** across those 3 areas, each at least 60 seconds, escalating
  difficulty (more cows, faster need-decay, fewer hearts), with a
  wandering-cow rescue mechanic from Stage 4 and a protect-the-herd
  mechanic from Stage 7. Stage 10 is endless — leave whenever you want and
  your time survived banks as stars and coins.
- **NPCs with real art and dialogue** — a cowherd friend, the Goshala
  Sevak, or the Elder Devotee greets you at the start of each stage with a
  short tip, using your uploaded NPC portraits.
- **Real animals throughout** — cows and calves from your sheets appear in
  the goshala; peacocks and monkeys appear in mini-games.
- **Two working mini-games**, not thirteen: Flower Collection (tap falling
  flowers before they land, 30-second timer) and Memory Match (pair-matching
  using your character/animal art). Both feed the same coin/flower economy
  as the main game.
- **Rewards**: coins, flowers, stars (1–3/stage), and badges at stages 3,
  6, 10 — all saved permanently via `@capacitor/preferences`.
- Your uploaded background music plays through every stage, with a mute
  toggle.

**Explicitly not included**: character XP/leveling, unlockable
outfits/accessories, friendship levels, a world map screen, an inventory
screen, an achievement gallery, day/night or weather cycles, festival
calendar events, and 9 of the 13 requested mini-games. The code is
organized so any of these could be added later (each stage is one config
object in an array; each mini-game is a self-contained block) — but
building all of it is a genuinely large ongoing project, not a single pass.

**Where the art came from:** your 13 uploaded reference sheets were sliced
into individual sprites via connected-component detection, then the
specific poses used in the game were selected from those crops. If any
sprite looks off (wrong crop, wrong character), tell me which one and I'll
fix that specific asset.

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
