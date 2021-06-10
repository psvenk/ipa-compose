from bs4 import BeautifulSoup
import requests
import re
from string import ascii_letters

HELP_URL = "https://help.keyman.com/keyboard/sil_ipa/1.8.5/sil_ipa"
OUTFILE = "ipa.compose"

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

# TODO implement substring detection for keystrokes (use . as sentinel)

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
    if (re.search(r", \d{4}", ipa_desc) or "IPA" in ipa_desc
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
                "keystrokes": reversed(strokes),
                "usv": usv,
                "symbol_name": symbol_name,
                "ipa_desc": ipa_desc,
            })
        continue

    if len(keystrokes) > 2:
        print(keystrokes)
    # if len(glyph) > 1:
    #     print(glyph)

    symbols.append({
        "glyph": glyph,
        "keystrokes": reversed(keystrokes),
        "usv": usv,
        "symbol_name": symbol_name,
        "ipa_desc": ipa_desc,
    })

for symbol in symbols:
    strokes = [KEYSYMS[k] for k in symbol["keystrokes"]]
    print(strokes)
    # print(symbol)
