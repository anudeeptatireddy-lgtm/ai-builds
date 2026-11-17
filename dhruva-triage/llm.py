import json
import re
from pathlib import Path
import config

_CANNED = Path(__file__).parent / "fixtures" / "llm_responses.json"


class LLMError(Exception):
    """The model reply was missing, unparseable, or malformed."""


def _parse(text):
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", (text or "").strip())
    data = json.loads(text)
    if not isinstance(data, dict) or not isinstance(data.get("criteria"), dict):
        raise ValueError("reply must be a JSON object with a 'criteria' object")
    return data


def assess(app_id, prompt):
    """Return {'criteria': {...}, 'tokens_in': int, 'tokens_out': int} for one application."""
    if config.OFFLINE:
        try:
            return json.loads(_CANNED.read_text())[app_id]
        except KeyError:
            raise LLMError(f"no canned reply for application {app_id}")

    if not config.API_KEY:
        raise LLMError("GEMINI_API_KEY is not set (add it to .env or use OFFLINE=1)")

    from google import genai
    client = genai.Client(api_key=config.API_KEY)
    last = None
    for _ in range(3):
        try:
            resp = client.models.generate_content(
                model=config.MODEL, contents=prompt,
                config={"temperature": config.TEMPERATURE, "response_mime_type": "application/json"})
            data = _parse(resp.text)
            usage = resp.usage_metadata          # the live reply has no token counts of its own
            data["tokens_in"] = usage.prompt_token_count or 0
            data["tokens_out"] = usage.candidates_token_count or 0
            return data
        except Exception as e:
            last = e
    raise LLMError(f"assessment of {app_id} failed after 3 tries: {last}")
