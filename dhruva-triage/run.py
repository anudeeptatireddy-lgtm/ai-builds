import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import config
import cost
import guard
import llm
import loader
import prompt
import score


def triage(app):
    reply = llm.assess(app["id"], prompt.build(app))
    verdicts = score.normalise(reply["criteria"])
    fit = score.fit_score(verdicts)
    gaps = score.missing(verdicts)
    term = guard.anti_thesis(app)
    rec = score.recommend(fit, len(gaps), term)
    inr = cost.cost_inr(reply.get("tokens_in", 0), reply.get("tokens_out", 0))
    row = {"id": app["id"], "name": app["name"], "fit": fit, "rec": rec,
           "could_not_establish": gaps, "cost_inr": round(inr, 2),
           "over_cost_ceiling": inr > config.COST_CEILING_INR}
    return row, verdicts


def run(path):
    apps = loader.load(path)
    rows = []
    Path("reports").mkdir(exist_ok=True)
    for app in apps:
        try:
            row, verdicts = triage(app)
        except Exception as e:                # one bad application must not stop the batch
            row, verdicts = {"id": app["id"], "name": app["name"], "fit": None,
                             "rec": f"ERROR: {type(e).__name__}: {e}", "could_not_establish": [],
                             "cost_inr": 0.0, "over_cost_ceiling": False}, {}
        rows.append(row)
        Path("reports", app["id"] + ".json").write_text(json.dumps({**row, "criteria": verdicts}, indent=1))

    print(f"{'application':14}{'fit':>5}  {'missing':>7}  recommendation")
    for r in sorted(rows, key=lambda r: -(r["fit"] if r["fit"] is not None else -1)):
        fit = "-" if r["fit"] is None else r["fit"]
        print(f"{r['name']:14}{fit:>5}  {len(r['could_not_establish']):>7}  {r['rec']}")

    ok = [r for r in rows if not r["rec"].startswith("ERROR")]
    if ok:
        avg = sum(r["cost_inr"] for r in ok) / len(ok)
        print(f"\ncost per application: Rs {avg:.2f} (ceiling Rs {config.COST_CEILING_INR}); "
              f"projected quarter ({config.QUARTERLY_VOLUME} apps): Rs {avg * config.QUARTERLY_VOLUME:,.0f}")
        over = [r["name"] for r in ok if r["over_cost_ceiling"]]
        if over:
            print(f"WARNING: over the Rs {config.COST_CEILING_INR} ceiling: {', '.join(over)}")
    errors = [r["name"] for r in rows if r["rec"].startswith("ERROR")]
    if errors:
        print(f"WARNING: {len(errors)} application(s) failed: {', '.join(errors)} (see reports/)")

    Path("runs").mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with open("runs/run_log.jsonl", "a") as f:
        for r in rows:
            f.write(json.dumps({**r, "time": stamp}) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apps", default="data/applications.csv")
    run(ap.parse_args().apps)
