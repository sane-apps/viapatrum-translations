#!/usr/bin/env python3
"""Build docs/CORPUS_AUTHORITY.md: external cross-check of corpus completeness.

Sources (all checked in beside this script):
  docs/ccel-english.json      ANF/NPNF tables of contents (scripts/ccel_harvest.py)
  docs/ccel-author-map.json   hand-verified CCEL -> repo author crosswalk
  docs/pg-volume-titles.json  archive.org Migne PG scan titles (70 vols)
  books/*/book.yml            repo corpus (PG/PL edition citations)
Missing-author dates: Wikidata entity claims/descriptions where clean,
standard datings (ODCC-level) where entities were missing or conflicted;
provenance is recorded per row. Years are ordering-grade (floruit/death),
not a scholarly edition of dates.
"""
import html
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (display, sort year, date display, date provenance, map key or None)
MISSING = [
    ("Didache (Teaching of the Twelve Apostles)", 100, "c.100 (work)", "standard", "anonymous",
     ["anf07"]),
    ("Clement of Rome", 100, "d.c.100", "wikidata-Q42887", "clement_rome"),
    ("Ignatius of Antioch", 108, "d.c.108", "wikidata-Q44170", "ignatius_antioch"),
    ("Papias of Hierapolis", 150, "c.70-c.150", "wikidata-Q273053", "ignatius_antioch"),
    ("Aristides of Athens", 140, "fl.c.140", "standard", "aristides"),
    ("Hermas (Shepherd)", 140, "c.140 (work)", "standard", "hermas"),
    ("Mathetes (Epistle to Diognetus)", 150, "c.150 (work)", "standard", "mathetes"),
    ("Polycarp of Smyrna", 155, "69-155", "wikidata-Q192371", "polycarp"),
    ("Justin Martyr", 165, "c.100-165", "wikidata-Q185117", "justin_martyr"),
    ("Athenagoras of Athens", 177, "fl.c.177", "wikidata-Q309772-desc", "athenagoras"),
    ("Tatian", 180, "c.120-c.180", "standard", "tatian"),
    ("Theophilus of Antioch", 180, "fl.c.180", "wikidata-Q220787", "theophilus"),
    ("Scillitan Martyrs (Passion)", 180, "180 (work)", "standard", "rutherford_an"),
    ("Minucius Felix", 200, "fl.c.200 (disputed)", "wikidata-Q319423", "felix"),
    ("Caius (Gaius) of Rome", 200, "fl.c.200", "standard", "caius"),
    ("Clement of Alexandria", 215, "c.150-c.215", "wikidata-Q188883", "clement_alex"),
    ("Tertullian", 220, "c.150-c.220", "wikidata-Q174929", "tertullian"),
    ("Asterius Urbanus", 230, "fl.c.230", "standard", "asterius"),
    ("Hippolytus of Rome", 235, "c.170-c.235", "wikidata-Q207113-desc", "hippolytus"),
    ("Commodianus", 250, "fl.c.250 (disputed)", "wikidata-Q1115768", "commodianus"),
    ("Alexander of Cappadocia (of Jerusalem)", 251, "d.250/251", "standard", "alexander_capp"),
    ("Cyprian of Carthage", 258, "c.210-258", "wikidata-Q190240-desc", "cyprian"),
    ("Novatian", 258, "c.220-258", "wikidata-Q222890", "novatian"),
    ("Dionysius of Alexandria", 265, "d.265", "wikidata-Q328736", "dionysius"),
    ("Malchion of Antioch", 270, "fl.270", "standard", "malchion"),
    ("Theognostus of Alexandria", 280, "fl.c.280", "standard", "theognostus"),
    ("Anatolius of Laodicea", 283, "d.283", "wikidata-Q2524557", "anatolius"),
    ("Pierius of Alexandria", 300, "fl.c.300", "wikidata-Q2335606", "pierus"),
    ("Theonas of Alexandria", 300, "d.c.300", "standard", "theonas"),
    ("Alexander of Lycopolis", 300, "fl.c.300", "wikidata-Q2094745", "alexander_lyc"),
    ("Archelaus (Acts of Disputation)", 300, "c.300 (work; quasi-fictional)", "standard", "archelaus"),
    ("Victorinus of Pettau", 303, "d.303/304", "wikidata-Q469199", "victorinus"),
    ("Phileas of Thmuis", 307, "d.307", "wikidata-Q2348355", "phileas"),
    ("Pamphilus of Caesarea", 309, "d.309", "wikidata-Q1855156", "pamphilus"),
    ("Methodius of Olympus", 311, "d.311", "wikidata-Q518300", "methodius"),
    ("Peter of Alexandria", 311, "d.311", "wikidata-Q365927", "peter_alexandria"),
    ("Lactantius", 317, "c.240-c.317", "wikidata-Q209102", "lactantius"),
    ("Alexander of Alexandria", 326, "d.326", "wikidata-Q44794", "alexander_alexandria"),
    ("Arnobius of Sicca", 327, "c.255-c.327", "wikidata-Q342416", "arnobius"),
    ("Eusebius of Caesarea", 339, "c.265-339", "wikidata-Q142999", "npnf_eusebius"),
    ("Aphrahat", 346, "c.270-346", "wikidata-Q434222", "npnf_aphrahat"),
    ("Hilary of Poitiers", 367, "c.315-367", "wikidata-Q44344", "npnf_hilary"),
    ("Athanasius of Alexandria", 373, "296-373", "wikidata-Q44024", "npnf_athanasius"),
    ("Ephrem the Syrian", 373, "c.306-373", "wikidata-Q200608", "npnf_ephraim"),
    ("Basil of Caesarea", 379, "329-379", "wikidata-Q44258", "npnf_basil"),
    ("Gregory of Nazianzus", 390, "329-c.390", "wikidata-Q44011", "npnf_nazianzen"),
    ("Gregory of Nyssa", 395, "c.335-395", "wikidata-Q191734", "npnf_nyssa"),
    ("Ambrose of Milan", 397, "c.340-397", "wikidata-Q43689-desc", "npnf_ambrose"),
    ("John Chrysostom", 407, "349-407", "wikidata-Q43706", "npnf_chrysostom"),
    ("Rufinus of Aquileia", 411, "c.345-411", "wikidata-Q365835", "npnf_rufinius"),
    ("Jerome", 420, "c.345-420", "wikidata-Q44248", "npnf_jerome_hist"),
    ("Sulpitius Severus", 420, "c.360-c.420", "wikidata-Q336704", "npnf_sulpitius"),
    ("Augustine of Hippo", 430, "354-430", "wikidata-Q8018", "npnf_augustine"),
    ("John Cassian", 435, "c.360-435", "wikidata-Q313795", "npnf_cassian"),
    ("Socrates of Constantinople", 440, "c.380-c.440", "wikidata-Q336198", "npnf_socrates_sozomen"),
    ("Vincent of Lerins", 445, "d.445", "wikidata-Q644057", "npnf_vincent"),
    ("Sozomen", 450, "c.400-c.450", "wikidata-Q354350", "npnf_socrates_sozomen"),
    ("Theodoret of Cyrrhus", 457, "c.393-457", "wikidata-Q317029", "npnf_theodoret"),
    ("Leo the Great", 461, "390-461", "wikidata-Q43954", "npnf_leo"),
    ("Gennadius of Massilia", 496, "d.496", "wikidata-Q373675", "npnf_gennadius"),
    ("Gregory the Great", 604, "540-604", "wikidata-Q42827", "npnf_gregory_great"),
    ("Venantius (On Easter)", 9999, "undated (CCEL ANF07 as given)", "ccel-only", "venantius"),
]

SCOPE_ITEMS = [
    ("Excerpts of Theodotus (ANF08)", "Valentinian Gnostic fragments via Clement - heretical corpus, owner call"),
    ("Narrative of Zosimus + Testament of Abraham (ANF09)", "OT pseudepigrapha, not patristic - owner call"),
    ("Seven Ecumenical Councils (NPNF214)", "conciliar documents, not authored works - owner call"),
    ("NT Apocrypha bundle (ANF08/09: Peter, Diatessaron, Testaments, Apocalypses)",
     "apocrypha - owner call whether in charter scope"),
]


def cell(s, width=60):
    s = re.sub(r"\s+", " ", html.unescape(str(s or ""))).strip().replace("|", "/")
    return s[:width - 1] + "..." if len(s) > width else s


def main():
    ccel = json.loads((ROOT / "docs/ccel-english.json").read_text())
    amap = json.loads((ROOT / "docs/ccel-author-map.json").read_text())
    pg_titles = json.loads((ROOT / "docs/pg-volume-titles.json").read_text())["titles"]

    # sanity: every fine CCEL author mapped, every map key real
    fine = set(ccel["authors"])
    mapped_fine = {k for k in amap if not k.startswith(("_", "npnf_"))}
    assert mapped_fine == fine, "map drift: %s" % (fine ^ mapped_fine)

    def vols_for(key):
        if key in ccel["authors"]:
            vols = sorted({v for e in ccel["authors"][key]["works"].values() for v in e["volumes"]})
            return vols
        return amap[key]["ccel_volumes"]

    repo_authors = set()
    pg_cite = Counter()
    pl_cite = Counter()
    for f in (ROOT / "books").glob("*/book.yml"):
        txt = f.read_text()
        m = re.search(r"(?m)^author: (.*)$", txt)
        if m:
            repo_authors.add(m.group(1).strip().strip('"'))
        for v in re.findall(r"PG\s+(\d+)", txt):
            pg_cite[int(v)] += 1
        for v in re.findall(r"PL\s+(\d+)", txt):
            pl_cite[int(v)] += 1

    covered_repo = {e["repo_author"] for e in amap.values()
                    if isinstance(e, dict) and e.get("repo_author")}
    first_english_authors = sorted(a for a in repo_authors - covered_repo
                                   if "topical library" not in a)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    md = []
    md.append("# Corpus Authority Report\n")
    md.append("Generated %s by scripts/build_corpus_authority.py. Cross-checks the repo "
              "corpus against outside authorities: CCEL's ANF/NPNF (prior English), "
              "Migne PG/PL volume citations, and Wikidata datings. Re-run after "
              "corpus or crosswalk changes.\n" % now)
    md.append("## Method in one paragraph\n")
    md.append("CCEL's 38 Schaff volumes were harvested (authors + works + volumes) and "
              "hand-mapped to repo authors, calling out same-name different-person cases "
              "(Antioch/Alexandria, Urbanus/Amasea, Caesarea/Emesa, Massilia/Constantinople). "
              "Missing authors are dated from Wikidata claims, falling back to standard "
              "datings where entities were absent or conflicted; provenance per row. "
              "PG/PL coverage counts direct volume citations in book.yml files (alternate "
              "editions like GCS undercount true coverage - see caveats).\n")
    md.append("## A. Authors with CCEL English but zero repo books (%d, oldest first)\n" % len(MISSING))
    md.append("This is the charter queue: oldest first, each with dated prior English to beat.\n")
    md.append("| Year | Author | Dates | CCEL English |")
    md.append("|---|---|---|---|")
    for row in sorted(MISSING, key=lambda r: r[1]):
        display, year, dates, prov, key = row[:5]
        vols = row[5] if len(row) > 5 else vols_for(key)
        y = "?" if year == 9999 else year
        md.append("| %s | %s | %s (%s) | %s |"
                  % (y, display, dates, prov, ", ".join(vols)))
    md.append("\n## B. Shared authors: repo AND CCEL (complementarity)\n")
    md.append("| Repo author | CCEL has | Relationship |")
    md.append("|---|---|---|")
    for key in sorted(amap):
        if key.startswith("_"):
            continue
        e = amap[key]
        if e.get("repo_author"):
            md.append("| %s | %s | %s |"
                      % (e["repo_author"], ", ".join(vols_for(key)), cell(e["note"], 90)))
    md.append("\n## C. Repo authors with no CCEL English (%d, first-English territory)\n"
              % len(first_english_authors))
    md.append(", ".join("`%s`" % a for a in first_english_authors) + "\n")
    md.append("## D. PG volume triage (cited %d/161 volumes)\n" % len(pg_cite))
    md.append("Gap volumes with archive.org scan-title cues; bare/UNVERIFIED rows need the "
              "scan's own table of contents before claiming contents.\n")
    md.append("| PG vol | Repo cites | Scan-title cue |")
    md.append("|---|---|---|")
    for v in range(1, 162):
        if v in pg_cite:
            continue
        title = pg_titles.get(str(v), "")
        cue = title.split("Volume %d" % v)[-1].strip(" -") if title else ""
        if not cue:
            cue = "UNVERIFIED (no scan title)"
        md.append("| %d | 0 | %s |" % (v, cell(cue, 70)))
    md.append("\nCovered volumes: %s\n"
              % ", ".join(str(v) for v in sorted(pg_cite)))
    md.append("## E. PL volume triage (cited %d/217 volumes)\n" % len(pl_cite))
    if pl_cite:
        md.append("Covered volumes: %s\n" % ", ".join(str(v) for v in sorted(pl_cite)))
    else:
        md.append("ZERO Latin Father coverage by Migne citation. The missing Latin authors "
                  "from table A (Tertullian, Cyprian, Minucius, Novatian, Lactantius, "
                  "Arnobius, Commodianus, Victorinus, Ambrose, Jerome, Augustine, Hilary, "
                  "Sulpitius, Vincent, Cassian, Leo, Gregory I) confirm it: the Latin "
                  "corpus is unstarted.\n")
    md.append("## F. Scope questions for the owner\n")
    for title, note in SCOPE_ITEMS:
        md.append("- %s: %s" % (title, note))
    md.append("")
    md.append("## Caveats\n")
    md.append("- Book-level granularity: an author marked present may still lack individual "
              "works (work-level CPG/CPL cross-check is future work).")
    md.append("- PG citations undercount coverage where books use GCS/SC/OCT instead of Migne.")
    md.append("- Missing-author years are ordering-grade, not critical datings.")
    md.append("")
    (ROOT / "docs/CORPUS_AUTHORITY.md").write_text("\n".join(md), encoding="utf-8")
    n_cited = sum(pg_cite.values())
    print("missing_authors=%d shared=%d first_english_authors=%d pg_cited_vols=%d pg_cites=%d"
          % (len(MISSING), len(covered_repo), len(first_english_authors),
             len(pg_cite), n_cited))


if __name__ == "__main__":
    main()
