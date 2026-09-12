from pathlib import Path
from datetime import date

CLAIMS = Path("docs/CLAIMS.md")

def add_open(cid: str, slice_txt: str, agent: str = "StephanMini", book: str = "ante-nicene-topics", notes: str = "Topics lane") -> None:
    text = CLAIMS.read_text()
    if f"| {cid} |" in text:
        return
    row = (
        f"| {cid} | claimed | {book} | {slice_txt} | {agent} | "
        f"{date.today().isoformat()} | wip/{cid} | {notes} |\n"
    )
    lines = text.splitlines(keepends=True)
    out = []
    in_open = False
    inserted = False
    for line in lines:
        out.append(line)
        if line.startswith("## Open / active claims"):
            in_open = True
        elif in_open and line.startswith("## "):
            in_open = False
        elif in_open and line.startswith("|---") and not inserted:
            out.append(row)
            inserted = True
    CLAIMS.write_text("".join(out))
    assert "jer-h20b" in CLAIMS.read_text()

def close_done(cid: str, done_slice: str, notes: str) -> None:
    lines = CLAIMS.read_text().splitlines(keepends=True)
    out = []
    in_open = False
    for line in lines:
        if line.startswith("## Open / active claims"):
            in_open = True
            out.append(line)
            continue
        if in_open and line.startswith("## "):
            in_open = False
        if in_open and line.startswith(f"| {cid} |"):
            continue
        out.append(line)
    text2 = "".join(out)
    done = f"| {cid} | done | {done_slice} | {date.today().isoformat()} | {notes} |\n"
    lines = text2.splitlines(keepends=True)
    out = []
    in_done = False
    inserted = False
    for line in lines:
        out.append(line)
        if line.startswith("## Done / closed"):
            in_done = True
        elif in_done and line.startswith("## "):
            in_done = False
        elif in_done and line.startswith("|---") and not inserted:
            out.append(done)
            inserted = True
    CLAIMS.write_text("".join(out))
    assert "jer-h20b" in CLAIMS.read_text()
