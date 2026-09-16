# Hardware: what fits, what swaps, what it costs to run

The brain of BOMLLM is a **Mac Mini M4 Pro 48GB** (14-core CPU, 20-core
GPU, unified memory). This document is the memory map we actually run,
including the mistakes.

## The golden rule of 48 GB

**One big model resident at a time.** Not two. Ever.

Our 27B-class MLX model (nvfp4) loads to **~23 GB resident** (disk size
~18 GB; resident is bigger — KV cache and runtime buffers live in the
same unified memory). That leaves comfortable headroom:

```
48 GB total
- 23 GB  main model (27B nvfp4, ctx 32768)
- ~1 GB  bge-m3 embeddings + nomic (small, always warm)
- ~8 GB  macOS + Ollama runtime + headroom
= ~16 GB free → memory pressure green, swap 0
```

### The swap incident (why the rule exists)

We briefly kept a second 16 GB model resident with a 24 h keep-alive.
Result: memory footprint 47.7 GB, **3.8 GB swap**, TTFT ballooning to
28–60 s, swapout counters climbing by thousands per minute. Evicting the
second model (`keep_alive: 0`) stopped new swapouts within 27 minutes.

The kit encodes the fix:

- One `KEEP_ALIVE=24h` model maximum.
- LiteLLM health checks must not sweep-load unused models
  (`disable_background_health_check` on cold routes — a full `/health`
  sweep re-loaded our evicted model for ~24 h; measured, documented).
- Warmup cron pings the *one* production model, nothing else.

## Measured performance (this exact box)

From the reproducible harness (`benchmarks/README.md`), Ollama 0.33,
MLX backend, warm runs:

| Metric | GGUF Q4_K_M | MLX nvfp4 | Delta |
|---|---|---|---|
| Decode (avg of 5 prompts) | 7.85 tok/s | **30.23 tok/s** | **+285%** |
| TTFT warm | 0.288 s | **0.040 s** | −0.25 s |
| Resident RAM | 18 GB | 23 GB | +5 GB |
| Swap | 0 | 0 | — |

Production (through LiteLLM, real prompts, thinking enabled where
configured): **19–24 tok/s** median, TTFT 0.5–2 s. The gap between bench
and production is prompt length, thinking tokens, and the occasional
alias-switch reload — all explained in `benchmarks/README.md`.

### MLX alias gotcha (measured, Sep 2026)

Ollama's MLX backend does **not** fully share a runner across *different
manifests* of the same weights: switching aliases costs ~1.2 s config
reload (16 s on first switch after a fresh 32k context allocation).
Identical manifests (`ollama cp`) switch for free (~0.8 s pings).

**Design consequence:** keep one shared manifest per model and vary
behavior via route-level sampling params (LiteLLM), not via per-alias
Modelfiles. `configs/ollama-modelfile.example` follows this.

## What else fits on 48 GB

| Config | Fits? | Notes |
|---|---|---|
| 27B nvfp4 + embeddings | ✅ daily driver | our production |
| 27B nvfp4 + 7B vision (bom-read-image, vision alias → turbo) | ⚠️ tight | works, watch pressure; evict vision when idle |
| 2× 27B anything | ❌ | swap thrash, measured |
| 32B mxfp8 (~32 GB) | ❌ practical | loads, but headroom gone; swap risk on long ctx |
| 70B any quant | ❌ | not on 48 GB |

## The rest of the fleet

| Machine | Spec | Draw (measured at wall) | Role |
|---|---|---|---|
| Mac Mini M4 Pro | 48 GB | ≈8 W idle (est. wall; SoC package 0.03–0.06 W measured via powermetrics) / ~65 W load | LLM |
| i9-13900K + 2× RTX 5060 Ti | 128 GB | ≈93 W idle (GPUs 32.8 W measured via nvidia-smi + 60 W CPU/board estimated) / ≈250 W load (gpu0 render ~170 W measured) | image + voice |
| Synology DS725+ | — | ~20–35 W | n8n, monitoring, backups |
| VPS (Contabo-class) | 12 vCPU / 47 GB | n/a (rented) | proxy, UI, RAG stores |

Fill your own numbers with `scripts/cost_meter.sh`; the method is in
`docs/cost.md`.

## Buying advice (if you're speccing a box today)

- **48 GB is the sweet spot** for one 27B-class MLX model + embeddings.
  36 GB works if you keep context ≤16k. 24 GB does not.
- M4 Pro's memory bandwidth (~273 GB/s) is what makes 30 tok/s possible;
  a base M4 (120 GB/s) lands roughly half that on the same quant.
- Skip the internal SSD upgrade tax; models live fine on an external
  Thunderbolt SSD (`OLLAMA_MODELS` on the external volume).
- A used i9 + two 16 GB NVIDIA cards is *optional*. Start Mac-only;
  add media later.
