#!/usr/bin/env python3
"""Burn free CF neurons + NVIDIA NIM in parallel on Fathers claims.

Lanes (separate budgets):
  cf — Workers AI draft/check until ~10k neurons/day (UTC) reserve
  nv — NIM draft/check (RPM/latency bound; no CF neuron burn)

Optional (artifact-only, never promotes):
  gemini — Flash-Lite prep / checker-C under outputs/gemini-prep/
           Enable: --enable-gemini | FATHERS_GEMINI_PREP=1 | lanes.gemini.enabled

  source ~/.config/nv/env && export CF_TOKEN="$CLOUDFLARE_API_TOKEN"
  python3 scripts/overnight_quota.py --lanes both --agent overnight
  python3 scripts/overnight_quota.py --lanes both --enable-gemini

Recovery: resumes this agent's claimed-but-not-done rows before taking free ones.
Does NOT Logos-compile or deploy the site.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "overnight-quota"
CLAIMS = ROOT / "docs" / "CLAIMS.md"
DEFAULT_ACCOUNT = "2c267ab06352ba2522114c3081a8c5fa"
FREE_NEURONS = 10_000
RESERVE = 800
FATHERS_CF_BUDGET = 10_000  # our delta/night; account is shared/granted
SECTION_COST_EST = 160  # Qwen + Gemma + 70B-ish

NV_DRAFT_DEFAULT = "nvidia/nemotron-3-super-120b-a12b"
NV_CHECKER_A_DEFAULT = "mistralai/mistral-nemotron"
NV_CHECKER_B_DEFAULT = "mistralai/mistral-nemotron"

CF_DRAFT_DEFAULT = "@cf/qwen/qwen3-30b-a3b-fp8"
CF_CHECKER_A_DEFAULT = "@cf/google/gemma-4-26b-a4b-it"
CF_CHECKER_B_DEFAULT = "@cf/meta/llama-3.3-70b-instruct-fp8-fast"


def gql(token: str, query: str) -> dict:
    body = json.dumps({"query": query}).encode()
    req = urllib.request.Request(
        "https://api.cloudflare.com/client/v4/graphql",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def neurons_today(token: str, account: str) -> int:
    end = datetime.now(timezone.utc)
    start = end.replace(hour=0, minute=0, second=0, microsecond=0)
    q = f"""
query {{
  viewer {{
    accounts(filter: {{accountTag: "{account}"}}) {{
      aiInferenceAdaptiveGroups(
        limit: 1
        filter: {{
          datetimeHour_geq: "{start.strftime('%Y-%m-%dT%H:%M:%SZ')}"
          datetimeHour_lt: "{end.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        }}
      ) {{
        sum {{ totalNeurons }}
        count
      }}
    }}
  }}
}}
"""
    data = gql(token, q)
    if data.get("errors"):
        raise SystemExit(f"GraphQL neurons error: {data['errors']}")
    groups = (
        ((data.get("data") or {}).get("viewer") or {})
        .get("accounts") or [{}]
    )[0].get("aiInferenceAdaptiveGroups") or []
    if not groups:
        return 0
    return int(((groups[0].get("sum") or {}).get("totalNeurons")) or 0)


def parse_open_rows() -> list[dict[str, str]]:
    text = CLAIMS.read_text(encoding="utf-8")
    rows: list[dict[str, str]] = []
    in_open = False
    headers: list[str] = []
    for line in text.splitlines():
        if line.startswith("## Open / active claims"):
            in_open = True
            continue
        if in_open and line.startswith("## "):
            break
        if not in_open or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells or cells[0].startswith("---"):
            continue
        if cells[0] == "Claim ID":
            headers = cells
            continue
        if not headers:
            continue
        rows.append(dict(zip(headers, cells)))
    return rows


def _hold_blocks(row: dict) -> bool:
    """A held slice gets one repair. A second fail while held stays parked."""
    if not row or not row.get("held"):
        return False
    return bool(row.get("repair_spent"))


def free_auto_claims() -> list[str]:
    hold = load_hold()
    fresh = []
    repair = []
    for r in parse_open_rows():
        cid = str(r.get("Claim ID", ""))
        if r.get("Status") != "free":
            continue
        notes = (r.get("Notes") or "").casefold()
        if "betacode" in notes or "do not publish" in notes:
            continue
        if not _auto_claim(cid):
            continue
        row = hold.get(cid) or {}
        if _hold_blocks(row):
            continue
        if row.get("held"):
            repair.append(cid)
        else:
            fresh.append(cid)
    return fresh + repair


def claimed_for_agent(agent: str) -> list[str]:
    """Stuck claimed rows for this overnight agent (resume after interrupt)."""
    return [
        r["Claim ID"]
        for r in parse_open_rows()
        if r.get("Status") in {"claimed", "checking", "review"}
        and r.get("Agent", "").strip() == agent
        and _auto_claim(str(r.get("Claim ID", "")))
        and not _hold_blocks(load_hold().get(str(r.get("Claim ID", "")), {}))
    ]


def _claim_wall_s() -> int:
    try:
        cfg = json.loads((ROOT / "docs" / "LLM_LANE_CONFIG.json").read_text(encoding="utf-8"))
        return int(cfg.get("claim_wall_s") or 5400)
    except Exception:  # noqa: BLE001
        return 5400


HOLD_PATH = OUT / "HOLD.jsonl"
AUTO_PREFIXES = ("jer-h", "cyr-isa-")
_QUEUE_SKIP = {"origen-jeremiah-samuel", "cyril-alexandria-isaiah"}


def _auto_claim(cid: str) -> bool:
    """Isaiah and Jeremiah keep their ids. Other books use slug--section."""
    return bool(cid) and (cid.startswith(AUTO_PREFIXES) or "--" in cid)


def _auto_wall_s() -> int:
    try:
        cfg = json.loads((ROOT / "docs" / "LLM_LANE_CONFIG.json").read_text(encoding="utf-8"))
        return int(cfg.get("auto_wall_s") or 10800)
    except Exception:  # noqa: BLE001
        return 10800


def load_hold() -> dict:
    if not HOLD_PATH.is_file():
        return {}
    data = {}
    for line in HOLD_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if row.get("claim"):
            data[row["claim"]] = row
    return data


_HOLD_LOCK = threading.Lock()


def effective_lane_shares(active_lanes, share_of) -> dict:
    """Normalize budget shares over lanes that actually have queued work.

    Raw shares from work-lanes.json sum to 1.0 across ALL lanes; when some
    lanes have nothing queued, their idle share would otherwise be
    unspendable while a busy lane caps out. Normalizing reallocates within
    the same fixed total, so the overall budget cap binds exactly as before.
    """
    shares = {}
    for lane_name in (active_lanes or []):
        try:
            shares[lane_name] = max(0.0, float(share_of(lane_name) or 0.0))
        except (TypeError, ValueError):
            shares[lane_name] = 0.0
    total = sum(shares.values())
    if total <= 0:
        n = len(shares)
        return {lane_name: (1.0 / n if n else 0.0) for lane_name in shares}
    return {lane_name: value / total for lane_name, value in shares.items()}


def _concrete_defect_key(claim_id: str):
    """Use the newest readable receipt. Empty means do not park."""
    from pipeline_autonomy import stable_defect_key
    root = ROOT / "outputs" / "ai-promote"
    if not root.is_dir():
        return ""
    suffix = "-" + claim_id
    dirs = sorted(
        p for p in root.iterdir() if p.is_dir() and p.name.endswith(suffix)
    )
    data = None
    for folder in reversed(dirs):
        summary = folder / "summary.json"
        try:
            loaded = json.loads(summary.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(loaded, dict):
            data = loaded
            break
    if not isinstance(data, dict):
        return ""
    texts = []
    for entry in data.get("results") or []:
        if not isinstance(entry, dict):
            continue
        for gap in entry.get("lemma_gap") or []:
            texts.append(str(gap))
        defect = entry.get("clause_defect") or {}
        if isinstance(defect, dict):
            for item in defect.get("actionable") or []:
                texts.append(str(item))
        for key in ("checker_a", "checker_b", "arbiter"):
            check = entry.get(key) or {}
            if not isinstance(check, dict) or check.get("ok") is not False:
                continue
            parsed = check.get("parsed") or {}
            if not isinstance(parsed, dict):
                continue
            notes = parsed.get("notes")
            if isinstance(notes, str):
                texts.append(notes)
            elif isinstance(notes, list):
                texts.extend(str(item) for item in notes)
    blob = "\n".join(texts)
    if "Rewrite this sentence" in blob or "Restore the sense of" in blob:
        return ""
    return stable_defect_key(texts)


def _write_hold(hold: dict) -> None:
    HOLD_PATH.write_text(
        "\n".join(json.dumps(hold[c]) for c in sorted(hold)) + "\n",
        encoding="utf-8",
    )


def record_claim_fail(claim: str, reason: str, defect_key=None) -> dict:
    with _HOLD_LOCK:
        hold = load_hold()
        row = hold.get(claim) or {"claim": claim, "fails": 0}
        already_held = bool(row.get("held"))
        row["reason"] = reason
        row["updated"] = datetime.now(timezone.utc).isoformat()
        if defect_key == "":
            row["fails"] = 1
            row["held"] = True
            row["repair_spent"] = False
            row["same_fails"] = 0
            row["defect_key"] = ""
        elif isinstance(defect_key, str) and defect_key:
            previous = str(row.get("defect_key") or "")
            if previous and previous != defect_key:
                row["fails"] = 1
                row["held"] = True
                row["repair_spent"] = False
                row["same_fails"] = 1
                row["defect_key"] = defect_key
            else:
                row["fails"] = int(row.get("fails") or 0) + 1
                row["defect_key"] = defect_key
                if previous == defect_key:
                    row["same_fails"] = int(row.get("same_fails") or 0) + 1
                else:
                    row["same_fails"] = 1
                if row["fails"] >= 2:
                    row["held"] = True
                if int(row.get("same_fails") or 0) >= 3:
                    row["held"] = True
                    row["repair_spent"] = True
        else:
            row["fails"] = int(row.get("fails") or 0) + 1
            if row["fails"] >= 2:
                row["held"] = True
            if already_held:
                row["repair_spent"] = True
        hold[claim] = row
        _write_hold(hold)
    return row


def clear_claim_hold(claim: str) -> None:
    """A slice that just promoted is not parked."""
    with _HOLD_LOCK:
        hold = load_hold()
        if claim not in hold:
            return
        hold.pop(claim, None)
        if hold:
            HOLD_PATH.write_text(
                "\n".join(json.dumps(hold[c]) for c in sorted(hold)) + "\n",
                encoding="utf-8",
            )
        else:
            HOLD_PATH.write_text("", encoding="utf-8")


def run_wall(cmd: list[str], env: dict, timeout_s: int) -> int:
    from fathers_run_lock import run_bounded  # noqa: WPS433

    print("+", " ".join(cmd), flush=True)
    label = Path(cmd[1]).name if len(cmd) > 1 else "child"
    return run_bounded(cmd, cwd=ROOT, env=env, timeout_s=timeout_s, label=label)


def run(cmd: list[str], env: dict) -> int:
    from fathers_run_lock import run_bounded  # noqa: WPS433

    print("+", " ".join(cmd), flush=True)
    label = Path(cmd[1]).name if len(cmd) > 1 else "child"
    return run_bounded(cmd, cwd=ROOT, env=env, timeout_s=_claim_wall_s(), label=label)


def english_present(claim_id: str, env: dict) -> bool:
    """True when every section in the claim already has Pass B english on disk."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from ai_promote import parse_claim_row, sections_from_slice, paths_for_section  # noqa: WPS433

    row = parse_claim_row(claim_id)
    sections = sections_from_slice(row.get("Slice (sections)") or "")
    eng_path = ROOT / "books/origen-jeremiah-samuel/translations/jeremiah_english.json"
    if not eng_path.is_file():
        return False
    rows = {str(r.get("section")): r for r in json.loads(eng_path.read_text(encoding="utf-8"))}
    for section in sections:
        row_e = rows.get(section)
        if not row_e or not (row_e.get("english") or []):
            return False
        _eng, just = paths_for_section(section)
        if not just.is_file():
            return False
    return True


def process_claim(
    claim_id: str,
    *,
    agent: str,
    env: dict,
    lane: str,
    draft_model: str,
    already_claimed: bool,
    mode: str = "prep",
    rounds: int = 2,
) -> dict:
    entry: dict = {"claim": claim_id, "ok": False, "lane_agent": agent, "lane": lane, "mode": mode}
    if not already_claimed:
        rc = run(
            [sys.executable, "scripts/claims.py", "take", claim_id, "--agent", agent],
            env,
        )
        if rc != 0:
            entry["error"] = "take_failed"
            return entry
    else:
        print(f"Resume claimed {claim_id} as {agent}", flush=True)

    if mode == "auto":
        rc = run_wall(
            [sys.executable, "scripts/auto_section.py", "--claim", claim_id,
             "--agent", agent, "--rounds", str(rounds),
             "--model", draft_model],
            env, _auto_wall_s(),
        )
        entry["promote_rc"] = rc
        if rc == 0:
            entry["ok"] = True
            clear_claim_hold(claim_id)
        elif rc == 2:
            entry["error"] = "api_fail"
        elif rc == 4:
            entry["error"] = "promote_wall_timeout"
        elif rc == 5:
            entry["error"] = "source_not_greek"
        else:
            entry["error"] = "hold"
        if not entry.get("ok"):
            # Release the row: one-slice rule would otherwise block the night.
            # HOLD.jsonl keeps the fail count; resume only matters on kill -9.
            run([sys.executable, "scripts/claims.py", "mark", claim_id,
                 "--status", "free", "--agent", agent], env)
        return entry

    if mode == "prep":
        if already_claimed and english_present(claim_id, env):
            print(f"Leave existing English on {claim_id} for human Pass B", flush=True)
            entry["ok"] = True
            entry["skipped"] = "has_english"
            return entry
        rc = run(
            [
                sys.executable,
                "scripts/draft_claim.py",
                "--claim",
                claim_id,
                "--agent",
                agent,
                "--model",
                draft_model,
                "--max-tokens",
                "4096",
                "--prep",
            ],
            env,
        )
        if rc != 0:
            entry["error"] = "prep_failed"
            return entry
        rc = run(
            [
                sys.executable,
                "scripts/claims.py",
                "mark",
                claim_id,
                "--status",
                "prepped",
                "--agent",
                agent,
            ],
            env,
        )
        entry["ok"] = rc == 0
        if rc != 0:
            entry["error"] = "mark_prepped_failed"
        return entry

    skip_draft = already_claimed and english_present(claim_id, env)
    if skip_draft:
        print(f"Skip draft (english already present) for {claim_id}", flush=True)
        entry["skipped_draft"] = True
    else:
        rc = run(
            [
                sys.executable,
                "scripts/draft_claim.py",
                "--claim",
                claim_id,
                "--agent",
                agent,
                "--model",
                draft_model,
                "--max-tokens",
                "4096",
            ],
            env,
        )
        if rc != 0:
            entry["error"] = "draft_failed"
            return entry

    rc = run(
        [
            sys.executable,
            "scripts/ai_promote.py",
            "--claim",
            claim_id,
            "--agent",
            agent,
            "--lane",
            lane,
            "--draft-model",
            draft_model,
        ],
        env,
    )
    entry["ok"] = rc == 0
    entry["promote_rc"] = rc
    if rc == 3:
        entry["ok"] = False
        entry["error"] = "promote_lock_busy"
    elif rc == 4:
        entry["ok"] = False
        entry["error"] = "promote_wall_timeout"
    elif rc == 1:
        entry["error"] = "content_fail"
    elif rc == 2:
        entry["error"] = "api_fail"
    elif rc != 0:
        entry["error"] = "promote_failed"
    return entry


def run_lane(lane: str, args: argparse.Namespace, env: dict) -> dict:
    from llm_lane_config import as_list, load_lane_config  # noqa: WPS433

    agent = f"{args.agent}-{lane}"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log: dict = {
        "lane": lane,
        "agent": agent,
        "started": stamp,
        "claims": [],
        "stop_reason": None,
    }
    cfg = load_lane_config(args.config or None)
    lane_cfg = (cfg.get("lanes") or {}).get(lane) or {}
    drafts = as_list(lane_cfg.get("draft"))
    draft = (
        args.cf_draft
        if lane == "cf" and args.cf_draft
        else args.nv_draft
        if lane == "nv" and args.nv_draft
        else (drafts[0] if drafts else (CF_DRAFT_DEFAULT if lane == "cf" else NV_DRAFT_DEFAULT))
    )

    used_start = 0
    fathers_budget = FATHERS_CF_BUDGET
    account_cap = 0
    token = env.get("CF_TOKEN") or env.get("CLOUDFLARE_API_TOKEN") or ""
    account = env.get("CLOUDFLARE_ACCOUNT_ID") or DEFAULT_ACCOUNT
    if lane == "cf":
        if not token:
            log["stop_reason"] = "missing_cf_token"
            return log
    else:
        if not (env.get("NV_API_KEY") or env.get("NVIDIA_API_KEY")):
            log["stop_reason"] = "missing_nv_key"
            return log
        print(f"[nv] NIM lane draft={draft} (checkers from LLM_LANE_CONFIG)", flush=True)
    # Every lane can spend CF neurons via checker/draft fallbacks: meter all.
    cf_metered = bool(token)
    if cf_metered:
        fathers_budget = int(cfg.get("fathers_cf_budget") or FATHERS_CF_BUDGET)
        account_cap = int(cfg.get("cf_account_cap") or 0)
        used_start = neurons_today(token, account)
        log["neurons_start"] = used_start
        log["fathers_cf_budget"] = fathers_budget
        print(f"[{lane}] account neurons today={used_start} fathers_budget={fathers_budget} cap={account_cap or 'none'}", flush=True)
        if account_cap and used_start >= account_cap - args.reserve:
            log["stop_reason"] = "already_at_reserve"
            return log

    queue: list[tuple[str, bool]] = [(c, True) for c in claimed_for_agent(agent)]
    for c in free_auto_claims():
        queue.append((c, False))

    # Work-lane governance (docs/WORK_LANES.md): paused lanes yield no new
    # rows (in-flight resume rows still complete); free rows run oldest
    # book first within active lanes.
    try:
        from work_lanes import book_lane, book_year, is_active, lane_share
    except ImportError:
        book_lane = book_year = is_active = lane_share = None
    lane_skipped: list[dict] = []
    _eff_shares: dict = {}
    if book_lane is not None:
        rows0 = {r["Claim ID"]: r for r in parse_open_rows()}

        def lane_of(cid: str) -> tuple[str, str]:
            slug = (rows0.get(cid) or {}).get("Book slug", "")
            return book_lane(slug), slug

        kept: list[tuple[str, bool]] = []
        for c, r in queue:
            wlane, wslug = lane_of(c)
            if not r and not is_active(wlane):
                lane_skipped.append({"claim": c, "lane": wlane, "book": wslug})
                continue
            kept.append((c, r))
        resume_rows = [(c, r) for c, r in kept if r]
        free_rows = [(c, r) for c, r in kept if not r]
        free_rows.sort(key=lambda cr: book_year((rows0.get(cr[0]) or {}).get("Book slug", "")))
        queue = resume_rows + free_rows
        _q_lanes = {lane_of(c)[0] for c, _r in queue if not _r}
        _eff_shares = effective_lane_shares(_q_lanes, lane_share)
        print(f"[{lane}] effective lane shares: " + ", ".join(f"{k}={v:.2f}" for k, v in sorted(_eff_shares.items())), flush=True)
        if lane_skipped:
            print(f"[{lane}] work-lane pause skips: {len(lane_skipped)}", flush=True)
    log["lane_skipped"] = lane_skipped

    if not queue:
        log["stop_reason"] = "queue_empty"
        log["queue"] = []
        log["finished"] = datetime.now(timezone.utc).isoformat()
        print(f"[{lane}] no auto claims left", flush=True)
        return log

    if args.dry_run:
        log["stop_reason"] = "dry_run"
        log["queue"] = [{"claim": c, "resume": r} for c, r in queue[:20]]
        return log

    done = 0
    content_skips = 0
    consec_api_fail = 0
    lane_spent: dict[str, int] = {}
    lane_capped = 0
    prev_used = used_start
    last_lane: str | None = None
    for claim_id, resume in queue:
        if done >= args.max_claims:
            log["stop_reason"] = "max_claims"
            break
        if cf_metered:
            used = neurons_today(token, account)
            spent = used - used_start
            if last_lane is not None:
                lane_spent[last_lane] = lane_spent.get(last_lane, 0) + max(0, used - prev_used)
            prev_used = used
            last_lane = None
            if account_cap and used >= account_cap - args.reserve:
                log["stop_reason"] = "hit_reserve"
                break
            if spent >= fathers_budget:
                log["stop_reason"] = "hit_budget"
                break
            if spent + 3 * SECTION_COST_EST > fathers_budget:
                log["stop_reason"] = "insufficient_for_next_claim"
                break

        rows = {r["Claim ID"]: r for r in parse_open_rows()}
        row = rows.get(claim_id)
        if not row:
            continue
        st = row.get("Status")
        if resume:
            if st not in {"claimed", "checking", "review"}:
                continue
            if row.get("Agent", "").strip() != agent:
                continue
        else:
            if st != "free":
                continue

        claim_lane = book_lane(row.get("Book slug", "")) if book_lane else "unknown"
        if cf_metered and not resume and lane_share is not None:
            eff_share = _eff_shares.get(claim_lane, lane_share(claim_lane)) if _eff_shares else lane_share(claim_lane)
            if lane_spent.get(claim_lane, 0) >= eff_share * fathers_budget:
                lane_capped += 1
                print(f"[{lane}] {claim_id} skipped: work lane {claim_lane} share spent", flush=True)
                continue

        if not resume and _hold_blocks(load_hold().get(claim_id) or {}):
            print("[%s] %s skipped: repair already spent" % (lane, claim_id), flush=True)
            continue

        entry = process_claim(
            claim_id,
            agent=agent,
            env=env,
            lane=lane,
            draft_model=draft,
            already_claimed=resume,
            mode=args.mode,
            rounds=args.rounds,
        )
        log["claims"].append(entry)
        entry["work_lane"] = claim_lane
        last_lane = claim_lane
        if entry.get("error") == "take_failed":
            continue
        if entry.get("ok"):
            done += 1
            consec_api_fail = 0
            time.sleep(0.5)
            continue
        # Failures: never infinite-loop one claim.
        err = entry.get("error")
        if err == "draft_failed":
            log["stop_reason"] = "draft_failed"
            break
        if err in {"content_fail", "hold"}:
            row = record_claim_fail(claim_id, err, _concrete_defect_key(claim_id))
            content_skips += 1
            print("[%s] %s on %s (fails=%s held=%s spent=%s); next claim" % (
                lane, err, claim_id, row.get("fails"), bool(row.get("held")),
                bool(row.get("repair_spent"))), flush=True)
            continue
        if err == "promote_lock_busy":
            print(f"[{lane}] {claim_id} promote lock busy; next claim", flush=True)
            continue
        if err == "promote_wall_timeout":
            row = record_claim_fail(claim_id, err)
            print(f"[{lane}] {claim_id} hit wall (fails={row['fails']} held={bool(row.get('held'))}); next claim", flush=True)
            continue
        if err == "api_fail":
            consec_api_fail += 1
            print(f"[{lane}] API fallbacks exhausted on {claim_id} (consec={consec_api_fail}); next claim", flush=True)
            if consec_api_fail >= 3:
                log["stop_reason"] = "consecutive_failures"
                break
            continue
        if err == "source_not_greek":
            print("[%s] %s skipped: source is not Unicode Greek" % (lane, claim_id), flush=True)
            continue
        log["stop_reason"] = err or "promote_failed"
        break

    if not log.get("stop_reason"):
        if done:
            log["stop_reason"] = "queue_exhausted"
        elif content_skips:
            log["stop_reason"] = "content_skips_only"
        else:
            log["stop_reason"] = "no_progress"
    log["finished"] = datetime.now(timezone.utc).isoformat()
    log["done_count"] = done
    log["content_skips"] = content_skips
    log["lane_capped"] = lane_capped
    log["held_count"] = sum(1 for r in load_hold().values() if r.get("held"))
    if cf_metered:
        try:
            log["neurons_end"] = neurons_today(token, account)
            log["neurons_spent"] = log["neurons_end"] - used_start
            if last_lane is not None:
                lane_spent[last_lane] = lane_spent.get(last_lane, 0) + max(
                    0, log["neurons_end"] - prev_used
                )
        except Exception as exc:  # noqa: BLE001
            log["neurons_end_error"] = str(exc)
    log["lane_spent"] = lane_spent
    return log


def run_gemini_side(args: argparse.Namespace, env: dict, cfg: dict) -> dict:
    """Optional parallel Gemini prep/QA. Artifacts only — never promotes or claims."""
    from llm_lane_config import as_list, gemini_enabled  # noqa: WPS433

    log: dict = {
        "lane": "gemini",
        "role": "prep_qa_only",
        "auto_promote": False,
        "started": datetime.now(timezone.utc).isoformat(),
    }
    if not gemini_enabled(cfg, force=bool(args.enable_gemini)):
        log["skipped"] = True
        log["reason"] = "disabled"
        return log
    if args.dry_run:
        log["skipped"] = True
        log["reason"] = "dry_run"
        return log
    if not (env.get("GEMINI_API_KEY") or "").strip():
        log["ok"] = False
        log["stop_reason"] = "missing_gemini_key"
        return log

    lane = (cfg.get("lanes") or {}).get("gemini") or {}
    sections = (args.gemini_sections or "").strip()
    if not sections:
        defaults = as_list(lane.get("overnight_default_sections"))
        if not defaults:
            log["ok"] = True
            log["skipped"] = True
            log["reason"] = "no_sections"
            log["finished"] = datetime.now(timezone.utc).isoformat()
            print("[gemini] skip: no sections configured", flush=True)
            return log
        sections = ",".join(defaults)
    cmd = [
        sys.executable,
        "scripts/gemini_prep_lane.py",
        "--require-enabled",
        "--sections",
        sections,
    ]
    if args.enable_gemini:
        cmd.append("--force")
    if args.gemini_checker_c:
        cmd.extend(["--prep", "--checker-c"])
    if args.gemini_book:
        cmd.extend(["--book", args.gemini_book])
        log["book"] = args.gemini_book
    if args.config:
        cmd.extend(["--config", args.config])

    print(f"[gemini] artifact prep sections={sections} (no promote)", flush=True)
    rc = run(cmd, env)
    log["ok"] = rc == 0
    log["rc"] = rc
    log["sections"] = sections
    log["finished"] = datetime.now(timezone.utc).isoformat()
    if rc != 0:
        log["stop_reason"] = "gemini_prep_failed"
    return log



def reopen_unsupported_done(dry_run: bool = False) -> list[str]:
    """Put today's done slices back in the queue when Pass B outruns the gloss.

    Wide scans do not un-mark an archive. A scan error must not fail the batch.
    """
    try:
        return _reopen_unsupported_done(dry_run)
    except Exception as exc:  # noqa: BLE001
        print("reopen scan failed: %s" % type(exc).__name__, flush=True)
        return []


def _reopen_unsupported_done(dry_run: bool) -> list[str]:
    import sys as _sys

    _sys.path.insert(0, str(ROOT / "scripts"))
    from ai_promote import _failer_texts, load_section_bundle
    from pipeline_autonomy import unsupported_pass_b_quotes

    text = CLAIMS.read_text(encoding="utf-8")
    if "## Done / closed" not in text:
        return []
    head, _, tail = text.partition("## Done / closed")
    hits = []
    for line in tail.splitlines():
        if "20260928" not in line and "20260929" not in line:
            continue
        if not line.startswith("| "):
            continue
        if "accept-current" in line:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 5 or cells[1] != "done":
            continue
        claim = cells[0]
        if not claim.startswith(("jer-h", "cyr-isa-")):
            continue
        if ("| %s |" % claim) in head:
            continue
        if "receipt " not in line:
            continue
        receipt = line.split("receipt ", 1)[1].strip().strip("|").strip()
        summary = ROOT / "outputs" / "ai-promote" / receipt / "summary.json"
        if not summary.is_file():
            continue
        try:
            data = json.loads(summary.read_text(encoding="utf-8"))
        except ValueError:
            continue
        book = ""
        bad = False
        for entry in data.get("results") or []:
            book = entry.get("book") or book
            texts = []
            for key in ("checker_a", "checker_b", "arbiter"):
                check = entry.get(key) or {}
                parsed = check.get("parsed") or {}
                if check.get("ok") is False and isinstance(parsed, dict):
                    texts.extend(_failer_texts(parsed))
            if not texts:
                continue
            try:
                bundle = load_section_bundle(entry.get("section"), entry.get("book"))
            except SystemExit:
                continue
            just = bundle.get("justification") or {}
            english = (bundle.get("english_row") or {}).get("english") or []
            if not isinstance(english, list):
                english = [english]
            if unsupported_pass_b_quotes(
                texts, str(just.get("pass_a_gloss") or ""), "\n".join(str(item) for item in english)
            ):
                bad = True
                break
        if bad:
            hits.append((claim, book or "cyril-alexandria-isaiah", cells[2]))
    print("reopen candidates: %s" % (", ".join(item[0] for item in hits) or "(none)"), flush=True)
    if dry_run or not hits:
        return [item[0] for item in hits]
    if len(hits) > 3:
        print("reopen skipped: %d candidates" % len(hits), flush=True)
        return []
    drop = {"| %s |" % item[0] for item in hits}
    out = []
    inserted = False
    in_done = False
    for line in text.splitlines(keepends=True):
        bare = line.strip()
        if bare.startswith("## Done"):
            in_done = True
        if in_done and any(bare.startswith(prefix) for prefix in drop):
            continue
        out.append(line)
        if not inserted and not in_done and bare.startswith("|---"):
            for claim, book, slice_id in hits:
                out.append(
                    "| %s | free | %s | %s |  |  | wip/%s | repair unsupported Pass B |\n"
                    % (claim, book, slice_id, claim)
                )
            inserted = True
    if not inserted:
        print("reopen skipped: no open table", flush=True)
        return []
    tmp = CLAIMS.with_suffix(".md.reopen")
    tmp.write_text("".join(out), encoding="utf-8")
    os.replace(str(tmp), str(CLAIMS))
    print("reopened %s" % ", ".join(item[0] for item in hits), flush=True)
    return [item[0] for item in hits]


def reopen_scaffold_done(dry_run: bool = False) -> list[str]:
    """Put done slices whose English is still operational text back in the queue.

    Four per batch. A scan error must not fail the batch.
    """
    try:
        return _reopen_scaffold_done(dry_run)
    except Exception as exc:  # noqa: BLE001
        print("scaffold reopen failed: %s" % type(exc).__name__, flush=True)
        return []


def _reopen_scaffold_done(dry_run: bool) -> list[str]:
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "scripts"))
    from ai_promote import load_section_bundle, sections_from_slice
    from pipeline.check_pass_ab import content_errors

    text = CLAIMS.read_text(encoding="utf-8")
    if "## Done / closed" not in text:
        return []
    head, _, tail = text.partition("## Done / closed")
    hits = []
    for line in tail.splitlines():
        if not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 3 or cells[1] != "done":
            continue
        claim = cells[0]
        if claim.startswith("cyr-isa-"):
            book = "cyril-alexandria-isaiah"
        elif claim.startswith("jer-h"):
            book = "origen-jeremiah-samuel"
        elif "--" in claim:
            book = claim.split("--", 1)[0]
        else:
            continue
        if ("| %s |" % claim) in head:
            continue
        try:
            sections = sections_from_slice(cells[2], book)
        except (SystemExit, Exception):  # noqa: BLE001
            continue
        scaffold = False
        for section in sections:
            try:
                bundle = load_section_bundle(section, book)
            except SystemExit:
                continue
            english = (bundle.get("english_row") or {}).get("english") or []
            if content_errors(english, "english"):
                scaffold = True
                break
        if scaffold:
            hits.append((claim, book, cells[2]))
    hits.sort(key=lambda item: (not item[0].startswith("cyr-isa-"), item[0]))
    print(
        "scaffold candidates: %d" % len(hits),
        flush=True,
    )
    if dry_run or not hits:
        return [item[0] for item in hits]
    hits = hits[:4]
    drop = {"| %s |" % item[0] for item in hits}
    out = []
    inserted = False
    in_done = False
    for line in text.splitlines(keepends=True):
        bare = line.strip()
        if bare.startswith("## Done"):
            in_done = True
        if in_done and any(bare.startswith(prefix) for prefix in drop):
            continue
        out.append(line)
        if not inserted and not in_done and bare.startswith("|---"):
            for claim, book, slice_id in hits:
                out.append(
                    "| %s | free | %s | %s |  |  | wip/%s | repair scaffold closeout |\n"
                    % (claim, book, slice_id, claim)
                )
            inserted = True
    if not inserted:
        print("scaffold reopen skipped: no open table", flush=True)
        return []
    tmp = CLAIMS.with_suffix(".md.scaffold")
    tmp.write_text("".join(out), encoding="utf-8")
    os.replace(str(tmp), str(CLAIMS))
    with _HOLD_LOCK:
        hold = load_hold()
        changed = False
        for claim, _book, _slice in hits:
            if claim in hold:
                hold.pop(claim, None)
                changed = True
        if changed:
            if hold:
                HOLD_PATH.write_text(
                    "\n".join(json.dumps(hold[c]) for c in sorted(hold)) + "\n",
                    encoding="utf-8",
                )
            else:
                HOLD_PATH.write_text("", encoding="utf-8")
    print("reopened scaffold %s" % ", ".join(item[0] for item in hits), flush=True)
    return [item[0] for item in hits]



def _queue_helpers():
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from book_adapter import get_adapter
    from pipeline.check_pass_ab import PLACEHOLDER, content_errors
    from pipeline_autonomy import source_is_betacode
    from work_lanes import book_year
    return get_adapter, content_errors, PLACEHOLDER, source_is_betacode, book_year


def _prefer_section(section: str) -> tuple:
    preferred = section == "open" or section.endswith("-open") or section.endswith("_open")
    return (0 if preferred else 1, section)


def earliest_scaffold_candidates(limit: int = 4) -> list:
    """Oldest Greek scaffold fragments, one claim per identical source. No writes."""
    import hashlib
    import re as _re

    get_adapter, content_errors, _placeholder, source_is_betacode, book_year = _queue_helpers()
    claims = CLAIMS.read_text(encoding="utf-8") if CLAIMS.is_file() else ""
    books = []
    root = ROOT / "books"
    if not root.is_dir():
        return []
    for book_dir in root.iterdir():
        if not book_dir.is_dir():
            continue
        slug = book_dir.name
        if slug in _QUEUE_SKIP or "melito" in slug:
            continue
        yml = book_dir / "book.yml"
        if not yml.is_file():
            continue
        language = ""
        for line in yml.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("language:"):
                language = line.split(":", 1)[1].strip().strip("\"'").casefold()
                break
        if not language.startswith("greek"):
            continue
        trans = book_dir / "translations"
        if not trans.is_dir() or not any(trans.glob("*_source.json")):
            continue
        books.append((book_year(slug), slug))
    books.sort()
    found = []
    for year, slug in books:
        if len(found) >= limit:
            break
        try:
            adapter = get_adapter(slug)
            index = adapter._source_index()
        except SystemExit:
            continue
        groups = {}
        order = []
        for section in index:
            try:
                fix = adapter.load_source_row(section)
            except SystemExit:
                continue
            greek = "\n".join(fix.get("greek") or [])
            if len(greek.strip()) < 40 or source_is_betacode(greek):
                continue
            if _re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", section) is None:
                continue
            digest = hashlib.sha256(greek.encode("utf-8")).hexdigest()
            if digest not in groups:
                groups[digest] = []
                order.append(digest)
            groups[digest].append(section)
        for digest in order:
            if len(found) >= limit:
                break
            members = sorted(groups[digest], key=_prefer_section)
            section = members[0]
            claim_id = "%s--%s" % (slug, section)
            if _re.fullmatch(adapter.claim_re, claim_id) is None:
                continue
            if ("| %s |" % claim_id) in claims:
                continue
            try:
                eng_path = adapter.english_path_for_section(section)
                payload = json.loads(eng_path.read_text(encoding="utf-8"))
                payload_rows = payload if isinstance(payload, list) else [payload]
                english = payload_rows[adapter.english_row_index(section)].get("english")
            except (OSError, ValueError, IndexError, KeyError, TypeError):
                continue
            if not content_errors(english):
                continue
            found.append((claim_id, slug, section, year))
    return found


def _rewrite_claims(text: str) -> None:
    if "## Open / active claims" not in text or "| Claim ID |" not in text:
        raise SystemExit("CLAIMS.md lost its open table")
    tmp = CLAIMS.with_suffix(".md.queue")
    tmp.write_text(text, encoding="utf-8")
    os.replace(str(tmp), str(CLAIMS))


def note_betacode_free_rows(dry_run: bool = False) -> list:
    """Free rows whose source is still betacode stop occupying a slot."""
    _get_adapter, _errors, _placeholder, source_is_betacode, _year = _queue_helpers()
    from book_adapter import get_adapter

    hits = []
    for row in parse_open_rows():
        if row.get("Status") != "free":
            continue
        notes = (row.get("Notes") or "").casefold()
        if "betacode" in notes or "do not publish" in notes:
            continue
        cid = str(row.get("Claim ID") or "")
        if not _auto_claim(cid):
            continue
        slug = row.get("Book slug") or ""
        try:
            adapter = get_adapter(slug)
            greek_bits = []
            for section in adapter.sections_from_slice(row.get("Slice (sections)") or ""):
                fix = adapter.load_source_row(section)
                greek_bits.extend(fix.get("greek") or [])
        except SystemExit:
            continue
        if source_is_betacode("\n".join(str(bit) for bit in greek_bits)):
            hits.append(cid)
    print("betacode free rows: %s" % (", ".join(hits) or "(none)"), flush=True)
    if dry_run or not hits:
        return hits
    text = CLAIMS.read_text(encoding="utf-8")
    out = []
    in_open = False
    for line in text.splitlines(keepends=True):
        bare = line.strip()
        if bare.startswith("## Open / active claims"):
            in_open = True
        elif in_open and bare.startswith("## "):
            in_open = False
        if in_open and bare.startswith("|"):
            cells = [cell.strip() for cell in bare.strip("|").split("|")]
            if cells and cells[0] in hits and not cells[0].startswith("---"):
                cells[-1] = "source is betacode; do not publish"
                line = "| " + " | ".join(cells) + " |\n"
        out.append(line)
    _rewrite_claims("".join(out))
    return hits


def enqueue_earliest_scaffolds(limit: int = 4, dry_run: bool = False) -> list:
    rows = earliest_scaffold_candidates(limit)
    print(
        "earliest candidates: %s" % (", ".join(item[0] for item in rows) or "(none)"),
        flush=True,
    )
    if dry_run or not rows:
        return [item[0] for item in rows]
    text = CLAIMS.read_text(encoding="utf-8")
    rows = [item for item in rows if ("| %s |" % item[0]) not in text]
    if not rows:
        return []
    out = []
    inserted = False
    in_open = False
    for line in text.splitlines(keepends=True):
        bare = line.strip()
        if bare.startswith("## Open / active claims"):
            in_open = True
        elif bare.startswith("## "):
            in_open = False
        out.append(line)
        if in_open and not inserted and bare.startswith("|---"):
            for claim_id, slug, section, _year in rows:
                out.append(
                    "| %s | free | %s | %s |  |  | wip/%s | earliest scaffold |\n"
                    % (claim_id, slug, section, claim_id)
                )
                just_dir = ROOT / "books" / slug / "reviews" / "justifications"
                if not just_dir.is_dir():
                    just_dir.mkdir(parents=True)
            inserted = True
    if not inserted:
        print("earliest enqueue skipped: no open table", flush=True)
        return []
    _rewrite_claims("".join(out))
    print("enqueued %s" % ", ".join(item[0] for item in rows), flush=True)
    return [item[0] for item in rows]


def _load_english_cache(adapter, section: str, cache: dict):
    path = adapter.english_path_for_section(section)
    if path not in cache:
        text = path.read_text(encoding="utf-8")
        raw = json.loads(text)
        wrapped = not isinstance(raw, list)
        cache[path] = {
            "rows": [raw] if wrapped else raw,
            "wrapped": wrapped,
            "text": text,
            "dirty": False,
        }
    entry = cache[path]
    item = entry["rows"][adapter.english_row_index(section)]
    return entry, item


def mirror_identical_greek(dry_run: bool = False) -> list:
    """Copy one gated reading onto scaffold copies of the same Greek."""
    import hashlib

    get_adapter, content_errors, placeholder, _betacode, _year = _queue_helpers()
    if not CLAIMS.is_file():
        return []
    slugs = []
    seen = set()
    in_done = False
    for line in CLAIMS.read_text(encoding="utf-8").splitlines():
        if line.startswith("## Done"):
            in_done = True
            continue
        if not in_done or not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 2 or cells[1] != "done" or "--" not in cells[0]:
            continue
        slug = cells[0].split("--", 1)[0]
        if slug in seen or slug in _QUEUE_SKIP or "melito" in slug:
            continue
        seen.add(slug)
        slugs.append(slug)
    copied = []
    for slug in slugs:
        try:
            adapter = get_adapter(slug)
            index = adapter._source_index()
        except SystemExit:
            continue
        groups = {}
        for section, (_path, _i, row) in index.items():
            greek = row.get("greek") or ""
            if not isinstance(greek, str):
                greek = "\n".join(str(part) for part in greek)
            if len(str(greek).strip()) < 40:
                continue
            digest = hashlib.sha256(str(greek).encode("utf-8")).hexdigest()
            groups.setdefault(digest, []).append(section)
        cache = {}
        for members in groups.values():
            if len(members) < 2:
                continue
            clean = None
            disagree = False
            scaffolds = []
            for section in members:
                try:
                    entry, item = _load_english_cache(adapter, section, cache)
                except (OSError, ValueError, IndexError, KeyError, SystemExit, TypeError):
                    continue
                english = item.get("english")
                if content_errors(english):
                    scaffolds.append((entry, item))
                    continue
                if clean is None:
                    clean = english
                elif clean != english:
                    disagree = True
                    break
            if disagree or not clean or not scaffolds:
                continue
            joined = clean if isinstance(clean, str) else " ".join(str(part) for part in clean)
            if len(joined.strip()) < 40 or placeholder.search(joined):
                continue
            reading = list(clean) if isinstance(clean, list) else [str(clean)]
            for entry, item in scaffolds:
                item["english"] = list(reading)
                entry["dirty"] = True
                copied.append("%s:%s" % (slug, item.get("section")))
        if dry_run:
            continue
        for path, entry in cache.items():
            if not entry["dirty"]:
                continue
            payload = entry["rows"][0] if entry["wrapped"] else entry["rows"]
            rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
            tmp = path.with_suffix(path.suffix + ".mirror")
            tmp.write_text(rendered, encoding="utf-8")
            os.replace(str(tmp), str(path))
    if copied:
        print("mirrored identical greek: %s" % ", ".join(copied), flush=True)
    return copied


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", default="overnight")
    ap.add_argument("--lanes", default="both", choices=["cf", "nv", "both"])
    ap.add_argument("--max-claims", type=int, default=12)
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--reserve", type=int, default=RESERVE)
    ap.add_argument("--config", default="")
    ap.add_argument("--cf-draft", default="")
    ap.add_argument("--nv-draft", default="")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--mode",
        default="prep",
        choices=["prep", "translate", "auto"],
        help="prep = crib only (default). translate = old Pass B + promote (not trusted). auto = auto_section draft-promote-revise-done.",
    )
    ap.add_argument(
        "--enable-gemini",
        action="store_true",
        help="Also run optional Gemini Flash-Lite prep/QA into outputs/gemini-prep/ "
        "(never promotes; CF/NV stay primary). Or set FATHERS_GEMINI_PREP=1 / "
        "lanes.gemini.enabled=true.",
    )
    ap.add_argument(
        "--gemini-sections",
        default="",
        help="Comma sections for Gemini side lane (default from LLM_LANE_CONFIG).",
    )
    ap.add_argument(
        "--gemini-checker-c",
        action="store_true",
        help="With Gemini side lane, also run checker-C on those sections (artifact-only).",
    )
    ap.add_argument(
        "--gemini-book",
        default="",
        help="Book slug for Gemini --sections (default origen-jeremiah-samuel).",
    )
    args = ap.parse_args()

    env = os.environ.copy()
    if env.get("CLOUDFLARE_API_TOKEN") and not env.get("CF_TOKEN"):
        env["CF_TOKEN"] = env["CLOUDFLARE_API_TOKEN"]
    env["PATH"] = "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:" + env.get("PATH", "")
    # Children skip global lock so CF+NV can promote different claims in parallel.
    # Wrapper still holds global-burn; claim locks stop same-claim double promote.
    env["SANE_FATHERS_NESTED"] = "1"

    from fathers_run_lock import acquire_global, clear_wall_deadline, install_wall_deadline, release_all  # noqa: WPS433
    from llm_lane_config import gemini_enabled, load_lane_config  # noqa: WPS433

    # Standalone overnight (no wrapper) still single-instances.
    if os.environ.get("SANE_FATHERS_WRAPPER") != "1":
        held = acquire_global(f"overnight_quota:{args.agent}")
        if held is None:
            print("Another Fathers burn holds the global lock — exit 0.", flush=True)
            return 0
    cfg = load_lane_config(args.config or None)
    # Soft job wall (default 6h): SIGALRM on main thread; lane threads may finish
    # their current promote (bounded by claim_wall_s). Exit 0 = normal stop.
    job_wall = int(cfg.get("overnight_wall_s") or 21600)
    install_wall_deadline(job_wall, label=f"overnight:{args.agent}", exit_code=0)

    OUT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lanes = ["cf", "nv"] if args.lanes == "both" else [args.lanes]
    want_gemini = gemini_enabled(cfg, force=bool(args.enable_gemini))
    if args.mode == "auto":
        reopen_unsupported_done(dry_run=bool(args.dry_run))
        reopen_scaffold_done(dry_run=bool(args.dry_run))
        note_betacode_free_rows(dry_run=bool(args.dry_run))
        enqueue_earliest_scaffolds(dry_run=bool(args.dry_run))

    logs: dict[str, dict] = {}
    try:
        # CF/NV remain the only claim/promote lanes. Gemini is optional side work.
        with ThreadPoolExecutor(max_workers=3 if want_gemini else 2) as pool:
            futs = {pool.submit(run_lane, lane, args, env): lane for lane in lanes}
            if want_gemini:
                futs[pool.submit(run_gemini_side, args, env, cfg)] = "gemini"
            for fut in as_completed(futs):
                lane = futs[fut]
                logs[lane] = fut.result()

        summary = {
            "started": stamp,
            "lanes": logs,
            "finished": datetime.now(timezone.utc).isoformat(),
        }
        if not args.dry_run:
            path = OUT / f"{stamp}-dual.json"
            path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2), flush=True)

        # Nonzero only for true infra gaps / draft crash — not content/API/wall/lock.
        # Gemini side-lane failure never fails the overnight job (CF/NV primary).
        hard = {"draft_failed", "missing_cf_token", "missing_nv_key"}
        for name, lane_log in logs.items():
            if name == "gemini":
                continue
            if lane_log.get("stop_reason") in hard:
                return 2
        return 0
    finally:
        if args.mode == "auto" and not args.dry_run:
            try:
                mirror_identical_greek()
            except Exception as exc:  # noqa: BLE001
                print("mirror failed: %s" % type(exc).__name__, flush=True)
        clear_wall_deadline()
        release_all()


if __name__ == "__main__":
    raise SystemExit(main())
