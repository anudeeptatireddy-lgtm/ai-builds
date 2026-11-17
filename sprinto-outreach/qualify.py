import config
import llm
import scrape
import extract

PROMPT = """Sprinto sells compliance automation (SOC 2, ISO 27001, GDPR) to SaaS
companies at Series A-C that are preparing for an audit or pressed by enterprise
customers. Score this company's fit and say if more information is needed.
Return JSON: score (0-100), reason, needs_more (bool).

COMPANY: {company}"""

EXTRA_PAGES = ["about"]   # pages we may fetch when the model says it needs more; each is tried once


def _check(result):
    s = result.get("score")
    if isinstance(s, bool) or not isinstance(s, (int, float)) or not 0 <= s <= 100:
        raise llm.LLMError(f"score must be a number 0-100, got {s!r}")
    result.setdefault("reason", "")
    result["needs_more"] = bool(result.get("needs_more", False))
    return result


def qualify(domain, company):
    result = _check(llm.ask("qualify", domain, PROMPT.format(company=company)))
    pages = iter(EXTRA_PAGES[:config.MAX_ROUNDS])
    notes = []
    while result["needs_more"]:
        path = next(pages, None)
        if path is None:
            notes.append("still unsure after extra pages")
            break
        try:
            more = scrape.fetch(domain, path)
            company = extract.merge(company, extract.extract(domain, more))
            result = _check(llm.ask("qualify_more", domain, PROMPT.format(company=company)))
        except (scrape.ScrapeError, llm.LLMError) as e:
            notes.append(f"could not get /{path}: {e}")   # keep the first score, but say so
            break
    if notes:
        result["reason"] = f"{result['reason']} [{'; '.join(notes)}]"
    result["qualified"] = result["score"] >= config.QUALIFY_THRESHOLD
    return result
