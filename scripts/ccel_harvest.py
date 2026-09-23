#!/usr/bin/env python3
"""Harvest CCEL's ANF/NPNF tables of contents into docs/ccel-english.json.

Provenance: https://ccel.org/fathers (38 Schaff volumes). Polite: one
request per ~1.5s with a descriptive UA. Re-run rarely; output is checked in
so the catalog does not depend on the network.
"""
import json
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs/ccel-english.json"
UA = {"User-Agent": "SaneApps-translations-corpus-audit/1.0 (contact: hi@saneapps.com)"}

VOLS = (["anf%02d" % i for i in range(1, 11)]
        + ["npnf1%02d" % i for i in range(1, 15)]
        + ["npnf2%02d" % i for i in range(1, 15)])

LINK = re.compile(r'href="https?://ccel\.org/ccel/([a-z0-9_]+)/([a-z0-9_]+)/[a-z0-9]+"[^>]*>\s*([^<]{3,100})<')
TITLE = re.compile(r"<title>\s*Work info:\s*[A-Z0-9-]+\.\s*(.*?)\s*-\s*Christian Classics", re.S)


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as resp:
        return resp.read().decode("utf-8", "replace")


def main():
    authors = {}
    volumes = {}
    for vol in VOLS:
        html = fetch("https://ccel.org/ccel/schaff/%s.html" % vol)
        seen = set()
        for author, work, title in LINK.findall(html):
            if author == "schaff":
                continue
            key = (author, work)
            if key in seen:
                continue
            seen.add(key)
            entry = authors.setdefault(author, {"works": {}})
            entry["works"].setdefault(work, {"title": title.strip(), "volumes": []})
            if vol not in entry["works"][work]["volumes"]:
                entry["works"][work]["volumes"].append(vol)
        title = TITLE.search(html)
        volumes[vol] = {"description": re.sub(r"\s+", " ", title.group(1)).strip() if title else "",
                        "works": sorted("%s/%s" % (a, w) for a, w in seen)}
        print("%s: %d works | %s" % (vol, len(seen), volumes[vol]["description"][:70]), flush=True)
        time.sleep(1.5)
    for entry in authors.values():
        entry["works"] = {k: entry["works"][k] for k in sorted(entry["works"])}
    OUT.write_text(json.dumps({"source": "https://ccel.org/fathers",
                               "authors": authors, "volumes": volumes}, indent=1))
    print("authors=%d works=%d" % (len(authors), sum(len(e["works"]) for e in authors.values())))


if __name__ == "__main__":
    main()
