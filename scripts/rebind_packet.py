"""Rebind a tip audit packet after an English edit. Usage (stdin, from repo root):
  rebind <book-slug> <packet-file> <english-file> <section>
Recomputes the English file sha, the section english_sha256, and packet_id
using the pipeline's own digest functions, after self-validating the method
against an untouched section and the current packet_id. Edits by exact hex
replacement: no reformatting noise."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline.verify_translation_qa import digest, file_digest

slug, packet_name, english_name, section = sys.argv[1:5]
book = Path("books") / slug
english_path = book / "translations" / english_name
packet_path = book / "reviews" / "audit" / packet_name
review_path = packet_path.with_name(packet_name.replace(".packet.json", ".review.json"))

packet = json.loads(packet_path.read_text(encoding="utf-8"))
rows = {
    str(s.get("section")): s
    for s in json.loads(english_path.read_text(encoding="utf-8"))
    if isinstance(s, dict)
}

others = [k for k in rows if k != section]
assert others, "need an untouched section to self-check against"
probe = others[0]
stored = next(s["english_sha256"] for s in packet["sections"] if str(s.get("section")) == probe)
assert digest(rows[probe]) == stored, f"digest method mismatch on section {probe}"

old_id = packet["packet_id"]
body = {k: v for k, v in packet.items() if k != "packet_id"}
assert digest(body) == old_id, "packet_id method mismatch"

new_file_sha = file_digest(english_path)
old_file_sha = next(f["sha256"] for f in packet["files"] if f["path"].endswith(english_name))
sec = next(s for s in packet["sections"] if str(s.get("section")) == section)
old_en_sha, new_en_sha = sec["english_sha256"], digest(rows[section])
assert (new_file_sha, new_en_sha) != (old_file_sha, old_en_sha), "nothing changed?"

new_body = json.loads(json.dumps(body))
for f in new_body["files"]:
    if f["path"].endswith(english_name):
        f["sha256"] = new_file_sha
for s in new_body["sections"]:
    if str(s.get("section")) == section:
        s["english_sha256"] = new_en_sha
new_id = digest(new_body)

for p, old, new in (
    (packet_path, old_file_sha, new_file_sha),
    (packet_path, old_en_sha, new_en_sha),
    (packet_path, old_id, new_id),
):
    s = p.read_text(encoding="utf-8")
    assert s.count(old) == 1, f"{p.name}: {old[:12]} found {s.count(old)}x"
    p.write_text(s.replace(old, new), encoding="utf-8")

if review_path.exists():
    s = review_path.read_text(encoding="utf-8")
    assert s.count(old_id) == 1, f"review: packet_id found {s.count(old_id)}x"
    review_path.write_text(s.replace(old_id, new_id), encoding="utf-8")
    print("review rebound too", flush=True)

print(f"rebound: file {old_file_sha[:12]} -> {new_file_sha[:12]}", flush=True)
print(f"rebound: sec {section} {old_en_sha[:12]} -> {new_en_sha[:12]}", flush=True)
print(f"rebound: packet {old_id[:12]} -> {new_id[:12]}", flush=True)
