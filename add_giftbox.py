#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adds a devotional gift-box launch experience to Journey to Mayapur.

Architecture (why this needs zero changes to existing Home Page / quote
code): the gift box is a full-screen overlay, added as the very last
element before </body>, with the highest z-index in the app. It is
visible by default (no JS flag, no storage needed) because a fresh page
load IS a new app launch in this Capacitor app -- every cold launch
reloads the whole page fresh, while in-app tab navigation (Home -> Japa ->
Games -> Home) never reloads the page at all, just shows/hides existing
views. So "visible on load, hidden on tap" already exactly matches "every
launch, never on navigation" with no session-tracking code required.
Everything underneath (Home Page, daily quote, init()) continues to load
and run completely normally in the background, untouched, while the
overlay sits on top of it until tapped.

Honest caveat: this resets on every fresh WebView load (cold app start).
If Android keeps the app process alive in the background and the user
simply switches back to it without fully closing it, the overlay will not
reappear, since no page reload happened. This matches every example in
the spec (all of which describe fully closing and relaunching).

Requires giftbox_music_b64.txt to sit in the same folder as this script.

Usage:
    python3 add_giftbox.py
"""
import sys, os

TARGET = "www/index.html"
AUDIO_FILE = "giftbox_music_b64.txt"

if not os.path.isfile(TARGET):
    print("ERROR: could not find " + TARGET + ". Run this from your repo root.")
    sys.exit(1)

if not os.path.isfile(AUDIO_FILE):
    print("ERROR: could not find " + AUDIO_FILE + " in the current folder. "
          "Make sure both add_giftbox.py and giftbox_music_b64.txt are in your repo root.")
    sys.exit(1)

with open(TARGET, "r", encoding="utf-8") as f:
    html = f.read()

if 'id="giftBoxOverlay"' in html:
    print("Gift box already present in this file -- no changes made, to avoid duplicating it.")
    sys.exit(0)

with open(AUDIO_FILE, "r", encoding="ascii") as f:
    AUDIO_B64 = f.read().strip()

body_close = "</body>"
if body_close not in html:
    print("ERROR: could not find </body> to attach the gift box before. No changes made.")
    sys.exit(1)

giftbox_block = """
<!-- ================= GIFT BOX LAUNCH EXPERIENCE ================= -->
<style>
#giftBoxOverlay{ position:fixed; inset:0; z-index:999999; background:radial-gradient(ellipse at center, #2a1f42 0%, #140f22 70%); display:flex; flex-direction:column; align-items:center; justify-content:center; touch-action:manipulation; }
#giftBoxOverlay.gb-hidden{ display:none; }
.gb-sparkle-field{ position:absolute; inset:0; overflow:hidden; pointer-events:none; }
.gb-sparkle{ position:absolute; font-size:14px; opacity:0; animation:gbTwinkle 2.6s ease-in-out infinite; }
@keyframes gbTwinkle{ 0%,100%{ opacity:0; transform:scale(0.6);} 50%{ opacity:0.9; transform:scale(1.1);} }
.gb-box{ font-size:110px; cursor:pointer; user-select:none; filter:drop-shadow(0 0 24px rgba(243,206,127,0.55)); animation:gbFloat 3s ease-in-out infinite; transition:transform .15s ease; }
.gb-box:active{ transform:scale(0.94); }
@keyframes gbFloat{ 0%,100%{ transform:translateY(0);} 50%{ transform:translateY(-10px);} }
.gb-hint{ margin-top:22px; font-family:'Cormorant Garamond',serif; font-size:16px; letter-spacing:0.5px; color:var(--cream,#F3E9D8); opacity:0.85; animation:gbPulseText 2s ease-in-out infinite; }
@keyframes gbPulseText{ 0%,100%{ opacity:0.55;} 50%{ opacity:0.95;} }
.gb-box.gb-tapped{ animation:gbBounceOpen 0.5s ease forwards; }
@keyframes gbBounceOpen{ 0%{ transform:scale(1) rotate(0deg);} 30%{ transform:scale(1.18) rotate(-6deg);} 55%{ transform:scale(1.05) rotate(4deg);} 100%{ transform:scale(1.35) rotate(0deg); opacity:0;} }
.gb-lightburst{ position:absolute; width:10px; height:10px; border-radius:50%; background:radial-gradient(circle, #FFF7DD 0%, #F3CE7F 35%, rgba(243,206,127,0) 70%); opacity:0; pointer-events:none; }
.gb-lightburst.gb-burst-active{ animation:gbBurst 1.1s ease-out forwards; }
@keyframes gbBurst{ 0%{ opacity:0; width:10px; height:10px;} 25%{ opacity:1;} 100%{ opacity:0; width:1400px; height:1400px; } }
#giftBoxOverlay.gb-fading{ animation:gbOverlayFade 0.6s ease forwards; }
@keyframes gbOverlayFade{ from{ opacity:1;} to{ opacity:0; } }
</style>
<div id="giftBoxOverlay">
  <div class="gb-sparkle-field" id="gbSparkleField"></div>
  <div class="gb-lightburst" id="gbLightburst"></div>
  <div class="gb-box" id="gbBoxEl">GIFT_EMOJI_PLACEHOLDER</div>
  <div class="gb-hint" id="gbHintEl">Tap the gift to begin</div>
</div>
<script>
(function(){
  var GB_AUDIO_SRC = "data:audio/mp3;base64,AUDIO_PLACEHOLDER";
  var overlay = document.getElementById('giftBoxOverlay');
  var boxEl = document.getElementById('gbBoxEl');
  var hintEl = document.getElementById('gbHintEl');
  var burstEl = document.getElementById('gbLightburst');
  var sparkleField = document.getElementById('gbSparkleField');
  var opened = false;

  var sparkleGlyphs = ['SPARK1_PLACEHOLDER','SPARK2_PLACEHOLDER','SPARK3_PLACEHOLDER'];
  for(var i=0;i<14;i++){
    var s = document.createElement('div');
    s.className = 'gb-sparkle';
    s.textContent = sparkleGlyphs[i % sparkleGlyphs.length];
    s.style.left = (Math.random()*90+5) + '%';
    s.style.top = (Math.random()*90+5) + '%';
    s.style.animationDelay = (Math.random()*2.4) + 's';
    sparkleField.appendChild(s);
  }

  function openGift(){
    if(opened) return;
    opened = true;
    hintEl.style.opacity = '0';

    try{
      var giftAudio = new Audio(GB_AUDIO_SRC);
      giftAudio.volume = 0.85;
      var playPromise = giftAudio.play();
      if(playPromise && playPromise.catch) playPromise.catch(function(){ });
    }catch(e){ }

    boxEl.classList.add('gb-tapped');
    setTimeout(function(){
      var boxRect = boxEl.getBoundingClientRect();
      burstEl.style.left = (boxRect.left + boxRect.width/2 - 5) + 'px';
      burstEl.style.top = (boxRect.top + boxRect.height/2 - 5) + 'px';
      burstEl.classList.add('gb-burst-active');
    }, 260);

    setTimeout(function(){
      overlay.classList.add('gb-fading');
    }, 650);

    setTimeout(function(){
      overlay.classList.add('gb-hidden');
      overlay.style.pointerEvents = 'none';
    }, 1300);
  }

  boxEl.addEventListener('click', openGift);
  boxEl.addEventListener('touchend', function(e){ e.preventDefault(); openGift(); }, {passive:false});
})();
</script>
"""

giftbox_block = giftbox_block.replace("AUDIO_PLACEHOLDER", AUDIO_B64)
giftbox_block = giftbox_block.replace("GIFT_EMOJI_PLACEHOLDER", "\U0001F381")
giftbox_block = giftbox_block.replace("SPARK1_PLACEHOLDER", "\u2728")
giftbox_block = giftbox_block.replace("SPARK2_PLACEHOLDER", "\U0001F31F")
giftbox_block = giftbox_block.replace("SPARK3_PLACEHOLDER", "\u2726")

html = html.replace(body_close, giftbox_block + "\n" + body_close, 1)

with open(TARGET, "w", encoding="utf-8") as f:
    f.write(html)

print("Gift box launch experience added successfully.")
print("Audio embedded: " + str(len(AUDIO_B64)) + " base64 characters (~" + str(len(AUDIO_B64)*3//4//1024) + " KB decoded).")
print("Next: git add -A && git commit -m 'Add gift box launch experience' && git push")
