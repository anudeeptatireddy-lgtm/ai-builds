import re

import config

POINTS = {"match": 1, "partial": 0.5, "no-match": 0}
MISSING = "insufficient-data"


def normalise(verdicts):
    """Make the model's reply safe to score: all six criteria present, valid verdicts only,
    and no verdict without a citation (an uncited verdict is a guess, so it counts as missing)."""
    out = {}
    for c in config.CRITERIA:
        v = dict(verdicts.get(c) or {})
        verdict = v.get("verdict")
        if verdict not in POINTS and verdict != MISSING:
            v = {"verdict": MISSING, "citation": None, "why": f"model returned no valid verdict ({verdict!r})"}
        elif verdict in POINTS and not v.get("citation"):
            v = {"verdict": MISSING, "citation": None, "why": "model gave a verdict with no citation"}
        out[c] = v
    return out


def raw_score(verdicts):
    """Points over the criteria we could establish. Unknown criteria earn nothing."""
    return sum(POINTS.get(v["verdict"], 0) for v in verdicts.values())


def missing(verdicts):
    return [c for c, v in verdicts.items() if v["verdict"] == MISSING]


def fit_score(verdicts):
    """Fit out of 10 over the criteria we could establish; None if nothing could be established.
    (Scored on an absolute scale, not relative to other applications in the batch.)"""
    established = len(verdicts) - len(missing(verdicts))
    if established == 0:
        return None
    return round(raw_score(verdicts) / established * 10, 1)


def recommend(fit, n_missing, term):
    if term:
        return f"PASS (anti-thesis: {term})"
    if fit is None or n_missing > config.MAX_MISSING:
        return "INSUFFICIENT DATA TO RECOMMEND"
    return "ADVANCE TO CALL" if fit >= config.ADVANCE_AT else "PASS"


def verify_citations(verdicts, app):
    """Do not trust the model's quotes. Returns (verdicts, flags).
    - 'form: field=value' citations are checked against the real form; a mismatch downgrades the
      verdict to insufficient-data (the model cited something the form does not say).
    - 'deck:' citations whose wording barely appears in the deck are only flagged, because
      citations may legitimately paraphrase."""
    out, flags = {}, []
    deck = (app.get("deck") or "").lower()
    for c, v in verdicts.items():
        v = dict(v)
        cit = v.get("citation") or ""
        if v["verdict"] in POINTS:
            for field, val in re.findall(r"form:\s*(\w+)\s*=\s*([^;]+)", cit):
                if val.strip().lower() != str(app.get(field, "")).strip().lower():
                    v = {"verdict": MISSING, "citation": None,
                         "why": f"cited form {field}={val.strip()!r} does not match the form"}
                    flags.append(f"{c}: form citation mismatch")
                    break
            else:
                m = re.search(r"deck:\s*(.+?)(?:;\s*form:|$)", cit)
                if m:
                    words = [w for w in re.findall(r"[a-z0-9]{4,}", m.group(1).lower())]
                    if words and sum(w in deck for w in words) / len(words) < 0.5:
                        flags.append(f"{c}: deck citation not found in deck")
        out[c] = v
    return out, flags
