# Benchmarks: reproduce every number we publish

House rule: **receipts, not adjectives.** Every number in the README comes
from a run you can repeat. This folder has the harness, the result
structure, and the hardware pin. Cells marked `[BENCH_DATA_PENDING]` in
the CSVs are re-measured on the release hardware before launch
(tracking: docs/show-hn.md item L-7).

## Hardware pin (the numbers are only valid against this)

| | |
|---|---|
| Machine | Mac Mini M4 Pro, 48 GB unified memory, 14-core CPU |
| OS | macOS 26.x arm64 |
| Runtime | Ollama 0.33.3, MLX backend (release rerun pending L-7) |
| Weights | 27B-class Qwen fine-tune (TURBO-Fable series), nvfp4, ~18 GB on disk / ~23 GB resident |
| Context | 32768 |
| Baseline | same weights, GGUF Q4_K_M (llama.cpp path) |
| Cloud baseline | GLM-4.5-Flash via z.ai, thinking disabled, max_tokens 2000 |

## Bench 1 — Speed (MLX vs GGUF)

Method: 5 fixed prompts × 3 runs, `num_predict=256`, `temperature=0.7`,
`top_p=0.8`, `stream=false`; run 1 discarded as warmup; tok/s =
`eval_count / eval_duration` from `/api/generate`. All models unloaded
before each phase (`ollama ps` empty, verified).

| Metric | GGUF Q4_K_M | MLX nvfp4 | Delta |
|---|---|---|---|
| Decode avg | 7.85 tok/s | **30.23 tok/s** | +285% |
| TTFT warm | 0.288 s | **0.040 s** | −0.248 s |
| Resident | 18 GB | 23 GB | +5 GB |
| Swap | 0 | 0 | — |

Per-prompt warm averages (tok/s):
GGUF `7.80 / 7.43 / 8.13 / 8.12 / 7.77` · MLX `31.36 / 28.77 / 31.29 / 31.53 / 28.22`

Production reality check (through LiteLLM, real prompts, Sep 2026):
median **19–24 tok/s**, TTFT 0.5–2 s. The delta vs bench is prompt
length, thinking tokens, and alias-switch reloads — all documented in
`docs/hardware.md`.

## Bench 2 — Thai quality (the protocol that matters)

Harness: `python3 scripts/bench_thai.py` (in this repo).
Bank: 60 prompts, sha256-pinned (`30 general_short / 15 report_long /
15 code_mixed`). Scorer: `thai_ratio = thai/(thai+latin)` chars,
reasoning stripped. Stats: paired bootstrap, 10,000 resamples, 95% CI.

Headline (2026-09-11, 300 completions, 0 errors):

| Arm | System | Temp | thai_ratio | Han/100 | Completion |
|---|---|---|---|---|---|
| A — **Config G** | Thai-only + Han ban + 2-shot | 1.0 | **0.7974** (0.8318 strict) | **15** | 100% |
| B — mirror prompt | mirror | 1.0 | 0.7688 | 20 | 100% |
| C — no system | none | 1.0 | 0.7616 | 35 | 100% |
| E — mirror, cool | mirror | 0.6 | 0.7955 | 23 | 100% |
| D — stock weights | mirror | 1.0 | 0.7843 | 43 | 100% |

Read: Config G beats mirror (+0.0286) and no-system (+0.0358) with CIs
excluding zero; turbo vs stock shows **no Thai regression** (CI includes
zero) while leaking fewer Han characters.

## Bench 3 — Graded head-to-head vs cloud (50 cases)

50 production-style cases across 5 categories (LINE_QA, RAGSA_SIGNAL,
CLASSIFIER, TRANSLATE, EDGE_CASES), dual-graded (local 27B grader +
Gemini cross-grader on 18/40 graded cases; Pearson 0.72, Spearman 0.75):

| Category | n | BOMLLM | Cloud | Ratio |
|---|---|---|---|---|
| LINE_QA | 10 | **8.93** | 6.33 | **1.41** |
| RAGSA_SIGNAL | 10 | **8.53** | 5.80 | **1.47** |
| CLASSIFIER | 10 | 1.00 | 1.00 | 1.00 (tie) |
| TRANSLATE | 10 | **9.63** | 8.50 | 1.13 |
| EDGE_CASES | 10 | 8.10 | **8.47** | 0.96 ⚠️ |
| **Overall** | 50 | **7.24** | 6.02 | **1.20** |

Latency (measured over WAN): BOMLLM p50 **5.2 s** / p95 19.9 s vs cloud
p50 35.1 s / p95 85.6 s. Errors: BOMLLM 2/50 (30 s cap on edge-format
cases), cloud 0/50.

**Known grader bias:** the local grader is the same model family as the
system under test; the Gemini-only subset agrees on direction (ratio
1.28 vs 1.44). Both are published so you can discount appropriately.

## Bench 4 — Chain passthrough probe (do this after ANY LiteLLM upgrade)

Verifies your sampling params actually reach Ollama:
1. Set `repeat_penalty: 8.0` on a test route → output visibly degrades
   (passthrough proven).
2. Set `presence_penalty: 1.5` with `drop_params: true` → silently
   dropped (proven; that's why the recipe puts presence_penalty at the
   Modelfile layer or accepts the drop).

## Running the harness

```bash
# Thai quality, full 60-bank, against your endpoint
python3 scripts/bench_thai.py \
  --endpoint http://127.0.0.1:4000/v1 \
  --key $BOM_KEY_SMOKE \
  --model thai-chat \
  --out benchmarks/results/$(date +%Y%m%d)

# Speed micro-bench (direct Ollama, warm)
python3 scripts/bench_thai.py --mode speed \
  --endpoint http://100.x.y.z:11434 --model turbo-fable-nvfp4
```

Contamination rules (we learned these the hard way):
- One model resident; log every reload; quarantine rows from polluted
  windows (we once quarantined 58 rows after external traffic starved
  the bench — the sidecar file is in our raw evidence).
- Fixed seed where the runtime supports it; single run per arm is a
  limitation — say so in your report.

## Contributing results

PR a row into `benchmarks/thai-quality.csv` or
`benchmarks/cost-comparison.csv` with hardware, runtime version, date,
and the exact command. Rows without a reproduce command are rejected.
