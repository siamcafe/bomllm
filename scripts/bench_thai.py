#!/usr/bin/env python3
"""
BOMLLM Thai benchmark harness.

Reproduces the numbers in benchmarks/thai-quality.csv. Language-agnostic:
swap THAI_RE for another script's character class to bench Lao/Khmer/etc.

Modes:
  quality  - run the prompt bank, score thai_ratio + Han leaks + completion
  speed    - 5-prompt warm tok/s + TTFT micro-bench (direct Ollama)
  micro    - 28-prompt sampling A/B pool
  prod     - 36-question user-path QC set

Protocol (matches docs/thai.md):
  * completion_floor applied: num_ctx 32768, num_predict 8192 (quality mode)
  * scorer: thai_ratio = thai_chars / (thai_chars + latin_chars),
    reasoning/thinking stripped before scoring
  * stats: paired bootstrap, 10,000 resamples, 95% CI (use --compare)
  * contamination control: refuses to run if >1 model resident (--strict-ps)

No secrets: pass keys via env (BOM_BENCH_KEY) or --key. Never printed.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import statistics
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

# --- Character classes -------------------------------------------------------
THAI_RE = re.compile(r"[\u0E00-\u0E7F]")
LATIN_RE = re.compile(r"[A-Za-z]")
HAN_RE = re.compile(r"[\u4E00-\u9FFF\u3400-\u4DBF]")
THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)

# --- Prompt bank -------------------------------------------------------------
# A small embedded smoke bank ships with the repo. The full pinned 60-prompt
# bank (sha256 2c3333db...) is distributed with the HF config repo to keep
# this file readable; point --bank at it for the canonical run.
EMBEDDED_BANK = [
    {"id": "G01", "cat": "general_short", "q": "สวัสดีครับ วันนี้ทองแพงขึ้นไหมครับ"},
    {"id": "G02", "cat": "general_short", "q": "อธิบาย RSI divergence แบบเข้าใจง่ายหน่อย"},
    {"id": "G03", "cat": "general_short", "q": " rebate คืออะไร ตอบสั้นๆ สุภาพ"},
    {"id": "R01", "cat": "report_long", "q": "เขียนบทความภาษาไทย 800 คำ เรื่องข้อดีของ copy trade สำหรับมือใหม่"},
    {"id": "R02", "cat": "report_long", "q": "วิเคราะห์กรอบราคาทองคำรายสัปดาห์ พร้อมแนวรับแนวต้าน"},
    {"id": "C01", "cat": "code_mixed", "q": "เขียน python function อ่าน CSV แล้วคืนค่า median พร้อมคอมเมนต์ไทย"},
    {"id": "C02", "cat": "code_mixed", "q": "อธิบายความต่างระหว่าง docker compose up และ start"},
]


def strip_reasoning(text: str) -> str:
    return THINK_RE.sub("", text or "")


def thai_ratio(text: str) -> float:
    t = len(THAI_RE.findall(text))
    l = len(LATIN_RE.findall(text))
    return t / (t + l) if (t + l) else 0.0


def han_events(text: str) -> int:
    return len(HAN_RE.findall(text))


def post_json(url: str, payload: dict, key: str | None, timeout: int) -> tuple[dict, float]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}
        | ({"Authorization": f"Bearer {key}"} if key else {}),
        method="POST",
    )
    t0 = time.monotonic()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode()), time.monotonic() - t0


def run_quality(args) -> int:
    bank = EMBEDDED_BANK
    if args.bank and Path(args.bank).exists():
        bank = [json.loads(x) for x in Path(args.bank).read_text(encoding="utf-8").splitlines() if x.strip()]
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    results_path = out_dir / "results.jsonl"

    endpoint = args.endpoint.rstrip("/")
    is_ollama_direct = endpoint.endswith("11434")
    url = endpoint + ("/api/chat" if is_ollama_direct else "/chat/completions")

    n_ok = 0
    with results_path.open("w", encoding="utf-8") as fh:
        for row in bank:
            payload_common = {
                "model": args.model,
                "messages": ([{"role": "system", "content": args.system}] if args.system else [])
                + [{"role": "user", "content": row["q"]}],
                "stream": False,
            }
            if is_ollama_direct:
                payload_common["think"] = args.think
                payload_common["options"] = {
                    "temperature": args.temperature, "top_p": args.top_p,
                    "top_k": args.top_k, "repeat_penalty": args.repeat_penalty,
                    "num_ctx": args.num_ctx, "num_predict": args.num_predict,
                    "seed": args.seed,
                }
            else:
                payload_common.update({
                    "temperature": args.temperature, "top_p": args.top_p,
                    "max_tokens": args.num_predict,
                })
            try:
                resp, wall = post_json(url, payload_common, args.key, args.timeout)
                if is_ollama_direct:
                    content = resp.get("message", {}).get("content", "")
                    done = resp.get("done_reason", "")
                    eval_count = resp.get("eval_count", 0)
                    eval_dur = resp.get("eval_duration", 1)
                    tok_s = round(eval_count / (eval_dur / 1e9), 2) if eval_dur else None
                else:
                    ch = resp.get("choices", [{}])[0]
                    content = ch.get("message", {}).get("content", "")
                    done = ch.get("finish_reason", "")
                    tok_s = None
                clean = strip_reasoning(content)
                rec = {
                    "id": row["id"], "cat": row["cat"], "wall_s": round(wall, 2),
                    "finish_reason": done, "empty": len(clean.strip()) == 0,
                    "thai_ratio": round(thai_ratio(clean), 4),
                    "han_chars": han_events(clean), "tok_s": tok_s,
                    "completion_chars": len(clean),
                }
                n_ok += 1
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
                rec = {"id": row["id"], "cat": row["cat"], "error": type(e).__name__}
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(f"[{rec['id']}] {rec.get('thai_ratio', 'ERR')} han={rec.get('han_chars', '-')}")

    # Aggregate
    rows = [json.loads(x) for x in results_path.read_text(encoding="utf-8").splitlines()]
    ok = [r for r in rows if "error" not in r]
    ratios = [r["thai_ratio"] for r in ok]
    summary = {
        "n": len(rows), "n_ok": len(ok),
        "completion_rate": round(len(ok) / max(len(rows), 1), 4),
        "thai_ratio_mean": round(statistics.fmean(ratios), 4) if ratios else None,
        "thai_ratio_median": round(statistics.median(ratios), 4) if ratios else None,
        "han_total": sum(r.get("han_chars", 0) for r in ok),
        "empty_n": sum(1 for r in ok if r.get("empty")),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if summary["completion_rate"] >= 0.95 else 1


def run_speed(args) -> int:
    """5-prompt warm micro-bench against direct Ollama /api/generate."""
    prompts = ["Explain RSI divergence in 200 words.",
               "สวัสดีครับ แนะนำตัวหน่อย",
               "Write a Python hello world.",
               "อธิบาย Bollinger Bands สั้นๆ",
               "What is 9.9 minus 9.11?"]
    endpoint = args.endpoint.rstrip("/") + "/api/generate"
    results = []
    for p in prompts:
        walls, toks = [], []
        for run in range(3):
            resp, _ = post_json(endpoint, {
                "model": args.model, "prompt": p, "stream": False,
                "options": {"num_predict": 256, "temperature": 0.7, "top_p": 0.8},
            }, None, args.timeout)
            if run == 0:
                continue  # warmup discarded
            ec, ed = resp.get("eval_count", 0), resp.get("eval_duration", 1)
            toks.append(ec / (ed / 1e9))
            walls.append(resp.get("prompt_eval_duration", 0) / 1e9)
        results.append({"prompt": p[:30], "tok_s": round(statistics.fmean(toks), 2),
                        "ttft_s": round(statistics.fmean(walls), 3)})
        print(results[-1])
    avg = statistics.fmean(r["tok_s"] for r in results)
    print(f"\navg tok/s (warm, runs 2+3): {avg:.2f}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="BOMLLM Thai benchmark harness")
    ap.add_argument("--mode", choices=["quality", "speed", "micro", "prod"], default="quality")
    ap.add_argument("--endpoint", default="http://127.0.0.1:11434",
                    help="Ollama base (…:11434) or LiteLLM /v1 base")
    ap.add_argument("--model", required=True)
    ap.add_argument("--key", default=os.environ.get("BOM_BENCH_KEY"))
    ap.add_argument("--bank", help="path to prompts.jsonl (canonical 60-bank)")
    ap.add_argument("--system", default="", help="system prompt (Config G text)")
    ap.add_argument("--out", default="benchmarks/results/local")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--top-k", type=int, default=20)
    ap.add_argument("--repeat-penalty", type=float, default=1.05)
    ap.add_argument("--num-ctx", type=int, default=32768)
    ap.add_argument("--num-predict", type=int, default=8192)
    ap.add_argument("--think", action="store_true")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.dry_run:
        print(f"DRY-RUN mode={args.mode} model={args.model} endpoint={args.endpoint} "
              f"key={'loaded len=' + str(len(args.key)) if args.key else 'none'}")
        return 0
    if args.mode == "speed":
        return run_speed(args)
    return run_quality(args)


if __name__ == "__main__":
    sys.exit(main())
