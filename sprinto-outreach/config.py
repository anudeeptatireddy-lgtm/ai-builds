import os
from dotenv import load_dotenv

load_dotenv()

OFFLINE = os.getenv("OFFLINE", "1") == "1"
API_KEY = os.getenv("GEMINI_API_KEY", "")          # no fake default: live mode fails loudly without a key
MODEL = "gemini-2.0-flash"
TEMPERATURE = 0.2                                   # low: we need stable, parseable JSON, not creativity

QUALIFY_THRESHOLD = 70    # minimum ICP fit to email (score is 0-100, so this is 70, not 0.7)
MAX_ROUNDS = 2            # extra pages the qualifier may ask for
TO_ADDRESS = "growth.lead@example.com"  # case rule: all mail goes to the student's own inbox

SCRAPE_RETRIES = 3        # attempts per page for transient failures (timeouts, 5xx, 429)
SCRAPE_BACKOFF_S = 1.0    # wait 1s, 2s, 4s ... between attempts
SCRAPE_TIMEOUT_S = 10
MIN_PAGE_CHARS = 50       # shorter than this = blocked / JS-only / empty page, not real content
LLM_RETRIES = 3
