# Illustrative assumptions from Case 2 (15-20 min per company by hand, 8-15 companies a week).
MANUAL_MINUTES_PER_COMPANY = 17.5
COMPANIES_PER_WEEK = 12
WEEKS_PER_MONTH = 52 / 12
HOURLY_COST_INR = 1200
TOOL_COST_PER_MONTH_INR = 6000


def monthly_summary():
    hours_per_week = MANUAL_MINUTES_PER_COMPANY * COMPANIES_PER_WEEK / 60
    hours_per_month = hours_per_week * WEEKS_PER_MONTH      # was weekly hours labelled as monthly
    value = hours_per_month * HOURLY_COST_INR
    return {
        "hours_saved_per_month": round(hours_per_month, 1),
        "net_value_per_month_inr": round(value - TOOL_COST_PER_MONTH_INR),
    }
