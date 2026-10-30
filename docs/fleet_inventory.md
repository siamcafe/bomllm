# BOM LLM Fleet Inventory
Generated from live SSH survey — 2026-10-30

## Overview
| Machine | IP | SSH | Role | Status |
|---------|----|----|------|--------|
| Mac Mini M4 Pro | .254 | :22 | Primary Inference (Brain) | LIVE |
| C2 VPS | 109.123.233.171 | TS :99 | Gateway (Frontend) | LIVE |
| UA Ubuntu | .248 | :99 | Primary Inference + Staging | LIVE |
| AM4 Ubuntu | .249 | :99 | ComfyUI Primary + Hub | LIVE |
| i9 Windows | .20 | :22 | GPU Worker | LIVE |
| AM5 Windows | N/A | local | Coding Workstation (zcode) | LIVE |
| NAS DS725+ | .253 | :22 | Infra (router/monitor/backup) | LIVE |
| CAT Server | 122.155.168.7 | :99 | Web Hosting | LIVE |

## Detailed Specs per Machine

### Mac Mini M4 Pro
- OS: macOS 27.2 (Build 26B123)
- RAM: 48GB unified
- GPU: M4 Pro (integrated)
- Ollama: 0.40.10 (client; server reports 0.40.2)
- Role: Primary inference — TURBO-Fable nvfp4 MLX
- Survey: macOS 27.2 (26B123); ollama client 0.40.10 server 0.40.2; 6 models incl bomai-pro qwen3-vl:2b; disk 926Gi system vol

### C2 VPS Singapore
- OS: Debian 12 (kernel 6.1.0-54-cloud-amd64)
- RAM: 47Gi
- Docker containers: OWUI, LiteLLM, SearXNG, postgres
- Role: Frontend gateway — all client traffic
- Survey: Debian 6.1.0-54-cloud-amd64; 11 containers (live-router, litellm 1.106.4, searxng, open-webui, qdrant 1.20.0, infinity, valkey, chart-overlay, postgres 16.15, pgbouncer, beszel-agent); RAM 47Gi; disk 394G 22% used

### UA Ubuntu
- OS: Ubuntu (kernel 7.0.0-38-generic)
- RAM: 123Gi
- GPU: RTX 5080 16GB + RTX 5060 Ti 16GB
- Ollama: 0.40.13
- Docker: LiteLLM staging, bomai-safe, qdrant
- Role: Primary inference + staging proxy
- Survey: Ubuntu kernel 7.0.0-38-generic; ollama 0.40.13; 12 containers (litellm + litellm-staging 1.106.4, librechat stack, comfyui x2, llm-smart, netdata, beszel); RTX 5080 + RTX 5060 Ti; RAM 123Gi; disk / 913G 37%, /data 3.6T 46%

### AM4 Ubuntu
- OS: Ubuntu (kernel 7.0.0-38-generic)
- RAM: 121Gi
- GPU: 2x RTX 5060 Ti 16GB
- Ollama: 0.40.13 (API /api/version on :11434; CLI not in PATH)
- Docker: ComfyUI x2, hub services
- Role: ComfyUI primary worker + task hub
- Survey: Ubuntu kernel 7.0.0-38-generic; ollama API 0.40.13 on :11434 (CLI not in PATH); 29+ containers (comfy-gpu0/gpu1, litellm-gw, agent-hub-v2, whisper, chatwoot, matomo, listmonk, bookstack, code-server, uptime-kuma, beszel); 2x RTX 5060 Ti; RAM 121Gi; disk / 935G 32%, /data 1.8T 40%

### i9 Windows
- OS: Windows 10 Pro
- RAM: 128GB
- GPU: 2x RTX 5060 Ti (16GB each)
- GPU0 :8188: ComfyUI (FLUX Dev fp8)
- GPU1 :8190: PuLID sandbox (⛔ UNTOUCHABLE)
- Role: GPU worker — image gen, TTS, music, EA
- Survey: Windows 10 Pro; 128GB RAM (130836 MB); 2x RTX 5060 Ti 16GB (11.9GB/10.5GB in use at survey time); ComfyUI GPU0 :8188 alive (verified from AM5, generated hero banner)

### AM5 Windows
- Role: Coding workstation (zcode GLM-5.3)
- GPU: RTX 5060 Ti (16GB)
- ComfyUI: 3rd worker

### NAS DS725+
- Docker: comfy-router, monitoring, n8n (⛔ OWNER HOLD)
- Role: Infrastructure — routing, monitoring, backups
- Survey: Synology DS725+ (DSM kernel 5.10.55+); /volume1 5.3T 1.6T used 30%

### CAT Server
- OS: Ubuntu 20.04.6 LTS (kernel 5.4.0-244)
- Role: Web hosting — DirectAdmin, 5 WordPress sites
- ⛔ NEVER restart httpd/nginx/DA
- Survey: Ubuntu 20.04.6 LTS; kernel 5.4.0-244; RAM 62Gi; disk 439G 9% used; Apache/2.4.66

## GPU Assignment
| Machine | GPU | VRAM | Primary Use |
|---------|-----|------|-------------|
| i9 | RTX 5060 Ti x2 | 16GB x2 | ComfyUI GPU0 + PuLID GPU1 |
| UA | RTX 5080 + RTX 5060 Ti | 16GB x2 | gpt-oss-120b + inference |
| AM4 | 2x RTX 5060 Ti | 16GB x2 | ComfyUI x2 + hub |
| AM5 | RTX 5060 Ti | 16GB | zcode + ComfyUI 3rd |

## Network Topology
- Tailscale mesh VPN for inter-machine
- Public HTTPS via Cloudflare Tunnel (C2)
- TB5 direct link: Mac <-> UA (10.99.0.0/30, ~25% faster than LAN)
- All API endpoints key-gated

## Service Map
| Service | Machine | Port | Purpose |
|---------|---------|------|---------|
| OWUI | C2 | :3000 | Chat frontend |
| LiteLLM | C2 | :4000 | Primary proxy |
| LiteLLM | UA | :4100 | Staging proxy |
| Ollama | Mac | :11434 | MLX inference |
| Ollama | UA | :11434 | GGUF inference |
| Ollama | AM4 | :11434 | GGUF inference |
| gpt-oss-120b | UA | :8380 | Vision (LIVE PROD ⛔) |
| ComfyUI | i9 GPU0 | :8188 | Image gen |
| ComfyUI | i9 GPU1 | :8190 | PuLID sandbox (⛔) |
| comfy-router | NAS->AM4 | :8788 | Worker balancer |
| SearXNG | C2 | :8888 | Web search |
| Hub | AM4 | :8192 | Task hub |
