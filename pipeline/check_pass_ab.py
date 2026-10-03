#!/usr/bin/env python3
"""Deterministic two-pass checks. A clean result is not a fidelity verdict.

Also the tip/SERIES closeout gate: English and source files must pass
`check_translation_files` before a claim may be marked done. The fathers site
catalogue gate uses the same scaffold/contamination smells — tip closeout must
not outrun that gate.
"""
from __future__ import annotations

import argparse
from difflib import SequenceMatcher
import json
from pathlib import Path
import re
import sys
import unicodedata

GREEK = re.compile(r"[\u0370-\u03ff\u1f00-\u1fff]")
PLACEHOLDER = re.compile(
    r"\b(?:TODO|TBD|FIXME|YYYY)\b|\[n\d+\]|\blemma-led\s+open\b|"
    r"\brem\s+(?:early|mid|closeout)\s*:|\blemma and argument toward the thesis\b|"
    r"\b(?:see translations/|see working file|full cleaned source)\b|"
    r"\b(?:scaffold|placeholder|translation pending)\b",
    re.I,
)
CONTAMINATION = re.compile(
    r"\bMelito skipped\b|\bnever Cyril Matthew densify\b|\bpro cibo temporary\b|"
    r"\b(?:SERIES CLOSEOUT|true OET|skip Pusey-PD)\b",
    re.I,
)
# English token that must never appear inside Greek/Latin source fields.
SOURCE_ENGLISH_LEAK = re.compile(r"\btemporary\b", re.I)


def join_b(value) -> str:
    if isinstance(value, list):
        return " ".join(str(x) for x in value).strip()
    return str(value or "").strip()


def visible_text(text: str) -> str:
    text = re.sub(r"\[\[([^\[\]]+?)\s*>>\s*[^\]]+\]\]", r"\1", text)
    return re.sub(r"\[\[@[^\]]+\]\]", "", text)


def normalized(text: str) -> str:
    text = unicodedata.normalize("NFKC", visible_text(text)).casefold()
    return " ".join(re.findall(r"[^\W_]+", text, re.UNICODE))


def greek_ratio(text: str) -> float:
    return len(GREEK.findall(text)) / max(sum(c.isalpha() for c in text), 1)


def content_errors(value, label="english", *, source=False) -> list[str]:
    if not isinstance(value, (str, list)) or (isinstance(value, list) and any(
            not isinstance(p, str) or not p.strip() for p in value)):
        return [f"{label}: expected nonempty strings"]
    text = join_b(value)
    errors = []
    if not text:
        errors.append(f"{label}: empty text")
    # Numbered footnote markers belong in some raw-source transcriptions;
    # they remain invalid unresolved placeholders in the English reading text.
    check_text = re.sub(r"\[n\d+\]", "", text) if source else text
    if PLACEHOLDER.search(check_text) or CONTAMINATION.search(check_text):
        errors.append(f"{label}: placeholder or operational text")
    if source and SOURCE_ENGLISH_LEAK.search(text):
        errors.append(f"{label}: English/operational token in source")
    if not source and text and greek_ratio(visible_text(text)) > 0.25:
        errors.append(f"{label}: copied Greek needs review; expected English")
    visible = visible_text(text)
    if not source and _repeated_phrase(visible):
        errors.append(f"{label}: repeated phrase; the same words run three times in a row")
    if not source and _latin_bleed(visible):
        errors.append(f"{label}: Latin left in the English")
    if not source and (_debris_text(visible) or _bare_debris(value)):
        errors.append(f"{label}: printer, page, or footnote debris")
    if source and _failed_greek_scan(text):
        errors.append(f"{label}: source is betacode or a broken Greek scan")
    return errors


LATIN_FUNCTION = {
    "cum", "ut", "quod", "quia", "enim", "autem", "sunt", "neque", "quasi",
    "etiam", "tamen", "igitur", "ergo", "atque", "sive", "nisi", "eius",
    "eorum", "quae", "quam", "quo", "qua", "nec", "sed", "est", "sit",
}
LATIN_ENDING = re.compile(r"(?:ibus|ntur|tur|tionis|tatem|tate|us|um|ae)$")
ENGLISH_FUNCTION = {
    "the", "a", "of", "and", "to", "that", "is", "in", "for", "not", "we",
    "he", "his", "this", "from", "by", "or", "as", "with", "which", "be",
    "are", "was", "were", "their", "it", "but", "if", "than", "who", "an",
    "on", "at", "they", "them", "she", "her", "our", "your",
}

_GLUED = re.compile(r"\b[A-Za-z]{4,}\d{2,}\b")
_SIGNATURE = re.compile(r"\b[A-Z][ij]{2,4}\b")
_PHYS = re.compile(r"\bPHYS\b")
_DENSIFY = re.compile(r"\bdensify\s+complete\b", re.I)
_BLEED_EXTRA = {"et", "non"}


def _tokens(text: str) -> list[str]:
    text = unicodedata.normalize("NFKC", visible_text(text)).casefold()
    return re.findall(r"[^\W_]+", text, re.UNICODE)


def _repeated_phrase(text: str) -> bool:
    """Same 4 to 8 word run, three times, with no words between the copies.

    A verse list such as Romans 5:15 repeated by the scripture linker is mostly
    digits, so it does not count. One-word refrains do not count either.
    """
    words = _tokens(text)
    for n in range(4, 9):
        need = n * 3
        if len(words) < need:
            continue
        for i in range(0, len(words) - need + 1):
            phrase = words[i:i + n]
            if phrase != words[i + n:i + 2 * n] or phrase != words[i + 2 * n:i + 3 * n]:
                continue
            if len(set(phrase)) < 2:
                continue
            if sum(w.isdigit() for w in phrase) * 2 >= len(phrase):
                continue
            return True
    return False


# Save-time output guard (2026-10-02). Model drafts sometimes stutter
# ("many.many.many"), double words, or stop mid-clause. Drafting scripts call
# output_guard_errors() BEFORE writing so damaged text never replaces good
# text. Deliberately not part of content_errors(): the publish gate stays as
# it was, so already-live passages are not newly blocked.
_GLUED_STUTTER = re.compile(r"\b([A-Za-z]{2,})(?:[.,;:\-]?\1){2,}\b", re.I)
# Same word four times, separated only by spaces/commas (no verse digits):
# "Genesis 1:1; Genesis 2:3" lists and "Holy, holy, holy" stay legal.
_WORD_RUN = re.compile(r"\b([A-Za-z]+)\b(?:[ ,]+\1\b){3,}", re.I)
# Doubled function words with only a space between are model stutter;
# "Lord, Lord" / "Amen, amen" (punctuated) are Scripture and stay legal.
_DOUBLED = re.compile(r"\b(the|a|an|and|of|to|in|for|with|by|from|on|at|is|was|but|or)\s+\1\b", re.I)
_END_OK = re.compile(r"[.!?…:;”’\"')\]—]\s*$")


def output_guard_errors(english, *, require_full_stop: bool = False) -> list[str]:
    """Reject damaged model output before it is saved.

    require_full_stop: also reject a paragraph that stops mid-clause. Leave it
    off for chunked sources, whose slices legitimately end mid-sentence.
    """
    paras = [english] if isinstance(english, str) else list(english or [])
    errors = []
    for i, para in enumerate(paras, 1):
        text = visible_text(str(para or "")).strip()
        if not text:
            errors.append(f"paragraph {i}: empty")
            continue
        for rx, what in ((_GLUED_STUTTER, "stuttered word fragment"), (_WORD_RUN, "word repeated four times"),
                         (_DOUBLED, "doubled word")):
            m = rx.search(text)
            if m:
                errors.append(f"paragraph {i}: {what} ({m.group(0)[:40]})")
        if _repeated_phrase(text):
            errors.append(f"paragraph {i}: repeated phrase")
        if require_full_stop and not _END_OK.search(text):
            errors.append(f"paragraph {i}: stops mid-sentence ('...{text[-30:]}')")
    return errors


def _latin_bleed(text: str) -> bool:
    """A stretch of Latin function words inside an English reading."""
    words = [w for w in _tokens(text) if w.isascii()]
    if len(words) < 8:
        return False
    for i in range(0, len(words) - 7):
        chunk = words[i:i + 12]
        if len(chunk) < 8:
            break
        latin = sum((w in LATIN_FUNCTION or w in _BLEED_EXTRA) for w in chunk)
        english = sum(w in ENGLISH_FUNCTION for w in chunk)
        if latin >= 6 and english <= 1:
            return True
    return False


def _debris_text(text: str) -> bool:
    if _GLUED.search(text) or _PHYS.search(text) or _DENSIFY.search(text):
        return True
    for match in _SIGNATURE.finditer(text):
        if match.group(0).casefold() != "dii":
            return True
    return False


def _bare_debris(value) -> bool:
    parts = value if isinstance(value, list) else [value]
    for part in parts:
        if not isinstance(part, str):
            continue
        stripped = part.strip()
        if re.fullmatch(r"\d{1,4}", stripped):
            return True
        if re.fullmatch(r"[A-Z][ij]{2,4}", stripped) and stripped.casefold() != "dii":
            return True
    return False


def _failed_greek_scan(text: str) -> bool:
    """Betacode, or a Greek scan that collapsed into backslash codes.

    A Latin lock, even a short gloss with few function words, stays legal.
    Marginal marks the lock never stored cannot be reconstructed here.
    """
    if greek_ratio(text) >= 0.15 or sum(c.isalpha() for c in text) < 80:
        return False
    return text.count("\\") >= 8




def _hyphen_gloss(text: str, words: list) -> bool:
    joins = len(re.findall(r"[A-Za-z]-[A-Za-z]", text))
    return joins >= 8 and joins >= 0.03 * max(1, len(words))


def check_record(j: dict) -> list[str]:
    if not isinstance(j, dict):
        return ["justification must be an object"]
    a, b, src = (join_b(j.get(k)) for k in ("pass_a_gloss", "pass_b_english", "source_text"))
    errors = content_errors(j.get("pass_a_gloss"), "pass_a_gloss")
    errors += content_errors(j.get("pass_b_english"), "pass_b_english")
    errors += content_errors(j.get("source_text"), "source_text", source=True)
    na, nb = normalized(a), normalized(b)
    a_words, b_words = na.split(), nb.split()
    if na and nb:
        if na == nb:
            errors.append("Pass A copies Pass B (including formatting-only differences)")
        elif min(len(a_words), len(b_words)) >= 25:  # short maxims: gloss can be the English
            smaller, larger = sorted((na, nb), key=len)
            ratio = SequenceMatcher(None, a_words, b_words, autojunk=False).ratio()
            if smaller in larger or ratio >= 0.82:
                errors.append(
                    "Pass A and Pass B are near-copies; Pass B is still the gloss in source "
                    "word order. Rewrite the sentences without adding or dropping a claim"
                )
    if len(b_words) >= 40 and len(a_words) < 0.45 * len(b_words):
        errors.append("Pass A is too short to constrain Pass B; gloss every clause in English")
    if a_words:
        latin = sum(1 for w in a_words if w in LATIN_FUNCTION or LATIN_ENDING.search(w))
        english = sum(1 for w in a_words if w in ENGLISH_FUNCTION)
        if latin / len(a_words) >= 0.12 and english / len(a_words) < 0.20:
            errors.append("Pass A is a Latin note, not an English sense gloss")
    # Interlinear cribs hyphenate most words; long sections legitimately
    # carry a few compounds ("well-known", "God-befitting"), so use a share.
    if _hyphen_gloss(a, a_words):
        errors.append("Pass A is an interlinear hyphen gloss; write a normal English sense gloss")
    if normalized(src) and normalized(src) == nb:
        errors.append("Pass B copies source text")
    # Literary Pass B (STYLE.md): accurate sense in readable prose — not gloss residue.
    if b_words:
        if _hyphen_gloss(b, b_words):
            errors.append(
                "Pass B is still an interlinear hyphen gloss; write literary English sentences"
            )
        # Ignore Scripture / cited quotations; flag archaic diction in the translator's own prose.
        b_unquoted = re.sub(r'["\u201c\u201d][^"\u201c\u201d]{0,400}["\u201c\u201d]', " ", b)
        b_unquoted = re.sub(r"'[^']{0,200}'", " ", b_unquoted)
        if re.search(
            r"\b(?:hath|wherefore|thereof|\bye\b|thou|thee|\bthy\b|hast|doth|saith)\b",
            b_unquoted,
            re.I,
        ):
            errors.append(
                "Pass B uses archaic King James diction outside quotations; use modern literary English"
            )
        # Greek/Latin genitive calques that survived the literary pass
        if len(re.findall(r"\bthe of (?:the|a|an)\b", b, re.I)) >= 2:
            errors.append(
                "Pass B keeps source-word-order calques (the of the…); rewrite as English prose"
            )
        # Gloss left in place: almost no sentence punctuation on a long reading text
        if len(b_words) >= 60 and b.count(".") + b.count("?") + b.count("!") < 2:
            errors.append(
                "Pass B lacks sentence shape; polish into readable prose without adding claims"
            )
    for key in ("lemmas", "choices"):
        rows = j.get(key)
        if not isinstance(rows, list) or not rows or any(not isinstance(x, dict) or not x for x in rows):
            errors.append(f"{key}: expected nonempty objects")
    return errors


def check_file(path: Path) -> list[str]:
    try:
        return check_record(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        return [f"cannot read justification: {exc}"]


def _row_key(row: dict) -> str:
    sec = row.get("section")
    if sec is None:
        # Codex-keyed rows (Photius Bibliotheca) identify by codex, not section.
        sec = row.get("codex")
    return str(sec)


def _load_rows(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        # Codex-keyed books (Photius Bibliotheca) keep one source object per file.
        return [data]
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected a JSON list of section rows")
    return data


def check_english_rows(rows: list) -> list[str]:
    errors: list[str] = []
    if not rows:
        return ["english: empty file"]
    for row in rows:
        if not isinstance(row, dict):
            errors.append("english: row must be an object")
            continue
        sec = row.get("section")
        for err in content_errors(row.get("english"), "english"):
            errors.append(f"section {sec}: {err}")
    return errors


def check_source_rows(rows: list) -> list[str]:
    errors: list[str] = []
    if not rows:
        return ["source: empty file"]
    for row in rows:
        if not isinstance(row, dict):
            errors.append("source: row must be an object")
            continue
        sec = row.get("section")
        body = row.get("greek") if row.get("greek") not in (None, [], "") else None
        if body is None:
            body = row.get("latin") if row.get("latin") not in (None, [], "") else None
        if body is None:
            body = row.get("source_text")
        if body is None:
            # Julian-style rows carry the author's Latin under "julian"
            # (Augustine's replies ride along under "augustine" and are not
            # the translation source). Without this fallback every Julian
            # row fails as empty text.
            body = row.get("julian")
        for err in content_errors(body, "source", source=True):
            errors.append(f"section {sec}: {err}")
    return errors


def check_translation_files(english_path: Path, source_path: Path) -> list[str]:
    """Tip/SERIES closeout gate for a paired english.json + source.json."""
    errors: list[str] = []
    try:
        english_rows = _load_rows(english_path)
    except (OSError, ValueError) as exc:
        return [f"english: {exc}"]
    try:
        source_rows = _load_rows(source_path)
    except (OSError, ValueError) as exc:
        return [f"source: {exc}"]
    errors.extend(check_english_rows(english_rows))
    errors.extend(check_source_rows(source_rows))
    eng_secs = {_row_key(r) for r in english_rows if isinstance(r, dict)}
    src_secs = {_row_key(r) for r in source_rows if isinstance(r, dict)}
    if eng_secs != src_secs:
        errors.append(
            f"section set mismatch: english={sorted(eng_secs)} source={sorted(src_secs)}"
        )
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tip-ready",
        nargs=2,
        metavar=("ENGLISH_JSON", "SOURCE_JSON"),
        help="Refuse tip/SERIES closeout unless both files are publication-ready",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="justification files or directories (default mode)",
    )
    args = parser.parse_args(argv)

    if args.tip_ready:
        eng, src = (Path(p) for p in args.tip_ready)
        errors = check_translation_files(eng, src)
        if errors:
            for err in errors[:40]:
                print(f"FAIL: {err}")
            if len(errors) > 40:
                print(f"FAIL: … {len(errors) - 40} more")
            print(f"tip-ready: fail={len(errors)} pair={eng.name}+{src.name}")
            return 1
        print(f"tip-ready: ok pair={eng.name}+{src.name}")
        return 0

    files = sorted({f for path in args.paths for f in
                    (path.glob("*.json") if path.is_dir() else [path])})
    if not files:
        print("FAIL: no justification files found")
        return 1
    failures = 0
    for path in files:
        errors = check_file(path)
        if errors:
            failures += 1
            print(f"FAIL {path.name}: {'; '.join(errors)}")
    print(f"ok={len(files) - failures} fail={failures} total={len(files)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
