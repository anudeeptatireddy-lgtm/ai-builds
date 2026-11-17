import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import contacts
import drafts
import extract
import qualify
import scrape
import send
import impact


def process(d, contacts_path, row):
    """Run one company through the pipeline, filling `row`. Every early exit records why."""
    try:
        text = scrape.fetch(d)
    except scrape.ScrapeError as e:
        row.update(score=0, qualified=False, reason=f"scrape failed: {e}")
        return
    company = extract.extract(d, text)
    q = qualify.qualify(d, company)
    row.update(score=q["score"], qualified=q["qualified"], reason=q["reason"])
    if not q["qualified"]:
        return
    contact = contacts.find_contact(d, contacts_path)
    if not contact:
        row["send"] = "skipped: no contact found"
        return
    row["contact"] = contact["name"]
    try:
        mail = drafts.draft(d, company, contact)
    except ValueError as e:
        row["send"] = f"skipped: {e}"
        return
    row["subject"] = mail["subject"]
    row["send"] = send.send(d, mail["subject"], mail["body"])


def run(domains, contacts_path):
    rows = []
    for d in dict.fromkeys(domains):          # drop duplicates, keep order
        t0 = time.time()
        row = {"domain": d, "score": 0, "qualified": False, "reason": ""}
        try:
            process(d, contacts_path, row)
        except Exception as e:                # one bad company must not kill the whole run
            row["error"] = f"{type(e).__name__}: {e}"
            row["qualified"] = False
        row["seconds"] = round(time.time() - t0, 2)
        row["time"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        rows.append(row)
        status = row.get("send") or row.get("error") or row["reason"]
        print(f"{d:22} score={row['score']:<4} qualified={row['qualified']!s:5} "
              f"{row.get('contact', '-'):14} {status}")
    Path("runs").mkdir(exist_ok=True)
    with open("runs/run_log.jsonl", "a") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    failed = [r["domain"] for r in rows if r.get("error") or r["reason"].startswith("scrape failed")]
    print(f"\n{len(rows)} companies, {sum(r['qualified'] for r in rows)} qualified, "
          f"{len(failed)} failed{': ' + ', '.join(failed) if failed else ''}")
    print(impact.monthly_summary())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--domains", default="data/domains.txt")
    ap.add_argument("--contacts", default="data/contacts.csv")
    a = ap.parse_args()
    run(Path(a.domains).read_text().split(), a.contacts)
