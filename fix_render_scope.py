#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fixes the language-switching bug: renderStoryText() was declared inside
openIntro(), but called from the button click handlers outside it, so it
was invisible to them and silently failed. This moves the function
declaration to the top level (same fix pattern as the earlier
currentStoryLang bug), leaving the call inside openIntro() untouched.

Usage:
    python3 fix_render_scope.py
"""
import re, sys, os

TARGET = "www/index.html"

if not os.path.isfile(TARGET):
    print("ERROR: could not find " + TARGET + ". Run this from your repo root.")
    sys.exit(1)

with open(TARGET, "r", encoding="utf-8") as f:
    html = f.read()

# Find the renderStoryText function declaration, wherever it currently sits,
# and extract its full body (matching braces).
func_start_pattern = re.compile(r"function renderStoryText\(lv\)\{")
m = func_start_pattern.search(html)
if not m:
    print("ERROR: could not find 'function renderStoryText(lv){' anywhere. No changes made.")
    sys.exit(1)

start = m.start()
# walk forward from the opening brace to find its matching closing brace
i = m.end()  # position right after the opening '{'
depth = 1
while depth > 0:
    if html[i] == '{':
        depth += 1
    elif html[i] == '}':
        depth -= 1
    i += 1
end = i  # position right after the matching closing '}'

func_text = html[start:end]
print("Found renderStoryText function, " + str(end-start) + " characters.")

# Remove it from its current (nested) location.
html_without = html[:start] + html[end:]

# Insert it as a top-level declaration, right before 'function openIntro(i){'
oi_pattern = re.compile(r"function openIntro\(i\)\{")
oi_match = oi_pattern.search(html_without)
if not oi_match:
    print("ERROR: could not find 'function openIntro(i){' to attach it before. "
          "No changes were written, to avoid losing the function.")
    sys.exit(1)

insert_pos = oi_match.start()
html_fixed = html_without[:insert_pos] + func_text + "\n" + html_without[insert_pos:]

# Verify: exactly one declaration should exist now, and it should now be
# positioned before openIntro (i.e. at top level, not nested inside it).
final_count = len(func_start_pattern.findall(html_fixed))
print("Verification: " + str(final_count) + " renderStoryText declaration(s) after fix (should be 1).")

if final_count != 1:
    print("ERROR: verification failed. Nothing was written to disk. Please paste this "
          "entire output and I will fix it directly.")
    sys.exit(1)

with open(TARGET, "w", encoding="utf-8") as f:
    f.write(html_fixed)

print("")
print("Done. renderStoryText is now a top-level function, callable from the language buttons.")
print("Next: git add -A && git commit -m 'Fix renderStoryText scope bug' && git push")
