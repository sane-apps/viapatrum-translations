#!/usr/bin/env python3
"""Historical-print OCR for Via Patrum (16th-19th c. Latin, Greek, and bilingual scans).

Prefers Kraken 7.x with the CATMuS-Print historical model (catmus-print-fondue-large),
which preserves early-modern long-s, æ/œ ligatures, grave accents, and embedded polytonic
Greek far better than Tesseract. Falls back gracefully to Tesseract when Kraken or its
model is unavailable.

Usage:
  python3 scripts/ocr_historical.py input.pdf -o out.txt
  python3 scripts/ocr_historical.py page.png --engine kraken --join-hyphens
  python3 scripts/ocr_historical.py scan.pdf --first 1 --last 5 --engine auto
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_KRAKEN_BINS = [
    Path.home() / "SaneApps/outputs/tool-trials/kraken-venv/bin/kraken",
    Path.home() / ".local/bin/kraken",
]

DEFAULT_MODEL_GLOBS = [
    str(Path.home() / "Library/Application Support/htrmopo/*/catmus-print-fondue-large.mlmodel"),
    str(Path.home() / "Library/Application Support/htrmopo/*/*.mlmodel"),
    str(Path.home() / ".local/share/htrmopo/*/*.mlmodel"),
    str(Path.home() / "SaneApps/outputs/tool-trials/*.mlmodel"),
]


def find_kraken_bin() -> str | None:
    env_bin = os.environ.get("KRAKEN_BIN")
    if env_bin and Path(env_bin).is_file():
        return env_bin
    for cand in DEFAULT_KRAKEN_BINS:
        if cand.is_file():
            return str(cand)
    return shutil.which("kraken")


def find_kraken_model() -> str | None:
    env_model = os.environ.get("KRAKEN_MODEL")
    if env_model and Path(env_model).is_file():
        return env_model
    for pat in DEFAULT_MODEL_GLOBS:
        matches = sorted(glob.glob(pat))
        if matches:
            return matches[0]
    return None


def clean_ocr_text(text: str, *, join_hyphens: bool = True) -> str:
    """Normalize line endings and optionally rejoin early-modern line-break hyphens (¬ / -)."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if join_hyphens:
        # Early-modern prints & CATMuS mark soft line-break hyphens with U+00AC (¬) or '-'.
        text = re.sub(r"(\w)[¬-]\s*\n\s*(\w)", r"\1\2", text)
    return text.strip() + "\n"


def render_pdf_pages(pdf_path: Path, out_dir: Path, *, dpi: int = 250, first: int | None = None, last: int | None = None) -> list[Path]:
    cmd = ["pdftoppm", "-png", "-r", str(dpi)]
    if first is not None:
        cmd += ["-f", str(first)]
    if last is not None:
        cmd += ["-l", str(last)]
    prefix = out_dir / "page"
    cmd += [str(pdf_path), str(prefix)]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return sorted(out_dir.glob("page-*.png"))


def ocr_page_kraken(image_path: Path, kraken_bin: str, model_path: str) -> str:
    with tempfile.TemporaryDirectory(prefix="vp-kraken-") as td:
        out_txt = Path(td) / "out.txt"
        cmd = [
            kraken_bin, "-i", str(image_path), str(out_txt),
            "binarize", "segment", "-bl", "ocr", "-m", model_path,
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return out_txt.read_text(encoding="utf-8", errors="replace")


def ocr_page_tesseract(image_path: Path, lang: str = "lat+grc") -> str:
    with tempfile.TemporaryDirectory(prefix="vp-tess-") as td:
        base = Path(td) / "out"
        cmd = ["tesseract", str(image_path), str(base), "-l", lang, "--psm", "6"]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return Path(str(base) + ".txt").read_text(encoding="utf-8", errors="replace")


def ocr_file(
    input_path: Path,
    *,
    engine: str = "auto",
    lang: str = "lat+grc",
    dpi: int = 250,
    first: int | None = None,
    last: int | None = None,
    join_hyphens: bool = True,
) -> tuple[str, str]:
    """Run OCR on a PDF or image file. Returns (text, engine_used)."""
    kbin = find_kraken_bin()
    kmodel = find_kraken_model()
    use_kraken = (engine == "kraken") or (engine == "auto" and bool(kbin and kmodel))
    if engine == "kraken" and not (kbin and kmodel):
        raise RuntimeError(f"Kraken requested but unavailable (bin={kbin!r}, model={kmodel!r})")

    with tempfile.TemporaryDirectory(prefix="vp-ocr-") as td:
        if input_path.suffix.lower() == ".pdf":
            pages = render_pdf_pages(input_path, Path(td), dpi=dpi, first=first, last=last)
        else:
            pages = [input_path]

        chunks: list[str] = []
        used = "kraken" if use_kraken else "tesseract"
        for i, page in enumerate(pages, 1):
            if use_kraken:
                try:
                    raw = ocr_page_kraken(page, kbin, kmodel)  # type: ignore[arg-type]
                except Exception:
                    if engine == "kraken":
                        raise
                    used = "tesseract-fallback"
                    raw = ocr_page_tesseract(page, lang=lang)
            else:
                raw = ocr_page_tesseract(page, lang=lang)
            if len(pages) > 1:
                chunks.append(f"<!-- page {i} -->\n{raw.strip()}")
            else:
                chunks.append(raw.strip())

    return clean_ocr_text("\n\n".join(chunks), join_hyphens=join_hyphens), used


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Historical-print OCR for Via Patrum (Kraken-first, Tesseract fallback).")
    ap.add_argument("input", type=Path, help="Input PDF or PNG/JPG/TIF scan")
    ap.add_argument("-o", "--output", type=Path, help="Output text path (defaults to stdout)")
    ap.add_argument("--engine", choices=("auto", "kraken", "tesseract"), default="auto")
    ap.add_argument("--lang", default="lat+grc", help="Tesseract language fallback (default: lat+grc)")
    ap.add_argument("--dpi", type=int, default=250, help="PDF render DPI (default: 250)")
    ap.add_argument("--first", type=int, help="First PDF page (1-based)")
    ap.add_argument("--last", type=int, help="Last PDF page (1-based)")
    ap.add_argument("--no-join-hyphens", action="store_true", help="Keep ¬ and - line breaks untouched")
    args = ap.parse_args(argv)

    text, used = ocr_file(
        args.input,
        engine=args.engine,
        lang=args.lang,
        dpi=args.dpi,
        first=args.first,
        last=args.last,
        join_hyphens=not args.no_join_hyphens,
    )
    if args.output:
        args.output.write_text(text, encoding="utf-8")
        print(f"ocr_historical: wrote {len(text)} chars to {args.output} (engine={used})", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
