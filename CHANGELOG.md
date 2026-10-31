# Changelog

All notable changes to the BOMLLM release kit are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
versioning follows [SemVer](https://semver.org/).

## [Unreleased]

### Planned
- Curated screenshot set for README (tracked in docs/show-hn.md).
- 90-second walkthrough video link.
- Filled benchmark CSVs from the reproducible harness (`benchmarks/`).

## [0.8.1] - 2026-10-31

### Added
- GOD CONFIG v7.0 documentation (`GOD_CONFIG.md` — locked params, 20-model compliance table, protected deviations)
- QC system on AM4 (OCR/Whisper/ASR/Gateway) — 10/10 PASS
- Fleet-wide Grok deep survey (30 findings, 7/7 machines)
- K3 LFM3 lightweight model blueprint

### Fixed
- F001 CRIT: UA :4100 litellm-staging recreated (NetworkSettings corrupt)
- F003: i9 ComfyUI GPU1 NSSM re-pointed to start_gpu1.bat
- F006: Mac firewall enabled with pf anchor for Ollama LAN
- F007: AM4 QC 4/4 models presence_penalty pinned to 0
- F008: UA bomai-gateway disabled (upstream incompatible)
- F009: AM5 Ollama upgraded 0.40.5 → 0.40.13
- F010: NAS Kuma port corrected :32769 → :3001
- llm-smart rebind 127.0.0.1 → 0.0.0.0
- Mac qwen38-uni restored from backup
- AM5 OWUI port conflict 8080 → 3000
- AM4 Whisper max_new_tokens + ASR NeMo extraction bugs

### Verified
- E2E production chain: 13/13 PASS
- Grok street test: 30/35 PASS (5 behavioral, not system)
- GOD CONFIG pp=0 verified 15 models all machines
- LiteLLM v1.106.4 pinned fleet-wide (v1.107.0 absent)

## [0.8.0] - 2026-10-30

### Changed
- GOD CONFIG: v5.5 -> v7.0 (art#54324) — 9 parameter corrections, presence_penalty=0 enforced fleet-wide
- Ollama: UA/AM4 upgraded to 0.40.13 (Mac stays 0.40.10 for production stability)
- Fleet role assignment updated per Mega Tuning Report
- Fleet documentation expanded: 5 -> 8 machines (added UA, AM4, CAT)

### Added
- `configs/config_g_v7.0.yaml` — locked Config G reference for TURBO-Fable under GOD CONFIG v7.0
- `images/hero_banner_v8.png` — ComfyUI-generated v0.8 hero banner (FLUX Dev fp8)
- `docs/fleet_inventory.md` — full fleet specs from live SSH survey
- `bomai-safe` model deployed on UA and AM4

### Fixed
- OWUI valve/TTS config reloaded from DB (C2 container restart)
- UA lfm3-audio:latest GOD v7.0 compliance (was temperature=0, 6 params missing)
- 9 GOD CONFIG parameter corrections across 5 model configurations
- 10 orphan model paths + 1 stale Ollama tag removed (UA/AM4/Mac)
- 9 dead LiteLLM routes removed + 3 staged for UA :4100
- 15 unused Docker images removed (19.33 GiB)
- i9 llamacpp-gpu1 auto-start: Manual -> Automatic
- NAS nas-hub auto-start: no -> unless-stopped

### Metrics
- Net disk reclaimed: **210.43 GiB** across fleet
- Docker cleanup: 19.33 GiB images + 3.60 GiB build cache
- Fleet GOD compliance: all models 7/7 locked params (after lfm3-audio fix)

## [7.0.0] - 2026-10-27

### Changed
- Production sampling config: GOD CONFIG v5.4 -> v5.5 (art#53479) — 9 changes: Ollama 0.40.10, router truth table, rollback containers, overlay base images
- Open WebUI: v0.11.3 -> v0.12.4 (C2, Python 3.12.15, Pillow 13) — upgraded via art#52989
- LiteLLM proxy: v1.100 -> v1.106.3-pil2 (security patched, 32 routes) — v1.107.0 supply-chain compromise avoided
- Ollama: 0.40.1 -> 0.40.10 (Mac MLX, LaunchDaemon pattern with versioned-dir)
- Qdrant: 1.19 -> 1.20.0 (C2)
- Architecture diagram: all version numbers updated to match production
- Fleet table: updated to reflect current versions
- Thai section: v4 -> v7

### Added
- `configs/config_g_v5.5.yaml` — locked Config G reference for TURBO-Fable under GOD CONFIG v5.5
- `images/hero_banner_v7.png` — ComfyUI-generated v7 hero banner (FLUX Dev fp8)
- `images/benchmark_v7_stats.png` — v7 benchmark stat card
- Git tag v7.0.0 — first release tag in repo history

### Fixed
- LiteLLM think=false routing: 21 routes patched, qwen38-think exempted (art#53465->53480)
- SWAP optimization: UA 2114->320GB, AM4 837->320GB, ~2.3TB NVMe reclaimed (art#53183)
- Fleet garbage cleanup: 33.2GB freed across 6 machines (art#53052)
- Mac CoreSimulator cleanup: 261->6 processes, 6695MB RSS freed, swap 1110->254MB
- C2 litellm-gw OOM: 640m->1280m (art#53483)
- QUEUE_LIMIT drift fixed: disk=runtime=8

### Security
- LiteLLM v1.107.0 supply-chain compromise identified and blocked — pinned to v1.106.4 safe target
- pil2 transformation.py integrity verified (SHA f2b63f8206035add6cdcafa356497f8b8916eb27b1459f88a2d0ea6c6c7b9ca3)

## [6.0.0] - 2026-10-25

### Changed
- Production model: Fable 732 -> TURBO-Fable (DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic, nvfp4 MLX, digest 7fc322da) under tag `qwen38-uni`
- Bench: Thai gate 20/20=1.00, Han leak 0/5, street test 3/3 PASS, speed 18.5 tok/s avg (art#52920)
- README updated to v6 with TURBO-Fable spec table and benchmark results
- GOD CONFIG: v5.3 -> v5.4 (art#52999)

### Added
- `benchmarks/turbo_fable_bench.yaml` — full TURBO-Fable benchmark data
- `configs/config_g_v5.4.yaml` — locked Config G for TURBO-Fable
- `huggingface/model-card-turbo-fable.md` — HF model card template
- `images/bomllm_promo_00001_.png` through `00003_.png` — ComfyUI promo art

## [5.0.0] - 2026-10-10

### Changed
- Production model: Fable 709-L -> Fable 732 (DavidAU Qwen3.8-27B
  Fable-735-882, nvfp4 MLX, ollama digest `5bd9e2dc6f01`); tag `qwen38-uni`
  unchanged. README hero banner and measured speeds updated.

### Added
- `benchmarks/v5_732/bench_v5_results.json` - 40-prompt bench: direct Ollama
  Han 0/40 (Thai 20.78 tok/s, English 21.52; rerun 21.87 vs gate 22,
  long-generation num_predict 4096 methodology); LiteLLM path 1/40 response
  leaked 6 Han chars on the Confucius prompt (deterministic, direct path
  clean; GPT-6.1 persona upgrade recommended).
- `configs/config_g_v5.yaml` - locked Config G reference for Fable 732.
- `images/benchmark_732.png`, `images/benchmark_732_han_detail.png`,
  `images/hero_banner_v5.png` (ComfyUI FLUX Dev fp8 + data overlay).

## [1.0.0] - 2026-10-07

First public release, timed with the Show HN launch.

### Added
- Full reference architecture: Mac Mini M4 Pro (Ollama MLX) + Linux VPS
  (LiteLLM, Open WebUI, Postgres, Qdrant, Valkey, SearXNG) + Windows GPU
  workstation (ComfyUI, TTS) + NAS (n8n, monitoring), meshed with
  Tailscale and fronted by Cloudflare Tunnel.
- `scripts/bootstrap.sh` — one-command bring-up for the VPS layer.
- `configs/` — sanitized, production-derived examples:
  LiteLLM proxy config, Ollama Modelfile, validated Thai sampling recipe,
  and `.env.example`.
- `benchmarks/` — reproducible Thai-quality and cost harness with the
  production numbers we measured (see `benchmarks/README.md`).
- `docs/` — architecture, hardware, cost methodology, Thai language
  playbook, channel wiring, security model, upgrade runbook.
- Hugging Face config repo card (`huggingface/`): sampling recipe and
  Thai evaluation protocol. No weights are redistributed.

### Production provenance
- Stack in continuous production since 2026-08 serving 4 fully-BOM
  channels + a hybrid LINE bot (web chat, n8n content pipelines,
  live-stream Q/A overlay, chart-vision overlay, LINE bot with cloud
  fallback disclosed).
- Cloud LLM spend replaced: ~$50/day → ~$0.54/day electricity
  (methodology in `docs/cost.md`).
