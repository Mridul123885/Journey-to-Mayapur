#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fixes the chapter-opening bug introduced by add_multilang.py: the
`currentStoryLang` variable was declared with `let` inside openIntro(),
after an earlier plain assignment to the same name in the same function —
a JavaScript temporal-dead-zone error that threw on every chapter tap.

This script only touches that one declaration. It does not change any
story text, Bengali/Hindi content, UI, or anything else.

Usage:
    python3 fix_chapter_open_bug.py
"""
import sys, os

TARGET = "www/index.html"

if not os.path.isfile(TARGET):
    print(f"ERROR: could not find {TARGET}. Run this from your repo root.")
    sys.exit(1)

with open(TARGET, "r", encoding="utf-8") as f:
    html = f.read()

changed = False

# 1. Remove the erroneous `let currentStoryLang = 'en';` that sits right
#    before `function renderStoryText(lv){` inside openIntro() — this was
#    the duplicate declaration causing the crash.
bad_snippet = "let currentStoryLang = 'en';\nfunction renderStoryText(lv){"
good_snippet = "function renderStoryText(lv){"
if bad_snippet in html:
    html = html.replace(bad_snippet, good_snippet, 1)
    print("Removed the duplicate in-function 'let' declaration.")
    changed = True
else:
    print("Did not find the expected duplicate declaration — it may already be fixed, "
          "or the file differs from what add_multilang.py produced. No change made here.")

# 2. Add a single, proper top-level declaration of currentStoryLang right
#    before the openIntro function itself, so the variable exists safely
#    for the whole script, declared exactly once.
anchor = "function openIntro(i){"
if anchor in html and "let currentStoryLang = 'en';\nfunction openIntro(i){" not in html:
    html = html.replace(anchor, "let currentStoryLang = 'en';\n" + anchor, 1)
    print("Added a single top-level declaration of currentStoryLang before openIntro().")
    changed = True
elif "let currentStoryLang = 'en';\nfunction openIntro(i){" in html:
    print("Top-level declaration already present — no change needed there.")
else:
    print("ERROR: could not find 'function openIntro(i){' to attach the top-level "
          "declaration to. No change made.")
    sys.exit(1)

if not changed:
    print("\nNo changes were made. If chapters are still broken, please tell me and "
          "paste a screenshot or description of what happens when you tap a chapter, "
          "so I can look deeper.")
else:
    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(html)
    print("\nDone. www/index.html has been fixed in place.")
    print("Next: git add -A && git commit -m 'Fix chapter-opening bug' && git push")
