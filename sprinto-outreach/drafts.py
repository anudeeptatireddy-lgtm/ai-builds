import llm

PROMPT = """Write a short cold email from Sprinto to {name} ({title}) at {company}.
Name two likely pain points and use one specific hook from: {signals}.
Return JSON: pain_points (list of 2), subject, body."""


def draft(domain, company, contact):
    signals = company.get("compliance_signals") or []
    if not signals:
        # no specific hook = generic spam; don't write the email
        raise ValueError("no compliance signals to use as a hook")
    p = PROMPT.format(
        name=contact["name"], title=contact["title"],
        company=company.get("company") or domain, signals=signals,
    )
    mail = llm.ask("draft", domain, p)
    if not mail.get("subject") or not mail.get("body"):
        raise llm.LLMError("draft is missing subject or body")
    return mail
