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
 3. Decided 2026-10-07: every audiobook is re-voiced into the current voice (Aura-2 orion; Scripture quotations in arcas). The drain does it under a daily dollar cap (REVOICE_USD_PER_DAY, default $150). The owner approved the spend.
 Cost: Aura-2 $0.03 / 1k characters (CF model page, 2026-10-05) -> the missing ~1M words about $150-200, on the CF grant.
B. Downloadable audiobook per work
 master_audiobook.py already makes ACX-spec chapters + .m4b with cover (Wesley, Origen On Prayer). Roll out: one .m4b per work to R2, a Download button on the work page, a library page. Needs per-work 3000 px covers (template, not hand art) and the AI-narration disclosure in credits.
C. YouTube read-along audiobooks (no music). Facts checked 2026-10-07 on official Google/YouTube pages (support.google.com/youtube = yt/, developers.google.com/youtube = dev/).
 Render: 16:9 1080p only. A square or vertical upload of 3 min or less becomes a Short, and a Short over 1 min with an active Content ID claim is blocked worldwide (yt/answer/15424877, 12779649). Still background + the current paragraph with the spoken sentence highlighted, from the sentence timings in every manifest (ffmpeg + libass, -tune stillimage). CPU-only batch on the Mini or the Air headless-batch exception.
 Render cost: before any batch, run one pilot encode (one long work, 1080p) while the Mini is idle. Record wall time, peak RSS and output size in websites/fathers.saneapps.com/docs/GPU_RENDER_COSTS.md. The Mini has 8 GiB RAM. Not run yet.
 Channel: a new Via Patrum Brand Account channel; the owner creates it in YouTube Studio. Never move an existing channel onto a Brand Account that has its own channel: the move deletes that channel's videos, playlists and comments for good (yt/answer/3056283).
 Limits: one upload is at most 12 h or 256 GB, whichever is less (yt/answer/71673; dev/v3/docs/videos/insert). Over 15 min needs a phone-verified channel; so do custom thumbnails (yt/answer/9890437).
 Chapters: description timestamps, first at 00:00, at least 3 in ascending order, each chapter at least 10 s, no active strikes (yt/answer/9884579). Chapters are an advanced feature: they need ID or video verification by the primary owner (review usually 24 h) or enough channel history (yt/answer/9890437, 9891124). Until then, plain timestamp text.
 API quota: 10,000 units/day per project by default. videos.insert has its own bucket of 100 calls/day (dev/v3/determine_quota_cost, videos/insert). The same page's summary still says 1,600 units; that figure is stale since the 2025-12-04 change (dev/v3/revision_history). captions.insert 400, thumbnails.set 50, playlistItems.insert 50, videos.update 50. A fully dressed upload (video + caption + thumbnail + playlist = 500 units) allows about 20 per day. Studio uploads are not API calls, so they use no API quota.
 API audit: videos.insert from an unaudited project created after 2020-07-28 is locked PRIVATE until the project passes the API compliance audit. Locked videos cannot be appealed, only re-uploaded (dev/v3/docs/videos/insert; yt/answer/7300965). Google gives no time frame; it says only "as soon as possible" (dev/v3/guides/quota_and_compliance_audits). The form asks for a privacy policy URL, the Cloud project number, a demo account, and OAuth consent, scope and revocation screenshots (yt/contact/yt_api_form). The privacy policy must say the app uses YouTube API Services and link the Google Privacy Policy (dev/terms/developer-policies III.A.2). No screencast is required; screenshots are.
 Podcast RSS ingestion is not an easy fallback: RSS Upload is an advanced feature (yt/answer/9890437), it is open only in some countries (yt/answer/13525207), and it makes static show-art videos with no highlight.
 Changes after upload: a video file cannot be replaced; a new upload gets a new URL (yt/answer/55770). videos.update changes metadata only (dev/v3/docs/videos/update). Keep outputs/youtube/manifest.json with video id, english_sha256 and audio hash per work. When a work's text or audio changes after upload, the watch flags it; delete the video and upload it again. Accuracy beats view counts on a new channel.
 Monetization: no YouTube Partner Program application with this catalogue. YPP refuses "readings of other materials you did not originally create" and "image slideshows ... or scrolling text", and reviews the channel as a whole (yt/answer/1311392). Every video names a specific work: real title, author, work URL, art licence, and the computer-voice disclosure line (CONTENT_SOPS).
 Art: background and cover art are generated in-house or public domain. Each work has a licence record, and the uploader checks it.
 Decisions (2026-10-07, at the owner's request): do not start the API audit now; no uploader exists and nothing is ready to publish. First uploads, if any, go through YouTube Studio by hand, by the owner. Agents publish nothing.
 Owner actions open: create the Brand channel; identity-verify it when he creates it, so chapters work.

