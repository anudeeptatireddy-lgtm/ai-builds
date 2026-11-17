import config

TEMPLATE = """You are screening one inbound startup application for Dhruva Capital.
Judge it against each of the six thesis criteria below, using ONLY the application
form and pitch deck provided. Do not use outside knowledge about the company.

THESIS CRITERIA
{criteria}

For each criterion return a verdict:
- "match": clearly fits the criterion
- "partial": fits in part, or fits weakly
- "no-match": clearly does not fit
- "insufficient-data": the form and deck do not say enough. Use this instead of guessing.

Every verdict other than "insufficient-data" MUST have a "citation" that quotes or points
to where you found it, as "form: <field>=<value>" or "deck: <short quote>".
For "insufficient-data", set "citation" to null and give a "why".

Return ONLY JSON in this shape:
{{"criteria": {{"stage": {{"verdict": "...", "citation": "...", "why": "..."}}, ...all six criteria...}}}}

APPLICATION FORM
{form}

PITCH DECK
{deck}
"""


def build(app):
    criteria = "\n".join(f"- {c}: {config.THESIS[c]}" for c in config.CRITERIA)
    form = "\n".join(f"{k}: {app[k] or '(blank)'}" for k in
                     ("name", "stage", "sector", "hq", "founders", "model", "round_size_cr"))
    return TEMPLATE.format(criteria=criteria, form=form, deck=app["deck"] or "(no deck provided)")
