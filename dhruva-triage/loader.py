import csv
from pathlib import Path

FIELDS = ["id", "name", "stage", "sector", "hq", "founders", "model", "round_size_cr"]


def load(path="data/applications.csv"):
    apps = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        # strip stray whitespace in headers (applications_v2.csv has 'round_size_cr ')
        reader.fieldnames = [h.strip() for h in reader.fieldnames or []]
        missing = [c for c in FIELDS if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"{path} is missing columns: {', '.join(missing)}")
        for row in reader:
            app = {k: (row.get(k) or "").strip() for k in FIELDS}
            deck = Path("decks", app["id"] + ".txt")
            app["deck"] = deck.read_text() if deck.exists() else ""   # a missing deck is a data gap, not a crash
            apps.append(app)
    return apps
