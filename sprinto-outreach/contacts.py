import csv


def find_contact(domain, path="data/contacts.csv", live=False):
    if live:
        try:
            from hunter import HunterClient
        except ImportError:
            raise RuntimeError("live contact lookup needs the 'hunter' package, which is not installed")
        return HunterClient().find_decision_maker(domain)

    domain = domain.strip().lower()
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if row["domain"].strip().lower() == domain:
                return {"name": row["name"], "title": row["title"], "email": row["email"]}
    return None
