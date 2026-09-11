# Security Policy

## Reporting a vulnerability

**Do not open a public issue for security reports.**

Email: security@bomllm.example (replace with the live address at launch —
see docs/show-hn.md checklist item L-3)

Include:
- Affected component and version/commit
- Reproduction steps or proof of concept
- Impact assessment (what can an attacker do?)

We aim to acknowledge within 72 hours and to ship a fix or mitigation
within 14 days for high-severity issues.

## Scope

BOMLLM is an integration kit. Security issues in **upstream components**
(Open WebUI, LiteLLM, Ollama, SearXNG, ComfyUI, n8n, Qdrant, etc.) should
be reported to those projects directly. We track and pin upstream fixes in
`docs/upgrade.md`.

In scope for this repo:
- The bootstrap and helper scripts in `scripts/`
- The example configs in `configs/` (e.g. an example that encourages an
  unsafe default is a bug we want to hear about)
- Documentation that recommends an insecure practice

## Our own production security posture

The reference deployment follows these rules, and the shipped configs
encode them:

1. Everything binds to localhost or the Tailscale interface by default.
2. Public exposure goes through Cloudflare Tunnel with key-gated APIs.
3. No credential is ever committed, logged, or printed — see
   `docs/security.md` for the full threat model and
   `docs/security-audit.md` for the sanitization regime applied to this
   repository before every push.
4. The MT5/trading integration is strictly read-only.

## Supported versions

| Version | Supported |
| ------- | --------- |
| 1.0.x   | Yes       |
| < 1.0   | No        |
