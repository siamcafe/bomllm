# HOW-TO v5.0 — BOMLLM System Operations

project: bom-llm
recommendation: INSPECT
step: fix_c2_perf_survey_fix_release
version: "5.0"
previous: "4.2"
date: "2026-11-14"
configuration: MEGA GOD CONFIG v12.0 (7/7 locked params untouched; keep_alive "24h")
architecture: GOD BLUEPRINT v8.0

This guide is for routine operations and bounded incident handling. It does not authorize a change outside the owner's live-chat scope. Never print credentials; load them only into the process that needs them.

v5.0 updates (from the mega repo update v18, spec art#60851):
1. **NEW §0: Install + Deploy** — bootstrap, docker compose, Ollama pull commands for BOM AI v2.1.8 tiers, OWUI v0.13.3.
2. Pinned versions refreshed: LiteLLM 1.108.8 LTS, OWUI v0.13.3, ComfyUI v0.45.0, Ollama 0.40.16 (unifying).
3. keep_alive policy recorded: "24h" on every route, NEVER "-1" (incident #33).

v4.2 updates (from the C2 performance survey/fix/release task, spec art#55876, blueprint v5.2):
1. **NEW §3.13: SSH guard list maintenance** — how to add/remove blocked CIDRs safely, NEVER-BLOCK rules.
2. **NEW §3.14: LiteLLM DB-load checks** — the S5-S7 commands and the gated prune procedure.
3. **NEW §3.15: Poller interval policy** — 5-minute floor for :3000/:4000/docker-exec probing, 15-minute opshub drop-in.
4. **NEW §3.16: External TTFB measurement recipe** — AM5 10-shot median only; hairpin/localhost numbers are never public-TTFB evidence.
5. **NEW §3.17: Headless screenshot QC method** — Playwright Chromium as the evidence gate (panel screenshots do not count).
6. Squid tailscale-rebind is now automated by a tailscaled.service drop-in (squid-rebind-v52.conf); manual `squid -k reconfigure` remains the fix after a tailscaled restart.

v4.1 updates (from the C2 SSH-slowness task):
1. **NEW §3.10: SSH slow-connect triage on C2** — brute-force churn vs box contention, with the exact measurement commands.
2. **NEW §3.11: Tailscale on-demand on C2** — start/stop scripts and the dependency warning list. tailscaled is LOAD-BEARING on C2 (not optional).
3. **NEW §3.12: SSH brute-force subnet block** — the reversible iptables rule and how to persist/remove it.
4. Squid audit result: both C2 and Contabo1 run AUTHENTICATED CCTV proxies — KEEP, do not disable.
5. "query-engine" high RSS/CPU is LiteLLM's Prisma engine — a component, not an orphan. Never kill it standalone.

SHARED INSTANCE: this OWUI serves BOTH BOMLLM and BOMAI (own banner, custom buttons, branding). Every UI check below means BOTH surfaces.

## 0. Install + Deploy (NEW v5.0)

### 0.1 Fresh install (gateway host)

```bash
git clone https://github.com/siamcafe/bomllm.git
cd bomllm
./scripts/bootstrap.sh          # base checks + secrets prompt (never commit them)
docker compose up -d            # OWUI v0.13.3 + LiteLLM 1.108.8 LTS + Postgres 16 + Qdrant 1.20.0 + Valkey 9.1.3
curl -fsS http://127.0.0.1:3000/api/version    # expect 0.13.3
curl -fsS http://127.0.0.1:4000/health/liveliness
```

### 0.2 Ollama models (BOM AI v2.1.8 tiers — Pro is GGUF Q4_K_M on all platforms)

```bash
# Light tier (4B, ~3 GB)
ollama pull siamcafe/bom-ai:light-v2.1.8

# Pro tier (709-L 27B DavidAU, GGUF Q4_K_M: text 16.5 GB + mmproj 518 MB)
ollama pull siamcafe/bom-ai:pro-v2.1.8

# keep models warm on every route (incident #33: "-1" caused the regression)
# LiteLLM route config: keep_alive: "24h"   <- NEVER -1
```

### 0.3 Deploy checklist

1. `docker compose ps` — all Up (healthy)
2. OWUI `/api/version` = 0.13.3; LiteLLM `/health/liveliness` + `/health/readiness` = 200
3. GOD CONFIG locked params 7/7 (§1.2); keep_alive "24h" on every route
4. Web search default OFF (3 layers: model preset, admin default_interface, builtinTools.web_search=false)
5. Gateway rc3 runtime deployed (bom_runtime.py sha cd1d5f14...)

## 1. Daily operations

### 1.1 Quick health sweep

```bash
# C2 containers, load and public application health
ssh -p 99 bom@100.83.20.100
uptime
docker ps --format '{{.Names}}|{{.Image}}|{{.Status}}'
curl -fsS --max-time 20 http://127.0.0.1:3000/api/version      # expect 0.13.3
curl -fsS --max-time 20 http://127.0.0.1:4000/health/liveliness

# Alembic version must be e42c8f710a36 (v0.13.0 live)
docker exec bomllm-postgres-1 psql -U openwebui -d openwebui -At -c "SELECT version_num FROM alembic_version;"

# Mac primary model (LAN IP — Tailscale path is DERP-sin)
ssh bom@192.168.1.254 "ollama ps"

# UA: read-only; do not touch EA burn or gpt-oss-120b
ssh -p 99 bom@100.82.173.22 "ollama ps; curl -fsS http://127.0.0.1:11466/health"

# AM4: read-only health; do not alter FX28 or live hub
ssh -p 99 bom@192.168.1.249 "curl -fsS http://192.168.1.249:8192/health"

# i9 ComfyUI: HTTP API only, never restart/kill as a check
curl -fsS http://192.168.1.20:8188/system_stats >/dev/null

# NAS and Contabo1 monitoring
curl -fsS http://192.168.1.253:5678/healthz
ssh -p 99 root@109.205.176.7 'curl -fsS http://127.0.0.1:5678/healthz'
```

A container listed as running is not sufficient. Require application HTTP evidence and inspect startup logs when health is starting or unhealthy. Never restart NAS n8n, Contabo n8n, CAT services, UA staging, `llm-smart`, or ComfyUI as a health probe.

### 1.2 Verify locked model parameters (GOD CONFIG 7/7)

```bash
ssh bom@192.168.1.254 "ollama show qwen38-uni --modelfile | grep -E 'temperature|top_p|top_k|repeat_penalty|presence_penalty|num_predict|num_ctx'"
ssh -p 99 bom@100.82.173.22 "ollama show bomai-safe --modelfile | grep -E 'temperature|top_p|top_k|repeat_penalty|presence_penalty|num_predict|num_ctx'"
ssh -p 99 bom@100.83.20.100 "docker exec bomllm-postgres-1 psql -U openwebui -d openwebui -At -c \"SELECT params::text FROM model WHERE id='bom-thai-chat';\""
```
Expected: temperature 0.6, top_p 0.95, top_k 20, repeat_penalty 1.0, presence_penalty 0.0, num_predict 4096, num_ctx 8192.

## 3. Incident recipes

### 3.8 C2 per-process CPU readings are unreliable (Known-Solved KN1)
On the Contabo KVM, interrupt/softirq time is billed to whichever task is running (CONFIG_IRQ_TIME_ACCOUNTING not set; host reports no steal). tailscaled's 18 hot threads collect the largest share (~30-55% ps CPU with only ~4.4% real utime). Diagnose with the utime/stime split and Go pprof before blaming any daemon. Same binary on bare metal = 0.1%.
v5.2 addendum: the 30-second utime/stime delta sampler is the standard truth source (blueprint v5.2 P.2 S2); ps/top %CPU on C2 is never evidence.

### 3.9 Tailscale DERP vs direct path checks
```bash
tailscale status          # "relay sin" = DERP relay; "direct x.x.x.x:port" = direct
tailscale debug prefs | grep -E "CorpDNS|AdvertiseRoutes|ExitNode"
```

### 3.10 SSH slow-connect triage on C2
Symptom: SSH takes 30s-2min to connect. Check IN THIS ORDER:
```bash
# 1. Is it config? (should be: usedns no, gssapiauthentication no)
ssh -p 99 bom@109.123.233.171 "sudo sshd -T | grep -E 'usedns|gssapi|maxstartups'"

# 2. Is it DNS? (should be <100ms)
ssh -p 99 bom@109.123.233.171 "time getent hosts 109.123.233.171"

# 3. Is it brute-force churn? (attackers preauth-flooding port 99)
ssh -p 99 bom@109.123.233.171 "sudo journalctl -u ssh --since '-1h' --no-pager | grep -cE 'Invalid user|Failed password'"
ssh -p 99 bom@109.123.233.171 "sudo journalctl -u ssh --since '-1h' --no-pager | grep -oE 'from [0-9.]+' | sort | uniq -c | sort -rn | head"

# 4. Is it box contention? (runqueue > vCPU count = connects stall)
ssh -p 99 bom@109.123.233.171 "vmstat 1 4"   # watch column r vs nproc=12

# 5. Is MaxStartups dropping? (>10 unauthenticated conns = random drop/delay)
ssh -p 99 bom@109.123.233.171 "sudo ss -tn state syn-recv; sudo ss -tn | grep -c ':99 '"
```
Findings map:
- `usedns yes` or `gssapiauthentication yes` -> owner must edit sshd_config (agents FORBIDDEN, IRON 37/38).
- Attack /24 spamming -> apply §3.12/§3.13 subnet block.
- r > 12 sustained -> reduce box load (see top offenders: litellm<->postgres loop, OWUI single worker, docker exec pollers).
- Journal shows `Accepted publickey` and `session opened` in the SAME SECOND for your login -> sshd itself is fast; the delay is pre-auth (network/KEX scheduling), i.e. items 3-5, NOT PAM, NOT logind.
- v5.2 note: failed-auth churn can also come from the OWNER's own ISP range (180.183.0.0/16 = NEVER-BLOCK; 2,189 failed lines/24h observed 2026-11-04). NEVER block it; report to owner instead.

### 3.11 Tailscale on-demand on C2 — LOAD-BEARING, read before stopping
Owner policy: tailscale on-demand, not 24/7. **On C2 this is conditional** because these production paths ride Tailscale 100.x (C2 has no LAN route to 192.168.1.0/24):
- `hub.siam2r.com`   -> cloudflared -> 100.111.221.102:8191 (NAS relay -> AM4 hub)
- `docs.siam2r.com`  -> cloudflared -> 100.111.221.102:8060
- `llm.siam2r.com` overlay + worker-ws -> cloudflared -> 100.80.16.53:3100 (AM4)
- qdrant relay :6333 -> socat -> 100.80.16.53:6333
- rag-lb relay :7998 -> socat -> 100.80.16.53:7997
- LiteLLM -> Mac primary models: 15x api_base http://100.118.133.38:11434 in `/home/bom/bomllm/litellm/config.yaml`

Stopping tailscaled on C2 therefore = public outage of hub/docs + chat model routing. Start/stop scripts (installed 2026-11-04):
```bash
sudo tailscale-stop.sh    # tailscale down + systemctl stop tailscaled (OUTAGE while down)
sudo tailscale-start.sh   # systemctl start + tailscale up + status
```
tailscaled remains `enabled` at boot deliberately: an unintended reboot without tailscale = silent public outage. If the owner accepts that risk, `sudo systemctl disable tailscaled` completes full on-demand mode.
Other fleet machines (UA/AM4/NAS/Mac/i9/AM5) tailscaled = 0.0-0.3% — no action needed there.

SQUID INTERPLAY: Squid's tailnet listener `100.83.20.100:18080` is bound only if tailscale0 exists when squid (re)reads config. Any tailscaled restart silently drops that listener while the public `109.123.233.171:18080` stays up. Since v5.2 a systemd drop-in (`/etc/systemd/system/tailscaled.service.d/squid-rebind-v52.conf`, `ExecStartPost=/bin/sh -c 'sleep 8; /usr/sbin/squid -k reconfigure || true'`) re-binds it automatically ~8 s after tailscaled starts. Manual fix if ever needed: `sudo squid -k reconfigure`, then verify `ss -tlnp | grep 18080` (expect BOTH IPs).

RELAY PROBING: `qdrant-relay-am4` / `rag-lb-relay-am4` are socat containers on the `bomllm_default` bridge with NO published host port. `curl localhost:6333` on the host ALWAYS fails by design — probe the real consumer path instead: `docker exec litellm python3 -c "import urllib.request,json;print(len(json.load(urllib.request.urlopen('http://qdrant-relay-am4:6333/collections'))['result']['collections']))"` (expect 13).

### 3.12 SSH brute-force subnet block
PERSISTED since v5.2: the block lives in `/etc/c2-ssh-guard.list` and is applied at boot by `c2-ssh-guard.service` (idempotent `iptables -C || -I INPUT 1 -s <cidr> -p tcp --dport 99 -j DROP`). The K3-era live-only rule is superseded.
- Verify the guard: `systemctl is-enabled c2-ssh-guard; systemctl is-active c2-ssh-guard; sudo iptables -S INPUT | grep -c 'dport 99 -j DROP'` (must equal non-comment lines in the list file).
- Maintenance (add/remove CIDRs): see §3.13.
- fail2ban `sshd` jail remains active for all other sources (per-IP bans complement the per-subnet guard).

### 3.13 SSH guard list maintenance (NEW v4.2)
File: `/etc/c2-ssh-guard.list` (one CIDR per line, `#` comments allowed, cap 10 entries).
```bash
# ADD a subnet — ONLY after ALL THREE checks pass:
#   (a) >=100 'Invalid user|Failed password' lines from that /24 in 24h:
sudo journalctl -u ssh --since '-24h' --no-pager | grep 'Invalid user\|Failed password' | grep -oE 'from [0-9]+\.[0-9]+\.[0-9]+\.' | sort | uniq -c | sort -rn
#   (b) ZERO 'Accepted' logins from the range in the FULL journal:
sudo journalctl -u ssh --no-pager | grep Accepted | grep -cE '102\.220\.(160|161|162|163)\.'   # adapt regex; must be 0
#   (c) no overlap with NEVER-BLOCK (below).
echo '203.0.113.0/24' | sudo tee -a /etc/c2-ssh-guard.list
sudo systemctl start c2-ssh-guard     # script is idempotent; refuses NEVER-BLOCK ranges
# verify:
sudo iptables -S INPUT | grep -c 'dport 99 -j DROP'   # must equal list line count
# REMOVE a subnet:
sudo sed -i '\#203.0.113.0/24#d' /etc/c2-ssh-guard.list
sudo iptables -D INPUT -s 203.0.113.0/24 -p tcp --dport 99 -j DROP
```
NEVER-BLOCK (the guard script refuses these): 180.183.0.0/16 (owner ISP), 122.155.168.7 (CAT), 109.205.176.7 (Contabo1), 171.6.136.143 (am4_brain), 100.64.0.0/10 (tailnet), 192.168.0.0/16 (LAN).
NEVER: write iptables rules into DOCKER chains; install iptables-persistent (saves Docker chains -> reboot conflict); edit sshd_config (IRON 37/38).

### 3.14 LiteLLM DB-load checks (NEW v4.2)
Target config = GOD CONFIG v9.0 `machines.c2.litellm.general_settings` (proxy_batch_write_at 60, disable_error_logs true, maximum_spend_logs_retention_period 30d, background_health_checks false, database_disable_prepared_statements true). Measured 2026-11-04: tps=0, SpendLogs 153k rows/773 MB — the suspected LiteLLM<->Postgres write loop is NOT active in calm windows; re-check when C2 load is high and litellm real-user CPU (utime/stime, §3.8) exceeds ~60%.
```bash
CFG=/home/bom/bomllm/litellm/config.yaml
sudo awk '/^general_settings:/{f=1} f&&/^[a-z_]+:/&&!/^general_settings:/{f=0} f' $CFG
# who is on the DB right now (3x, 10 s apart):
for i in 1 2 3; do docker exec bomllm-postgres-1 psql -U litellm -d litellm -At -c "SELECT pid,state,extract(epoch from now()-query_start)::int,left(regexp_replace(query,E'\\s+',' ','g'),120) FROM pg_stat_activity WHERE datname='litellm' AND state<>'idle';"; sleep 10; done
# table sizes + TPS:
docker exec bomllm-postgres-1 psql -U litellm -d litellm -At -c "SELECT relname,n_live_tup,pg_size_pretty(pg_total_relation_size(relid)) FROM pg_stat_user_tables ORDER BY pg_total_relation_size(relid) DESC LIMIT 8;"
T1=$(docker exec bomllm-postgres-1 psql -U litellm -d litellm -At -c "SELECT xact_commit+xact_rollback FROM pg_stat_database WHERE datname='litellm';"); sleep 60; \
T2=$(docker exec bomllm-postgres-1 psql -U litellm -d litellm -At -c "SELECT xact_commit+xact_rollback FROM pg_stat_database WHERE datname='litellm';"); echo "tps=$(( (T2-T1)/60 ))"
```
PRUNE (gated): only when `LiteLLM_SpendLogs` > 1,000,000 rows OR > 2 GB (ErrorLogs > 100k); ALWAYS `docker exec bomllm-postgres-1 pg_dump -U litellm -d litellm -t '"LiteLLM_SpendLogs"' -F c` to /home/bom/backups FIRST and confirm the dump file exists; delete only rows older than 30 days (ErrorLogs: 7 days) in 50k batches with `ctid IN (SELECT ctid ... LIMIT 50000)`, then `VACUUM (ANALYZE)`. Never prune <30-day SpendLogs; never VACUUM FULL.
KEY POLICY: only ADD keys absent from live config; keys defined in GOD CONFIG v9.0 are locked. New general_settings keys need a LiteLLM restart (03:00-06:00 ICT window, 2-min drain with zero POST /chat/completions, health gate 20x10 s liveliness+readiness, rollback = restore .bak + restart). `proxy_config_reload_interval_seconds`-scoped changes apply without restart.

### 3.15 Poller interval policy (NEW v4.2)
Floor: nothing probes :3000/:4000 or runs `docker exec` more often than every 5 minutes; opshub-* systemd timers are relaxed to 15 min when found below the floor.
```bash
systemctl list-timers --all --no-pager | grep -i opshub
for t in /etc/systemd/system/opshub-*.timer; do grep -E 'OnCalendar|OnUnitActiveSec' "$t"; done
# relax an offender (drop-in, never disable):
sudo mkdir -p "/etc/systemd/system/opshub-c2-monitor.timer.d"
printf '[Timer]\nOnUnitActiveSec=\nOnUnitActiveSec=15min\n' | sudo tee /etc/systemd/system/opshub-c2-monitor.timer.d/interval-v52.conf   # use OnCalendar reset variant for OnCalendar timers
sudo systemctl daemon-reload && systemctl list-timers --no-pager | grep opshub
# cron check (edit only */1-*/4 offenders that hit 3000/4000/docker exec; backup first):
crontab -u bom -l | grep -nE '^\*/[1-4] .*(3000|4000|docker exec)'
```
Known state 2026-11-04: monitor hourly@:48, light daily 03:10, deep Sat 09:10, audit monthly — all above the floor; observer cron (`* * * * * ops_observer_c2.sh`) is outside the */1-4 edit rule and was left as-is (GOD pipeline). Warm-pin/keep-alive crons are GOD pipeline: keep unless <5 min.

### 3.16 External TTFB measurement recipe (NEW v4.2)
Public latency evidence is ONLY the AM5 10-shot median/p90 via curl.exe `%{time_starttransfer}`. C2 hairpin (`curl https://webui.siam2r.com` FROM C2) and localhost (`curl http://127.0.0.1:3000`) are diagnostic contrasts only — never report them as user latency (K3's 0.28 s "PASS" hairpin was not the user experience; Fable's external 1.17-6.53 s at load 15 was).
```powershell
1..10 | % { curl.exe -s -o NUL -A "Mozilla/5.0" -w "ttfb=%{time_starttransfer}`n" --max-time 60 https://webui.siam2r.com/api/version }
```
Gates: median < 0.5 s AND p90 < 1.0 s = PASS; median 0.5-1.0 s = PARTIAL (document the number); > 1.0 s or worse than the recorded baseline = FAIL (investigate before release). Compare against same-minute localhost TTFB on C2 to split edge-path vs box load; cloudflared metrics (127.0.0.1:<metrics-port>/metrics: ha_connections >= 2, request_errors slope) prove edge health.

### 3.17 Headless screenshot QC method (NEW v4.2)
Evidence-grade UI QC = headless Chromium via Playwright, never an agent-panel screenshot.
```python
# AM5: python -m pip install --user playwright; python -m playwright install chromium
from playwright.async_api import async_playwright
import asyncio
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        ctx = await b.new_context(viewport={"width":1920,"height":1080}, extra_http_headers={"Cache-Control":"no-cache"})
        page = await ctx.new_page()
        r = await page.goto("https://webui.siam2r.com/", wait_until="networkidle", timeout=120000)
        await page.screenshot(path="qc_landing.png", full_page=True)
        imgs = await page.eval_on_selector_all("img","els=>els.map(e=>({src:e.getAttribute('src'),ok:e.complete&&e.naturalWidth>0}))")
        print([i for i in imgs if not i["ok"]])   # must be empty (0 broken images)
        await b.close()
asyncio.run(main())
```
Checklist: landing HTTP 200; 0 broken images (`complete && naturalWidth > 0`); branded asset URLs return 200; DOM text contains the expected version strings; screenshots saved to the task evidence dir and zipped into the hub artifact. If AM5 Playwright is broken, run the same script on UA (scp screenshots back); both broken -> item DEAD with a note.

## 4. Fix procedures (selected)

### 4.4 Mac Ollama CLI skew (server 0.40.14 / CLI 0.40.10)
Update the Mac Ollama app (GUI or brew) so the CLI matches the server. Read-only verification from AM5: `ssh bom@192.168.1.254 "ollama --version"`.

## 6. Standing checklist (post-incident close-out)
1. `curl -s https://webui.siam2r.com/api/version` -> 200, version 0.13.3, external TTFB median <0.5 s from AM5 (§3.16).
2. `ssh -p 99 bom@109.123.233.171 "uptime"` connects in <5 s (guard active) and load < 12.
3. LiteLLM liveliness + readiness both 200.
4. `tailscale status` on C2 lists 8 peers; ds725-plus and macmini-ai paths known (direct / relay-sin respectively).
5. Squid on C2 + Contabo1: active with `proxy_auth REQUIRED` — do not disable; both C2 listeners present (§3.11).
6. GOD CONFIG 7/7 PASS (§1.2); functions = 18.
7. c2-ssh-guard enabled + active; DROP-rule count == guard-list line count (§3.13).
