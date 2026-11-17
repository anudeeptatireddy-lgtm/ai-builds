import json
import re
from pathlib import Path
import config

_CANNED = Path(__file__).parent / "fixtures" / "llm_responses.json"


class LLMError(Exception):
    """The model reply was missing, unparseable, or not a JSON object."""


def _parse(text):
    """Models often wrap JSON in ```json fences; strip them before parsing."""
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", (text or "").strip())
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("expected a JSON object")
    return data


def ask(step, domain, prompt):
    """Return the model's JSON reply as a dict. Raises LLMError if it cannot."""
    if config.OFFLINE:
        canned = json.loads(_CANNED.read_text())
        try:
            return canned[step][domain]
        except KeyError:
            raise LLMError(f"no canned reply for step={step!r} domain={domain!r}")

    if not config.API_KEY:
        raise LLMError("GEMINI_API_KEY is not set (add it to .env or use OFFLINE=1)")

    from google import genai
    client = genai.Client(api_key=config.API_KEY)
    last = None
    for _ in range(config.LLM_RETRIES):
        try:
            resp = client.models.generate_content(
                model=config.MODEL,
                contents=prompt,
                config={"temperature": config.TEMPERATURE,
                        "response_mime_type": "application/json"},
            )
            return _parse(resp.text)
        except Exception as e:           # API error or bad JSON: ask again
            last = e
    raise LLMError(f"{step} failed for {domain} after {config.LLM_RETRIES} tries: {last}")
