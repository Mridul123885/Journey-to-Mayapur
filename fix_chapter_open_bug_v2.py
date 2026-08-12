#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Robust fix for the chapter-opening bug. Unlike the previous fix script,
this one does not depend on exact whitespace matching — it finds every
`let currentStoryLang` declaration anywhere in the file (however it's
formatted), removes all of them, and inserts exactly one clean top-level
declaration. It also verifies the result before writing anything.

Usage:
    python3 fix_chapter_open_bug_v2.py
"""
import re, sys, os

TARGET = "www/index.html"

if not os.path.isfile(TARGET):
    print(f"ERROR: could not find {TARGET}. Run this from your repo root.")
    sys.exit(1)

with open(TARGET, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Find every `let currentStoryLang ... ;` declaration, wherever it is,
#    regardless of surrounding whitespace/newlines.
pattern = re.compile(r"let\s+currentStoryLang\s*=\s*'en'\s*;")
matches = list(pattern.finditer(html))
print(f"Found {len(matches)} 'let currentStoryLang' declaration(s) in the file.")

if len(matches) == 0:
    print("No 'let currentStoryLang' declarations found at all — the earlier fix may have "
          "already removed it, or something else is going on. Checking for the variable "
          "being used without any declaration...")
    if "currentStoryLang" not in html:
        print("ERROR: 'currentStoryLang' does not appear anywhere in the file. "
              "The multilingual feature may have been removed or the file is unexpected. "
              "Please tell me and paste `grep -c currentStoryLang www/index.html`.")
        sys.exit(1)
    else:
        print("The variable is used but never declared with 'let' anywhere — this itself "
              "would be a bug (ReferenceError: currentStoryLang is not defined in strict "
              "contexts, or accidental global creation otherwise). Proceeding to add a "
              "single top-level declaration.")

# 2. Remove every existing `let currentStoryLang = 'en';` occurrence.
html = pattern.sub("", html)

# 3. Clean up any now-empty/blank line left behind where those declarations were.
html = re.sub(r"\n[ \t]*\n[ \t]*function renderStoryText", "\nfunction renderStoryText", html)

# 4. Insert exactly one clean declaration immediately before `function openIntro(i){`.
open_intro_pattern = re.compile(r"function openIntro\(i\)\{")
oi_match = open_intro_pattern.search(html)
if not oi_match:
    print("ERROR: could not find 'function openIntro(i){' anywhere in the file. "
          "No changes were written. Please paste me "
          "`grep -n 'function openIntro' www/index.html` so I can see the exact current text.")
    sys.exit(1)

insert_pos = oi_match.start()
html = html[:insert_pos] + "let currentStoryLang = 'en';\n" + html[insert_pos:]
print("Inserted exactly one top-level 'let currentStoryLang' declaration before openIntro().")

# 5. Verify: after this fix, there should be exactly ONE `let currentStoryLang`
#    declaration in the whole file, and it should be a plain top-level
#    statement (not indented deep inside another block by multiple levels).
final_matches = list(re.finditer(r"let\s+currentStoryLang", html))
print(f"Verification: {len(final_matches)} 'let currentStoryLang' declaration(s) after fix "
      f"(should be exactly 1).")

if len(final_matches) != 1:
    print("ERROR: verification failed — did not end up with exactly one declaration. "
          "Nothing was written to disk, to avoid making things worse. Please paste me "
          "this entire script's output and I will fix it directly instead of guessing.")
    sys.exit(1)

with open(TARGET, "w", encoding="utf-8") as f:
    f.write(html)

print("\nVerification passed. www/index.html has been updated and written to disk.")
print("Next: git add -A && git commit -m 'Fix chapter-opening bug (v2)' && git push")
