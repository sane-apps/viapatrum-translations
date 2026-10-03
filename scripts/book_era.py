"""Which books are early (writer died by 450): lanes translate those first.

Owner 2026-10-03: focus on the first 450 years so the beliefs map can show
clearly what was early and what came later. `python3 book_era.py` prints
where early and later works stand.
"""
import json, re, sys
from collections import Counter
from functools import lru_cache
from pathlib import Path

T = Path.home() / "SaneApps/clients/translations"
DATES = json.loads((Path.home() / "SaneApps/websites/fathers.saneapps.com/data/author-dates.json").read_text())
# Writers missing from the site's date list, by death (or floruit) year.
EXTRA = {"Cyril of Jerusalem": 386, "Macarius the Egyptian": 391,
         "Origen (anthology by Basil & Gregory)": 254}
EARLY_UNTIL = 450


def year_of(dates: str):
    """Last year in a date string: death, or floruit. 'c. 376–444' -> 444; '2nd century' -> 199."""
    if not dates:
        return None
    m = re.findall(r"\b(\d{2,4})\b", dates)
    if m:
        return int(m[-1])
    c = re.search(r"(\d)(?:st|nd|rd|th) century", dates)
    return int(c.group(1)) * 100 - 1 if c else None


def author_of(book: str) -> str:
    f = T / "books" / book / "book.yml"
    if not f.is_file():
        return ""
    m = re.search(r'^author:\s*"?([^"\n]+)"?', f.read_text(), re.M)
    return m.group(1).strip() if m else ""


@lru_cache(maxsize=None)
def book_year(book: str):
    """book.yml `year:` first (intake books set it), else the writer's dates."""
    f = T / "books" / book / "book.yml"
    m = re.search(r"^year:\s*(\d{2,4})", f.read_text(), re.M) if f.is_file() else None
    if m:
        return int(m.group(1))
    a = author_of(book)
    return EXTRA.get(a) or year_of(DATES.get(a, ""))


def is_early(book: str) -> bool:
    y = book_year(book)
    return y is not None and y <= EARLY_UNTIL


if __name__ == "__main__":
    sys.path.insert(0, str(T / "scripts"))
    import work_pipeline as W
    q = json.loads(W.QUEUE_LOG.read_text()) if W.QUEUE_LOG.exists() else {}
    stats, unknown = Counter(), Counter()
    for unpub in (False, True):
        for words, b in W.site_books(unpub):
            a = author_of(b)
            y = book_year(b)
            if y is None:
                unknown[a] += 1
            era = "unknown" if y is None else ("early" if y <= 450 else "later")
            state = q.get(b, {}).get("result") or ("certified" if W.certified(b) else "waiting")
            stats[(("unpublished" if unpub else "live"), era, state)] += 1
    for k, v in sorted(stats.items()):
        print(v, k)
    print("authors with no date:", unknown.most_common(25))
