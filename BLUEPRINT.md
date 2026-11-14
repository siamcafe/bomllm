<!-- GOD BLUEPRINT v8.0 — full sync from hub art#57374 into BOM LLM release v18.0.0 (2026-11-14). v8.1 addendum appended from BOM AI v2.1.8 handoff art#60827. K3 Gateway Blueprint (rc3): hub art#60117. -->

# GOD BLUEPRINT v8.0 — BOMLLM Fleet

```yaml
project: bomllm
step: survey_god_blueprint_v8_howto_v5
version: "8.0"
previous: "7.0"
date: 2026-11-07
author: K3-256k /auto THINKING max
inputs: [art#57325, art#57278, art#57277, art#57247, art#57077]
supersedes: art#56687 (v7.0)
config_reference: art#56686 (GOD CONFIG v11.0 — locked params unchanged)
recommendation: INSPECT
mode: DOCUMENT_ONLY
changes_made: none
```

---

## 1. Executive Summary

The BOMLLM fleet is an 8-machine production estate (C2, UA, AM4, Mac, i9, NAS, CAT, CB1; AM5 command station recorded separately). Since GOD BLUEPRINT v7.0 (art#56687) the fleet state has shifted in three important ways:

**What regressed (new evidence, art#57325 + art#57278):**

- **Public TTFB regressed.** Bangkok `GET /api/version` median went from 369 ms (art#57278, 2026-11-07 ~00:40 UTC window) to **1,286 ms median / 3,243 ms max** (art#57325, ~02:00-02:25 UTC window). C2 localhost in the same window was only 49.6-87.6 ms median. The regression is NOT inside OWUI's request handler.
- **NEW primary whole-host root cause — C2 VPS storage latency (S001).** `/proc/diskstats` delta over 15.01 s on `sda`: read await 132.71 ms, write await 162.58 ms at only 78.6/97.6 KB/s, io_util 29.7%. Postgres independently logged COMMIT at 1.02-1.60 s and a 25.54 s checkpoint. CPU steal = 0, swap = 0. This is a **provider-side storage backend defect**, not capacity, not throughput, not guest tuning. It explains why both SSH (`ssh true` = 8.266 s) and OWUI feel sluggish.
- **NEW — C2↔Cloudflare network jitter (S003).** 10 of 16 BKK samples >1 s, four >2 s; C2 public-window TLS handshake reached 3.44 s while localhost stayed <100 ms. Cloudflared itself is healthy (ha_connections=4, concurrent=2, lifetime error ratio 1.75%).
- **NEW — LiteLLM SpendLogs stall (S004).** Legacy `/spend/logs?limit=10000` queries took 6.97 s / 11.35 s / 15.66 s against a 786 MB `LiteLLM_SpendLogs` table (~148,337 live rows). During the stall: liveliness 8.18 s, readiness 503; after it: liveliness 8.7-34.2 ms. High-confidence intermittent stall contributor.

**What is still broken (unchanged since v7/art#57278):**

- **Mac Ollama binds 127.0.0.1 only (S002/F001) — chat generation is DOWN.** `OLLAMA_HOST=127.0.0.1:11434` on macmini-ai; C2→`100.118.133.38:11434` = connection refused / HTTP 000. LiteLLM health showed 6 unhealthy endpoints. Mac localhost inference is healthy: cold 10-token 6.78 s (6.06 s load), warm 0.73 s.
- **C2↔Mac Tailscale stuck on DERP(sin)** both directions, no direct path (S007/F002); Mac→C2 samples hit 346-813 ms.
- **One Uvicorn worker** (`--workers 1`) still serializes the whole UI (S005/F004).
- **theme_designer_pro 1,215,035-byte event** still active (S008/F003).
- **Warmup crons still fire at the dead Mac port**, last 20 warm-pin entries all HTTP 000 (S009/F006).

**What improved (art#57325 vs art#57278):**

- live-router model is now `qwen38-uni` (was inactive `qwen38-chat`); zero comments/responses/queue.
- Netdata on C2 down to 12.6% of one core instantaneous (was 28%).
- ENABLE_OLLAMA_API=false ACTIVE; REDIS_URL / WEBSOCKET_MANAGER=redis SET; SearXNG alias CONNECTED.

**Fleet health summary (art#57247, 8/8 reached):** total reclaimable junk 31.8 GB (do NOT bulk-delete; safe-now subset = 3 dangling images only); AM4 UFW inactive + 13 wide 0.0.0.0 publishes remains the widest exposure (HIGH); CB1 n8n-parented zombies rose 75 → 144 (HIGH, owner-window recycle); i9 `:8080` bomai-pro target down (HIGH); CAT 176 ssh Failed/24h with UFW inactive (CSF expected, unverified) (HIGH). Locked model params verified **7/7** on Mac qwen38-uni (id 549badb7b84d, 22 GB resident, MLX, ctx 8192, Forever).

**Bottom line for v8.0:** The owner-visible pain order is now: (1) Mac bind fix restores chat; (2) C2 storage + C2↔CF network are provider-side and gate all further page tuning; (3) SpendLogs poller replacement removes the intermittent proxy stall; (4) only then do workers/theme/Tailscale tuning matter. Estimated outcome after P0-P1: chat back at ~0.4-0.7 s first token (warm), page median back to the ~370 ms geographic floor with the 2.5-3.6 s spikes cut once S001/S003 are resolved by the provider.

---

## 2. Fleet Architecture + Request Path Diagram

### 2.1 Machine roles (8 production machines + command station)

| Machine | Host / Address | Role | State (art#57247) |
|---|---|---|---|
| C2 | contabo2-bom-llm · `bom@100.83.20.100:99` (public 109.123.233.171:99) | Public OWUI + LiteLLM control plane, search, relays, live-router, price pipeline | healthy-ish; **storage latency CRITICAL (S001)**; load 9.7/10.6/10.0 on 12 cores |
| UA | ubuntu-ai · `bom@100.82.173.22:99` (LAN 192.168.1.248) | GPU inference (RTX 5080 + 5060 Ti), gpt-oss-120b, LiteLLM prod/staging, ComfyUI | RAM avail 26 Gi (above 20 Gi warn), 18 Gi swap occupied; admission FROZEN |
| AM4 | ubuntu · `bom@100.80.16.53:99` (LAN 192.168.1.249) | Embeddings (Infinity :7997), Qdrant v1.20.0, agent hub, LiteLLM-gw, business services | healthy capacity; **UFW INACTIVE + 13 wide publishes (HIGH)** |
| Mac | macmini-ai M4 Pro · `bom@100.118.133.38:22` (LAN 192.168.1.254) | **PRIMARY MLX inference** qwen38-uni 0.40.14 | **bind broken (S002)**; DERP-only path; 2 zombies; simulator volumes 98% |
| i9 | DESKTOP-G3MKH6J Win10 · `bomi9@100.85.255.14:22` | YuE2/ComfyUI :8190, bomai-pro llama.cpp | **:8080 down (HIGH)**; Win10 EOL, ESU owner decision; admission DENY |
| NAS | DS725+ DSM 7.4.1 · `siamcafe@100.111.221.102` | Storage, hub/docs relays, owner-held n8n 2.31.2, cleanup brain | healthy; 1 dangling image; synoindex-checkpackage failed unit |
| CAT | server-122-155-168-7.da.direct · `bom@122.155.168.7:99` | DirectAdmin production hosting (OWNER_EXECUTE only) | 176 ssh Failed/24h; backups stale since 11-01; PHP CLI 7.4 defect |
| CB1 | vmi3108393 · `root@109.205.176.7:99` | Monitoring (Grafana/Prometheus/Kuma), independent n8n 2.10.3, browserless | **144 chromium zombies (HIGH)**; oversized logs |
| AM5 | DESKTOP-PE1B0VH (Ryzen 9950X3D) | Command station — not counted among the 8 | recorded separately |

### 2.2 Live chat request path (measured, art#57278 + art#57325)

```
Browser (Bangkok)
  │  TCP ~12.2 ms median · TLS-ready ~38.7 ms median · CF colo BKK (16 samples)
  ▼
Cloudflare edge ── QUIC ──► C2 host cloudflared 2026.10.7 (systemd, ha_connections=4)
  │  derived CF→C2 tunnel/queue ≈ 1.16 s median during regression window
  │  (BKK TTFB 1285.9 ms − edge TLS 38.7 ms − C2 OWUI 87.6 ms; derived, not instrumented)
  │  webui.siam2r.com → http://127.0.0.1:3000
  ▼
C2 Open WebUI 0.13.0 · uvicorn --workers 1 · bind 127.0.0.1:3000→8080
  │  localhost /api/version median 49.6/87.6 ms (two windows), max 575.3 ms
  │  13 active filters · 4 pipes · 2 events (theme_designer_pro 1.2 MB browser-side)
  ▼
C2 LiteLLM 1.106.5-pil2 :4000 (tailscale + loopback binds)
  │  /health 6.63 s and /health/liveliness 8.18 s DURING S004 stall;
  │  8.7-34.2 ms after. 31 models visible, memory 3.47 GiB
  ▼
TCP 100.118.133.38:11434 over Tailscale — DERP(sin) 34-180 ms C2→Mac,
  │  346-813 ms Mac→C2, NO direct path … currently REFUSED (S002)
  ▼
Mac Ollama 0.40.14 — listens 127.0.0.1:11434 ONLY  ◄── ROOT OF CHAT OUTAGE
     qwen38-uni id 549badb7b84d · 21.9 GB resident · 100% GPU · MLX · ctx 8192
     cold 10-token: 6.78 s (load 6.06 s) · warm: 0.73 s (load 0)
```

**Explicitly OFF the chat path (measured so they are not guessed, art#57278):** NAS `nas-hub` cloudflared (hub/docs only), UA `:4100` staging (nothing listens on UA loopback 4100), AM4 LiteLLM `:4000` (flood-runner only). Do not re-route chat through UA or AM4 (F015).

**Known ingress defect (unchanged):** `llm.siam2r.com` is listed 3× in C2 `/etc/cloudflared/config.yml`; first match (→ AM4 `100.80.16.53:3100`) wins; the later `127.0.0.1:4000` rule never runs. Does NOT affect `webui.siam2r.com`. Owner must declare intended origin before any dedupe (F010 / v7 ACTION-10).

### 2.3 Production dependencies (carry-over, still binding)

- C2 `tailscaled` is load-bearing (hub/docs/chart, Qdrant, embeddings, Mac generation) — never stop.
- C2 `rag-lb-relay-am4` and `qdrant-relay-am4` are production-critical — never remove.
- `chart-overlay_offloaded_to_am4_20261103T0352Z` remains KEEP_PENDING_OWNER_REVIEW; `litellm_old_20261105_223945` remains the rollback asset.
- NAS n8n 2.31.2 and CB1 n8n 2.10.3 are OWNER_HOLD — no restart, no upgrade, no forced alignment.
- Single OWUI worker: every filter inlet path must be non-blocking until S005/ACT-04 lands.

---

## 3. Root Cause Analysis (merged from art#57325 + art#57278)

Duplicate pairs merged into single entries: S002=F001, S003 (new, paired with F008 as baseline), S004 (new), S005=F004, S007=F002, S008=F003, S009=F006. Severity reflects current impact, not discovery order.

### S001 — C2 VPS virtual disk / storage backend latency (CRITICAL · owner_only: yes) — NEW art#57325

- **Evidence:** 15.01 s `/proc/diskstats` delta on `sda`: read await 132.71 ms, write await 162.58 ms, read 78.6 KB/s, write 97.6 KB/s, io_util 29.7%, weighted queue ~2.98. Postgres COMMIT 1.02-1.60 s; checkpoint total 25.54 s (sync 2.08 s). CPU steal 0; swap 0; disk 27% used, inodes 4%. `ssh true` = 8.266 s (auth done at 4.031 s).
- **Impact:** every service stalls on small reads/writes, journal flushes, DB commits. This is the primary whole-host amplifier behind both SSH and OWUI sluggishness. No container-level tuning can compensate.
- **Fix:** owner opens a Contabo storage/performance incident with these measurements; if the provider cannot restore normal latency, plan a verified migration to healthy storage/VPS — backup first, then repeat the same 15 s diskstats + OWUI TTFB probes.
- **Verify:** `cat /proc/diskstats` twice 15 s apart → compute sda await; target read/write await < 20 ms at this low throughput; BKK `/api/version` median back toward ≤ 0.45 s.
- **Rollback:** n/a (provider-side). Migration rollback = restore from the pre-migration backup.
- **Risk:** HIGH to ignore (whole-host degradation persists); MED for migration (mitigated by backup + verify).

### S002 (≡ F001) — Mac Ollama not reachable from C2 (CRITICAL · owner_only: yes)

- **Evidence:** Mac launchd `OLLAMA_HOST=127.0.0.1:11434`; netstat shows only `127.0.0.1:11434` LISTEN. C2→`100.118.133.38:11434`: HTTP 000 (46/283/52 ms); same refusal from inside the `litellm` container. LiteLLM health: 6 unhealthy endpoints, all `ollama_chat/qwen38-uni` connection errors. Mac localhost `/api/version` 0.44-0.75 ms; warm 10-token 0.73 s — the model is fine; the bind is not.
- **Impact:** every Mac-backed chat route (`bom-thai-chat`, `qwen38-uni`, thai-* family) dies at TCP before inference. OWUI pages render while every answer fails.
- **Fix (owner-approved window):** set `OLLAMA_HOST=100.118.133.38:11434` (the tailnet address, **never 0.0.0.0**) in the Mac Ollama launch agent; restart only the Ollama serve process. Do not edit LiteLLM `api_base` values — they already point at the right address.
- **Verify:** `curl --max-time 5 http://100.118.133.38:11434/api/version` from C2 → HTTP 200; then one real logged-in Thai webui send returns Thai text (`/api/version` alone is not proof).
- **Rollback:** set `OLLAMA_HOST` back to `127.0.0.1:11434`, restart serve (returns to pre-change outage state; use only if the tailnet bind exposes something unexpected).
- **Risk:** MED — serve restart unloads the 21.9 GB resident model; first request after restart pays the ~6 s cold load (S006).

### S003 — C2↔Cloudflare network jitter / tunnel path (HIGH · owner_only: yes) — NEW art#57325

- **Evidence:** BKK edge fast (TCP 12.2 ms, TLS-ready 38.7 ms medians) yet 10/16 BKK samples >1 s, 4 >2 s, max 3.243 s. Second C2 public window: TTFB median 2.605 s, max 3.620 s; TLS up to 3.440 s; TCP connect up to 0.844 s — while adjacent C2 localhost was 87.6 ms median. Cloudflared active, ha_connections=4, concurrent_requests=2, lifetime errors 1205/68666 = 1.75%.
- **Impact:** owner sees 1-3 s first-byte delays even when OWUI answers locally in tens of ms. TLS/connect delays occur before any request reaches OWUI.
- **Fix:** owner/provider diagnoses the Contabo↔CF route (packet loss/jitter) with the recorded samples; validate cloudflared QUIC transport in a separate approved window. Re-measure from Bangkok; the realistic comparison baseline is the ~369 ms geographic median (F008), not sub-100 ms.
- **Verify:** 16-shot BKK `GET /api/version` — median ≤ 0.45 s AND max ≤ 0.80 s (today: median 1.286 s, max 3.243 s).
- **Rollback:** n/a (diagnostic/provider action).
- **Risk:** MED — tunnel transport experiments can briefly drop sessions; do them in the low-traffic window.

### S004 — LiteLLM legacy SpendLogs read stall (HIGH · owner_only: yes) — NEW art#57325

- **Evidence:** Postgres logged legacy `/spend/logs` queries with `LIMIT 10000` at 6.973 s, 11.349 s, 15.664 s selecting large message/response fields. LiteLLM logged repeated result-truncation warnings, Prisma DB reconnect, liveliness 8.183 s, readiness 503 (2.061 s) → recovered to 200 in 78.4 ms; post-window liveliness 23.0/8.7/34.2 ms. litellm DB 806 MB; `LiteLLM_SpendLogs` 786 MB, ~148,337 live rows, 10,068 dead tuples. After stall: litellm idle=7, openwebui idle=6 sessions, no active waits.
- **Impact:** one spend/admin read can block or destabilize the proxy event loop and DB connection, delaying cheap health checks and potentially chat dispatch.
- **Fix:** identify the legacy `/spend/logs?limit=10000` caller (poller/dashboard) and replace it with `/spend/logs/v2` using small pages and only required columns; close or stop the offending poller. **Do NOT prune the table** — it is below both GOD CONFIG v11 thresholds (1M rows / 2 GB; policy: prune only >1M rows or >2 GB after pg_dump, 30 d age, 50 k batches + VACUUM ANALYZE, no VACUUM FULL).
- **Verify:** re-test `/health/liveliness` during the replacement read — stays < 100 ms; Postgres logs show no >1 s spend query.
- **Rollback:** re-enable the legacy caller (not recommended); the v2 endpoint change is caller-side only.
- **Risk:** LOW for the v2 swap; HIGH if someone prunes under threshold against policy.

### S005 (≡ F004) — One Uvicorn worker serializes the UI (MEDIUM · owner_only: yes)

- **Evidence:** `docker top open-webui` = exactly one process `uvicorn … --workers 1`. OWUI CPU samples 65.71% / 35.91%, memory ~763 MiB; localhost `/api/version` spikes 547.9-575.3 ms persist despite ENABLE_OLLAMA_API=false. No memory/CPU cap (HostConfig.Memory=0, NanoCpus=0).
- **Impact:** one slow request (storage wait per S001, hung upstream, filter HTTP) serializes all other requests and enlarges public TTFB spikes.
- **Fix:** ONLY after S001/S003 are addressed and S002 verified: raise to `--workers 2` in `/root/bomllm-owui-compose.yaml` (root-owned; running argv is source of truth), keep publish on `127.0.0.1:3000`, keep `WEBSOCKET_MANAGER=redis` (`redis://valkey:6379/1`). Recreate `open-webui` only. Do not treat this as a substitute for S001/S003.
- **Verify:** `docker top open-webui` shows 2 workers; repeat 16-shot public TTFB + localhost sets.
- **Rollback:** set `--workers 1`, recreate container.
- **Risk:** MED — restart blip; in-process filter caches (price router 30 s cache) duplicate per worker, which is safe.

### S006 — Mac qwen38-uni warm residency (MEDIUM · owner_only: no) — NEW art#57325

- **Evidence:** pre-survey `/api/ps` had only bomai-safe (3.4 GB); first qwen38-uni 10-token call 6.78 s (load 6.06 s, eval 0.57 s); immediate warm repeat 0.73 s (load 0). Probe left qwen38-uni resident at 21.9 GB, ctx 8192.
- **Impact:** after S002 repair, the first request following any eviction/expiry still pays ~6 s before normal speed resumes.
- **Fix:** after S002, restore one validated qwen38-uni warm path and confirm keep-alive/residency (Forever per art#57247) remains effective. Do not change any of the 7 locked parameters.
- **Verify:** two consecutive 10-token localhost generates: second call load_duration ≈ 0 and total < 1 s.
- **Rollback:** n/a (residency is self-healing once the path works).
- **Risk:** LOW.

### S007 (≡ F002) — C2↔Mac Tailscale stays on DERP(sin), directions asymmetric (MEDIUM · owner_only: yes)

- **Evidence:** C2→Mac DERP(sin) 34/173/174/180 ms (art#57325) and 165/1071/343/132 ms (art#57278), no direct path either survey. Mac→C2 346-813 ms (art#57325) and 33/31/32/341 ms (art#57278). Mac `tailscale status`: `MagicSock ReceiveIPv4 is not running`.
- **Impact:** after S002, connection setup and first token still jitter; the C2→Mac direction is the jumpy one and it is the one that opens the socket.
- **Fix:** owner network work restores the documented direct UDP/NAT path (UDP 41641 or equivalent NAT policy per v11) or stable sub-200 ms DERP both directions. Do not bounce tailscaled as a speculative fix.
- **Verify:** `tailscale ping --c 4 100.118.133.38` from C2 — pass = no sample > 500 ms, preferably one `direct` line.
- **Rollback:** n/a.
- **Risk:** MED — may require tailscaled bounce or Mac NAT change (owner window).

### S008 (≡ F003) — theme_designer_pro 1.2 MB browser event on every page (MEDIUM · owner_only: yes)

- **Evidence:** Postgres `function` row `theme_designer_pro` type event, active, `length(content)=1,215,035`; source contains `setInterval`, `MutationObserver`, `fetch`, `WebSocket`, `requestAnimationFrame`. Companion `claude_clone_ui` 9,329 bytes also active with a MutationObserver.
- **Impact:** browser main-thread work after TTFB — the "feels slow" component curl cannot see. Independent of the 369 ms floor.
- **Fix:** owner-approved A/B: set `theme_designer_pro.is_active=false`, reload, compare feel + a browser performance trace. If responsiveness improves, split the theme into static CSS + slim event and re-enable the slim version. **Do not delete the function row.**
- **Verify:** `SELECT length(content), is_active FROM function WHERE id='theme_designer_pro';` matches the owner-chosen state; visual QC on BOTH BOMLLM and BOMAI surfaces (shared instance).
- **Rollback:** `is_active=true`.
- **Risk:** MED — product look changes while off.

### S009 (≡ F006) — Warmup crons fire at the dead port with a stale model name (LOW · owner_only: no)

- **Evidence:** `bomllm-warmup.sh` (*/4 min) still posts `model=qwen38-chat` (stale name; live target is qwen38-uni); `bomllm-warm-pin.sh` (*/5 min) posts `qwen38-uni` to the refused Mac port. Last 20 warm-pin entries all HTTP 000, durations 0.039-2.299 s. `ops_observer_c2.sh` every minute stays.
- **Impact:** a failing request every 4-5 minutes adds error noise on the single worker and LiteLLM; does not warm anything.
- **Fix:** comment out the two curl lines NOW (`/home/bom/bomllm/scripts/bomllm-warmup.sh` line 12, `bomllm-warm-pin.sh` line 6); after S002 passes, re-enable ONE 5-minute qwen38-uni pin against the tailnet URL and retire the 4-minute job. Preserve the observer cron.
- **Verify:** `tail -20` the warm-pin log — no new HTTP 000 lines while disabled; after re-enable, entries show HTTP 200.
- **Rollback:** uncomment the lines.
- **Risk:** LOW.

### S010 — LiteLLM health-probe cadence amplifies stalls (LOW · owner_only: no) — NEW art#57325

- **Evidence:** last 500 LiteLLM log lines span 18 m 47 s and include 73 `/health/liveliness` calls ≈ 3.9/min — above the GOD CONFIG poller contract (no :4000 probing more often than 5 minutes). Normally fast; they queue during S004 stalls.
- **Impact:** monitoring adds request pressure exactly when the proxy is already stalled.
- **Fix:** inventory pollers by source, consolidate, enforce/stagger the documented ≥5-minute interval. Do not increase probe frequency to compensate for current symptoms.
- **Verify:** log sample shows ≤ 12 liveliness calls/hour per poller source after consolidation.
- **Rollback:** restore previous poller cadence.
- **Risk:** LOW.

### F005 — live-router idle burn (LOW-MED · owner_only: restart yes / code no) — carried, partially improved

- **Evidence (art#57278):** live-router 35.77% CPU idle, 38 MB, healthy; own logs `comments_per_min=0 … ws_connected=true`; env `OWUI_MODEL=qwen38-uni` (now correct — was the v11 inactive-model defect). art#57325 confirms model row improved and router idle.
- **Impact:** ~0.3 core of pure waste on the shared C2 box.
- **Fix:** read the idle loop (likely tight websocket poll); back off to 1 s cadence when `queue_depth=0`. Ship in the same restart window as S005.
- **Verify:** `docker stats live-router` idle < 5% CPU; minute-stats lines still flowing.
- **Rollback:** redeploy `live-router:v2` prior image.
- **Risk:** LOW to profile, MED to ship.

### F007 — Intent-filter busy check can block the worker up to 4 s (LOW-MED · owner_only: no)

- **Evidence (art#57278):** `bom_intent_filter` (42,276 B, global toggle off, `target_models=bom-thai-chat`) `_is_busy()` uses blocking `requests.get` (2 s timeout + second 2 s try to `100.85.255.14` with Host header) on image-intent turns. Measured classify 7.86 ms / 261.8 ms. `enable_music_intent` defaults false (no :8188 queue check). Price router v2 already does this correctly (executor + 2 s + keyword gate).
- **Impact:** an image-intent turn can freeze the single worker up to ~4 s — every user's spinner while S005 is unfixed.
- **Fix:** run `_is_busy` via `run_in_executor`, same pattern as `bom_price_router._fetch`. Do not widen the filter. Ship with S005 so behavior is tested once.
- **Verify:** synthetic image-intent turn: worker stays responsive (parallel `/api/version` < 200 ms during the turn).
- **Rollback:** restore previous function content from the v11 hash baseline (md5 `bd079a60…`); keep a DB dump of the `function` row before edit (backup contract).
- **Risk:** LOW.

### F010 — Triplicate `llm.siam2r.com` ingress rules (INFO · owner_only: yes) — carried

- **Evidence:** C2 `/etc/cloudflared/config.yml` lines 16-23: two rules → `100.80.16.53:3100` (AM4 chart), one → `127.0.0.1:4000`. First match wins.
- **Impact:** none on webui; `llm.siam2r.com` users hit AM4 chart ingress, not C2 LiteLLM.
- **Fix:** none until the owner declares the intended origin. Do not "clean up" in a performance window.
- **Risk:** HIGH if the wrong duplicate is deleted.

### F011 — Admission hook: separate connect timeout from the 300 s generation budget (LOW · owner_only: no, window yes)

- **Evidence (art#57278):** `/app/admission_hook.py` 878 lines; `INTERACTIVE_QUEUE_TIMEOUT_S=300`, `BATCH_QUEUE_TIMEOUT_S=300`, per-lane cap 4. At ~20 tok/s, `num_predict=4096` ≈ 200 s, so 300 s is the right generation budget; a refused port fails in <300 ms, but a *hung* upstream would pin a lane 5 minutes.
- **Fix:** after S002, add a 3 s connect timeout on Mac routes, separate from the 300 s budget — only if LiteLLM config exposes connect timeout without cutting global `request_timeout` (global 60 s and `bom-thai-chat` 60 s stay). LiteLLM reload in the 03:00-06:00 ICT window after 2-minute drain.
- **Verify:** kill-path test in window: dead upstream fails in ≤ 3 s; normal 4096-token answer completes uncut.
- **Rollback:** remove the connect-timeout line, reload.
- **Risk:** LOW.

### Not-root-causes (confirmed negative evidence — do not re-investigate)

CPU steal 0% (all vmstat samples); memory pressure/swap on C2 (40 GiB avail, 0 swap); disk full/inodes (27% / 4%); container bloat (10 running, same as prior); Netdata CPU (12.6% one core now); cloudflared process failure (active, 4 HA conns, 1.75% lifetime errors); Valkey config (PONG, 2.01 MB, dbsize 8); SearXNG alias (connected); Postgres/PgBouncer waits (DB 49 MB, `config` table 128 kB with 1.05M index scans, PgBouncer idle 0.02%); the 7 locked sampler values (live, matched, not the outage — F014); Bangkok↔Europe geography (~370 ms floor — F008; a tunnel endpoint move is a separate future project, not this blueprint).

---

## 4. Performance Recovery Plan (prioritized actions)

Execution contract: one hypothesis per round (P4); timestamped backup before every change; LiteLLM/OWUI restarts only 03:00-06:00 ICT after 2-minute drain; every action lists verify + rollback. "zcode" below = any agent lane executing under these rules.

### P0 — restore chat + stop the bleeding (owner window required)

| # | Action | Maps to | Executor | Window |
|---|---|---|---|---|
| P0-1 | Mac `OLLAMA_HOST=100.118.133.38:11434`, restart Ollama serve only; verify C2 curl 200 + one real Thai webui send | S002 | owner-authorized lane | owner-approved; low traffic |
| P0-2 | Open Contabo storage incident with S001 diskstats/Postgres evidence; plan verified migration if unresolved (backup → migrate → re-measure) | S001 | owner + provider | owner decision |
| P0-3 | Open Contabo↔CF route/jitter diagnosis with S003 samples; cloudflared QUIC validation in a separate approved window | S003 | owner + provider | owner decision |
| P0-4 | Disable the two dead warmup curls (comment lines; keep observer cron) | S009 | zcode autonomous | none needed |

### P1 — remove the intermittent stalls (after P0-1 verified)

| # | Action | Maps to | Executor | Window |
|---|---|---|---|---|
| P1-1 | Find legacy `/spend/logs?limit=10000` caller; replace with `/spend/logs/v2` small pages / required columns; verify liveliness < 100 ms during the read. NO table pruning (under v11 thresholds) | S004 | zcode finds caller; owner approves poller change | none for read; restart n/a |
| P1-2 | Restore single qwen38-uni warm path (one 5-min pin via tailnet URL); re-enable exactly one warmup job | S006/S009 | zcode autonomous | after P0-1 |
| P1-3 | Consolidate :4000 pollers to the ≥5 min contract, staggered | S010 | zcode autonomous | none |

### P2 — structural page improvements (only after S001/S003 re-measurement)

| # | Action | Maps to | Executor | Window |
|---|---|---|---|---|
| P2-1 | `--workers 2` on OWUI (keep loopback publish + redis websocket manager) | S005 | owner window | 03:00-06:00 ICT |
| P2-2 | theme_designer_pro A/B (is_active=false → measure → split into static CSS + slim event) | S008 | owner-approved | owner preview window |
| P2-3 | `_is_busy` → `run_in_executor` in bom_intent_filter | F007 | zcode, ship with P2-1 | same window |
| P2-4 | live-router idle backoff 1 s when queue_depth=0 | F005 | zcode code; owner restart | same window |
| P2-5 | Tailscale direct-path/NAT repair (UDP 41641) or stable <200 ms DERP | S007 | owner network | owner window |
| P2-6 | LiteLLM 3 s connect timeout on Mac routes (keep 300 s admission / 60 s request budgets) | F011 | zcode staged | 03:00-06:00 ICT after drain |

### Explicitly NOT in this plan

n8n restart/upgrade (OWNER HOLD); sshd/DNS changes (IRON 38/41); LiteLLM version change (stay 1.106.5-pil2; 1.107.0 BANNED; 1.106.7/1.108.1 exist but no advisory forces a move — owner window only); moving chat through UA/AM4 (F015); cloudflared `llm.siam2r.com` dedupe (awaits owner origin decision, F010); SpendLogs pruning (under threshold); Mac Ollama upgrade to 0.40.15 (no advisory; production stays 0.40.14).

---

## 5. Auto Cleanup System (from art#57277)

**Status: BLUEPRINT APPROVED FOR DEPLOYMENT PATH — nothing executed yet.** Central design: one master script on NAS (`/volume1/homes/siamcafe/bomllm-cleanup/fleet_cleanup.sh`, mode 700) run by DSM Task Scheduler **weekly Sunday 04:00 ICT**; zero installed files on remote machines (parameterized bash/PowerShell payloads piped over SSH, ed25519 key, BatchMode, ConnectTimeout=10, hard cap 30 s/machine, 40 s i9); unreachable machine ≠ failed run; **no service is ever restarted**; kill switch = presence of `$BASE_DIR/DISABLED`.

**Fleet target matrix:** C2/UA (docker-linux: docker prunes, journal 200M, rotated logs >100MB, /tmp >7d) · AM4 (same + pip cache purge + /tmp >3d aggressive) · CAT (gentle-linux: no docker; journal, rotated logs, kern.log/lastlog >100MB, /tmp >7d) · CB1 (same as C2 + nginx access.log/exim mainlog/lfd.log/fb_poll_bridge_v2.log >50MB truncations + monitoring tarballs >14d) · Mac (health-only: ollama process + API + disk free — NO deletes) · i9 (PowerShell temp >7d, `$env:TEMP` + `C:\Windows\Temp` — **C: only, NEVER D:**) · NAS local.

**Safety model (binding):** never delete model files / container data volumes / swap / prod configs / anything under `/home`, `/ai`, `/data`, `/archive`, `/volume1` user shares, `/opt/djbom`, or `D:\`; never prune NAMED docker volumes — only anonymous 64-hex dangling volumes without a `keep` label, individually (deviation D1: protects `bomllm_qdrant_data` which sits dangling on C2 with a must-not-drop note); never delete files <7 days (AM4 /tmp = 3d sole exception); truncation not deletion for logs; all deletes non-interactive; everything logged to NAS log + hub artifact + joblog lane `nas` step `fleet_auto_cleanup`.

**Expected effect:** ~9 GB/week fleet-wide (C2 journal archives ~1.4 GB/wk, AM4 pip cache 3-4 GB, CAT kern.log+lastlog ~350 MB/wk, CB1 app logs 300+ MB/wk).

**Deployment gates (from art#57277 §7):** T0 `bash -n` syntax → T1 full `--dry-run` (8/8 reached or noted; `dry_run: 1` on hub) → T2 `--only cb1 --dry-run` → T3 kill-switch test → T4 bogus-host timeout test → T5 supervised first live run (sane reclaim vs art#57269 baseline, `docker ps` counts unchanged) → T6 scheduled Sunday run. Only after T1-T5 is the system live; two clean scheduled runs → owner may retire the art#54414 per-machine dry-run scripts. C2's existing Sunday 05:00 builder-prune cron stays (idempotent, runs 1 h after central pass).

**Hub reporting:** full YAML run report → `POST /v1/artifacts -F project=bomllm` every run (dry runs labeled); joblog `POST /v1/jobs/nas/report` DONE with reclaimed human summary; credentials from chmod-600 `~/.config/bomllm_cleanup.conf`, never hardcoded; hub-down = WARN, exit 0 (reporting failure never masks a successful cleanup).

---

## 6. Fleet Version Matrix (art#57077 + art#57247, 2026-11-07)

| Component | GOD pin | C2 | UA | AM4 | Mac | i9 | NAS | CB1 | Status |
|---|---|---|---|---|---|---|---|---|---|
| LiteLLM | 1.106.5 | 1.106.5-pil2 | prod 1.106.5 / staging 1.106.4 (NO_RESTART) | 1.106.5-pil2 (litellm-gw) | — | — | relay only | — | MATCH (staging excepted by rule) |
| Open WebUI | C2 0.13.0 | 0.13.0 | 0.12.4 host (independent) | 0.11.4 host | 0.12.0 (independent) | — | — | — | C2 MATCH; others independent |
| Ollama | 0.40.14 | client 0.40.8, server down (not a pin host) | 0.40.14 | 0.40.13 (blocked: FX28 + window; staged script) | 0.40.14 | 0.40.13 client, server down (OWNER_DECISION) | — | — | Mac/UA MATCH; AM4/i9 blocked |
| SearXNG | 2026.11.2 | 2026.11.6-ac11e14c5 | — | 2026.11.6-ac11e14c5 | — | — | — | — | DRIFTED ahead of pin (review) |
| ComfyUI | i9 0.43.0 | — | 0.43.0 (8188/8189) | 0.43.0 | — | 0.43.0 (:8190) | — | — | MATCH (0.44.0 exists; no advisory; HTTP API only) |
| Netdata | no fleet pin | v2.12.3 | v2.12.3 | v2.12.3 | v2.12.0 | — | v2.12.3 | 2.12.0-422-nightly (stopped, leave stopped) | mixed, safe |
| cloudflared | — | 2026.10.7 | not installed | not in path | 2026.8.2 | — | image 2026.10.7 | — | mixed, safe |
| Docker | — | 29.9.3 | 29.9.3 | 29.9.3 | client 29.7.2 (daemon stopped) | absent | 24.0.2 | 29.9.2 | NAS/Mac below 29.8.2 advisory line — report only |
| Valkey | 9.1.2-alpine | up | n/a | megaqc-valkey up | — | — | — | — | MATCH |
| Postgres | C2 16.15-alpine | healthy | — | — | — | — | — | — | MATCH |
| Qdrant | v1.20.0 | relay only | — | v1.20.0 up | — | — | — | — | MATCH |
| n8n | do not align | — | — | — | — | — | 2.31.2 | 2.10.3 | OWNER_HOLD divergence, untouched |
| MariaDB | — | — | — | — | — | — | 11.4.13 | 10.4.13 EOL (blue/green separate) | recorded |

Latest stable reference (art#57077): litellm v1.108.1 (same-line v1.106.7; v1.107.0 BANNED/absent), owui v0.13.0, ollama v0.40.15, comfyui v0.44.0, cloudflared 2026.10.7, docker 29.9.3, qdrant v1.20.0, searxng 2026.11.6, netdata v2.12.3, n8n 2.46.6. Survey counts: 36 components — 8 current, 19 outdated_safe, 5 outdated_risk, 0 compromised, 2 owner_decision, 2 owner_hold, 0 unreachable.

---

## 7. Security Posture (from art#57247)

**HIGH alerts (open):**
1. **AM4 UFW inactive + 13 wide 0.0.0.0 publishes** (LiteLLM 4000, Comfy 8188/8189, chart 3100/3001, 8082/8892/3456/5002/8060, rpcbind 111, 8788, 99). Same defect as v11 ACTION-05; v7 two-phase fix (consumer-proof gate → rebind + ufw enable) still staged. SSH-lockout risk until port-99 rule proven from a second session.
2. **CB1 144 chromium/chrome_crashpad zombies** (v11: 75) — parent is n8n itself; fix = owner-window n8n recycle only. Watch cron daily. Do NOT kill zombies directly (n8n OWNER_HOLD).
3. **i9 no listener on :8080** — bomai-pro route target down; Ollama server not running (admission DENY until GPU attribution).
4. **CAT 176 ssh Failed/24h, UFW inactive** — expected IF CSF is the firewall (CSF not re-queried); DirectAdmin/sshd inventoried only (IRON 38).
5. **C2 load ~9-10 on 12 cores** — CPU load, RAM fine; monitor only.

**MEDIUM (open):** UA 26 Gi avail / 18 Gi swap occupied (above 20 Gi warn line; freeze holds); UA wide publishes 4000/8380/3080/8188/8189 (UFW active, Comfy LAN-scoped; Docker can bypass UFW — DOCKER-USER audit pending); SearXNG drift to 2026.11.6 vs pin 2026.11.2; AM4 GPU0 down to 2,840 MiB used (was ~15 GB both GPUs — workload attribution); CAT kern.log 174 MB + lastlog 163 MB; CB1 auth.log 85 MB / nginx 101 MB / 61 ssh Failed; NAS load 2.65/4 cores, USB 65%, synoindex-checkpackage failed; Mac↔C2 DERP-only; C2 Ollama client drift 0.40.8 (not serving).

**LOW:** Mac 2 zombies + simulator volumes 98% + old ollama lib trees; C2 /tmp 1.7 GB + 3 exited rollback/review containers; i9 Win10 past EOL (ESU decision pending; firewall on; RDP/8190 wide — no listener disable without owner review); NAS root-fs blind to /volume1.

**Advisory watch (art#57077):** NAS Docker 24.0.2 & Mac Docker 29.7.2 < 29.8.2 (GHSA-7cfq-22r6-qp73, report only); n8n NAS/CB1 < 2.43.3/2.46.1 patches (GHSA-9p7v-45m2-wxgj, GHSA-f2cw-9483-7vcp — OWNER HOLD, do not touch); UA litellm-staging 1.106.4 < GHSA-w4c7-34wj-hqm8 patched 1.106.5 (NO_RESTART; prod already 1.106.5); Mac OWUI 0.12.0 / AM4 OWUI 0.11.4 < 0.12.2 (GHSA-3vvh-g22g-jq6r, medium, no auto-upgrade).

**Unchanged no-touch inventory:** sshd/PasswordAuthentication/PermitRootLogin observations (IRON 38 — inventory only); DNS/resolv.conf (IRON 41); healthy n8n instances; CSF SYNFLOOD/LF; price API no-auth (IRON 19); gpt-oss-120b LIVE_NO_TOUCH; all ComfyUI HTTP_API_ONLY; FX28 untouched; i9 D: UNTOUCHABLE; webui.siam2r.com credentials untouched.

---

## 8. GOD CONFIG v11 Verification

Reference: art#56686 (v11.0). **Locked parameters — verified live, do NOT change:**

| Param | v11 locked | Live (Mac qwen38-uni modelfile, art#57247/57077) | Match |
|---|---|---|---|
| temperature | 0.6 | 0.6 | ✔ |
| top_p | 0.95 | 0.95 | ✔ |
| top_k | 20 | 20 | ✔ |
| repeat_penalty | 1.0 | 1 | ✔ |
| presence_penalty | 0.0 | 0 | ✔ |
| num_predict | 4096 | 4096 | ✔ |
| num_ctx | 8192 | 8192 | ✔ |

**7/7 match.** Resident weight now reported as 22 GB (v11 said ~30 GB) — same model id 549badb7b84d, same ctx 8192, MLX, keep-alive Forever. Not a parameter drift; report-only note.

Other v11 verification points: LiteLLM pin 1.106.5 reconciled and matched fleet-wide (UA staging 1.106.4 NO_RESTART; 1.107.0 BANNED and absent); C2 OWUI 0.13.0 on loopback bind LIVE; price router v2 live in DB (keyword gate, 2 s timeout, run_in_executor, 30 s cache — v11 ACTION-02 defect closed); live-router env now qwen38-uni (v11 ACTION-04 closed, art#57325); function hash baseline — 18 baseline + 3 price rows retained as the reference set; SearXNG tag drifted past the v11 pin (2026.11.6 vs 2026.11.2) — flagged for pin reconciliation, not rollback.

**Verification gaps carried forward:** UA secret-file perms 664→600 staged (ACTION-12, unverified this round); AM4 UFW/rebind (ACTION-05) still open; CAT staged scripts remain OWNER_EXECUTE unexecuted; CB1 9090 shadow rule staged (ACTION-22); NAS swap/root items (ACTION-21) blocked-no-root; i9 0.40.14 staged script not run (ACTION-16); i9 ESU decision open (ACTION-23); cloudflared MODE decision open (ACTION-10); bomai-safe system-text contradiction open (ACTION-13); Mac↔C2/UA direct path (ACTION-06) open — superseded in priority by S002/S007.

---

## 9. Owner-Only Actions (prioritized, with time windows)

| Priority | Action | Window | Blocks |
|---|---|---|---|
| 1 | **Mac Ollama tailnet bind** (`OLLAMA_HOST=100.118.133.38:11434`, restart serve; verify C2 200 + real Thai send) | any owner-approved low-traffic window | ALL chat |
| 2 | **Contabo storage incident** (S001 evidence pack) → migration decision if unresolved | provider ticket, owner decision | all C2 services |
| 3 | **Contabo↔CF route diagnosis** (S003 samples) + cloudflared QUIC validation | provider ticket + approved window | public TTFB |
| 4 | SpendLogs legacy caller replacement approval (P1-1) | none (no restart) | intermittent proxy stalls |
| 5 | OWUI `--workers 2` restart window (with F007/F005 shipped together) | 03:00-06:00 ICT | TTFB spikes |
| 6 | theme_designer_pro A/B preview decision | owner preview window | browser jank |
| 7 | Tailscale direct-path/NAT (UDP 41641) | owner network window | upstream jitter |
| 8 | CB1 n8n recycle (144 zombies) | owner window | zombie growth |
| 9 | AM4 UFW enable + wide-publish rebinds (v7 ACTION-05 two-phase) | owner window, second-session SSH proof | exposure HIGH |
| 10 | LiteLLM connect-timeout change (F011) | 03:00-06:00 ICT after drain | hung-upstream lane pins |
| 11 | cloudflared `llm.siam2r.com` origin intent (F010) | owner decision, any time | route correctness |
| 12 | CAT batch (PHP default 8.3, backups, CSF 19999) — OWNER_EXECUTE scripts staged | owner executes | CAT HIGH items |
| 13 | i9 ESU-or-migrate decision; i9/AM4 Ollama 0.40.14 windows; UA un-freeze decision | owner decision | gated lanes |
| 14 | NAS cleanup-system go-live approval (T5→T6) + optional NAS docker permission choice | after T1-T4 pass | weekly automation |
| 15 | Mac simulator volumes (~32 GB) + old ollama lib trees deletion decision | owner decision | disk hygiene |

---

## 10. Deferred Phases (C/D/E/F)

- **Phase C (post-S001/S003 re-measurement):** OWUI workers → 2, theme split, live-router backoff, intent-filter executor, LiteLLM connect timeout. Entry gate: provider re-measure shows disk await < 20 ms and BKK median ≤ 0.45 s.
- **Phase D (network hardening):** Tailscale direct path C2↔Mac and UA; AM4 UFW + rebinds; UA DOCKER-USER audit; CB1 9090 shadow rule. Entry gate: owner network windows booked.
- **Phase E (lifecycle/versions):** LiteLLM 1.106.7/1.108.1 evaluation (no advisory pressure; staged only), SearXNG pin reconciliation (adopt 2026.11.6 or roll), Ollama 0.40.15 evaluation, ComfyUI 0.44.0 evaluation, NAS/Mac Docker advisory-line upgrades, CB1 MariaDB blue/green. Entry gate: owner windows; one component per round.
- **Phase F (structural):** C2 storage migration (if provider cannot fix S001), tunnel endpoint geography review (BKK/SIN termination — would move the 369 ms floor), UA memory capacity decision (un-freeze), i9 OS migration, CAT OS lifecycle. Entry gate: owner decision each.

---

## 11. Known Residuals

- 369 ms BKK↔Europe geographic floor persists regardless of tuning (F008); only a tunnel-endpoint move changes it.
- Even after S002, cold-model first token ≈ 6 s if residency is lost (S006).
- Cloudflared system journal and dmesg unreadable by `bom` on C2 — cloudflared log errors not excluded by surveys.
- CF→C2 hop time is derived, not instrumented.
- S004 rests on confirmed slow queries + observed stall/recovery correlation; the heavy endpoint was not deliberately replayed.
- OWUI exit-137 chronic flap risk unchanged; restart=always is the mitigation; boot→healthy 25-80 min under load.
- Single-container replace only for OWUI (no rolling two versions on one DB) after verified Postgres backup.
- UA memory relief is owner-blocked; alert-only does not create headroom.
- CB1 zombies grow until owner recycles n8n.
- AM4 UFW enable carries SSH-lockout risk until port-99 rule is proven from a second session.
- i9 admission gate + ESU remain owner-blocked; NAS swap clear root-blocked (margin healthy).
- Mac/UA cannot form direct tailscale paths until owner NAT/firewall work.
- 13 stale RUNNING hub jobs (art#57247) — none cancelled; owner decides.
- No paid z.ai/Anthropic/Moonshot calls were made for any input survey.

---

## 12. IRON Rules Summary (46 total)

The canonical 46-rule list lives in the GOD CONFIG series; v8.0 enforces it in full. Rules explicitly exercised by this blueprint's inputs:

| Rule | Content | Where applied |
|---|---|---|
| IRON 19 | Price API `168.119.176.113:5000` — no auth, no TLS change, no change at all (external service) | §7 no-touch; art#57278 F-findings |
| IRON 38 | No sshd / PasswordAuthentication / PermitRootLogin edits or recommendations — inventory only | CAT/CB1 surveys; forbidden list |
| IRON 40 | LiteLLM pin reconciled to live 1.106.5; downgrade only on owner order; 1.1070 BANNED | §6/§8 |
| IRON 41 | No DNS / resolv.conf changes | forbidden list |
| IRON 46 | Happy Meal update flow — version checks are read-only; upgrades only via owner windows; never auto-update production (full procedure in HOW-TO v5.0 §Happy Meal Update Flow) | art#57077; §6 |

Standing locks that duplicate IRON force: n8n OWNER_HOLD (NAS + CB1); gpt-oss-120b LIVE_NO_TOUCH; ComfyUI HTTP_API_ONLY; AM4 FX28 untouched; CAT OWNER_EXECUTE; i9 D: UNTOUCHABLE; webui credentials untouched; secrets never reproduced in artifacts; LiteLLM restarts only 03:00-06:00 ICT after 2-minute drain; timestamped backup before every change; retry contract max 2 attempts / 10 s cooldown; poller contract ≥ 5 min on :3000/:4000/docker-exec; SpendLogs prune only >1M rows or >2 GB with pg_dump first.

---

## 13. Monitoring & Alerting

**Post-fix verification set (run from a Bangkok station, not from C2 — a C2 hairpin is not the user's number):**

1. 10-16 shots `GET https://webui.siam2r.com/api/version`, record `time_starttransfer`. **Pass: median ≤ 0.45 s AND max ≤ 0.80 s.** Today: median 1.286 s, max 3.243 s. Baseline floor: 369 ms median.
2. From C2: `curl --max-time 5 http://100.118.133.38:11434/api/version` → 200. **This is the S002 gate.** (000 today.)
3. `tailscale ping --c 4 100.118.133.38` from C2 — pass: no sample > 500 ms, preferably one `direct` line.
4. Mac `ollama ps` shows qwen38-uni ctx 8192; two consecutive 10-token localhost generates — second < 1 s with load ≈ 0.
5. `docker top open-webui` shows intended worker count.
6. `SELECT length(content), is_active FROM function WHERE id='theme_designer_pro';` matches the owner-chosen state.
7. One real logged-in webui send returning Thai text. `/api/version` is never proof that generation works.
8. C2 diskstats 15 s delta: sda read/write await < 20 ms at low throughput (S001 gate).
9. LiteLLM `/health/liveliness` < 100 ms during a SpendLogs v2 read (S004 gate).

**Alert contract (v11, updated with v8 tripwires):**

| Signal | Warning | Critical | Now |
|---|---|---|---|
| UA memory available | < 20 GiB | < 16 GiB or any swap-out > 10 s | 26 GiB — OK, swap 18 GiB occupied |
| C2 netdata CPU | > 50% one core 15 m | > 75% one core 15 m | 12.6% — OK |
| CB1 chromium zombies | > 20 | > 50 | **144 — TRIPPED (owner window)** |
| Mac↔C2 path | DERP 24 h | generation health fail OR localhost 10-token > 30 s | DERP persists; localhost 0.73 s warm — warn |
| C2 storage latency (NEW) | sda await > 50 ms sustained | > 100 ms sustained | **132/162 ms — TRIPPED (provider)** |
| BKK TTFB median (NEW) | > 0.60 s | > 1.0 s | **1.286 s — TRIPPED** |
| LiteLLM liveliness (NEW) | > 500 ms | 503 readiness | recovered 8.7-34 ms — watch |
| live_router model row | is_active=false | — | OK (qwen38-uni active) |
| cloudflared ingress dupes | > 0 | — | 2 dupes — known, owner intent pending |
| CAT backup age | > 26 h | > 48 h or offsite missing | **TRIPPED (since 11-01)** |
| CAT TLS expiry | < 14 d | < 7 d | monitor |
| cb1 chart.icafeforex.com cert | < 30 d | — | 2027-01-05 — far |
| NAS USB usage | > 75% | > 85% | 65% — OK |
| NAS swap residual | > 1 GB with < 4 GB avail | — | 678 Mi/13 Gi — OK |
| kern.log | > 100 MiB | logrotate failure | CAT 174 MB — TRIPPED (cleanup covers) |
| AM4 syslog | > 200 MB | — | 261 MB — TRIPPED (ACTION-20/cleanup covers) |
| Ollama version | not 0.40.14 after approved window | locked-param regression | Mac/UA OK; AM4/i9 blocked |
| AM4 exposure | — | ufw inactive AND any 0.0.0.0 DB publish | **TRIPPED (ACTION-05)** |
| price router | any false-positive report (first weeks) | inlet p95 added latency > 1 s | v2 live, watch |

**Cadence:** daily sweeps and weekly/monthly tasks are defined operationally in GOD HOW-TO v5.0 (companion document). LiteLLM/OWUI restart window remains 03:00-06:00 ICT after 2-minute drain.

---

```yaml
verification:
  live_changes_by_this_task: NONE
  ssh_by_this_task: NONE
  inputs_read_fully: [57325, 57278, 57277, 57247, 57077, 56687, 56686]
  merged_duplicates: [S002=F001, S005=F004, S007=F002, S008=F003, S009=F006]
  locked_params_touched: false
  n8n_restart_included: false
  sshd_dns_changes_included: false
recommendation: INSPECT
```


---

# GOD BLUEPRINT v8.1 Addendum — BOM AI v2.1.8 deltas (2026-11-14, handoff art#60827)

Adopted by BOM LLM release v18.0.0. These are live-state deltas recorded by the BOMAI project closure (v2.1.8, 14 Nov 2026) that sit on top of v8.0.

## 1. Pro Tier Now GGUF (was MLX-only)
- BEFORE: Pro = MLX NVFP4 21.6GB Apple Silicon ONLY
- AFTER: Pro = GGUF Q4_K_M (text 16.5GB + mmproj 518MB) all 3 OS
- Ollama tags: `siamcafe/bom-ai:pro-v2.1.8` (GGUF), `siamcafe/bom-ai:light-v2.1.8`
- Mac still runs MLX nvfp4 as bomai-pro:latest (21.6GB), NOT the GGUF
- ubuntu-ai has GGUF Pro tag + source files at /data/models/709l-gguf/
- Pro GGUF sha: text 5c45be04, mmproj d6bb4695
- Blueprint impact: model routing table, tier specs, disk/VRAM requirements

## 2. OWUI Web Search Default OFF
- BEFORE: builtinTools.web_search=true, Default Features web_search=ON, admin webSearch='always'
- AFTER: builtinTools.web_search=false, Default Features OFF, admin webSearch=null
- 3 layers fixed: model preset + admin default_interface + builtin tools
- Capabilities web_search KEPT true (user can manually enable)

## 3. Gateway rc3 Stream Han Resume
- bom_runtime.py sha256: cd1d5f1439d831d68b957fbe50dce015851466504c3f532947786208366c6857
- NEW: MAX_STREAM_RESUMES=3, MIN_RESUME_KEPT_CHARS=40
- Chain: pass1 -> resume (up to 3) -> ONE rc1x rewrite -> v2.1.6 cut notice
- Stream cut rate: 0/272 (was 13.97% on v2.1.6, bomai-chart-official)
- think=false enforced by gateway (Ollama 0.40.16 doesn't support PARAMETER think)
- Full K3 verdict + 8-gate evidence: hub art#60117 (GOD BLUEPRINT — stream Han resume gateway)

## 4. Version 2.1.8
- Installer version: 2.1.8 (BAT sha 2a2e864c, SH sha eef9fc3c, MAC sha a1c6d4d4)
- Website bomai.app: v2.1.8 all 15 languages; JSON-LD dateModified: 2026-11-14
- GitHub: v2.1.8 release with 3 assets; HuggingFace: v2.1.8 README + release.json

## 5. Mac OWUI Re-seed
- Default model: bomai-pro (was bomai-gemma3); preset "BOM AI Pro" desc "709-L 27B DavidAU"
- LaunchAgent DEFAULT_INTERFACE_SETTINGS updated; 0 users, 0 chats (clean state)

## 6. Fleet Versions (14 Nov)
- LiteLLM 1.108.8 LTS applied C2/UA/AM4 (2026-11-14); ComfyUI v0.45.0 fleet (i9:8189 included); Ollama 0.40.13-0.40.16 (Mac fleet daemon 0.40.16)
- keep_alive "24h" on all routes (NEVER "-1")
