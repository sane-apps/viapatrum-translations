#!/usr/bin/env python3
"""Regenerate a book scope packet with a declared (append-tolerant) scope.

Migration aid for reviewed-prefix publishing: freezes the CURRENT file rows
as the declared reviewed set. The reviewer still writes the receipt by hand;
this script never signs anything.

  python3 scripts/regen_declared_packet.py BOOK \\
      --english translations/x_english.json --source translations/x_source.json \\
      --raw sources/print.txt --identity-from reviews/audit/old.packet.json \\
      --scope-json reviews/audit/publication_scope.json \\
      --out reviews/audit/tipNNN.packet.json [--verify-old reviews/audit/old.packet.json]

--verify-old reports, per old expected section, whether source/English still
match (by hash), plus the new tail ids that need review. Exit 1 with a
report (not silence) when old declared rows changed: changed history must be
re-reviewed, never carried forward blind.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline.verify_translation_qa import (  # noqa: E402
    digest, indexed, load_rows, make_audit_packet, source_paragraphs,
)


def row_hashes(rows: list[dict]) -> dict[str, tuple[str, str]]:
    out = {}
    for key, row in indexed(rows, "rows").items():
        paras = source_paragraphs(row)
        out[key] = (digest(paras), digest(row))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Regenerate a declared-scope audit packet.")
    ap.add_argument("book", help="books/<slug>")
    ap.add_argument("--english", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--raw", nargs="+", required=True)
    ap.add_argument("--identity-from", required=True, help="old packet.json to reuse identity from")
    ap.add_argument("--scope-json", required=True, help="current publication scope snapshot")
    ap.add_argument("--out", required=True)
    ap.add_argument("--verify-old", default="", help="old packet.json to diff declared rows against")
    ap.add_argument("--expected", nargs="*", default=None,
                    help="declared section ids (default: all current source rows)")
    args = ap.parse_args()

    book = ROOT / args.book
    eng_path = (book / args.english).resolve()
    src_path = (book / args.source).resolve()
    raw = [(book / r).resolve() for r in args.raw]
    identity = json.loads(((book / args.identity_from).read_text()))["identity"]
    scope = json.loads((book / args.scope_json).read_text())
    if args.verify_old:
        old = json.loads((book / args.verify_old).read_text())
        eng_rows = load_rows(eng_path)
        src_rows = load_rows(src_path)
        eng_h = {k: digest(r) for k, r in indexed(eng_rows, "English").items()}
        src_h = row_hashes(src_rows)
        changed, missing = [], []
        for item in old.get("sections", []):
            sec = item["section"]
            live_src = src_h.get(sec, (None, None))[0]
            live_eng = eng_h.get(sec)
            if live_src is None or live_eng is None:
                if sec not in missing:
                    missing.append(sec)
            elif live_src != item.get("source_sha256") or live_eng != item.get("english_sha256"):
                changed.append(sec)
        old_expected = [str(s) for s in old.get("expected_sections", [])]
        current_ids = list(indexed(src_rows, "source"))
        tail = [i for i in current_ids if i not in set(old_expected)]
        print(json.dumps({"old_packet_sections": len(old.get("sections", [])),
                          "missing_declared_rows": missing,
                          "changed_declared_rows": changed,
                          "new_tail_ids": tail}, indent=1))
        if missing or changed:
            print("REFUSING: declared history changed; re-review before regenerating.",
                  file=sys.stderr)
            return 1
    eng_rows = load_rows(eng_path)
    src_rows = load_rows(src_path)
    expected = args.expected or list(indexed(src_rows, "source"))
    # Full selection: every declared section is individually hash-bound, which
    # is what makes the packet append-tolerant at validate time.
    packet = make_audit_packet(eng_path, src_path, raw_sources=raw, identity=identity,
                               expected_sections=expected, selected_sections=list(expected),
                               publication_scope=scope)
    out = book / args.out
    out.write_text(json.dumps(packet, ensure_ascii=False, indent=2))
    print(f"wrote {out} declared={len(expected)} packet_id={packet['packet_id'][:12]}")
    print("NEXT: write the receipt by genuine review, then update the manifest.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
