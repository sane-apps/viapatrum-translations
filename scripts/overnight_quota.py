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


def free_auto_claims() -> list[str]:
    hold = load_hold()
    out = []
    for r in parse_open_rows():
        cid = str(r.get("Claim ID", ""))
        if r.get("Status") != "free":
            continue
        if not cid.startswith(AUTO_PREFIXES):
            continue
        if hold.get(cid, {}).get("held"):
            continue
        out.append(cid)
    return out


def claimed_for_agent(agent: str) -> list[str]:
    """Stuck claimed rows for this overnight agent (resume after interrupt)."""
    return [
        r["Claim ID"]
        for r in parse_open_rows()
        if r.get("Status") in {"claimed", "checking", "review"}
        and r.get("Agent", "").strip() == agent
        and str(r.get("Claim ID", "")).startswith(AUTO_PREFIXES)
        and not load_hold().get(str(r.get("Claim ID", "")), {}).get("held")
    ]


def _claim_wall_s() -> int:
    try:
        cfg = json.loads((ROOT / "docs" / "LLM_LANE_CONFIG.json").read_text(encoding="utf-8"))
        return int(cfg.get("claim_wall_s") or 5400)
    except Exception:  # noqa: BLE001
        return 5400


HOLD_PATH = OUT / "HOLD.jsonl"
AUTO_PREFIXES = ("jer-h", "cyr-isa-")


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


def record_claim_fail(claim: str, reason: str) -> dict:
    hold = load_hold()
    row = hold.get(claim) or {"claim": claim, "fails": 0}
    row["fails"] = int(row.get("fails") or 0) + 1
    row["reason"] = reason
    row["updated"] = datetime.now(timezone.utc).isoformat()
    if row["fails"] >= 2:
        row["held"] = True
    hold[claim] = row
    HOLD_PATH.write_text("\n".join(json.dumps(hold[c]) for c in sorted(hold)) + "\n", encoding="utf-8")
    return row


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
        elif rc == 2:
            entry["error"] = "api_fail"
        elif rc == 4:
            entry["error"] = "promote_wall_timeout"
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
    for claim_id, resume in queue:
        if done >= args.max_claims:
            log["stop_reason"] = "max_claims"
            break
        if cf_metered:
            used = neurons_today(token, account)
            spent = used - used_start
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
            row = record_claim_fail(claim_id, err)
            content_skips += 1
            print(f"[{lane}] {err} on {claim_id} (fails={row['fails']} held={bool(row.get('held'))}); next claim", flush=True)
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
    log["held_count"] = sum(1 for r in load_hold().values() if r.get("held"))
    if cf_metered:
        try:
            log["neurons_end"] = neurons_today(token, account)
            log["neurons_spent"] = log["neurons_end"] - used_start
        except Exception as exc:  # noqa: BLE001
            log["neurons_end_error"] = str(exc)
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
        clear_wall_deadline()
        release_all()


if __name__ == "__main__":
    raise SystemExit(main())
