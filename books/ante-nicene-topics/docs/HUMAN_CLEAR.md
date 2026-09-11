# Human clear checklist — MVP golden set (Soteriology / Free Will)

## Status (v0.8.4)

**Professional GTG: Yes** (second-model PASS WITH CAVEATS on golden set + hold-unlock PASS).  
Reports:
- `outputs/reviews/second_model_golden_set_audit_2026-09-10_v081.md` (46 clears)
- `outputs/reviews/second_model_hold_unlock_audit_2026-09-10.md` (Melito + Victorinus)
- `outputs/reviews/caveat_settlement_2026-09-10.md`

**MVP: 48/48 `source_verified`.**  
`--strict-professional` green. Harvey print-check cleared. Sellable GTG still No.

| Bucket | Count | Notes |
|--------|------:|-------|
| `source_verified` + second-model clear | 48 | Full golden set |

### Optional Sellable follow-ups

| Item | Action |
|------|--------|
| Human spot-check | Owner glance of sample receipts |
| Melito PDF label | Aegean digital Fragmenta (PG 5 tradition), not camera-scan of Migne |
| Optional Routh page-check | Confirm ἀπέκρυβε vs ἀπεκρύβη on Reliquiae I print |
| Same-locus seeds | Christology Melito seeds synced in English; still `seed_edition` until mined clears |

### Owner clear (if overriding)

1. Open `reviews/justifications/<id>.json`.
2. Confirm edition + English.
3. Set `"reviewer": "owner-YYYY-MM-DD"` and `"checks.human_clear": "pass"`.

```bash
.venv/bin/python books/ante-nicene-topics/scripts/qa_professional.py --strict-professional
```
