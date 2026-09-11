# Security model

BOMLLM's security posture in one paragraph: **everything binds to
localhost or the Tailscale interface; the only public surface is
Cloudflare Tunnel; every API is key-gated; every key has a budget; no
secret is ever committed, logged, or printed.** This document is the
long version, including the threat model and the mistakes we made.

## Bind discipline (the actual `ss -tlnp` policy)

| Service | Binds | Why |
|---|---|---|
| LiteLLM :4000 | 127.0.0.1 (+ Tailscale IP via socat for mesh probes) | public path is the tunnel only |
| Open WebUI :3000 | 127.0.0.1 | fronted by tunnel |
| SearXNG :8888 | 127.0.0.1 | internal-only; AGPL unmodified |
| Qdrant :6333 | 127.0.0.1 | no public vectors |
| Postgres / Valkey | container network only | no host ports at all |
| Ollama :11434 (Mac) | Tailscale IP only | mesh-only, pf firewall on |
| Netdata :19999 | 127.0.0.1 | we *found* it on 0.0.0.0 once — fixed, and it's in our audit checklist now |
| SSH | non-standard port, key-only, ufw DROP default | |

The compose file in this repo encodes the localhost bindings. If you
change a bind, you own the exposure.

## Public surface

Exactly two hostnames, both behind Cloudflare:

- `chat.example.com` → Open WebUI (user auth; consider Cloudflare Access
  in front for extra paranoia — we flag this as optional hardening)
- `llm.example.com` → LiteLLM (401 without a key; verified by
  unauthenticated probe in every audit round)

Verified properties (re-checked in every survey):

- `POST /v1/chat/completions` without a key → `401 auth_error`
- WebUI `/api/models` without session → `401`
- No `docker.sock` mounted into any container
- ufw: default INPUT DROP, allow SSH port + Tailscale only

## Key hygiene

1. **Master key** (`LITELLM_MASTER_KEY`): exists only in `.env` on the
   VPS. Never in git, never in chat, never in screenshots.
2. **Virtual keys** per channel (see `docs/channels.md`): budget-capped,
   model-scoped, rotatable without touching the master.
3. **Storage:** `.env` files with `chmod 600`, gitignored (the
   `.gitignore` in this repo is part of the security model — read it).
4. **In reports/logs:** the house rule is *"key loaded, length=N"* —
   you may state that a key exists and its length, never its value.
5. **n8n:** secrets only via n8n credentials or container env. Hardcoded
   literals in workflow nodes are forbidden; a weekly scanner checks.

## Threat model

| Threat | Mitigation |
|---|---|
| API key leak (git, screenshot, log) | gitignore regime + pre-push audit (`docs/security-audit.md`) + per-key budgets cap the blast radius |
| Internet scan hits LiteLLM | tunnel-only exposure; 401 without key; no model list without auth |
| VPS compromise | no models/data on VPS beyond DBs; Mac is mesh-only; DB dumps are off-box daily |
| Prompt injection via web search | SearXNG results are context, not instructions; system prompt pins behavior; bots have output post-processing |
| Rogue spend | per-key daily budgets + global `max_budget`; spend alerts |
| Supply chain (images) | pinned tags, no `latest`; upgrade runbook in `docs/upgrade.md` |
| Malicious insider (invited user) | invite-only, role-scoped models, per-user spend logs |

## Data residency

Prompts and completions never leave your hardware except when Tier-3
cloud fallback fires (and fallback routes are explicit in the LiteLLM
config — delete them for a hard-local deployment). RAG documents live in
Qdrant on the VPS. Backups: nightly Postgres dumps, off-box to the NAS,
retention 14 days.

## The MT5 boundary

The trading-terminal integration is **read-only by construction**
(zero order-send calls in the EA source, auditable). It holds one
budget-capped key. If you extend BOMLLM toward any action-taking
integration, that is your risk to model — this kit deliberately does not.

## Audit regime

Before every push to the public repo, run the checklist in
`docs/security-audit.md`. It exists because of real near-misses; treat
it as a gate, not a suggestion.
