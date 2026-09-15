# Claims — who is working on what

Take the next free slice:

**Tip/SERIES closeout gate:** `python3 scripts/assert_tip_ready.py <english.json> <source.json>` must exit 0 before marking done. Scaffold (`Lemma-led` / `Rem early|mid|closeout`) or tip ops in source are refused.


```bash
python3 scripts/claims.py start --agent YourName
```

That locks the top `free` row. One slice per person. Statuses: `free` → `claimed` → `prepped` (machine crib) or `done` (human Pass B).  
If a `claimed` row is older than 48 hours with no handoff, anyone may set it back to `free`.

**Pass B scripture gate (standing, 2026-09-12):** do **not** mark a claim `done` if the Father quotes or clearly alludes to Scripture and `english[]` lacks an inline parenthetical full-name ref beside the clause. Apparatus / `added_allusions` / `bible_refs` alone fail. No new Adorations densify until the corpus upgrade pass is solid (`docs/scripture-ref-upgrade-pass.md` in the Project store). See `docs/SOP.md`, `TRANSLATION_QA.md` Bible refs, Project store `docs/scripture-refs-inline.md`.

## Open / active claims

| Claim ID | Status | Book slug | Slice (sections) | Agent | Started | Branch | Notes |
|----------|--------|-----------|------------------|-------|---------|--------|-------|
| nemesius-de-natura-hominis-densify | prepped | nemesius-de-natura-hominis | Full work densify (Wither 1636 PD English) | Owner | 2026-09-14 | wip/nemesius-de-natura-hominis-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| macarius-spiritual-homilies-densify | prepped | macarius-spiritual-homilies | Full work densify (PD English exists) | Owner | 2026-09-14 | wip/macarius-spiritual-homilies-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| philostorgius-he-densify | prepped | philostorgius-he | Full work densify (Walford PD English) | Owner | 2026-09-15 | wip/philostorgius-he-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| greg-thaum-fide-xii-densify | prepped | gregory-thaumaturgus-de-fide-xii | Full work densify (ANF 4 exists) | Owner | 2026-09-15 | wip/greg-thaum-fide-xii-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| greg-thaum-ad-tatianum-densify | prepped | gregory-thaumaturgus-ad-tatianum-de-anima | Full work densify (ANF 4 exists) | Owner | 2026-09-15 | wip/greg-thaum-ad-tatianum-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| greg-thaum-annuntiationem-densify | prepped | gregory-thaumaturgus-in-annuntiationem | Full work densify (ANF 4 exists) | Owner | 2026-09-15 | wip/greg-thaum-annuntiationem-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| greg-thaum-sermo-omnes-densify | prepped | gregory-thaumaturgus-sermo-in-omnes-sanctos | Full work densify (ANF 4 exists) | Owner | 2026-09-15 | wip/greg-thaum-sermo-omnes-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| greg-thaum-panegyricus-densify | prepped | gregory-thaumaturgus-panegyricus | Full work densify (ANF 4 exists) | Owner | 2026-09-15 | wip/greg-thaum-panegyricus-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| greg-thaum-eccl-metaphrase-densify | prepped | gregory-thaumaturgus-ecclesiastes-metaphrase | Full work densify (ANF 4 exists) | Owner | 2026-09-15 | wip/greg-thaum-eccl-metaphrase-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| greg-thaum-epistula-can-densify | prepped | gregory-thaumaturgus-epistula-canonica | Full work densify (ANF 4 exists) | Owner | 2026-09-15 | wip/greg-thaum-epistula-can-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| serapion-fragmenta-densify | prepped | serapion-antioch-fragmenta | Full work densify (ANF 4 exists) | Owner | 2026-09-15 | wip/serapion-fragmenta-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| epiphanius-ancoratus-densify | prepped | epiphanius-ancoratus | Full work densify (ANF 4 exists) | Owner | 2026-09-15 | wip/epiphanius-ancoratus-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| epiphanius-panarion-densify | prepped | epiphanius-panarion | Full work densify (ANF 4 exists) | Owner | 2026-09-15 | wip/epiphanius-panarion-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| epiphanius-anaceph-densify | prepped | epiphanius-anacephalaeosis | Full work densify (ANF 4 exists) | Owner | 2026-09-15 | wip/epiphanius-anaceph-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| epiphanius-de-mensuris-densify | prepped | epiphanius-de-mensuris | Full work densify (ANF 4 exists) | Owner | 2026-09-15 | wip/epiphanius-de-mensuris-densify | machine crib (Pass A/lemmas/OCR); not reading English |
| photius-bibliotheca-densify | free | photius-bibliotheca | Full work densify (Freese PD English) |  |  |  | Rank-2 densify; Freese PD English exists; new English from Greek |
| cosmas-topographia-densify | free | cosmas-topographia | Full work densify (McCrindle 1897 PD English) |  |  |  | Rank-2 densify; McCrindle PD English exists; new English from Greek |
| paulus-silentarius-sophia-densify | free | paulus-silentarius-sophia | Full work densify (Lethaby PD English) |  |  |  | Rank-2 densify; Lethaby PD English exists; new English from Greek |
| paulus-silentarius-ambonis-densify | free | paulus-silentarius-ambonis | Full work densify (Lethaby/Swainson PD English) |  |  |  | Rank-2 densify; Lethaby/Swainson PD English exists; new English from Greek |

## How to claim

```bash
python3 scripts/claims.py start --agent YourName
```

Then do only that slice. Finish with `python3 scripts/ai_promote.py --claim <id> --agent YourName`.

## Done / closed

| Claim ID | Status | Slice | Closed | Notes |
|----------|--------|-------|--------|-------|
| strimesius-prefatio-si-tip | done (5fbe207dd) | Strimesius Prefatio section I tip ready; GB 3epYAAAAcAAJ 1708 PD Latin Francofurti ad Viadrum; Pass A≠B; Philippians 2:1-4 inline; tip only not SERIES CLOSEOUT | 2026-09-15 | Reformed retrieval #6 Frankfurt (Oder)/Viadrina; sister Arminianismum Halle queued |
|