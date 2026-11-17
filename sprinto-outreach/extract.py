import llm

PROMPT = """From this company page extract JSON with keys:
company, product, is_saas (bool), stage, employees (int), compliance_signals (list).
Use null when the page does not say.

PAGE:
{text}"""


def extract(domain, text):
    return llm.ask("extract", domain, PROMPT.format(text=text))


def merge(old, new):
    """Add facts from a second page without letting nulls/empties overwrite known values."""
    out = dict(old)
    for k, v in new.items():
        if v in (None, "", []):
            continue
        if isinstance(v, list) and isinstance(out.get(k), list):
            out[k] = out[k] + [x for x in v if x not in out[k]]
        else:
            out[k] = v
    return out
