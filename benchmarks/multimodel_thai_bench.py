#!/usr/bin/env python3
# bomllm_multimodel_bench [llm-mac-mini]
# Same 10 Thai prompts across BOMLLM TURBO (local ollama) + z.ai cloud models.
# seed=42, temp=0.6, max_tokens=2048. Keys fetched at runtime via ssh, never
# written to disk, never printed. Errors sanitized (no URL / no key).
import json, os, re, subprocess, sys, time, unicodedata

import requests, yaml

BENCH_DIR = r"D:\MY documents\thaillm\bomllm-release\benchmarks"
SMOKE = "--smoke" in sys.argv
SUFFIX = "_smoke" if SMOKE else ""
OUT_JSON = os.path.join(BENCH_DIR, f"multimodel_thai_bench{SUFFIX}.json")
OUT_CSV = os.path.join(BENCH_DIR, f"multimodel_thai_bench{SUFFIX}.csv")
PROGRESS = os.path.join(BENCH_DIR, f"bench_progress{SUFFIX}.log")
PARTIAL = os.path.join(BENCH_DIR, f"bench_partial{SUFFIX}.jsonl")

PROMPTS = [
    "อธิบายเรื่อง AI สั้นๆ ให้คนทั่วไปเข้าใจ",
    "วิเคราะห์เศรษฐกิจไทยปี 2026 สั้นๆ",
    "เขียนบทความเรื่องการลงทุนสำหรับมือใหม่",
    "อธิบาย blockchain เป็นภาษาไทย ให้เข้าใจง่าย",
    "สรุปข่าวเศรษฐกิจโลกวันนี้สั้นๆ",
    "แนะนำวิธีประหยัดเงิน 5 ข้อ",
    "อธิบายความแตกต่างระหว่าง AI กับ ML",
    "เขียนรีวิวร้านอาหารไทยให้น่าสนใจ",
    "อธิบายวิธีการเทรด forex สำหรับมือใหม่ เป็นภาษาไทย",
    "สรุปประวัติศาสตร์ไทยสมัยรัตนโกสินทร์สั้นๆ",
]
if SMOKE:
    PROMPTS = PROMPTS[:1]


def log(line):
    ts = time.strftime("%H:%M:%S")
    with open(PROGRESS, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {line}\n")
    print(f"[{ts}] {line}", flush=True)


def partial_write(obj):
    with open(PARTIAL, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def thai_ratio(text):
    if not text:
        return 0.0
    thai = sum(1 for c in text if "\u0E00" <= c <= "\u0E7F")
    total = sum(1 for c in text if not c.isspace())
    return thai / total if total > 0 else 0.0


def han_count(text):
    return sum(1 for c in text if "CJK" in unicodedata.name(c, ""))


def sanitize(err):
    e = str(err)
    e = re.sub(r"sk-[A-Za-z0-9_\-]{4,}", "***KEY***", e)
    e = re.sub(r"https?://\S+", "***URL***", e)
    e = re.sub(r"Bearer\s+\S+", "Bearer ***", e)
    return e[:200]


# === MODEL DISCOVERY ===
MODELS = [
    {
        "name": "BOMLLM TURBO",
        "api": "http://YOUR_SERVER_IP:11434/api/chat",
        "model": "qwen38-chat",
        "type": "ollama",
        "cost_per_1k": 0.0,
        "note": "Local Mac Mini M4 Pro 48GB",
    }
]

ZAI_WANTED = ["zai-fallback", "zai-brain", "glm-4.6v-flash", "zai-glm-4.6v"]
# secret-free fallback if the runtime config ssh fails (transient network);
# mirrors Contabo /home/bom/bomllm/litellm/config.yaml z.ai routes 2026-09-11
FALLBACK_ROUTES = [
    {"name": "zai-fallback", "model": "glm-4.5"},
    {"name": "zai-brain", "model": "glm-5.2"},
    {"name": "glm-4.6v-flash", "model": "glm-4.6v-flash"},
    {"name": "zai-glm-4.6v", "model": "glm-4.6v"},
]
config = None
for attempt in (1, 2):
    try:
        r = subprocess.run(
            ["ssh", "-p99", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes",
             "user@VPS_HOST_REDACTED", "cat /home/bom/bomllm/litellm/config.yaml"],
            capture_output=True, text=True, timeout=30,
        )
        if r.stdout and r.stdout.strip().startswith("general_settings"):
            config = yaml.safe_load(r.stdout)
            break
        log(f"config ssh attempt {attempt}: empty stdout, rc={r.returncode}")
    except Exception as e:
        log(f"config ssh attempt {attempt} failed: {sanitize(e)}")
if config is not None:
    for m in config.get("model_list", []):
        lp = m.get("litellm_params", {})
        name = m.get("model_name", "")
        if name in ZAI_WANTED:
            MODELS.append({
                "name": name,
                "api_base": lp.get("api_base", "").rstrip("/"),
                "model": lp.get("model", "").replace("openai/", ""),
                "api_key": lp.get("api_key", ""),
                "type": "openai",
                "note": "via z.ai",
            })
else:
    log("FALLBACK: using embedded route list (config ssh unavailable)")
    for fr in FALLBACK_ROUTES:
        MODELS.append({
            "name": fr["name"],
            "api_base": "https://api.z.ai/api/paas/v4",
            "model": fr["model"],
            "api_key": "os.environ/ZAI_API_KEY",
            "type": "openai",
            "note": "via z.ai (embedded fallback)",
        })

seen = set()
cloud = []
for m in MODELS[1:]:
    if m["name"] not in seen:
        seen.add(m["name"])
        cloud.append(m)
cloud = cloud[:5]
MODELS = [MODELS[0]] + cloud
if SMOKE and len(MODELS) > 2:
    MODELS = MODELS[:2]

# resolve os.environ/<VAR> api_key refs from process env (populated at launch);
# value never printed, never written to disk
for m in MODELS:
    k = m.get("api_key", "")
    if k.startswith("os.environ/"):
        var = k.split("/", 1)[1]
        m["api_key"] = os.environ.get(var, "")
        log(f"  key {m['name']}: env {var}, {'length=' + str(len(m['api_key'])) if m['api_key'] else 'MISSING'}")

log(f"=== MODELS TO BENCH ({len(MODELS)}) ===")
for m in MODELS:
    log(f"  {m['name']} -> {m.get('model', m.get('api', '?'))}")

# === RUN BENCH ===
all_results = []
for model_cfg in MODELS:
    model_results = []
    log(f"--- {model_cfg['name']} START ---")
    for i, prompt in enumerate(PROMPTS):
        t0 = time.time()
        log(f"  {i+1}/{len(PROMPTS)} ASK ({prompt[:18]}...)")
        try:
            if model_cfg["type"] == "ollama":
                resp = requests.post(model_cfg["api"], json={
                    "model": model_cfg["model"],
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "options": {"temperature": 0.6, "top_p": 0.95, "top_k": 20,
                                "repeat_penalty": 1.05, "num_predict": 2048,
                                "num_ctx": 16384, "seed": 42},
                }, timeout=900)
                d = resp.json()
                content = d.get("message", {}).get("content", "")
                tokens = d.get("eval_count", len(content) // 4)
                ptok = d.get("prompt_eval_count", 0)
            else:
                headers = {
                    "Authorization": f"Bearer {model_cfg.get('api_key', '')}",
                    "Content-Type": "application/json",
                }
                # z.ai paas/v4 base: chat endpoint = <api_base>/chat/completions
                resp = requests.post(
                    f"{model_cfg['api_base']}/chat/completions",
                    json={
                        "model": model_cfg["model"],
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.6,
                        "max_tokens": 2048,
                        "seed": 42,
                    },
                    headers=headers, timeout=120,
                )
                d = resp.json()
                if resp.status_code != 200:
                    raise RuntimeError(f"HTTP {resp.status_code}: {sanitize(json.dumps(d))[:150]}")
                content = d.get("choices", [{}])[0].get("message", {}).get("content", "")
                tokens = d.get("usage", {}).get("completion_tokens", len(content) // 4)
                ptok = d.get("usage", {}).get("prompt_tokens", 0)

            wall = time.time() - t0
            tr = thai_ratio(content)
            hc = han_count(content)
            tps = tokens / wall if wall > 0 else 0
            row = {
                "prompt_i": i + 1,
                "thai_ratio": round(tr, 4),
                "han": hc,
                "tokens": tokens,
                "prompt_tokens": ptok,
                "content_chars": len(content),
                "wall_s": round(wall, 1),
                "tok_s": round(tps, 1),
            }
            model_results.append(row)
            partial_write({"model": model_cfg["name"], **row})
            log(f"  {i+1}/{len(PROMPTS)} thai={tr:.4f} han={hc} tok={tokens} tok/s={tps:.1f} wall={wall:.1f}s")
        except Exception as e:
            row = {"prompt_i": i + 1, "error": sanitize(e)}
            model_results.append(row)
            partial_write({"model": model_cfg["name"], **row})
            log(f"  {i+1}/{len(PROMPTS)} ERROR: {sanitize(e)}")

    valid = [x for x in model_results if "thai_ratio" in x]
    if valid:
        avg_thai = sum(x["thai_ratio"] for x in valid) / len(valid)
        avg_tps = sum(x["tok_s"] for x in valid) / len(valid)
        total_han = sum(x["han"] for x in valid)
        avg_wall = sum(x["wall_s"] for x in valid) / len(valid)
        total_ctok = sum(x["tokens"] for x in valid)
        total_ptok = sum(x["prompt_tokens"] for x in valid)
    else:
        avg_thai = avg_tps = total_han = avg_wall = total_ctok = total_ptok = 0

    summary = {
        "model": model_cfg["name"],
        "model_id": model_cfg.get("model", ""),
        "note": model_cfg.get("note", ""),
        "avg_thai_ratio": round(avg_thai, 4),
        "total_han": total_han,
        "avg_tok_s": round(avg_tps, 1),
        "avg_wall_s": round(avg_wall, 1),
        "total_completion_tokens": total_ctok,
        "total_prompt_tokens": total_ptok,
        "valid_prompts": len(valid),
        "errors": len(model_results) - len(valid),
        "per_prompt": model_results,
    }
    all_results.append(summary)
    log(f"  {model_cfg['name']} AVG: thai={avg_thai:.4f} han={total_han} tok/s={avg_tps:.1f} ctok={total_ctok}")

# === RANKING ===
ranked = sorted(all_results, key=lambda x: x["avg_thai_ratio"], reverse=True)
log("=== RANKING (by Thai ratio) ===")
for i, rr in enumerate(ranked):
    log(f"  #{i+1} {rr['model']}: thai={rr['avg_thai_ratio']:.4f} han={rr['total_han']} tok/s={rr['avg_tok_s']:.1f}")

# === SAVE (no api keys, no endpoint URLs) ===
output = {
    "benchmark": "bomllm_multimodel_thai_bench",
    "date": "2026-09-11",
    "prompts": len(PROMPTS),
    "method": "same 10 Thai prompts, seed=42, temp=0.6, max_tokens=2048",
    "cost_basis": "token counts measured; TURBO local cost 0.0; z.ai USD pricing NOT_COVERED (no price table in config)",
    "ranking": [
        {"rank": i + 1, "model": rr["model"], "thai_ratio": rr["avg_thai_ratio"],
         "han": rr["total_han"], "tok_s": rr["avg_tok_s"], "wall_s": rr["avg_wall_s"],
         "completion_tokens": rr["total_completion_tokens"]}
        for i, rr in enumerate(ranked)
    ],
    "full_results": all_results,
}
os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
log(f"Saved to {OUT_JSON}")

with open(OUT_CSV, "w", encoding="utf-8") as f:
    f.write("rank,model,thai_ratio,han_leak,tok_s,wall_s,completion_tokens,note\n")
    for i, rr in enumerate(ranked):
        f.write(f"{i+1},{rr['model']},{rr['avg_thai_ratio']},{rr['total_han']},{rr['avg_tok_s']},{rr['avg_wall_s']},{rr['total_completion_tokens']},{rr.get('note','')}\n")
log(f"Saved CSV to {OUT_CSV}")
log("=== BENCH DONE ===")
