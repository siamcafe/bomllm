# Changelog

All notable changes to the BOMLLM release kit are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
versioning follows [SemVer](https://semver.org/).

## [Unreleased]

### Planned
- Curated screenshot set for README (tracked in docs/show-hn.md).
- 90-second walkthrough video link.
- Filled benchmark CSVs from the reproducible harness (`benchmarks/`).

## [12.0.0] - 2026-11-05

### Added
- Grok 4.7 full fleet audit — 8/8 machines verified (art#56080)
- Kuma monitoring v2.5.7 on AM4 + NAS
- ComfyUI fleet synchronization to v0.43.0 (7 instances)

### Changed
- Version bump v11.0.0 -> v12.0.0

### Fixed
- Chat residuals: keepalive timeout (KEEPALIVE_TIMEOUT=75) + web-search config
- LiteLLM incident 30: emergency model restore (28 models recovered)
- 8 stale RUNNING jobs cleared from hub
- Memory defrag: consolidated project memory

## [11.0.0] - 2026-11-04

### Changed
- Open WebUI upgraded v0.12.5 -> v0.13.0 (alembic e42c8f710a36, 18 functions verified, shared BOMLLM+BOMAI instance)
- Ollama servers v0.40.14 on Mac + UA (Mac CLI skew 0.40.10 documented; AM4 stays 0.40.13)
- C2 performance remediation: SSH brute-force guard persisted (systemd `c2-ssh-guard`), LiteLLM DB-load keys verified at GOD CONFIG v9.0 target, poller intervals audited against the 5-minute floor
- Hero banner regenerated for v11 (FLUX on UA ComfyUI, seed 111111, 1024x512)
- GOD CONFIG v7.0 -> v9.0 (policy ID bump; 7 locked params unchanged)
- IRON Rules 40 -> 43 (IRON 42 title format, IRON 43 structured reply)
- Fleet count corrected 9 -> 8 machines (8 tailscale peers verified)

### Added
- `BLUEPRINT.md` — GOD BLUEPRINT v5.2 full text (C2 performance Phase P: survey evidence, fixes, policies, dependency map)
- `HOWTO.md` — GOD HOW-TO v4.2 full text (§3.13-§3.17: SSH guard list maintenance, LiteLLM DB checks, poller policy, external TTFB recipe, headless QC)
- README Architecture section linking BLUEPRINT.md + HOWTO.md
- Squid tailscale-rebind systemd drop-in on C2 (auto `squid -k reconfigure` after tailscaled restart)

### Fixed
- Residual cleanup: `charming_gauss` stray container removed (v0.13.0 image kept)
- `/static/bomai/` hero banners now serve 200 (hero_banner_v11.png + hero_banner_v10.png)

### Security
- SSH brute-force subnet 102.220.160.0/22 blocked at boot via idempotent guard unit; NEVER-BLOCK ranges enforced in script

### Verified
- External TTFB from AM5: median 0.093 s / p90 0.182 s (api/version, 10 shots)
- SSH connect 5x from AM5: 0.86-1.12 s (all < 5 s); C2 load1 1.03/1.05/5.42
- Stress suite 7/8 in the 120 s window (T3 web-search passed on retry at 106.6 s)
- GOD CONFIG v9.0 7/7 locked params unchanged; functions=18; qdrant_collections=13; headless Chromium QC 0 broken images

## [10.0.0] - 2026-11-02

### Changed
- Open WebUI upgraded v0.12.4 -> v0.12.5 (18 mods intact, 14 overlays rebased, 12/12 QC PASS)
- Theme Designer Pro updated 1.8.0 -> 1.19.0
- docker-compose.yml versions updated to match production (OWUI v0.12.5, LiteLLM v1.106.4, Qdrant v1.20.0)
- Hero banner regenerated for v10 release

### Added
- Fleet cleanup: old containers removed, orphan skill IDs cleared, Docker pruned 6.4GB
- Grok plugin survey: 18 mods verified, 0 updates needed, GOD CONFIG v7.0 unchanged
- Incident #26 documented: C2 polling flood from WebSocket config, K3 fix dispatched

### Security
- OWUI v0.12.5 includes upstream security fixes
- LiteLLM pinned at v1.106.4 (v1.107.0 supply chain compromise blocked)

### Verified
- GOD CONFIG v7.0 locked params verified across 15 models (NO CHANGE)
- 40 IRON rules maintained
- 18/18 OWUI mods operational post-upgrade

## [9.0.0] - 2026-11-01

### Changed
- Version bump: v0.8.1 -> v9.0.0 (Project Closure Release)
- README: hero banner updated, SEO badges added, keywords section added
- Thai section: updated to v9.0.0

### Added
- `images/hero_banner_v9.png` — ComfyUI-generated v9 hero banner (FLUX Dev fp8)
- Git tag v9.0.0 — first release tag in repo history
- README SEO optimization: shields.io badges, keyword cloud, structured metadata
- README Keywords section for discoverability

### Verified (Project Closure)
- Fleet: 9/9 machines SSH verified, all containers healthy
- Pipeline: OWUI v0.12.4 → LiteLLM v1.106.4 → llm-smart → gpt-oss-120b — E2E PASS
- GOD CONFIG v7.0: pp=0 verified 15 models all machines
- IRON rules: 40 total (38/39/40 added for SSH safety after incident #24)
- SSH incident #24: PasswordAuthentication restored on all 9 fleet machines
- 14/14 findings from Grok deep scan resolved
- FINAL BLUEPRINT art#54961 (51KB, 15 sections) published
- FINAL HOW-TO art#54962 (32KB, 14 sections) published

### Security
- IRON 38: PasswordAuthentication config changes FORBIDDEN (owner-only)
- IRON 39: Claude cannot self-exempt IRON rules (owner command required)
- IRON 40: Working configs must not be changed for hardening without owner order
- LiteLLM v1.107.0 supply-chain compromise remains blocked — v1.106.4 pinned

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
