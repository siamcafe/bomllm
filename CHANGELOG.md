# Changelog

All notable changes to the BOMLLM release kit are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
versioning follows [SemVer](https://semver.org/).

## [Unreleased]

### Planned
- Curated screenshot set for README (tracked in docs/show-hn.md).
- 90-second walkthrough video link.
- Filled benchmark CSVs from the reproducible harness (`benchmarks/`).

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
