# P. Chester Beatty XII — image access state (2026-10-25)

Manuscript: P. Chester Beatty XII, Chester Beatty Library, Dublin
(shelf mark CBL BP XII). 4th century. 8 leaves + 1 fragment plate;
contents: Enoch, then Melito, Peri Pascha (incomplete). CSNTM manuscript
page: https://manuscripts.csntm.org/Manuscript/Group/BP_XII

## What was obtained

- `thumbnails/` — all 36 images the CSNTM page serves anonymously:
  18 surfaces (00i.1a/b, 008a/b, 009a/b, 011a/b, 013a/b, 015a/b, 018a/b,
  019a/b, 021a/b), each in the `_w` (white background) and `_k` (black
  background) variants, at the served size of 100 px width, JPEG.
  URL pattern per file:
  http://images.csntm.org/IIIFServer.ashx/BP_XII/BP_XII_<surface>_<variant>.jpg/full/100,/0/native.jpg
  (HTTPS to images.csntm.org fails through our proxy; HTTP works.)
- `CBL_BP_XII.pdf` — the 2-page PDF linked from the CSNTM manuscript page
  (http://images.csntm.org/Manuscripts/BP_XII/CBL%20BP%20XII.pdf), 90,620
  bytes. It is a cover/description sheet, not a scan set.

## The blocker (precise)

- CSNTM's deep-zoom viewer for this manuscript (OpenSeadragon) sits behind
  an account login: the viewer page links to
  /Account/Login?reason=OpenSeaDragon. Anonymous requests to the IIIF
  endpoint for any size above the 100 px thumbnail return HTTP 500
  (verified 2026-10-25 for widths 200-2000, full/full, and region tiles;
  pct: sizes return HTTP 400, "potentially dangerous Request.Path" —
  the colon is rejected by their ASP.NET pipeline).
- No account was created and no access control was bypassed, per project
  rules. Collation against this witness therefore waits on either
  (a) the owner creating a free CSNTM account and authorising its use, or
  (b) the Michigan-held leaves of the same codex: the codex is split
  between Dublin and the University of Michigan (Bonner's edition used
  both), and Michigan's papyrus images are public via APIS/Papyri.info —
  the exact inventory numbers for the Melito leaves are a Phase 2 lookup.
- Impact on Phase 1: none for the transcription itself. P. Bodmer XIII
  preserves the homily complete and its images are openly served at full
  resolution under CC BY-NC 4.0; Chester Beatty XII is the collation
  witness, and its opening leaves do not cover §§1-10 in any case (the
  Dublin leaves are the codex's later portion; which surfaces carry
  Melito vs Enoch could not be determined from 100 px thumbnails).
