import time
from pathlib import Path
import requests
import config

PAGES = Path(__file__).parent / "fixtures" / "pages"


class ScrapeError(Exception):
    """A page could not be fetched or had no usable text. The message says why."""


def fetch(domain, path="home"):
    """Return cleaned page text for a domain (home or about page).

    Transient failures (timeouts, connection errors, HTTP 429/5xx) are retried with
    exponential backoff. Permanent ones (404, no cached page, empty page) are not.
    Raises ScrapeError with the reason instead of silently returning "".
    """
    if config.OFFLINE:
        f = PAGES / f"{domain}_{path}.txt"
        try:
            text = f.read_text()
        except FileNotFoundError:
            raise ScrapeError(f"no cached page for {domain}/{path}")
        return _check(text, domain, path)

    url = f"https://{domain}/" + ("" if path == "home" else path)
    last = "unknown error"
    for attempt in range(1, config.SCRAPE_RETRIES + 1):
        try:
            resp = requests.get(url, timeout=config.SCRAPE_TIMEOUT_S,
                                headers={"User-Agent": "Mozilla/5.0 (compatible; outreach-research)"})
            if resp.status_code == 429 or resp.status_code >= 500:
                last = f"HTTP {resp.status_code}"              # transient: retry
            elif resp.status_code >= 400:
                raise ScrapeError(f"{url} returned HTTP {resp.status_code}")  # permanent: don't retry
            else:
                return _check(clean(resp.text), domain, path)
        except requests.RequestException as e:
            last = f"{type(e).__name__}: {e}"
        if attempt < config.SCRAPE_RETRIES:
            wait = config.SCRAPE_BACKOFF_S * 2 ** (attempt - 1)
            print(f"  [scrape] {url} attempt {attempt}/{config.SCRAPE_RETRIES} failed ({last}); retrying in {wait:g}s")
            time.sleep(wait)
    raise ScrapeError(f"{url} failed after {config.SCRAPE_RETRIES} attempts: {last}")


def _check(text, domain, path):
    if len(text.strip()) < config.MIN_PAGE_CHARS:
        raise ScrapeError(f"{domain}/{path} had no usable text (blocked, empty or JavaScript-only page)")
    return text


def clean(html):
    lines = [l.strip() for l in html.splitlines() if len(l.split()) >= 8]
    seen, out = set(), []
    for l in lines:
        if l not in seen:
            seen.add(l)
            out.append(l)
    return "\n".join(out)[:8000]
