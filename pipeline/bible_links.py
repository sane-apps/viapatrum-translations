"""Shared Bible-reference detection and Logos PBB link markup."""
from __future__ import annotations

import re

BOOKS_RAW = (
    "Genesis Exodus Leviticus Numbers Deuteronomy Joshua Judges Ruth|"
    "1 Samuel|2 Samuel|1 Kings|2 Kings|1 Chronicles|2 Chronicles|"
    "Ezra Nehemiah Esther Tobit Judith|Wisdom|Sirach|1 Maccabees|2 Maccabees|"
    "Job|Psalm|Psalms|Proverbs Ecclesiastes|Song of Songs|Song of Solomon|"
    "Isaiah Jeremiah Lamentations Baruch Ezekiel Daniel Hosea Joel Amos Obadiah "
    "Jonah Micah Nahum Habakkuk Zephaniah Haggai Zechariah Malachi "
    "Matthew Mark Luke John Acts Romans|1 Corinthians|2 Corinthians|"
    "Galatians Ephesians Philippians Colossians|1 Thessalonians|2 Thessalonians|"
    "1 Timothy|2 Timothy|Titus Philemon Hebrews James|1 Peter|2 Peter|"
    "1 John|2 John|3 John|Jude Revelation"
).split("|")

BOOKS = [
    b
    for group in BOOKS_RAW
    for b in ([group] if group[0].isdigit() or group.startswith("Song ") else group.split())
]

POINT = r"\d+(?::\d+)?(?:[–-]\d+(?::\d+)?)?"
CONT = (
    POINT
    + r"(?!\d|\s+(?:Samuel|Kings|Chronicles|Corinthians|Thessalonians|Timothy|Peter|John|Maccabees)\b)"
)
REF = re.compile(
    r"(?<![\w])(?P<book>"
    + "|".join(sorted(map(re.escape, BOOKS), key=len, reverse=True))
    + r")\s+(?P<loc>"
    + POINT
    + r"(?:\s*,\s*"
    + CONT
    + r")*(?:;\s*"
    + CONT
    + r"(?:\s*,\s*"
    + CONT
    + r")*)*)"
)

OLD_PREFIX = re.compile(r"(?:LXX(?:/Vulgate)?|Latin/Greek|Vulgate)\s*$")

# Logos targets: prefer canonical DC names so "Wisdom" (common noun) does not
# confuse the Bible datatype parser into orphan chapter milestones.
BOOK_TARGET_ALIAS = {
    "Wisdom": "Wisdom of Solomon",
    "Sirach": "Sirach",
}


def _logos_book_target(book: str) -> str:
    return BOOK_TARGET_ALIAS.get(book, book)


def _expand_one_chapter_group(loc: str) -> list[str]:
    """Turn '19:4, 6' into ['19:4', '19:6']; leave ranges and plain locs alone."""
    loc = loc.replace("–", "-").strip()
    # Single chapter:verse or chapter:verse-verse — keep as one target.
    if "," not in loc:
        return [loc]
    parts = [p.strip() for p in loc.split(",") if p.strip()]
    if not parts:
        return [loc]
    out: list[str] = []
    chapter = None
    for part in parts:
        if ":" in part:
            chapter, verse = part.split(":", 1)
            out.append(f"{chapter}:{verse}")
        elif chapter is not None and re.fullmatch(r"\d+(?:-\d+)?", part):
            # Continuation verse(s) under the prior chapter.
            out.append(f"{chapter}:{part}")
        else:
            # Unexpected — keep original chunk rather than invent.
            out.append(part)
    return out or [loc]


def _expand_comma_verses(book: str, loc: str) -> list[str]:
    """Expand locs; split semicolon chapter groups first.

    '13:1,3; 14:23,28; 16:5' → ['13:1','13:3','14:23','14:28','16:5']
    '1:9; 8:12' → ['1:9','8:12']
    Never emit '28; 16:5'-style targets (comma split across ';' used to).
    """
    loc = loc.replace("–", "-").strip()
    if ";" not in loc:
        return _expand_one_chapter_group(loc)
    out: list[str] = []
    for group in (g.strip() for g in loc.split(";")):
        if not group:
            continue
        out.extend(_expand_one_chapter_group(group))
    return out or [loc]



def _existing_markup_spans(text: str) -> list[tuple[int, int]]:
    """Byte spans already inside [[...]] so we do not re-link Bible targets."""
    return [(m.start(), m.end()) for m in re.finditer(r"\[\[.*?\]\]", text, flags=re.DOTALL)]


def _span_inside(spans: list[tuple[int, int]], start: int, end: int) -> bool:
    return any(start >= a and end <= b for a, b in spans)


class BibleLinker:
    """Stateful linker that accumulates receipts and scripture-index entries."""

    def __init__(self):
        self.link_receipts: list[dict] = []
        self.index: dict[str, list] = {}

    def _index_append(self, target: str, item: tuple):
        bucket = self.index.setdefault(target, [])
        if item not in bucket:
            bucket.append(item)

    def _record(self, display: str, target: str, key=None, label=None, note: bool = False):
        self.link_receipts.append(
            dict(
                display=display,
                target=target,
                datatype="Bible",
                section=key,
                editorial=note,
            )
        )
        if key and label is not None:
            self._index_append(target, (key, label + (" note" if note else "")))

    def _link_markup(self, display: str, book: str, loc: str, key=None, label=None, note: bool = False) -> str:
        """Emit one or more attached Logos Bible links (comma lists are split)."""
        book_t = _logos_book_target(book)
        locs = _expand_comma_verses(book, loc)
        if len(locs) == 1:
            target = f"{book_t} {locs[0]}"
            self._record(display, target, key=key, label=label, note=note)
            return f"[[{display} >> Bible:{target}]]"
        # Split "Matthew 19:4, 6" into two full attached links — trailing ", 6"
        # alone becomes Logos orphan milestones (`: =d~bible…`).
        chunks: list[str] = []
        for i, one in enumerate(locs):
            piece_disp = f"{book} {one}" if i else display.split(",")[0].strip()
            if i and not piece_disp.startswith(book):
                piece_disp = f"{book} {one}"
            target = f"{book_t} {one}"
            self._record(piece_disp, target, key=key, label=label, note=note)
            chunks.append(f"[[{piece_disp} >> Bible:{target}]]")
        return ", ".join(chunks)

    def bible_text(self, text: str, key=None, label=None, note: bool = False) -> str:
        if note:
            # Captions and notes (for example "Possible allusion:" lines) stay
            # plain text. They never become clickable Bible links and are never
            # recorded in the receipt. A possible link with no quotation or echo
            # in the source text is padding, and saying so honestly in the label
            # does not make it a link. Returning the text unchanged means a
            # passage with no real Scripture fails the at-least-one-link check,
            # which is the honest outcome: the Logos build stays on hold.
            return text
        def replace(m: re.Match) -> str:
            prefix = text[max(0, m.start() - 22) : m.start()]
            old = bool(OLD_PREFIX.search(prefix))
            book = "Psalm" if m["book"] == "Psalms" else m["book"]
            loc = m["loc"].replace("–", "-")
            if old:
                previous = [
                    v
                    for v in REF.finditer(text[: m.start()])
                    if not OLD_PREFIX.search(text[max(0, v.start() - 22) : v.start()])
                    and v["book"].rstrip("s") == book.rstrip("s")
                ]
                if not previous:
                    return "{{~ " + m.group() + " }}"
                loc = previous[-1]["loc"].replace("–", "-")
                # Keep LXX label visible; link modern equivalent only.
                book_t = _logos_book_target(book)
                target = f"{book_t} {loc}"
                self._record(m.group(), target, key=key, label=label, note=note)
                return f"[[{m.group()} >> Bible:{target}]]"
            return self._link_markup(m.group(), book, loc, key=key, label=label, note=note)

        _spans = _existing_markup_spans(text)
        replacements = [
            (m.start(), m.end(), replace(m))
            for m in REF.finditer(text)
            if not _span_inside(_spans, m.start(), m.end())
        ]
        old_pattern = re.compile(
            r"(LXX(?:/Vulgate)?|Vulgate)\s+(" + POINT + r"(?:\s*[,;]\s*" + CONT + r")*)"
        )
        for m in old_pattern.finditer(text):
            previous = list(REF.finditer(text[: m.start()]))
            if not previous:
                continue
            book = previous[-1]["book"]
            book = "Psalm" if book == "Psalms" else book
            loc = previous[-1]["loc"].replace("–", "-")
            book_t = _logos_book_target(book)
            target = f"{book_t} {loc}"
            self._record(m[0], target, key=key, label=label, note=note)
            # Keep book name in the linked display so Logos does not see a bare
            # "7:24" fragment that becomes an unattached datatype milestone.
            replacements.append(
                (
                    m.start(),
                    m.end(),
                    m[1] + f" [[{book} {m[2]} >> Bible:{target}]]",
                )
            )
        for start, end, value in sorted(replacements, reverse=True):
            text = text[:start] + value + text[end:]
        return text


def index_book_heading(ref: str) -> str:
    """Book name for scripture-index headings.

    Index keys may use Logos aliases (e.g. ``Wisdom of Solomon 2:24``) while
    ``REF`` only matches the short form ``Wisdom``.
    """
    m = REF.fullmatch(ref)
    if m:
        return m["book"]
    # Alias or compound: strip trailing chapter/verse group.
    parts = ref.rsplit(None, 1)
    if len(parts) == 2 and re.match(r"\d", parts[1]):
        return parts[0]
    return ref


def sort_ref_key(ref: str):
    order = {b: i for i, b in enumerate(BOOKS)}
    m = REF.fullmatch(ref)
    if m:
        return (order.get(m["book"], 999), tuple(map(int, re.findall(r"\d+", m["loc"]))))
    # Logos alias targets (Wisdom of Solomon …) — sort near Wisdom.
    heading = index_book_heading(ref)
    alias_to = {v: k for k, v in BOOK_TARGET_ALIAS.items()}
    book = alias_to.get(heading, heading)
    nums = tuple(map(int, re.findall(r"\d+", ref)))
    return (order.get(book, 999), nums or (0,))
