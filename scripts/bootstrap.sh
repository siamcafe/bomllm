#!/usr/bin/env bash
# ============================================================================
# BOMLLM bootstrap — brings up the VPS layer (LiteLLM + Open WebUI +
# Postgres + Qdrant + Valkey + SearXNG) with the safety defaults from
# docs/security.md. Idempotent. Safe to re-run.
#
# Usage:
#   ./scripts/bootstrap.sh            # full bring-up
#   ./scripts/bootstrap.sh --dry-run  # print what would happen, change nothing
#
# Prereqs: Linux host with docker + compose plugin, a .env file
# (cp configs/.env.example .env), and a Tailscale node joined to your mesh.
# ============================================================================
set -euo pipefail

DRY_RUN=0
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=1

say()  { printf '\033[1;34m[bomllm]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[bomllm WARN]\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m[bomllm FAIL]\033[0m %s\n' "$*" >&2; exit 1; }
run()  { if [[ $DRY_RUN -eq 1 ]]; then say "DRY-RUN: $*"; else eval "$@"; fi }

cd "$(dirname "$0")/.."
say "BOMLLM bootstrap starting (dry_run=$DRY_RUN)"

# --- 1. Prereqs --------------------------------------------------------------
command -v docker >/dev/null || die "docker not found. Install Docker first."
docker compose version >/dev/null 2>&1 || die "docker compose plugin missing."
[[ -f .env ]] || die ".env missing. Run: cp configs/.env.example .env && edit it."

# --- 2. Secret hygiene gate ---------------------------------------------------
say "Checking .env hygiene..."
[[ "$(stat -c '%a' .env 2>/dev/null || echo 000)" == "600" ]] || {
  warn ".env permissions are not 600 — fixing."
  run "chmod 600 .env"
}
if grep -qE 'CHANGE_ME' .env; then
  warn ".env still contains CHANGE_ME placeholders:"
  grep -oE '^[A-Z_]+=.*CHANGE_ME.*' .env | sed 's/=.*/= <placeholder>/' || true
  [[ $DRY_RUN -eq 1 ]] || die "Replace all CHANGE_ME values first."
fi
# Never allow a real config to be committed: confirm gitignore covers it.
grep -q '^litellm.yaml$' .gitignore || die ".gitignore missing litellm.yaml rule."

# --- 3. Real LiteLLM config ---------------------------------------------------
if [[ ! -f configs/litellm.yaml ]]; then
  say "Creating configs/litellm.yaml from example (gitignored)..."
  run "cp configs/litellm.yaml.example configs/litellm.yaml"
  warn "Edit configs/litellm.yaml: set MAC_OLLAMA_BASE_URL route + fallbacks."
fi

# --- 4. SearXNG settings volume ------------------------------------------------
mkdir -p volumes/searxng
if [[ ! -f volumes/searxng/settings.yml ]]; then
  say "Seeding minimal SearXNG settings (localhost, JSON enabled)..."
  if [[ $DRY_RUN -eq 0 ]]; then
    cat > volumes/searxng/settings.yml <<'YAML'
use_default_settings: true
server:
  secret_key: "CHANGE_ME_searxng_secret"
  bind_address: "0.0.0.0"   # container-internal; host port is 127.0.0.1 only
search:
  formats:
    - html
    - json
YAML
    warn "Set a random server.secret_key in volumes/searxng/settings.yml"
  else
    say "DRY-RUN: would write volumes/searxng/settings.yml"
  fi
fi

# --- 5. Bring up the stack ------------------------------------------------------
say "Pulling pinned images..."
run "docker compose pull"
say "Starting services..."
run "docker compose up -d"

# --- 6. Wait for health ----------------------------------------------------------
if [[ $DRY_RUN -eq 0 ]]; then
  say "Waiting for LiteLLM liveness..."
  for i in $(seq 1 30); do
    if curl -sf http://127.0.0.1:4000/health/liveliness >/dev/null 2>&1; then
      say "LiteLLM alive after ${i}0s."
      break
    fi
    [[ $i -eq 30 ]] && die "LiteLLM never became live. Check: docker compose logs litellm"
    sleep 10
  done
fi

# --- 7. Smoke gate ----------------------------------------------------------------
say "Running smoke gates..."
if [[ $DRY_RUN -eq 0 ]]; then
  code=$(curl -s -o /dev/null -w '%{http_code}' -X POST http://127.0.0.1:4000/v1/chat/completions)
  [[ "$code" == "401" ]] || die "Unauth gate broken: expected 401, got $code"
  say "Unauth gate: 401 OK"
  curl -sf "http://127.0.0.1:8888/search?q=test&format=json" -o /dev/null \
    && say "SearXNG: OK" || warn "SearXNG not answering yet (may still be booting)"
fi

cat <<'EOF'

============================================================================
BOMLLM VPS layer is up. Next steps:
  1. Front it with Cloudflare Tunnel (chat.example.com -> :3000,
     llm.example.com -> :4000). Do NOT publish the ports directly.
  2. On your Mac: build the model from configs/ollama-modelfile.example
       ollama create qwen38-chat -f configs/ollama-modelfile.example
  3. Create per-channel virtual keys (docs/channels.md):
       curl -X POST http://127.0.0.1:4000/key/generate \
         -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
         -d '{"max_budget": 2.0, "budget_duration": "1d"}'
  4. Run the full 6-probe smoke suite in docs/upgrade.md.
  5. Run the Thai bench: python3 scripts/bench_thai.py --help
============================================================================
EOF
say "Done."
