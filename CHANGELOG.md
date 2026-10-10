# Changelog

All notable changes to the BOMLLM release kit are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
versioning follows [SemVer](https://semver.org/).

## [Unreleased]

### Planned
- Curated screenshot set for README (tracked in docs/show-hn.md).
- 90-second walkthrough video link.
- Filled benchmark CSVs from the reproducible harness (`benchmarks/`).

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
