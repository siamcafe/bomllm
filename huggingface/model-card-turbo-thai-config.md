---
license: mit
tags:
  - thai
  - sampling-config
  - ollama
  - mlx
  - litellm
  - self-hosted
  - evaluation
library_name: bomllm
---

# bomllm/turbo-thai-config

**The validated Thai sampling recipe + evaluation harness for a 27B-class
Qwen fine-tune running on Apple Silicon (MLX, nvfp4).**

This is a **config-only repository — no weights**. The weights we run are
published by the original fine-tune author (DavidAU's TURBO-Fable series,
Qwen-based); pull them from the author's repo and respect the upstream
licenses (Qwen: Apache-2.0; fine-tune: author's terms).

Full platform (repo, docs, cost receipts): **https://github.com/siamcafe/bomllm**

## What's in this repo

| File | Purpose |
|---|---|
| `sampling-recipe.yaml` | The validated sampling parameters + completion floor + hard don'ts |
| `system_prompt.th.txt` | **Historical, invalidated** — the Config G system prompt (Thai-only persona + Han ban + 2 few-shots, 4,101 chars). Rolled back 2026-09-10 after a paired regression vs stock on the follow-up bench; kept for the record |
| `prompts.jsonl` | The pinned 60-prompt Thai eval bank: 60 lines, 21,248 bytes, sha256 `2c3333db5878cc5e` |
| `metrics.py` | The scorer: `thai_ratio`, Han events, reasoning stripper |
| `RESULTS.md` | Every measured run, with CIs (mirror of benchmarks/ on GitHub) |

## Quick use (Ollama)

**Modelfile pin** (locked 2026-09-12, artifact #34909): the prod Mac Ollama
Modelfiles are pinned to `temperature 0.6 · top_p 0.95 · top_k 20 ·
repeat_penalty 1.05`.

```bash
# 1. Pull weights from the original author (example tag — read their card)
ollama pull hf.co/<author>/<turbo-fable-repo>:nvfp4   # CHANGE_ME

# 2. Build with the completion-safe floor
ollama create my-thai -f Modelfile   # num_ctx 32768, from our recipe
```

## Sampling profiles (5-task matrix, locked artifact #33953)

Route-level sampling per task. These values live in the LiteLLM route layer,
not in the Modelfile:

| Profile | Task | Temp | top_p | top_k | rep_pen | presence_pen | ctx | predict | think |
|---|---|---|---|---|---|---|---|---|---|
| chat (default) | conversation | 0.6 | 0.95 | 20 | 1.05 | 0.0 | 32768 | 8192 | ON |
| code | coding | 0.6 | 0.95 | 20 | 1.0 | 0.0 | 32768 | 8192 | ON |
| deep | reasoning | 0.6 | 0.95 | 20 | 1.05 | 0.0 | 32768 | 12288 | ON |
| vision | OCR | 0.0 | 0.80 | 20 | 1.05 | 1.5 | 32768 | 2048 | OFF |
| realtime | short replies | 0.7 | 0.80 | 20 | 1.05 | 1.5 | 8192 | 256 | OFF |

## Runtime mapping

Open WebUI presets → LiteLLM routes (22 config-file routes, 0 DB deployments)
→ Ollama on the Mac (MLX, 6 model aliases, Modelfile pin above).

## Measured results (Mac Mini M4 Pro 48GB, Ollama 0.33.3 MLX)

60-prompt bank · 300 completions · paired bootstrap 10,000 × 95% CI ·
2026-09-11:

| Arm | thai_ratio | Han leaks /100 | Completion |
|---|---|---|---|
| **Config G (historical, invalidated)** | **0.7974** (0.8318 strict) | **15** | 100% |
| mirror prompt | 0.7688 | 20 | 100% |
| no system prompt | 0.7616 | 35 | 100% |
| stock weights (no fine-tune) | 0.7843 | 43 | 100% |

- Config G vs mirror: **+0.0286, CI excludes zero**.
- **Config G status: historical, invalidated** — the follow-up paired bench
  (2026-09-10) showed a regression vs stock (turbo 0.7382 / 12 Han vs stock
  0.7616 / 8) and Config G was rolled back byte-exact. The numbers above are
  retained as the record of that run.
- Fine-tune vs stock: **+0.0155, CI includes zero** — no Thai regression,
  and Han leakage drops from 43 → 15–20 per 100.
- Speed: **30.23 tok/s** MLX vs 7.85 GGUF Q4_K_M (same box, warm).

## The one thing to copy even if you copy nothing else

**Completion floor:** `num_ctx 32768`, `num_predict 8192`, and
`think: false` on bot routes. Most "Thai quality" variance we ever
measured was truncation and empty replies, not prompts. Fix the floor,
then tune.

## Evaluation protocol

1. Fixed bank, sha256-pinned. 2. Scorer strips reasoning before counting.
3. Paired bootstrap for CIs. 4. One model resident; log reloads;
quarantine polluted rows. 5. Promotion requires CI excluding zero.

Full protocol + known issues (Han leakage is ~15/100, not zero; strict
JSON + mixed-language can exceed 30 s bot timeouts):
**https://github.com/siamcafe/bomllm/blob/main/docs/thai.md**

## Citation

```bibtex
@software{bomllm2026,
  title  = {BOMLLM: a production-proven self-hosted LLM platform on Apple Silicon},
  author = {BOMLLM contributors},
  year   = {2026},
  url    = {https://github.com/siamcafe/bomllm},
  note   = {Config repo: bomllm/turbo-thai-config}
}
```
