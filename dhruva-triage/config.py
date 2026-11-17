import os
from dotenv import load_dotenv

load_dotenv()

OFFLINE = os.getenv("OFFLINE", "1") == "1"
API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL = "gemini-2.0-flash"
TEMPERATURE = 0.0       # scoring should be repeatable, not creative

CRITERIA = ["stage", "sector", "geography", "founder_profile", "business_model", "round_size"]

# What "match" means for each criterion. Inferred from the sample data and case brief:
# CHECK these against the Dhruva Capital thesis in Case 3 and adjust.
THESIS = {
    "stage": "Pre-seed or Seed. Series A and later is no-match.",
    "sector": "B2B software that automates back-office processes (finance, operations, compliance).",
    "geography": "Headquartered in India and selling mainly to Indian customers.",
    "founder_profile": "Founders with deep domain experience in the customer's industry and a technical co-founder.",
    "business_model": "Recurring B2B revenue (annual SaaS contracts). One-off, transaction-only or consumer sales are weak.",
    "round_size": "Early-stage round of roughly 3-10 crore INR. Far outside that range is no-match.",
}

ADVANCE_AT = 7.0       # fit score out of 10 (over the criteria we could establish) needed to advance
MAX_MISSING = 3        # MORE than this many criteria with insufficient data: no recommendation
COST_CEILING_INR = 20  # per application
QUARTERLY_VOLUME = 380
