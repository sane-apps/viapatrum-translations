# Democratize Christian History — Master Vision (owner, 2026-10-01)

Project name: VIA PATRUM — "Way of the Fathers" (owner, 2026-10-01; cf. Jeremiah 6:16, "ask for the ancient paths").
Domain: viapatrum.com (.org fallback) — decision: use it; registration + redirect plan pending.
Goal: the highest quality FREE resource in the world for Christian History.

1. Translate all previously untranslated works.
2. Re-translate translated works from source texts so nothing is under copyright.
3. Build a timeline of all Christian beliefs: who introduced what, when; visualize consensus over history.
4. Audiobooks of every work on the website + downloadable.
5. YouTube audiobooks of every work (read-along highlight + tasteful background; NO music — owner 2026-10-01).
6. Fully sourced, Logos-ready books of every work.
7. Native app (iOS/macOS, iPad-first): offline library, read-along audio, belief timeline, semantic search; Cloudflare backend (R2 + Workers + Vectorize).

Status ledger (update as phases land):
- [1] IN PROGRESS — 438-book corpus, pipeline active (claims locked, densify running).
- [2] IN PROGRESS — pipeline translates from sources (CC BY 4.0 new translations); needs per-book clean audit.
- [3] NOT STARTED.
- [4] IN PROGRESS — site audio bulk rendering on Cloudflare TTS (Odysseus/Orion/Apollo per author); downloadable M4B pipeline proven on Wesley, needs rollout.
- [5] QUEUED behind [4].
- [6] IN PROGRESS — Wesley v3 shipped w/ cover+intro; backlog of grandfathered books needs covers/intros/descriptions per CONTENT_SOPS.

Website bar: the best in the world at what it is — modern, beautiful, easy to use.
- Dark/light mode; best-in-class accessibility (blind users first-class).
- Best-in-class SEO: every section its own card, rich search presence.
- Project name + X profile card (owner switching profile to this project).
Style audit (2026-10-01): menus, titles, Greek/Latin seepage, formatting consistency.
Cloudflare AI features: semantic search/RAG ("ask the Fathers"), AI chapter summaries,
auto cross-refs feeding the belief timeline, verse/topic linking.
- [7] QUEUED behind content phases (needs stable corpus + audio + timeline API).

## Phases 4-5 route (researched 2026-10-05, Claude; owner: "all certified works need the full audio, an audiobook, and YouTube")

Today: 326 live works, 224 with read-along audio; 101 without (77 over the drain's 5,000-word cap, 24 small works the drain cannot find). 109 works certified by work_pipeline (~126k words, ~14 h); site total roughly 200-300 h of narration.

A. Every live work narrated (site player)
 1. build_audio.py MAX_WORDS=5000 is stale: its reason ("Pages refuses > 25 MiB") ended when audio moved to R2 on 2026-10-03, and the viapatrum-narrator Worker already encodes in ~20-min segments with an R2 multipart upload. Raise it (no hard cap; split only past YouTube's 12 h).
 2. _work_words(site slug) returns (0, scaffold) for split/renamed works; resolve through build_site.work_book.
 3. Works recorded in the retired voice whose text changed show no player (AUDIO_RESTEM_OLD_VOICE, ~$96 per 2026-10-03 handoff): owner decision.
 Cost: Aura-2 $0.03 / 1k characters (CF model page, 2026-10-05) -> the missing ~1M words about $150-200, on the CF grant.
B. Downloadable audiobook per work
 master_audiobook.py already makes ACX-spec chapters + .m4b with cover (Wesley, Origen On Prayer). Roll out: one .m4b per work to R2, a Download button on the work page, a library page. Needs per-work 3000 px covers (template, not hand art) and the AI-narration disclosure in credits.
C. YouTube read-along audiobooks (no music)
 Render: 1080p still background + the current paragraph with the spoken sentence highlighted, from the sentence timings already in every manifest (ffmpeg + libass, -tune stillimage); chapters from section times in the description. CPU-only batch -> Mini or the Air headless-batch exception (work-modes build, 2026-10-05 22:00).
 Upload facts (developers.google.com/youtube/v3, 2026-10-05): videos.insert has its own bucket, 100 uploads/day; videos from an unaudited API project are locked PRIVATE until the "YouTube API Services" compliance audit passes (weeks); max 12 h / 256 GB; > 15 min needs a phone-verified channel.
 Route: owner creates/verifies the Via Patrum channel; start the API audit now (Cloud project, OAuth consent, viapatrum.org/privacy, demo screencast); until it passes, upload through YouTube Studio in Mini Brave in batches, or wait. Fallback: podcast RSS ingestion (no audit, but static show art, no highlight).
 Policy: disclose AI narration in every description (CONTENT_SOPS); YouTube's altered-content label targets realistic impersonation; no monetization planned, so the 2025 "inauthentic content" rule (demonetization) does not bite.

