#!/usr/bin/env python3
"""Burn free CF neurons + NVIDIA NIM in parallel on Fathers claims.

Lanes (separate budgets):
  cf — Workers AI draft/check until ~10k neurons/day (UTC) reserve
  nv — NIM draft/check (RPM/latency bound; no CF neuron burn)

  source ~/.config/nv/env && export CF_TOKEN="$CLOUDFLARE_API_TOKEN"
  python3 scripts/overnight_quota.py --lanes both --agent overnight

Recovery: resumes this agent's claimed-but-not-done rows before taking free ones.
Does NOT Logos-compile or deploy the site.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
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
SECTION_COST_EST = 160  # Qwen + Gemma + 70B-ish

NV_DRAFT_DEFAULT = "nvidia/nemotron-3-super-120b-a12b"
NV_CHECKER_A_DEFAULT = "deepseek-ai/deepseek-v4-flash-0731"
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


def free_jer_claims() -> list[str]:
    return [
        r["Claim ID"]
        for r in parse_open_rows()
        if r.get("Status") == "free" and str(r.get("Claim ID", "")).startswith("jer-h")
    ]


def claimed_for_agent(agent: str) -> list[str]:
    """Stuck claimed rows for this overnight agent (resume after interrupt)."""
    return [
        r["Claim ID"]
        for r in parse_open_rows()
        if r.get("Status") in {"claimed", "checking", "review"}
        and r.get("Agent", "").strip() == agent
        and str(r.get("Claim ID", "")).startswith("jer-h")
    ]


def run(cmd: list[str], env: dict) -> int:
    print("+", " ".join(cmd), flush=True)
    return subprocess.call(cmd, cwd=ROOT, env=env)


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
) -> dict:
    entry: dict = {"claim": claim_id, "ok": False, "lane_agent": agent, "lane": lane}
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
    if rc == 1:
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

    if lane == "cf":
        token = env.get("CF_TOKEN") or env.get("CLOUDFLARE_API_TOKEN") or ""
        account = env.get("CLOUDFLARE_ACCOUNT_ID") or DEFAULT_ACCOUNT
        if not token:
            log["stop_reason"] = "missing_cf_token"
            return log
        used = neurons_today(token, account)
        left = FREE_NEURONS - used
        print(f"[cf] neurons today used={used} left≈{left} reserve={args.reserve}", flush=True)
        if left <= args.reserve:
            log["stop_reason"] = "already_at_reserve"
            return log
    else:
        if not (env.get("NV_API_KEY") or env.get("NVIDIA_API_KEY")):
            log["stop_reason"] = "missing_nv_key"
            return log
        print(f"[nv] NIM lane draft={draft} (checkers from LLM_LANE_CONFIG)", flush=True)

    queue: list[tuple[str, bool]] = [(c, True) for c in claimed_for_agent(agent)]
    for c in free_jer_claims():
        queue.append((c, False))

    if args.dry_run:
        log["stop_reason"] = "dry_run"
        log["queue"] = [{"claim": c, "resume": r} for c, r in queue[:20]]
        return log

    done = 0
    content_skips = 0
    for claim_id, resume in queue:
        if done >= args.max_claims:
            log["stop_reason"] = "max_claims"
            break
        if lane == "cf":
            used = neurons_today(token, account)
            left = FREE_NEURONS - used
            if left <= args.reserve:
                log["stop_reason"] = "hit_reserve"
                break
            if left < args.reserve + 3 * SECTION_COST_EST:
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

        entry = process_claim(
            claim_id,
            agent=agent,
            env=env,
            lane=lane,
            draft_model=draft,
            already_claimed=resume,
        )
        log["claims"].append(entry)
        if entry.get("error") == "take_failed":
            continue
        if entry.get("ok"):
            done += 1
            time.sleep(0.5)
            continue
        # Failures: never infinite-loop one claim.
        err = entry.get("error")
        if err == "draft_failed":
            log["stop_reason"] = "draft_failed"
            break
        if err == "content_fail":
            # Leave claimed for human/fix; move on so overnight still progresses.
            content_skips += 1
            print(f"[{lane}] content fail on {claim_id}; leave claimed, next claim", flush=True)
            continue
        if err == "api_fail":
            # One API-exhausted claim: try next; KeepAlive fuse handled in shell wrapper.
            print(f"[{lane}] API fallbacks exhausted on {claim_id}; next claim", flush=True)
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
    if lane == "cf":
        try:
            log["neurons_end"] = neurons_today(token, account)
        except Exception as exc:  # noqa: BLE001
            log["neurons_end_error"] = str(exc)
    return log


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", default="overnight")
    ap.add_argument("--lanes", default="both", choices=["cf", "nv", "both"])
    ap.add_argument("--max-claims", type=int, default=12)
    ap.add_argument("--reserve", type=int, default=RESERVE)
    ap.add_argument("--config", default="")
    ap.add_argument("--cf-draft", default="")
    ap.add_argument("--nv-draft", default="")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    env = os.environ.copy()
    if env.get("CLOUDFLARE_API_TOKEN") and not env.get("CF_TOKEN"):
        env["CF_TOKEN"] = env["CLOUDFLARE_API_TOKEN"]
    env["PATH"] = "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:" + env.get("PATH", "")

    OUT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lanes = ["cf", "nv"] if args.lanes == "both" else [args.lanes]

    logs: dict[str, dict] = {}
    if len(lanes) == 1:
        logs[lanes[0]] = run_lane(lanes[0], args, env)
    else:
        # Parallel CF + NVIDIA — separate claim agents so take locks don't collide
        with ThreadPoolExecutor(max_workers=2) as pool:
            futs = {pool.submit(run_lane, lane, args, env): lane for lane in lanes}
            for fut in as_completed(futs):
                lane = futs[fut]
                logs[lane] = fut.result()

    summary = {
        "started": stamp,
        "lanes": logs,
        "finished": datetime.now(timezone.utc).isoformat(),
    }
    path = OUT / f"{stamp}-dual.json"
    path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)

    # KeepAlive only for true infra gaps / draft crash — not content fails or exhausted API chains
    hard = {"draft_failed", "missing_cf_token", "missing_nv_key"}
    for lane_log in logs.values():
        if lane_log.get("stop_reason") in hard:
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
