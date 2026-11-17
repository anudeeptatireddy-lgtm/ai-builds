import re

ANTI_THESIS = ["consumer social", "gaming", "creator economy", "nbfc", "lending licen[cs]e",
               "d2c", "crypto", "web3"]
_PATTERNS = [(t, re.compile(rf"\b{t}\b", re.I)) for t in ANTI_THESIS]


def anti_thesis(app):
    """Return the anti-thesis term an application hits, or None.
    Checks the form AND the deck, so a banned business can't hide behind a vague sector field."""
    text = " ".join(str(app.get(k) or "") for k in ("sector", "model", "deck"))
    for term, pat in _PATTERNS:
        m = pat.search(text)
        if m:
            return m.group(0).lower()
    return None
