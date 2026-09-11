# Security audit — pre-push sanitization gate

This is the gate that runs **before every push** to the public repo, and
in full before the initial release. It exists because of real near-misses.
Treat it as a blocking CI step, not a suggestion.

## 1. The never-commit list

Nothing matching any of these may appear anywhere in the repo — code,
docs, configs, CSVs, screenshots, git history:

| Category | Examples (patterns) | Where they live in prod (and must stay) |
|---|---|---|
| API keys / tokens | `sk-…`, `Bearer …`, bot tokens, JWT, session cookies | `.env` (gitignored), n8n credential store |
| Passwords | DB passwords, WebUI `WEBUI_SECRET_KEY`, UI passwords | `.env`, Vaultwarden |
| Real public IPs | VPS IPv4, home/office WAN IP | DNS + Cloudflare only |
| Tailscale IPs | `100.64.0.0/10` addresses of any node | Tailscale ACL admin |
| Internal LAN IPs | `192.168.x.x` of real machines | router |
| Real domains/hostnames | production `*.example` real equivalents, internal hostnames | DNS |
| Webhook URLs | LINE/Telegram/n8n webhook endpoints with path secrets | n8n |
| Account numbers | MT5 login, bank, broker, customer IDs | terminal host ini, CRM |
| Personal data | real user emails, customer chat logs, LINE user IDs | WebUI DB |
| SSH keys / certs | `id_*`, `*.pem`, `*.p12` | `~/.ssh`, HSM |
| Meter exports with location metadata | smart-plug CSVs with address/GPS | local only; strip before commit |
| Model weights | `*.gguf`, `*.safetensors`, `*.mlx` blobs | Hugging Face / local disk |

## 2. File-by-file sanitization checklist (this repo)

| File | Sanitized item | Replacement |
|---|---|---|
| `docker-compose.yml` | all secrets → `${VAR}` from .env; ports → 127.0.0.1 | done at authoring |
| `configs/litellm.yaml.example` | Mac Tailscale IP → `os.environ/MAC_OLLAMA_BASE_URL`; cloud endpoint → `CHANGE_ME_CLOUD_PROVIDER.example`; master key → env ref | verify each push |
| `configs/.env.example` | every value → `CHANGE_ME*` | verify each push |
| `configs/ollama-modelfile.example` | weight source → `<author>/<repo>` placeholder | verify each push |
| `configs/sampling-recipe.yaml` | Config G verbatim prompt: review for any internal names before pasting | at L-7 |
| `docs/channels.md` | webhook URLs, bot tokens, MT5 account → `CHANGE_ME_*` | done at authoring |
| `docs/cost.md` + `benchmarks/cost-comparison.csv` | meter CSV: strip location metadata; tariff is fine, address is not | at L-7 |
| `docs/architecture.md` | real hostnames/IPs → roles (`chat.example.com`, `100.x.y.z`) | done at authoring |
| `benchmarks/thai-quality.csv` | source column references internal report names — acceptable (no secrets), keep generic | done |
| `scripts/*.sh`, `scripts/*.py` | no hardcoded endpoints, keys, or paths outside repo-relative | lint each push |
| `assets/screenshots/*` | blur keys/emails/IPs; staged demo content only; vision-verify | at M-1..M-6 |
| git history | no secret EVER committed — if one lands, rotate it AND rewrite history before the repo goes public | at L-2 |

## 3. The audit commands (run, paste output into the release PR)

```bash
# 3a. Secret-pattern sweep (working tree)
git grep -nEi '(sk-[a-z0-9]{8,}|bearer [a-z0-9._-]{8,}|api[_-]?key|secret|password|token)' \
  -- ':!*.example' ':!*.md' ':!.gitignore' || echo "CLEAN"

# 3b. IP sweep — no real IPv4 outside documentation ranges
git grep -nE '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' \
  | grep -vE '127\.0\.0\.1|0\.0\.0\.0|100\.x|100\.CHANGE|192\.168\.x' || echo "CLEAN"

# 3c. Domain sweep — only example domains
git grep -nEi 'https?://[a-z0-9.-]+' \
  | grep -vE 'example\.com|example\.org|github\.com|huggingface\.co|hf\.co|localhost|127\.0\.0\.1|keepachangelog|semver|contributor-covenant|apache\.org|postgresql\.org|gnu\.org' || echo "CLEAN"

# 3d. History sweep (pre-launch only)
git log -p --all | grep -Ei '(sk-[a-z0-9]{16,}|-----BEGIN)' && echo "HISTORY DIRTY" || echo "CLEAN"

# 3e. .gitignore coverage test — create a decoy, confirm it is ignored
echo "sk-decoy1234567890" > .env.decoy && git check-ignore .env.decoy && rm .env.decoy
```

## 4. Screenshot audit (per image, before commit)

- [ ] Opened and visually inspected (not just generated)
- [ ] No key fields visible (WebUI API-keys page, LiteLLM key list)
- [ ] No user emails in admin panels
- [ ] No Tailscale/LAN IPs in terminal shots
- [ ] No MT5 account number in any terminal screenshot
- [ ] Chat content is the staged demo set

## 5. If a secret lands anyway

1. **Rotate first, ask questions later.** A committed key is a leaked key.
2. Rewrite history (`git filter-repo`) BEFORE the repo is public; after
   public, assume permanent compromise and rotate everything in scope.
3. Post-incident note appended to this file: what pattern, which scanner
   rule should have caught it, and the new rule.

## 6. Sign-off block (release PR must include)

```
audit_date: YYYY-MM-DD
auditor: <name>
3a_secrets: CLEAN
3b_ips: CLEAN
3c_domains: CLEAN
3d_history: CLEAN
3e_gitignore: PASS
screenshots: N/N verified
notes: <any exceptions, with justification>
```
