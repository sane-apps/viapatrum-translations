"""Attribution list for the beliefs map, from the 2026-10-03 Claude audit.

spurious: left off the map. doubtful / catena: shown with a note, never sets
an earliest date. work_year: the work's own date instead of the writer's
death. Passage entries name the real speaker of a quotation inside a work.
"""
import json
from pathlib import Path

T = Path.home() / "SaneApps/clients/translations"
books = {}


def put(slugs, status, note, **extra):
    for s in slugs:
        books[s] = {"status": status, "note": note, **extra}


put(["epiphanius-homilia-in-laudes-mariae-deiparae", "epiphanius-homilia-in-assumptionem-christi",
     "epiphanius-homilia-in-christi-resurrectionem", "epiphanius-homilia-in-divini-corporis-sepulturam",
     "epiphanius-homilia-in-festo-palmarum"], "spurious",
    "Pseudo-Epiphanius: the homilies in PG 43 are later works transmitted under his name.")
put(["epiphanius-liturgia-praesanctificatorum"], "spurious", "A later Byzantine liturgy, not by Epiphanius.")
put(["epiphanius-index-discipulorum", "epiphanius-index-apostolorum", "epiphanius-notitiae-episcopatuum",
     "epiphanius-appendices-ad-indices-apostolorum-discipulorumque"], "spurious",
    "Pseudo-Epiphanius: Byzantine lists (the Notitiae use later titles such as Patriarch).")
put(["eustathius-hexaemeron"], "spurious", "Pseudo-Eustathius: not by Eustathius of Antioch.")
put(["gregory-thaumaturgus-sermo-in-omnes-sanctos"], "spurious", "Generally held to be spurious; the 270 date is unsafe.")
put(["epiphanius-anaphora-graeca"], "doubtful", "Authorship and date of this anaphora are uncertain.")
put(["epiphanius-testamentum-ad-cives", "epiphanius-epistula-ad-theodosium-imperatorem",
     "epiphanius-tractatus-contra-eos-qui-imagines-faciunt"], "doubtful",
    "Known only through iconoclast quotation; Nicephorus denied Epiphanius wrote it, and scholars still debate it.")
put(["epiphanius-testimonia-ex-divinis-et-sacris-scripturis"], "doubtful", "Attribution to Epiphanius is doubtful.")
put(["didymus-de-trinitate"], "doubtful", "Attribution of De Trinitate to Didymus is disputed.")
put(["severianus-de-caeco-nato"], "doubtful", "Transmitted among Chrysostom's spurious works; ascription to Severian is a modern proposal.")
put(["amphilochius-contra-haereticos"], "doubtful", "Ascription to Amphilochius is debated.")
put(["severianus-de-caeco-zacchaeo"], "doubtful", "Transmitted among Chrysostom's spurious works; given to Severian only by modern attribution.")
put(["cyril-alexandria-dialogus-nestorio"], "doubtful", "Widely doubted as Cyril's; some lines are given to Nestorius.")
catena = [s for s in (p.name for p in (T / "books").iterdir())
          if any(s.startswith(a) for a in ("apollinaris-fragmenta-", "didymus-fragment", "diodorus-fragmenta-",
                                           "eusebius-emesa-fragment", "gennadius-fragment", "severianus-fragmenta-",
                                           "ammonius-fragmenta-", "cyril-alexandria-matthew-fragments",
                                           "cyril-alexandria-lucam-fragmenta"))
          or (s.startswith("cyril-alexandria-fragment") and not any(k in s for k in ("contra-", "de-uno-filio", "homiliae", "papyraceum")))]
put(catena, "catena", "A catena fragment: the ascription rests on the catena heading and is not secure.")
books.setdefault("irenaeus-demonstration", {})["work_year"] = 180
books.setdefault("origen-heraclides-pascha", {})["work_year"] = 245
books.setdefault("julian-of-eclanum", {})["work_year"] = 418  # joint Pelagian letters, quoted by Augustine

# Quotations inside a work, by passage-id prefix from the audit reports.
PREFIX = {
    "a62c57": {"author": "Apollinaris of Laodicea (quoted as Athanasius)", "work_year": 363,
               "note": "Cyril quotes this as Athanasius; it is Apollinaris' creed to Jovian."},
    "6ef185": {"author": "Apollinaris of Laodicea (quoted as Athanasius)", "work_year": 363,
               "note": "Cyril quotes this as Athanasius; it is Apollinaris' creed to Jovian."},
    "fb28955b": {"author": "Apollinaris of Laodicea (quoted as Athanasius)", "work_year": 363,
                 "note": "Cyril quotes this as Athanasius; it is Apollinaris' creed to Jovian."},
    "70cab5": {"author": "Nestorius (as quoted)", "work_year": 431, "status": "doubtful",
               "note": "Nestorius' words, quoted in a dialogue whose ascription to Cyril is doubted."},
    "bc5fff": {"author": "Antiochus of Ptolemais (quoted by Cyril)", "work_year": 408},
    "e5dac4": {"author": "Severian of Gabala (quoted by Cyril)", "work_year": 408},
    "af945f": {"author": "Ammonius of Adrianople (quoted by Cyril)", "work_year": 431},
    "6166a3": {"author": "John Chrysostom (quoted by Cyril)", "work_year": 407, "status": "doubtful",
               "note": "Quoted by Cyril as Chrysostom; the ascription still needs checking."},
    "52c7c68c": {"author": "Origen (catena heading)", "work_year": 254, "status": "catena",
                 "note": "Filed under Didymus, but the catena heads it 'Of Origen'."},
    "dd9e49e8": {"author": "Athanasius (catena heading)", "work_year": 373, "status": "catena",
                 "note": "Filed under Origen but headed 'Of Athanasius' in the catena."},
}
ids = [json.loads(l)["id"] for l in (T / "outputs/doctrine-map/corpus.jsonl").read_text().splitlines()]
passages = {}
for pre, entry in PREFIX.items():
    hits = [i for i in ids if i.startswith(pre)]
    if len(hits) != 1:
        print(f"prefix {pre}: {len(hits)} matches; skipped")
        continue
    passages[hits[0]] = entry
out = Path.home() / "SaneApps/websites/fathers.saneapps.com/data/explore/attribution.json"
out.write_text(json.dumps({"source": "Claude audit of the beliefs map, 2026-10-03", "books": books,
                           "passages": passages}, ensure_ascii=False, indent=1))
print(f"attribution: {len(books)} books ({len(catena)} catena), {len(passages)} passages")
