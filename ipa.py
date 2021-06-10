from bs4 import BeautifulSoup
import requests
import re
from string import ascii_letters

"""
Copyright (c) 2021 psvenk
All rights reserved.

SPDX-License-Identifier: BSD-2-Clause

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

HELP_URL = "https://help.keyman.com/keyboard/sil_ipa/1.8.5/sil_ipa"

KEYSYMS = {
    "<": "less",
    ">": "greater",
    "=": "equal",
    "|": "bar",
    "^": "asciicircum",
    "~": "asciitilde",
    "?": "question",
    "!": "exclam",
    "]": "bracketright",
    "%": "percent",
    "$": "dollar",
    "{": "braceleft",
    "+": "plus",
    "_": "underscore",
    "*": "asterisk",
    "[": "bracketleft",
    "}": "braceright",
    ":": "colon",
    ".": "period",
} | {x: x for x in ascii_letters}

symbols = []

soup = BeautifulSoup(requests.get(HELP_URL).text, "lxml")
for row in soup.select("h1 ~ table > tr"):
    data = [re.sub(r"\s+", " ", cell.text.strip())
            for cell in row.select("td")]
    _, glyph, keystrokes, ipa_no, usv, symbol_name, ipa_desc = data

    if glyph == keystrokes:
        # We don't need a mapping for this
        continue
    if not keystrokes:
        # Symbol unsupported by keyboard
        continue
    if (re.search(r", ?[12]\d{3}", ipa_desc) or "IPA" in ipa_desc
            or "use" in ipa_no):
        # Withdrawn, superseded, not IPA usage, etc.
        continue
    if "@" in keystrokes or "#" in keystrokes:
        # Exclude tone and contour markers
        continue

    if match := re.fullmatch(r"(.+) or (.+)", keystrokes):
        for strokes in match.groups():
            symbols.append({
                "glyph": glyph,
                "keystrokes": strokes[::-1],
                "usv": usv,
                "symbol_name": symbol_name,
                "ipa_desc": ipa_desc,
            })
        continue

    symbols.append({
        "glyph": glyph,
        "keystrokes": keystrokes[::-1],
        "usv": usv,
        "symbol_name": symbol_name,
        "ipa_desc": ipa_desc,
    })

for symbol in symbols:
    # Get keysyms for keystrokes
    strokes = [KEYSYMS[k] for k in symbol["keystrokes"]]

    # If another sequence of keystrokes begins with this sequence, use "."
    # (period) to signal the end of this sequence
    for s in symbols:
        if (s["keystrokes"] != symbol["keystrokes"]
                and s["keystrokes"].startswith(symbol["keystrokes"])):
            assert s["keystrokes"][-1] != "."
            strokes.append(KEYSYMS["."])
            break

    # Event string for Compose file
    event = "<Multi_key> <Multi_key> " + " ".join(f"<{s}>" for s in strokes)
    # Result string for Compose file
    result = f'"{chr(int(symbol["usv"], 16))}" U{symbol["usv"]}'
    # IPA description
    ipa_desc = symbol["ipa_desc"].capitalize()
    # Symbol name
    symbol_name = symbol["symbol_name"]

    print(f"# {ipa_desc} ({symbol_name}) \n{event} : {result}")
