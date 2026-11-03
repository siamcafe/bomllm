# GOD BLUEPRINT v5.2 — BOMLLM Fleet (C2 performance survey + fix + release v11)
project: bom-llm
step: fix_c2_perf_survey_fix_release
version: "5.2"
previous: "5.1"
base_document: "art#55863 (GOD BLUEPRINT v5.1 — carried in full; this is a delta update)"
date: "2026-11-04"
author: "zcode (GLM-5.3), spec art#55876, plan art#55871 (Fable v1.0)"
recommendation: INSPECT
references:
  - "art#55876 — execution spec (this task)"
  - "art#55871 — Fable blueprint v1.0 (hypotheses H1-H5, decision tables)"
  - "art#55862 — K3 fix report (SSH 2-min root cause, tailscale dependency map, squid audit)"
  - "art#55863 — GOD BLUEPRINT v5.1"
  - "art#55864 — HOW-TO v4.1"
  - "art#55651 — GOD CONFIG v9.0 (locked params + LiteLLM general_settings target)"
  - "art#55406 — v10 release report"
  - "art#53622 — HF browser web-UI edit method"

v5.2 changes vs v5.1:
  1: "NEW Phase P: C2 performance survey (read-only, external + on-box) settling Fable H1-H5"
  2: "SSH brute-force guard PERSISTED as systemd unit c2-ssh-guard (was live-but-volatile iptables rule)"
  3: "LiteLLM DB-load policy verified against GOD CONFIG v9.0 target — live config already at target (no key added, no restart)"
  4: "Poller interval policy: opshub-* timers audited (all already >5 min; hourly/daily/weekly/monthly); no cron line matched the */1-*/4 relax rule"
  5: "Residuals closed: charming_gauss removed (v0.13.0 image kept); RR5 /static/bomai PNGs were genuinely absent (dir held js/css only) -> heroes delivered by v11 release; squid tailscale-rebind systemd drop-in installed"
  6: "Verification gates re-measured from AM5 (external TTFB median/p90 + SSH connect + stress 8/8 + headless Chromium)"

---
P. PHASE P — C2 PERFORMANCE SURVEY + FIX + VERIFY (2026-11-04, zcode)

P.1 External baseline (AM5, pre-fix, 2026-11-04T04:58:55+07:00, p1_external_baseline.txt)
  api_version_ttfb_s: {n: 10, median: 0.103, p90: 0.171, min: 0.097, max: 0.386}
  favicon_ttfb_s: {n: 10, median: 0.181, p90: 0.350, max: 1.765}
  hub_jobs_ttfb_s: {n: 10, median: 0.274, p90: 0.629}
  ssh_connect_s: [4.679, 10.021, 11.339, 1.815, 1.001]
  context: "load ~3.8 calm window; NOT the load-15 window where Fable measured 1.17-6.53 s"

P.2 On-box survey (survey.sh, 23:00-23:09 CET, p1_survey_c2.log)
  s1_runqueue: "r=1-7 on 12 vCPU, idle 82-99%, steal 0"
  s2_real_cpu_top15_30s:
    - "uvicorn open_webui 44.0% (33.3u/10.7s) — single OWUI worker"
    - "tailscaled 35.9% (7.4u/28.5s) — mostly sys = KN1 phantom IRQ billing"
    - "cloudflared 30.1% (8.1u/22.0s)"
    - "litellm 24.9% (20.2u/4.6s)"
    - "ksoftirqd/0 10.1 | live_router 9.6 | postgres 8.8 | valkey 8.3 | containerd 8.1 | searxng 7.8 | dockerd 6.9"
  s5_pg_stat_activity: "3 snapshots: only survey query active + 4 idle connections"
  s6_tables: "LiteLLM_SpendLogs 153,425 rows / 773 MB / 1,193 dead tup (below 1M-row / 2GB prune gates)"
  s7_tps: "litellm_db_tps=0 over 60 s"
  s9_config_keys_live: "general_settings already had proxy_batch_write_at 60, disable_error_logs true, maximum_spend_logs_retention_period 30d; store_prompts_in_spend_logs absent; bomai-safe block has NO repeat_penalty (clean)"
  s13_pollers: "opshub-c2-monitor hourly@:48, light daily 03:10, deep Sat 09:10, audit monthly 1st; docker exec rate 0 across 12x5 s samples; crontab observer runs * * * * * (untouched — not a */1-4 target per spec rule)"
  s14_cloudflared: "ha_connections=4 (sin07/09/12/16), total_requests 28361, request_errors 2590 cumulative, 292 journal err/h (client 'context canceled' aborts on hub route + :4000)"
  s15_localhost_ttfb: "api 0.005-0.016 s, static 0.007-0.015 s, litellm liveliness 0.006-0.052 s"
  s16_bruteforce_24h: "3,285 lines; 180.183.109.x 2,189 (owner ISP /16 = NEVER-BLOCK — reported to owner); 102.220.163.x 1,671 + 102.220.160.x 1,614 (pre-block hours, /22 DROP live); Accepted full journal: 0 from 102.220.0.0/16"
  s17_residuals: "charming_gauss=Created image v0.13.0; bomai_static_v1 holds ONLY js/css (no PNG) -> /static/bomai/*.png 404 were missing files, not name mismatch (H5 verdict); squid both listeners; no tailscaled drop-ins yet"
  s18_god_config: "bom-thai-chat params 7/7 PASS; functions=18"

P.3 Hypothesis verdicts (Fable H1-H5)
  H1_litellm_pg_loop: "NOT SUPPORTED — tps=0, conns idle, tables below prune gates, config already at GOD CONFIG v9.0 target, litellm real user CPU 20.2% (vs 115% during the load-15 window)"
  H2_poller_pressure: "NOT SUPPORTED — all opshub timers >5 min, docker exec rate 0, r=1-7"
  H3_edge_vs_box: "SUPPORTED — cloudflared healthy (ha=4), localhost 0.01 s vs external 0.10 s median; remaining delta is EU edge path (~0.09 s), not C2 queueing"
  H4_other_subnets: "PARTIAL — 24 h counts dominated by pre-block hours of the already-blocked /22; post-block fail2ban currently-failed=0; NEW owner-ISP failed-auth churn 2,189/24 h (NEVER-BLOCK, owner to investigate)"
  H5_rr5_statics: "SUPPORTED as missing files — static dir had no PNGs at all; heroes supplied by Phase 5"

P.4 Fixes applied (all on C2, sudo; logs p2_fix_*.log)
  ssh_guard: "DONE — /etc/c2-ssh-guard.list (1 CIDR 102.220.160.0/22) + /usr/local/sbin/c2-ssh-guard.sh + c2-ssh-guard.service enabled+active; list_lines=1 drop_rules=1; NEVER-BLOCK refused by script design; /24 candidates not added (already inside the /22)"
  litellm: "DONE as verified-no-change — changed=none (keys already at target), SpendLogs 153,442 rows / 811,016,192 bytes below gates, ErrorLogs 0 -> no prune, NO restart (decision row 1)"
  pollers: "DONE as verified-no-change — all 4 opshub timers kept (>5 min), 0 cron lines matched relax rule; crontab backups saved"
  charming_gauss: "DONE — docker rm (v0.13.0 image kept, 6.44 GB)"
  rr5_statics: "DONE via Phase 5 — hero_banner_v11.png (+hero_banner_v10.png copy) placed into bomai_static_v1 (persistent masters) AND docker cp'd into live container STATIC_DIR /app/backend/open_webui/static/bomai/ (serving path; no OWUI restart; both URLs 200). logo.png/favicon.png under /static/bomai/ remain absent (no candidates; reported)"
  bomai_safe_repeat_penalty: "NOT NEEDED — LiteLLM bomai-safe block already clean (no repeat_penalty key); UA modelfile verified 7/7 with repeat_penalty 1"
  squid_rebind_dropin: "DONE — /etc/systemd/system/tailscaled.service.d/squid-rebind-v52.conf (ExecStartPost sleep 8 + squid -k reconfigure); tailscaled NOT restarted to test (per FORBIDDEN); both squid listeners verified present"

P.5 Verification (post-fix, AM5 external + on-box; p3_external_after.txt, p3_verify_c2.log, qc_headless.json)
  external_am5_after:
    api_version_ttfb_s: {n: 10, median: 0.093, p90: 0.182, max: 0.234}
    favicon_ttfb_s: {n: 10, median: 0.118, p90: 0.186}
    hub_jobs_ttfb_s: {n: 10, median: 0.236, p90: 0.704}
    ssh_connect_s: [0.962, 0.861, 1.084, 1.123, 1.048]
    verdict: "PASS (median < 0.5 AND p90 < 1.0); improved vs baseline (api median 0.103 -> 0.093; ssh median 4.679 -> 1.048, worst 11.34 -> 1.12)"
  internal_c2:
    load1_samples: [1.03, 1.05, 5.42]   # all < 8; 3rd = midnight CET cron burst, vmstat idle 99%
    owui_200_ttfb_s: 0.017
    litellm: "liveliness 200 + readiness 200"
    services_active: "cloudflared, c2-ssh-guard, tailscaled, squid"
    tailscale_peers: 8
    squid_listeners: "100.83.20.100:18080 + 109.123.233.171:18080"
    god_config_7of7: "PASS (bom-thai-chat)"
    functions: 18
    qdrant_collections: 13
    guard_drop_rules: 1
  stress_8of8: "7/8 in the mandated 120 s window (T1 200/23.2s, T2 200/19.0s, T4 200/28.1s, T5 200/71.8s/928KB, T6 200/7.3s, T7 200, T8 200; T3 web-search HTTP 000 at 121 s). T3 retry at 180 s: 200 in 106.6 s / 95,897 chars — search path healthy, 120 s window too tight for a full web-search roundtrip. Release not blocked (spec: <8 records failures without blocking)."
  hero_static_serving_finding: "OWUI serves /static/* from container STATIC_DIR=/app/backend/open_webui/static (baked at image build), NOT from the bomai_static_v1 frontend bind (a new file in the bind 404s). v11/v10 heroes deployed via brand-dir copies (persistent masters) + docker cp into the live container (no restart); external URL 200 verified. Bake into image or add a backend bind at next OWUI rebuild."
  headless_qc:
    landing_status: 200
    images_broken: 0
    note: "networkidle never fires on OWUI (socket.io) — wait_until=load + 9 s settle; /static/bomai PNG 404 pre-release (heroes delivered by Phase 5)"

P.6 New policies (binding from v5.2)
  ssh_guard_list_maintenance:
    rule: "Brute-force subnets are blocked ONLY via /etc/c2-ssh-guard.list + c2-ssh-guard.service (iptables INPUT DROP tcp/99). Never write rules into DOCKER chains; never install iptables-persistent; NEVER-BLOCK ranges are refused by the guard script itself."
    add_cidr: "append /24 to the list (cap 10 entries) only when: >=100 Invalid/Failed lines in 24 h AND zero Accepted in the FULL journal AND no overlap with NEVER-BLOCK; then systemctl start c2-ssh-guard; verify drop_rules == list_lines"
    never_block: ["180.183.0.0/16 (owner ISP)", "122.155.168.7 (CAT)", "109.205.176.7 (Contabo1)", "171.6.136.143 (am4_brain)", "100.64.0.0/10 (tailnet)", "192.168.0.0/16 (LAN)"]
  litellm_db_load:
    rule: "LiteLLM general_settings target is the GOD CONFIG v9.0 set (proxy_batch_write_at 60, disable_error_logs true, maximum_spend_logs_retention_period 30d, background_health_checks false, database_disable_prepared_statements true). Only ADD keys absent from live config; never modify keys GOD CONFIG defines. SpendLogs prune only when >1M rows OR >2 GB, only after pg_dump -t backup exists, only rows older than 30 days, batched 50k + VACUUM ANALYZE. LiteLLM restart only in the 03:00-06:00 ICT window after a 2-minute drain, health gate 20x10 s; otherwise keys take effect at next natural restart (reload interval excepted)."
    measured: "2026-11-04 tps=0, SpendLogs 153k rows/773 MB — loop NOT active; H1 disproven for this window"
  poller_min_interval:
    rule: "Monitoring timers/cron must not hit :3000/:4000 or run docker exec more often than every 5 minutes; opshub-* systemd timers relax to 15 minutes via /etc/systemd/system/<timer>.d/interval-v52.conf drop-in (never disable); cron minute field */1-*/4 that targets :3000/:4000/docker exec is lengthened to */5 (backup crontab first). Warm-pin/keep-alive crons are GOD pipeline — keep, only lengthen if <5 min."
    measured: "2026-11-04: all 4 opshub timers already hourly-or-slower; docker exec rate 0/12 samples; nothing to relax"

P.7 Residual risks / open items (v5.2)
  - "KN1 phantom CPU accounting on C2: permanent (host KVM), diagnose with utime/stime only"
  - "OWUI single uvicorn worker ~44% real CPU at calm load: architectural; Phase C (move OWUI+Postgres off C2 to AM4 when EA burn ends) is the structural fix — owner decision"
  - "EU origin latency floor ~0.09-0.25 s to Thai users via CF SIN edge -> C2 path: structural (Phase C/D or Contabo node migration — owner decision / Contabo ticket)"
  - "Owner-ISP failed-auth churn: 2,189 Invalid/Failed lines/24 h from 180.183.109.x (NEVER-BLOCK) — owner should identify the misauthenticating client at 180.183.109.179 network"
  - "Mac ollama CLI skew (server 0.40.14 / CLI 0.40.10): report only, untouched"
  - "carried from v5.1: Contabo1 zombies + n8n export; UA/AM4 EA-burn loads; Mac DERP-sin relay; OWUI exit-137 flap untraced"
  - "/static/bomai/logo.png and /static/bomai/favicon.png remain 404 (no candidates ever existed; only heroes were regenerated) — future brand drop needed if required"

P.8 Owner decisions (report-only, no agent action)
  - "Phase C/D: move OWUI + Postgres off C2 (AM4/NAS) — gate: EA burn end"
  - "Contabo: open ticket about oversold node / silent steal / migration or resize"
  - "tailscaled full on-demand on C2: only after Phase C removes 100.x dependencies (§O.3)"
  - "sshd_config / PasswordAuthentication / resolv.conf: IRON 37/38/41 owner-only"

---
O. PHASE O — C2 SSH SLOW-CONNECT (2026-11-04, K3) [carried unchanged from v5.1]

O.1 Diagnosis evidence chain
  Owner symptom: SSH to C2 takes ~2 minutes (2026-11-04 03:06 ICT, load 15.34).
  Measured during fix window (21:15-21:35 CET, load 8.5-11.2): connects 8.0s -> 15.4s -> 19.0s -> 13.8s (degrading under diagnostic load; never 2min — contention-correlated).
  - sshd -T (READ ONLY): usedns no, gssapiauthentication no — CLEAN
  - getent reverse lookup: 33ms — CLEAN
  - journal: Accepted publickey and session opened SAME SECOND — auth path fast once reached
  - ss :99 conns 6 (limit 10 unauth) — near gate during bursts
  - brute-force churn: sshd 1385 lines/h from 102.220.160.0/22; fail2ban 103 CPU-min + journald 119 CPU-min since Nov02
  - vmstat r=10-18 on 12 vCPU with id 81-89% (silent host steal, KN1)
  Root cause chain: constant preauth brute-force stream keeps sshd children + fail2ban + journald hot; on the oversold KVM new TCP/KEX handshakes wait for CPU slices -> connect time scales with runqueue (~2min at load 15; 8-19 s at load ~10).

O.2 Actions applied (K3, all reversible)
  - iptables subnet block 102.220.160.0/22 tcp/99 DROP after verifying ZERO historical Accepted from the range (LIVE; v5.2: now PERSISTED via c2-ssh-guard.service)
  - tailscaled NOT stopped — dependency-proven (O.3); on-demand scripts installed /usr/local/bin/tailscale-{start,stop}.sh
  - Squid C2 + Contabo1 audited: authenticated ncsa proxies, proxy_auth REQUIRED, deny all — KEPT
  - query-engine = LiteLLM Prisma engine — component, untouched
  - sshd_config / resolv.conf READ-ONLY verified clean (IRON 37/38/41)

O.3 C2 Tailscale dependency map (why on-demand is conditional) [UNCHANGED, carried from v5.1]
  C2 has NO LAN route to 192.168.1.0/24; every home-fleet path rides Tailscale 100.x:
    - cloudflared hub.siam2r.com     -> 100.111.221.102:8191 (hub public ingress, incl. artifact push channel)
    - cloudflared docs.siam2r.com    -> 100.111.221.102:8060 (docs public ingress)
    - cloudflared llm overlay + /worker-ws -> 100.80.16.53:3100 (chart overlay + worker WS)
    - socat qdrant-relay :6333       -> 100.80.16.53:6333 (RAG queries)
    - socat rag-lb-relay :7998       -> 100.80.16.53:7997 (Infinity embeddings)
    - LiteLLM config.yaml x15 api_base -> 100.118.133.38:11434 (Mac qwen38-uni PRIMARY generation)
    - /etc/hosts 5x 100.x fleet names
  Verdict: tailscaled on C2 is production-critical infrastructure. On-demand = scripts installed + stop-impact documented + boot-enabled retained. Full stop+disable remains owner-decidable.

O.4 v5.1 residuals superseded by P.7 where overlapping.

O.5 K3 verification (2026-11-04 21:41-21:55 CET) [carried]
  SSH connect 1.5/0.9/2.8 s PASS; iptables 29 pkts/2232B dropped in 3 min; invalid-user lines 30-60/h -> 1;
  OWUI 200/0.015 s; LiteLLM 200/0.019 s; public TTFB hairpin 0.28-0.34 s; qdrant relay 200 (13 collections);
  squid tailnet listener restored; load decaying 11.19 -> 9.43.

---
UNCHANGED SECTIONS
  "S1 Hardware inventory, S2 role assignment, S3 service dependency map, S4-S12 ops content,
   S13 fleet baseline — carried from v5.0 (art#55840) via v5.1 (art#55863) unchanged.
   GOD CONFIG v9.0 (art#55651) remains the locked configuration; no parameter touched in this task."
