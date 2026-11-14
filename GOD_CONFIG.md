<!-- GOD CONFIG v12.0 — full sync from hub art#60163 into BOM LLM release v18.0.0 (2026-11-14). keep_alive "24h" rule (never -1) + 7/7 locked params unchanged. DOC_ONLY_RECONCILED_LIVE_R11_R13. -->

# MEGA GOD CONFIG v12.0 — BOMLLM System
# Date: 2026-11-13
# Full v11 data retained and reconciled against live state: R11 (art#59888), R12 (art#59917),
# R13 (art#59929) + this task's read-only live survey (evidence logs in god_v12_report).
project: bom-llm
step: fix_god_config_v12_thai_e2e
version: '12.0'
previous: '11.0'
date: '2026-11-13'
status: DOC_ONLY_RECONCILED_LIVE_R11_R13
recommendation: INSPECT
scope_note: DOCUMENT ONLY. No install, upgrade, container/config/service change was performed
  by v11 or by v12. v12.0 reconciles the document with the live fleet after R11-R13 changes
  (Mac queue fix, AM4 thai_prod re-route, key renewals) and records the first Thai E2E
  measurement set plus the OLLAMA_NUM_PARALLEL decision. Unknown values remain unknown.
fleet_scope: 8 surveyed production machines; AM5 command station recorded separately
shared_instance_scope: 'This OWUI instance serves BOTH projects: BOMLLM (bom-llm) and BOMAI
  (bomai — own banner, custom buttons, branding).'
credential_policy: Secrets are never reproduced. Redacted fields retain only the secret
  reference name.
source_artifacts:
  god_config_v10: 56564
  god_blueprint_v6: 56565
  previous_k3_report: 56543
  mega_implement_report: 56578
  atom_survey: 56608
  grok_fleet_survey_20261106: 56483
  god_config_v9: 55651
  god_blueprint_v5_2: 55907
  god_config_v11: 56686
  r11_report: 59888
  r12_report: 59917
  r13_report: 59929
changes_from_v11:
- '[CHANGED v12] C2 global num_retries is now zero (R11). Three routes carry per-route retry
  overrides above the global zero (thai-chat-rt, redhat-mcp-rt, bomai-safe) — live, untouched.'
- '[CHANGED v12] All six Mac-to-Mac fallback chains were removed by R11 from BOTH
  litellm_settings and router_settings; vision pairs now fall back to zai-glm-4.6v only;
  routing_strategy simple-shuffle. Mac-to-Mac fallback count live = zero.'
- '[CHANGED v12] C2 warm_pin cron is now warm_pin_v13_ps_only: GET /api/ps every 5 min against
  http://100.118.133.38:11434 (R11); /api/generate pinning is gone.'
- '[CHANGED v12] AM4 thai_prod upstream is http://100.118.133.38:11434 (R12; was LAN
  192.168.1.254). Live config path /data/migrated/litellm/config.yaml; timeout 300;
  keep_alive 24h; num_ctx 8192.'
- '[CHANGED v12] LiteLLM key expiries: kw-engine-nas and cctv_runner_flood_runner_p044
  renewed to 2027-02-10 21:39:04.426 (R13). cctv_runner_flood_runner_vision_p048 still
  expires 2026-11-11 (expired, zero presentations per R12, left in place).'
- '[CHANGED v12] AM4 hub image is agent-hub:webstats-v1-20261104_0301 (verified by live
  docker inspect this task; v11 recorded governance-v2-20261029).'
- '[CHANGED v12] Fleet LiteLLM moved to the 1.108.4 line: C2 bomllm/litellm:1.108.4-pil2,
  UA ghcr.io/berriai/litellm-non_root:v1.108.4, AM4 bomllm/litellm:1.108.4-pil2 (R13 D3).
  C2 Open WebUI 0.13.3 (was 0.13.0); C2 valkey 9.1.3-alpine (was 9.1.2).'
- '[NEW v12] Mac runs THREE ollama serve processes; fleet traffic 100.118.133.38:11434 is
  served by the BOM-AI binary v0.40.14 with qwen38-uni resident (31.02GB MLX nvfp4);
  loopback 127.0.0.1:11434 is the desktop app v0.40.16 idle. See mac.ollama_v12_topology.'
- '[NEW v12] First Thai E2E measurement set: three fresh probes median 83.45s / p90 87.98s,
  all answered in Thai, zero English contamination; identical prompts inside the valkey
  cache ttl 300 return cached copies in ~0.08s. See thai_e2e_probe_20261113.'
- '[NEW v12] OLLAMA_NUM_PARALLEL decision recorded: KEEP 1. See ollama_num_parallel_v12.'
- '[LOCKED v12] All v11 locked parameters, function hashes, protected deviations, production
  locks and never-touch rules carry over unchanged. v12 changed DOCUMENTS ONLY.'
changes_from_v10:
- '[CHANGED v11] LiteLLM pin reconciled UP to the live fleet: 1.106.5 (C2/AM4 bomllm/litellm:1.106.5-pil2,
  UA prod ghcr.io/berriai/litellm-non_root:v1.106.5, authorized prior lane). Written floor stays
  1.106.4; 1.107.0 remains COMPROMISED/BANNED. Downgrade to 1.106.4 only on explicit owner order
  (staged script), 03:00-06:00 ICT after 2-minute drain. No restart performed or scheduled.'
- '[CHANGED v11] C2 OWUI bind is now 127.0.0.1:3000->8080 LIVE (compose migration DONE after
  art#56578 C2-3 was superseded); public path is cloudflared only. OWUI remains user 0:0 with
  no memory cap — interim live memcap staged (ACTION-17).'
- '[CHANGED v11] Mac Ollama CLI aligned to 0.40.14 (art#56578 MAC-2); server 0.40.14; qwen38-uni
  7/7 locked. NEW finding: 70s localhost 10-token generate timeout; DERP sin + MagicSock
  ReceiveIPv4 down (ACTION-06).'
- '[CHANGED v11] Price pipeline (bom_price_pipe/router/tool) LIVE but defective: global router
  with broad intent + 10s inlet sleep (ACTION-02), no model row for the pipe, chart_reason model
  row inactive (ACTION-03), source mislabeled MT5 WebSocket with local-clock stamping.'
- '[CHANGED v11] live-router env model qwen38-chat is an INACTIVE model row; target qwen38-uni
  (ACTION-04).'
- '[CHANGED v11] AM4 is now the widest confirmed exposure: ufw inactive, llm-postgres 0.0.0.0:5432,
  LiteLLM/Comfy/chart wide (ACTION-05). AM4 netdata persisted+bound (DONE art#56578). AM4 kern.log
  rotated (DONE); syslog 261MB + audit backlog NEW (ACTION-20).'
- '[CHANGED v11] CAT: PHP CLI default still 7.4 with 8.3.33 present, PHP 5.6 on disk (ACTION-07);
  backups stale since 2026-11-01 (ACTION-14); CSF TCP_IN lacks 19999 for the UA netdata stream
  (ACTION-11). All CAT work OWNER_EXECUTE.'
- '[CHANGED v11] CB1 zombies re-parented to n8n itself (75, pid 65171); browserless recycle done
  did not reap them; n8n OWNER_HOLD -> owner-window recycle (ACTION-08). INPUT:9090 shadow rule
  removal staged (ACTION-22).'
- '[CHANGED v11] cloudflared on C2 has 3 llm.siam2r.com rules; first (AM4:3100) wins; dedupe
  staged with owner intent decision (ACTION-10).'
- '[CHANGED v11] UA netdata rebound 127.0.0.1+tailscale (DONE); secret files mode 664 -> 600
  staged (ACTION-12); 2 litellm-parent zombies tied to any future windowed recreate.'
- '[CHANGED v11] NAS: scripts.d off + node_exporter_old stopped (DONE); NEW: 3 auto_cron.sh
  zombies, 692MB swap (BLOCKED no-root), docker PATH note (ACTION-21).'
- '[LOCKED v11] Seven model parameters, 21 function hashes (18 baseline + 3 price), music
  pipeline, protected deviations, route constraints, no sshd/DNS/PasswordAuthentication changes,
  n8n OWNER_HOLD, gpt-oss-120b LIVE_NO_TOUCH, ComfyUI HTTP_API_ONLY, FX28 untouched.'
locked_params:
  temperature: 0.6
  top_p: 0.95
  top_k: 20
  repeat_penalty: 1.0
  presence_penalty: 0.0
  num_predict: 4096
  num_ctx: 8192
  enforcement: UNCHANGED values. UA gpt-oss-120b LIVE_NO_TOUCH; UA placements FROZEN on memory
    pressure; AM4 FX28 and all ComfyUI untouched.
model_matrix:
  mac:
    compliant_models: [qwen38-uni, bomai-pro, bomai-mini, bomai-gemma3]
    embedding_only: [nomic-embed-text, bge-m3]
    verified_live: '[v12] qwen38-uni resident on the FLEET instance 100.118.133.38:11434
      (v0.40.14, MLX nvfp4, 31.02GB, ctx 8192, digest 549badb7b84d..., observed 2026-11-13;
      residency is DYNAMIC — /api/ps was empty before the first Thai probe, model reloads on
      demand). v11 record: 7/7 params on server 0.40.14, CLI 0.40.14 aligned 2026-11-06, 70s
      localhost generate timeout ACTION-06 (that hit the loopback instance).'
  ua:
    compliant_models: [qwen3-vl:2b, bomai-safe, bomai]
    verified_live: bomai-safe 7/7 + frequency_penalty 0 explicit on Ollama 0.40.14; gpt-oss-120b
      LIVE_NO_TOUCH (llama-server holds 13918 MiB, not an Ollama tag).
    protected_deviations:
      siamcafe_and_r4_prod: {num_ctx: 32768, num_predict: 16384}
      bomai-v3: {sampler: server-default, num_ctx: 8192, num_predict: 4096, parallel: 2}
      gpt-oss-120b: {sampler: server-default, num_ctx: 32768, status: LIVE_NO_TOUCH}
  am4:
    compliant_models: [bomai-safe]
    verified_live: bomai-safe 7/7 (atom survey re-read). bomai-safe SYSTEM text contradicts the
      price router (ACTION-13). siamcafe_base protected ctx 32768/predict 16384 retained.
    ollama: 0.40.13 — upgrade to 0.40.14 staged, BLOCKED on FX28 stop + owner window
      (/usr/local/sbin/am4_ollama_04014.sh deployed).
  i9:
    bomai-pro: {sampler: server-default, num_ctx: 8192, parallel: 1}
    ollama: 0.40.13, resident none, GPUs hold 12994/11066 MiB; WDDM blocks per-process VRAM;
      model_admission: DENY_UNTIL_ATTRIBUTION (ACTION-16).
  c2:
    bom-thai-chat: {temperature: 0.6, top_p: 0.95, top_k: 20, repeat_penalty: 1.0,
      presence_penalty: 0.0, num_predict: 4096, num_ctx: 8192, function_calling: legacy}
function_hash_baseline:
  as_of: 2026-11-06 atom survey (21 rows = 18 v9 baseline + 3 price additions)
  unchanged_18:
  - {id: claude_clone_ui, type: event, active: true, global: true, md5: effde04867ac44300052db601bd1e5be}
  - {id: theme_designer_pro, type: event, active: true, global: true, md5: 40e9a234a5a90874282d99ad122c1bc5,
     note: "scanner hits are JS regex exec, not Python exec; 20336 lines"}
  - {id: bomai_live_guard, type: filter, active: true, md5: 81b24e54612ceadbfa913be96762a6d7}
  - {id: bom_han_guard, type: filter, active: true, md5: 8a2a07031eddbc4709f0978965213116}
  - {id: bom_intent_filter, type: filter, active: true, global: true, md5: bd079a60e0dd908133874947425c7a94,
     note: "calls i9 :8188 and tailscale :18188; busy-check uses old raw :8188 queue URL and fails open (zcode lane)"}
  - {id: bom_ui_polish, type: filter, active: true, global: true, md5: a0ab989e36c54912f95786e297cd4d05}
  - {id: chart_image_resizer, type: filter, active: true, md5: 915403c0f39eaf533306de14bd16c230}
  - {id: think_toggle, type: filter, active: true, md5: 92836d96cdfd384506475fa743965be9}
  - {id: fast_no_think, type: filter, active: true, md5: ba92b120102f7330e41ec3502c834fbd}
  - {id: force_web_search_global, type: filter, active: false, global: true, md5: f84d9cc1e064ffc5a5eac0e9ea33406d,
     note: "leave inactive"}
  - {id: json_guard, type: filter, active: true, global: true, md5: c669dc582d55317bdcde8c94dbba2e1c}
  - {id: keyword_template_injector, type: filter, active: true, md5: 5600dd6281a8d38211c011d262eeb199}
  - {id: reasoning_effort_setter, type: filter, active: true, md5: 677046b806efa55820c5206e5713e528}
  - {id: search_button, type: filter, active: true, global: true, md5: 778c2be553ef7996e86a3abf6320ceaf}
  - {id: mql4_api_gate, type: filter, active: true, md5: 75d6defcadb70b469ebeed3535fa57da}
  - {id: music_yue2, type: pipe, active: true, global: true, md5: 1dfc29042539a09e0d2dc895f80a15d7,
     note: "calls i9 tailscale :18188"}
  - {id: deep_think_pipe, type: pipe, active: true, md5: fb30656fd055a13ce893371e7b553364,
     note: "calls litellm:4000, api.z.ai, api.moonshot.ai; no paid probes"}
  - {id: chart_reason, type: pipe, active: true, md5: 2fb57bf16d3a3464f3479948b54d0ab8,
     note: "model row INACTIVE (ACTION-03); targets host.docker.internal:11434"}
  price_additions_v11:
  - {id: bom_price_router, type: filter, active: true, global: true, md5: e631e42744c0b5c0d63529d3fff5f6f4,
     status: DEFECTIVE — replaced by ACTION-02 v2 (broad intent, 10s inlet sleep, silent except)}
  - {id: bom_price_pipe, type: pipe, active: true, global: false, md5: ec4d063177927fd42e6309d04aca0e17,
     status: DEFECTIVE — no model row, mislabels source (ACTION-03)}
  - {id: bom_price_tool, type: tool, active: true, lines: 60,
     note: "get_live_price has no symbol allow-list; tracked in ACTION-03 follow-up"}
machines:
  c2:
    identity: {host: contabo2-bom-llm, os: Debian 12, cores: 12, memory_gib: 47, gpu: none}
    addresses: {public_ssh: 109.123.233.171:99, tailscale: 100.83.20.100, ssh_user: bom}
    role: Public Open WebUI and LiteLLM control plane; search, relays, live router, price pipeline
    resource_baseline: 'atom 2026-11-06: load 9.52/9.83/9.55, vmstat idle 79-90%, steal 0,
      mem_available 43655MB, swap 0, disk 28% — load is not saturation.'
    cron: observer every minute; staggered 5-minute herd on phases 0-5; canaries/kv-push/
      backups/budget-guard/version-watch unchanged from v10. '[CHANGED v12] warm_pin is now
      warm_pin_v13_ps_only (R11): */5 * * * * curl -s --max-time 10 -o /dev/null
      http://100.118.133.38:11434/api/ps — GET /api/ps only, no /api/generate pinning.'
      Rollback crontab backup: /home/bom/backups/c2_crontab_before_k3_20261102T180018Z.txt
    litellm:
      image: bomllm/litellm:1.108.4-pil2  # [CHANGED v12] live per R13 D3
      version_pin_note: 'v12 PIN = 1.108.4 line (live healthy per R13 D3; fleet-wide
        authorized bump after v11). v11 pin was 1.106.5 (ACTION-09 history); written floor
        1.106.4; 1.107.0 BANNED. old container litellm_old_20261105_223945 exited 137 kept
        as rollback asset (v11 record).'
      binds: [100.83.20.100:4000->4000, 127.0.0.1:4000->4000]
      health: liveliness 200 in 0.072s; readiness 200 in 0.175s
      general_settings: {enable_drain_endpoint: true, background_health_checks: false,
        budget_duration: 1d, database_disable_prepared_statements: true, disable_error_logs: true,
        health_check_concurrency: 32, health_check_skip_disabled_background_models: true,
        master_key: REDACTED, max_budget: 5.0, maximum_spend_logs_retention_period: 30d,
        proxy_batch_write_at: 60, proxy_config_reload_interval_seconds: 300}
      primary_routes: bom-thai-chat, qwen38-uni, thai-gate, thai-chat-rt and most chat routes ->
        ollama_chat/qwen38-uni at http://100.118.133.38:11434; bom-writer num_ctx 16384;
        bomai-safe route sets temperature 0.6/repeat_penalty 1.0/num_ctx 8192 -> AM4 :11434;
        bomai-pro -> http://100.85.255.14:8080/v1; zai-fallback/zai-brain/glm-4.6v-flash/
        zai-glm-4.6v -> api.z.ai (no paid probes).
      num_retries: 0  # [CHANGED v12] global, R11; three routes keep per-route retry overrides above the global zero (thai-chat-rt, redhat-mcp-rt, bomai-safe)
      fallbacks_live_v12:
        litellm_settings: {qwen38: none, qwen38-chat: none, qwen38-code: none, qwen38-deep: none,
          bom-writer: none, qwen38-vision-alt: zai-glm-4.6v, qwen38-vision: zai-glm-4.6v}
        router_settings: {typhoon25-content: qwen38-chat, flood-runner: none, qwen38: none,
          qwen38-chat: none, qwen38-code: none, qwen38-deep: none, bom-writer: none,
          qwen38-vision-alt: zai-glm-4.6v, qwen38-vision: zai-glm-4.6v, thai-chat-rt: none,
          ragsa-narrate: none, redhat-mcp-rt: none}
        context_window_fallbacks: {flood-runner: none, bomai-safe: qwen38-chat,
          typhoon25-content: qwen38-chat}
        content_policy_fallbacks: {flood-runner: none}
        mac_to_mac_fallbacks: 0  # [CHANGED v12] R11 removed all 6+6
        routing_strategy: simple-shuffle
    open_webui:
      version: 0.13.3  # [CHANGED v12] live per R13 D3
      alembic: e42c8f710a36
      image_id_short: 549badb7b84d
      bind_live: 127.0.0.1:3000->8080 (compose migration DONE; cloudflared is the only public path)
      restart_policy: always
      user: 0:0 — interim live memcap staged (ACTION-17); non-root awaits owner Compose file
      websocket_support: true
      uvicorn_workers: 1 (single-worker architecture is a known residual — the ACTION-02 inlet
        sleep defect stalled ALL chat through this worker)
      env_pins_live: {ENABLE_NOTIFICATIONS: 'false', CHAT_RESPONSE_MAX_TOOL_CALL_ITERATIONS: '256'}
      env_unset_kept_off: [ENABLE_COMMENTS, USER_PERMISSIONS_CHAT_SIDE_CHAT, ENABLE_SUBAGENTS]
      knowledge_caps: unset (None = no cap)
      patch_binds: 14 files built against 0.12.5, rebased for 0.13.0 in the compose migration;
        index.html/apikey-button.js/keys.html remain the MEDIUM-risk chrome files; visual QC on
        BOTH BOMLLM and BOMAI surfaces passed post-migration per spec done-list.
      bomai_ui: static_mount bomai_static_v1 + brand dir + image binds preserved; 5/5 static
        assets verified; functions theme_designer_pro/claude_clone_ui/bom_ui_polish/bomai_live_guard/
        bom_han_guard/music_yue2 all active on baseline hashes.
    live_router:
      version: 1.1.0
      lines: 572
      bind: 127.0.0.1:8090
      image: live-router:v2
      network: host
      init: true
      model_env_live: qwen38-chat (model row INACTIVE — defect)
      model_env_target: qwen38-uni (ACTION-04)
      active_alternatives: [qwen38-uni, bom-thai-chat]
      panic_resume_auth: none (loopback-only; accepted risk, alert-contract watched)
      overlay_default: http://127.0.0.1:8095
    price_pipeline:
      endpoint: http://168.119.176.113:5000/price
      auth: none (EXTERNAL service — IRON 19: do NOT add auth or change)
      tls: none (same IRON 19)
      live_sample: {symbol: XAUUSD, bid: 4096.912, ask: 4097.08, source_timestamp: absent}
      components: {bom_price_router: global filter DEFECTIVE (ACTION-02),
        bom_price_pipe: pipe DEFECTIVE no-model-row (ACTION-03),
        bom_price_tool: tool active, no symbol allow-list (ACTION-03 follow-up)}
      labeling_fix: source = HTTP poll; fetched_utc stamped; source_timestamp marked absent
    cloudflared:
      type: systemd
      config: /etc/cloudflared/config.yml
      credentials_file: referenced, never read
      ingress_defect: llm.siam2r.com listed 3x; rule 1 (AM4:3100) wins; 127.0.0.1:4000 rule
        unreachable (ACTION-10 owner MODE decision)
      healthy_rules: [contabo2.siam2r.com -> localhost:3000, webui.siam2r.com -> 127.0.0.1:3000,
        hub.siam2r.com -> 100.111.221.102:8191, docs.siam2r.com -> 100.111.221.102:8060,
        code.siam2r.com + ide.siam2r.com -> http_status:403]
    containers:
      running: [open-webui, litellm, bomllm-searxng-1, rag-lb-relay-am4, qdrant-relay-am4,
        live-router, beszel-agent, bomllm-valkey-1, bomllm-postgres-1, bomllm-pgbouncer-1]
      exited_kept: [litellm_old_20261105_223945 (rollback asset),
        chart-overlay_offloaded_to_am4_20261103T0352Z (KEEP_PENDING_OWNER_REVIEW)]
      never_remove: [rag-lb-relay-am4, qdrant-relay-am4]
      searxng: {image: searxng/searxng:2026.11.2, binds: [100.83.20.100:8888, 127.0.0.1:8888]}
      valkey: {image: valkey/valkey:9.1.3-alpine [CHANGED v12 per R13 D3], maxmemory: 256mb,
        eviction: allkeys-lru, port: 127.0.0.1:6379, cache_ttl_s: 300 on litellm namespace}
      postgres: {image: postgres:16.15-alpine, port: 127.0.0.1:5432, databases: [openwebui, litellm],
        new_tables: [comment, comment_reaction, notification]}
      pgbouncer: {image: edoburu/pgbouncer:latest, port: 127.0.0.1:6432->5432}
      disk: images 22.67GB (10.15GB reclaimable); build cache 11.09GB (5.95GB reclaimable,
        ACTION-19 >168h prune); volumes 7.03GB (5.97GB reclaimable — NOT pruned)
    tailscale:
      version_at_survey: 1.104.4
      home_derp: sin
      mac: {address: 100.118.133.38, path: relay-sin, direct: false}
      ua: {address: 100.82.173.22, path: relay-sin, direct: false}
      required_owner_action: Permit/forward UDP 41641 or equivalent NAT policy; no agent change
      load_bearing: hub/docs/chart, Qdrant, embeddings, Mac generation depend on tailscaled —
        never stop
    netdata:
      current: host systemd; bind 127.0.0.1; update_every 10; ml/ebpf/scripts.d/go.d/journal/
        otel/debugfs/network-viewer off
      history: 190-300% combined baseline (art56352) -> 56-68% -> 94% -> 73.9% (art56483) ->
        48-55% after ROLLED_BACK 2-sample gate (art#56578 C2-1)
      target: sustained <=50% one core; optional 15s only after two clean elevated audits
    ufw:
      state: active, default deny; ssh-guard DROP 102.220.160.0/22 tcp/99 (persisted; owner ISP
        NEVER-BLOCK list intact)
      defect: anywhere-allows on 3000/4000/8888/8090 vs loopback/tailscale sockets (ACTION-18:
        tailscale0-scoped 4000/8888, delete 3000/8090 dead rules)
    cleanup_targets:
      build_cache: prune >168h (ACTION-19)
      keep_pending_owner_review: [chart-overlay_offloaded_to_am4_20261103T0352Z]
      rollback_assets_keep: [litellm_old_20261105_223945]
  ua:
    identity: {host: ubuntu-ai, os: Ubuntu 26.04.1 LTS, cores: 24, memory_gib: 123,
      gpus: RTX 5080 16GB + RTX 5060 Ti 16GB}
    addresses: {lan: 192.168.1.248, tailscale: 100.82.173.22, ssh: bom@192.168.1.248:99}
    role: GPU inference, vision, gpt-oss-120b, LiteLLM, ComfyUI, permanent AI training
    ollama: {version: 0.40.14, active_unit: bomai-ollama.service, resident: bomai-qc-light 3.4GB
        llamacpp forever; bomai-safe 7/7; qwen3-vl:2b 7/7}
    gpt_oss_120b: {container: llm-smart, port: 8380, ctx: 32768, rule: LIVE_NO_TOUCH}
    capacity_admission: FROZEN
    memory_baseline:
      ram_total_mb: 126199
      ram_available_mb: 12680-13721 (atom survey window)
      swap_used_mb: 18247-18636
      swap_out_observed: true (vmstat so 154-225 kB/s during sample)
      critical: true
      action: freeze holds; guard ACTION-01; recovery per decision_table; NO eviction of
        gpt-oss-120b/ComfyUI/FX28
    gpu_baseline:
    - {model: RTX 5080, used_mib: 15345, total_mib: 16303, util_pct: 100, temp_c: 64}
    - {model: RTX 5060 Ti, used_mib: 14567, total_mib: 16311, util_pct: 0, temp_c: 38}
    gateways:
      main: {container: litellm, image: ghcr.io/berriai/litellm-non_root:v1.108.4 [CHANGED v12
        per R13 D3], port: 4000,
        bind_current: 0.0.0.0:4000, restart_constraint: 03:00-06:00 ICT after 2-min drain;
        bind script /usr/local/sbin/ua_litellm_bind.sh deployed (UA-3 DEFERRED_WINDOW) —
        NOTE: script pins 1.106.4, image is v1.106.5; reconcile per ACTION-09 before use}
      staging: {container: litellm-staging, bind: 100.82.173.22:4100->4000,
        image: v1.106.4, rule: NO_RESTART}
      prod_routes: [bomai-uni (Mac qwen38-uni), bomai-pro (i9 :8080), vision-light (UA qwen3-vl:2b),
        embed-bge-m3/embed-nomic/rerank-bge (AM4 Infinity :7997), tier_smart_local (gpt-oss-120b),
        zai-glm (external, not probed)]
    comfyui: {gpu0: 8188, gpu1: 8189, image: yanwk/comfyui-boot:cu130-slim-v2, rule: HTTP_API_ONLY,
      gpu0_at_100pct_64C: true}
    netdata: {container, update_every 5, ml off, binds: [127.0.0.1:19999, 100.82.173.22:19999] (DONE),
      stream: to 122.155.168.7:19999 with placeholder API key — CAT TCP_IN lacks 19999 (ACTION-11)}
    credential_files: {.webui_secret_key: 664->600 (ACTION-12), god.env: 664->600, proxy.env:
        664->600, librechat .env: 600 ok, fx28 secrets: 600 ok; 3 QC copies retired (ACTION-12)}
    zombies: 2 (litellm parent pid 3118377) — reaped at next windowed litellm recreate
    wide_publish_inventory: [litellm:4000 (REBIND_AFTER_DRAIN, staged), llm-smart:8380 NO_TOUCH,
      librechat:3080 OWNER_REVIEW, comfyui:8188/8189 NO_TOUCH]
    ufw: active default-deny; comfy allows from 192.168.1.0/24; Docker 0.0.0.0 publishes bypass
      possibility noted — DOCKER-USER audit pending
    open_webui_host: {version: 0.12.4, bind: 127.0.0.1:3000, policy: independent}
  am4:
    identity: {host: ubuntu, os: Ubuntu 26.04.1 LTS, cores: 32, memory_gib: 121,
      gpus: 2x RTX 5060 Ti 16GB}
    addresses: {lan: 192.168.1.249, tailscale: 100.80.16.53, ssh: bom@192.168.1.249:99}
    role: ComfyUI router/workers, embeddings, Qdrant, agent hub, LiteLLM, business services
    resource_baseline: 'atom 2026-11-06: load 6.73, idle 74-83%, mem_available 80151MB, disk 37%;
      GPUs 15254/15241 MiB used at 0% util (compute apps: two python3.13 + whisper, not ollama);
      FX28 burn untouched.'
    ollama: {version: 0.40.13, binary: /home/bom/.local/share/BOM-AI/ollama-v0.40.13/bin/ollama,
      target: 0.40.14, asset_sha256: 993e83d08c3d13d17c55009a3e2664c8a25445e644aec3a68bef5abb6abce67d,
      blocked_by: FX28 + 03:00-06:00 ICT window; script /usr/local/sbin/am4_ollama_04014.sh deployed}
    models: {bomai-safe: locked 7/7 (re-verified atom), system_text_contradiction: ACTION-13,
      typhoon: 30.5B Q4_K_M}
    gateway: {container: litellm-gw, image: bomllm/litellm:1.108.4-pil2 [CHANGED v12 per
      R13 D3], bind: 0.0.0.0:4000, store_model_in_db: true, yaml_route: thai_prod ->
      ollama_chat/qwen38-uni at http://100.118.133.38:11434 [CHANGED v12=R12, was LAN
      192.168.1.254] think false keep_alive 24h num_ctx 8192 timeout 300,
      config_path: /data/migrated/litellm/config.yaml}
    exposure:
      ufw: INACTIVE (defect — ACTION-05)
      wide_publish: [litellm-gw:4000, llm-postgres:5432 (REBIND staged), comfy-gpu0:8188,
        comfy-gpu1:8189, icafefx-chart:3100, icafefx-chart:3001, metube:8082, habibi:8892,
        serpbear:3456, changedetection:5002, bomllm-docs:8060]
      container_limits: comfy 24GiB each; infinity-cpu 12GiB/8CPU; code-server 4GiB; others unlimited
    comfyui: {router: 8788, image: yanwk/comfyui-boot:cu130-megapak-pt211, rule: HTTP_API_ONLY}
    infinity: {container: infinity-cpu, bind: 192.168.1.249:7997, role: fleet embedding backend}
    qdrant: {version: v1.20.0, storage: /home/bom/qdrant/storage, binds: 127.0.0.1+LAN+TS
        :6333/:6334, collections: 13}
    hub: {container: agent-hub-v2, image: agent-hub:webstats-v1-20261104_0301 [CHANGED v12 —
        verified by live docker inspect 2026-11-13; v11 recorded governance-v2-20261029],
        bind: 192.168.1.249:8192->8000, restart_policy: no (noted), rule: LIVE_NO_TOUCH}
    netdata: {host network, binds: [127.0.0.1, 100.80.16.53, 192.168.1.249] (DONE persisted to
        host volume), update_every 5, cpu 0.96%}
    logs: {kern_log: rotated 2026-11-06 (DONE, su syslog syslog fix applied), syslog: 261MB NEW
        (ACTION-20), kernel_audit_backlog: exceeded (ACTION-20 raise to 16384 runtime)}
    exited_cleanup: agent-hub-v2_prev_20261104_0301 retired (DONE)
  nas:
    identity: {host: DS725_PLUS, os: Synology DSM, cores: 4, memory_gib: 19, volume: 5.3TiB}
    addresses: {lan: 192.168.1.253, tailscale: 100.111.221.102, ssh: siamcafe@192.168.1.253
        (no sudo; bom publickey denied — inventory only)}
    role: Storage, backups, tunnels, hub/service relays, monitoring, owner-held n8n
    n8n: {image: n8nio/n8n:2.31.2, bind: 192.168.1.253:5678, rule: OWNER_HOLD_NO_RESTART_OR_UPGRADE}
    relays: {hub: 8191, router: 8788, postgres: 5432/5433/13306, redis: 6379, socat matrix preserved}
    database: {container: agent-hub-db, mariadb:11.4.13, role: live-hub-data}
    monitoring: {kuma: 0.0.0.0:3001 (LAN service, noted), navidrome: 0.0.0.0:4533, adguard:
        0.0.0.0:8081, netdata: scripts.d off (DONE), node_exporter_old_20261023: stopped (DONE),
        beszel: installed}
    resource_baseline: {ram_available_mb: 14071, swap_used_mb: 692 (residual; root-only clear
        BLOCKED, ACTION-21), raid: md0-md3 [UU] healthy, volume1_pct: 30, usb_pct: 65}
    defects_new: [3x auto_cron.sh zombies (parent-owned, MONITOR), docker at /usr/local/bin/docker
        absent from default PATH (user-scope fix ACTION-21)]
    schedule_targets: {apply_watermark_server.py: 03:00, tier2_daily.py: 03:07,
      grav_content_writer.py: 03:14, noncritical_monitors: 03:21, mode: OWNER_DSM_TASK_SCHEDULER}
  mac:
    identity: {host: macmini-ai, hardware: Mac Mini M4 Pro, cores: 14, memory_gib: 48}
    addresses: {lan: 192.168.1.254, tailscale: 100.118.133.38, ssh: bom@192.168.1.254:22}
    role: Primary qwen38-uni MLX inference and embeddings
    ollama_v12_topology: '[NEW v12] THREE ollama serve processes observed 2026-11-13.
        (a) FLEET instance: /Users/bom/.local/share/BOM-AI/bin/ollama listening on
        100.118.133.38:11434, version 0.40.14 (GET /api/version), serves ALL C2+AM4 traffic;
        qwen38-uni resident 31.02GB size_vram, runner mlx, quantization nvfp4, digest
        549badb7b84d..., context_length 8192, residency DYNAMIC (empty before first probe,
        reloads on demand, observed keep-alive expiry +2h). (b) DESKTOP app:
        /Applications/Ollama.app on 127.0.0.1:11434, version 0.40.16, idle/no models —
        R13 D3 measured THIS loopback instance. (c) ROOT system:
        /usr/local/lib/ollama-v0.40.14/ollama serve since Thursday, listener unconfirmed.
        Config pin location: ~/Library/LaunchAgents/com.bomai.ollama.plist (binary path there
        differs from the live fleet process — see ollama_num_parallel_v12). v11 record:
        server 0.40.14, cli 0.40.14 aligned, models_total 14, no_cloud true, keep-alive 24h.'
    defect_new: 10-token localhost generate TimeoutError at 70s while resident (ACTION-06)
    network: {c2_path: DERP-sin, udp: true, nat_mapping: stable, port_mapping: none,
      magicsock_receiveipv4: NOT RUNNING, required_owner_action: UDP 41641/NAT}
    owner_gateway: {port: 11435, rule: NO_TOUCH}
    services: {open_webui: :3000 (0.12.0 independent), searxng: :8888}
    storage_baseline: system 27% used / 659 GiB free; two iOS simulator volumes 98% —
      audit done (MAC-3), deletion is owner decision
    docker: installed 29.7.2, daemon intentionally stopped
  i9:
    identity: {host: DESKTOP-G3MKH6J, os: Windows 10 Pro 19045.6466, cpu: i9-13900K,
      logical_cores: 32, memory_gb: 128, gpus: 2x RTX 5060 Ti 16GB}
    addresses: {lan: 192.168.1.20, tailscale: 100.85.255.14, ssh: bomi9@192.168.1.20:22}
    role: YuE2/ComfyUI GPU host, bomai-pro llama.cpp, owner voice/GPU services
    bomai_pro: {service: llamacpp-gpu1, startup: Automatic, bind: 127.0.0.1:8080, ctx: 8192,
      parallel: 1}
    comfyui: {version: 0.43.0, listen: 192.168.1.20:8188 (LAN-only, keep), additional: [8189,
        8190 (pulid NO_TOUCH)], serve_endpoint: http://desktop-g3mkh6j.tailf5814f.ts.net:18188}
    yue2: {checkpoint: E:\comfy_models\models\checkpoints\yue2_3b_bf16.safetensors, bytes:
        7799983228, runtime_gpu: GPU0}
    ollama: {version: 0.40.13, target: 0.40.14, staged: C:/Users/bomi9/scripts_k3/i9_ollama_04014.py,
      setup_sha256: e069c7cc7d4808f77684e81efa0b1f853a5190b4b8f070bc8fd63041180e3eba,
      rollback_04013_sha256: 9e3c76e54e7184c68e88a2378b909bf59bbe454f83c076cb4f4a717e946ae719}
    gpu_residency: [{gpu: 0, used_mib: 12994}, {gpu: 1, used_mib: 11066}] — WDDM per-process
      attribution unavailable; residents named (ComfyUI x2, bom-siangtts, bom-voxcpm2, desktop)
    model_admission: DENY_UNTIL_BOTH_GPU_RESIDENT_SETS_ARE_ATTRIBUTED
    os_support: {status: Win10 Pro end of support 2025-10-14, license: VOLUME_MAK, esu:
        NOT_FOUND/UNVERIFIED, action: owner ESU-or-migrate decision (ACTION-23)}
    firewall: Domain/Private/Public ON, default inbound block
    wide_bind_inventory: [22, 445, 3389, 8190, 9200, 9400, 9401] — no listener disable without
      owner review
  cat:
    identity: {host: server-122-155-168-7.da.direct, os: Ubuntu 20.04.6 LTS, cores: 12,
      memory_gib: 62}
    addresses: {public: 122.155.168.7, ssh: bom@122.155.168.7:99, tailscale: false}
    role: DirectAdmin production hosting; READ_ONLY for agents; every script OWNER_EXECUTE
    directadmin: {version: '1.713', php_slots: {php1: 7.4 php-fpm, php2: '8.2', php3: '8.3'},
      secure_php: true}
    web: nginx 1.29.4 running; Apache 2.4.66 installed
    php: {cli_default: 7.4.33 via /usr/local/bin/php -> php74 (DEFECT, ACTION-07), php83: 8.3.33
        installed, php56: on disk (retire gated), opcache: enabled}
    mariadb: {version: 10.6.22, rss: 5.5GB, target: metric-driven 6-8GiB pool, max_connections
        <=200}
    csf: {version: '15.05', testing: 0, synflood: ON 75/s burst 25 keep, country_blocking:
        KEEP_EMPTY, tcp_in: [99, 2222, 3100-3300], tcp_in_missing: [19999 for UA netdata stream
        (ACTION-11 single-IP csf.allow if failing)], tcp_out: includes 19999}
    backup: {official_default: /home/admin/admin_backups, newest: 2026-11-01 (STALE >26h,
        ACTION-14), offsite: UNVERIFIED, target: daily local 03:30 ICT + offsite NAS 04:15 ICT}
    ssl: {manager: DirectAdmin ACME ec256, audit: warning <14d critical <7d, never read keys}
    failed_units: [cloud-init local/config/final, iptables-restore (CSF active policy), maldet
        (cause unknown), snap canonical-livepatch/cups/snapd.seeded]
    os_support: {release: 20.04.6, standard_support: ended 2025-05, esm_apps: ENABLED,
        esm_infra: ENABLED (atom survey), livepatch: entitled, warning}
    staged_scripts: /root/bomllm-scripts/ (13 scripts incl. cat_backup.sh, cat_php_retire_eol.sh,
      cat_csf_hardening.sh, cat_esm_service_audit.sh, cat_tls_audit.py, fleet_bind_audit.py,
      fleet_log_audit.sh — sha256 verified, chmod +x, NOT executed; + cat_php_default_83.sh and
      cat_csf_19999.sh from this report)
    ssh_inventory: PermitRootLogin yes + PasswordAuthentication yes observed; inventory only, NO
      recommendation (IRON 38)
  contabo1:
    identity: {host: vmi3108393, os: Debian 12, cores: 8, memory_gib: 23}
    addresses: {public: 109.205.176.7, ssh: root@109.205.176.7:99, tailscale: false}
    role: Monitoring, alerting, independent n8n, exporters
    n8n: {image: n8nio/n8n:2.10.3, bind: 127.0.0.1:5678, limits: 8GiB/4CPU, health 200 in 3ms,
      rule: OWNER_HOLD_NO_FORCED_ALIGNMENT_OR_RESTART; StartedAt 2026-11-06T00:45:39Z}
    zombies: 75 chromium/chrome_crashpad parented by n8n node server.js pid 65171 (started
      04:10:14) — browserless recycle done did NOT reap; owner-window n8n recycle (ACTION-08);
      watch cron daily
    browserless: {bind: localhost:3000, recycled 2026-11-06 same-image, health via /json/version
        401-accepted}
    monitoring: {grafana: :3001 (13.2.2), kuma: :3002 (2.5.6), prometheus: 127.0.0.1:9090 (3.14),
        alertmanager: :9093, exporters: 9100/9101/9102/9119/9120,
        netdata_binary: 2.12.0-405-nightly STOPPED with safe preventive config (10s/ml off/
        loopback/scripts.d+ebpf+debugfs off) — leave stopped}
    mariadb: {image: 10.4.13 EOL, action: separate blue/green migration, original retained}
    iptables: INPUT DROP; allows 99/80/443/9090; 9090 shadow rule removal staged (ACTION-22)
    tls: chart.icafeforex.com not_after 2027-01-05 — monitor only
  am5_command_station:
    identity: {host: DESKTOP-PE1B0VH, os: Windows 10 Pro, cpu: Ryzen 9 9950X3D, memory_gb: 128,
      gpu: RTX 4060 8GB}
    addresses: {lan: 192.168.1.22, tailscale: 100.110.83.99}
    role: Command station; not counted among the eight production machines
    rule: No fleet model or firewall changes in this task.
music_pipe:
  id: music_yue2
  exposed_model_id: music_yue2.music-yue2
  active: true
  global: true
  endpoint: http://desktop-g3mkh6j.tailf5814f.ts.net:18188
  content_md5: 1dfc29042539a09e0d2dc895f80a15d7
  valves: {ENABLED: true, MAX_DURATION_S: 30, MAX_CALLS_PER_DAY: 5, LOCAL_TIMEOUT_S: 600,
    ffmpeg_timeout_s: '60 HARDCODED in transcode() — no valve exists', ALLOWED_USER_IDS_count: 21,
    STATE_DIR: /app/backend/data/music_yue2}
  sampling: {temperature: 0.8, top_p: 0.95, top_k: 50, repetition_penalty: 1.1, cfg_scale: 4.0,
    ksampler: {cfg: 1.0, steps: 32, sampler: dpm_2, scheduler: sgm_uniform, denoise: 1.0}}
  style_presets: [calm, acoustic, piano, ambient, upbeat, jazz, cinematic, lofi, electronic,
    bossa, thai_lk, thai_lt, thai_tpop] (full prompt text preserved from v10, unchanged)
  residual: ASCII-90s duration ambiguity (zcode lane); busy-check stale :8188 URL fails open
    (zcode lane); ffmpeg 60s hardcap recurrence risk under iowait (zcode lane 60->240 or read
    LOCAL_TIMEOUT_S)
music_intent_filter:
  id: bom_intent_filter
  content_md5: bd079a60e0dd908133874947425c7a94
  music_model_id: music_yue2.music-yue2
  keywords: preserved (v10 list unchanged); negative_guards: MUSIC_NEG + refusal/explanation
    filters preserved
comfyui_thai_poster:
  available_nodes: [TextOverlay, WASImageDrawText, CreateTextMask] — font dropdowns lack Thai
  tested_fonts_full_coverage: [Sarabun-Regular.ttf, leelawad.ttf, tahoma.ttf]
  pillow_raqm: false in both ComfyUI embedded and system Python
  recommendation: text-free diffusion -> maintained Pillow overlay with Thai font + working raqm;
    extend existing image pipe; implementation_owner: zcode; this config: research-only
ollama_v04014_notes:
  sampler_fix: /v1 chat/completions no longer force temp 1.0/top_p 1.0 when omitted — FLEET
    IMPACT NONE (OWUI -> LiteLLM ollama_chat -> /api/chat path already uses Modelfile defaults)
  mlx_topk: chunked top-k for vocab>2048 when k<2048 — Mac qwen38-uni only; measure speed after
    direct-path repair (ACTION-06)
  release_asset_integrity: {linux_amd64_tar_zst_sha256: 993e83d08c3d13d17c55009a3e2664c8a25445e644aec3a68bef5abb6abce67d,
    darwin_tgz_sha256: f3bf9a528e908da0da5a2b3a4ad3252a369d62186501dc4880261e8d9023bff5,
    windows_setup_sha256: e069c7cc7d4808f77684e81efa0b1f853a5190b4b8f070bc8fd63041180e3eba,
    windows_rollback_04013_sha256: 9e3c76e54e7184c68e88a2378b909bf59bbe454f83c076cb4f4a717e946ae719}
policies:
  ssh_guard_list_maintenance: C2 blocks only via /etc/c2-ssh-guard.list + c2-ssh-guard.service;
    gate >=100 invalid lines/24h, zero accepted, NEVER-BLOCK [180.183.0.0/16, 122.155.168.7,
    109.205.176.7, 171.6.136.143, 100.64.0.0/10, 192.168.0.0/16]; cap 10 entries
  litellm_db_load: prune SpendLogs only >1M rows or >2GB after pg_dump, 30d age, 50k batches +
    VACUUM ANALYZE, no VACUUM FULL; restart only 03:00-06:00 ICT after 2-min drain
  poller_min_interval: no :3000/:4000/docker-exec probing more often than 5 minutes; opshub
    timers 15 minutes
  retry_contract: {max_attempts: 2, cooldown_s: 10}  # mandatory on every retry loop
  backup_contract: timestamped backup before every change
  production_locks: [gpt-oss-120b LIVE_NO_TOUCH, ComfyUI HTTP_API_ONLY, AM4 FX28 untouched,
    CAT OWNER_EXECUTE, n8n OWNER_HOLD, no sshd/DNS/PasswordAuthentication changes,
    i9 D: drive UNTOUCHABLE, price API 168.119.176.113:5000 no-auth-no-change,
    webui.siam2r.com credentials untouched, LiteLLM 1.107.0 BANNED]
alert_contract:
  ua_memory_available: {warning: <20 GiB, critical: <16 GiB or any swap-out over 10s}
  c2_netdata_cpu: {warning: '>50% one core for 15m', critical: '>75% one core for 15m'}
  contabo1_chromium_zombies: {warning: '>20', critical: '>50 (now 75 — owner window open)'}
  mac_c2_path: {warning: DERP for 24h, critical: generation health failure OR localhost
      10-token generate >30s (NEW from atom 70s timeout)}
  price_router: {warning: any price intent false-positive report in first week,
    critical: inlet p95 added latency >1s (NEW)}
  live_router: {warning: configured model row is_active=false (NEW — currently TRUE, ACTION-04)}
  cloudflared_ingress: {warning: duplicate hostname rules >0 (NEW — currently 2 duplicates)}
  cat_backup_age: {warning: '>26h (CURRENTLY TRIPPED: Nov 1)', critical: '>48h or offsite missing'}
  cat_tls_expiry: {warning: <14d, critical: <7d}
  cb1_cert: {warning: <30d for chart.icafeforex.com (expires 2027-01-05 — far)}
  nas_usb_usage: {warning: '>75%', critical: '>85%'}
  nas_swap_residual: {warning: '>1GB with <4GB available (not tripped: 692MB/14GB avail)'}
  kern_log: {warning: '>100 MiB', critical: logrotate failure}
  am4_syslog: {warning: '>200MB (TRIPPED at 261MB — ACTION-20)'}
  ollama_version: {warning: not 0.40.14 after approved window, critical: health/locked-param
      regression}
  am4_exposure: {critical: ufw inactive AND any 0.0.0.0 DB publish (CURRENTLY TRIPPED —
      ACTION-05)}
security_audit_summary:
  confirmed: [UA critical memory pressure, AM4 ufw-inactive + 0.0.0.0:5432, CB1 n8n-parented
      zombies, Mac DERP + 70s generate timeout, live-router inactive model id, price router
      blocking inlet, CAT PHP 7.4 default + stale backups, UA secret file perms 664]
  unverified_until_tested: [Docker wide-bind public reachability (UA/AM4 DOCKER-USER), i9 ESU,
      CAT backup offsite, CAT effective ModSecurity engine, i9 second-GPU ownership]
  no_change_inventory: [PasswordAuthentication/PermitRootLogin observations (IRON 38), healthy
      n8n versions, AM4 busy load, C2 load average, CSF SYNFLOOD/LF, price API no-auth (IRON 19)]
  iron_constraints: [no sshd/DNS edits or recommendations, no IRON exemption, no healthy-system
      changes without evidence, no CAT execution, no NAS n8n restart/upgrade, LiteLLM 1.107.0
      banned, no secrets in artifacts]
maintenance_schedule_recommendations:
  daily: [NAS 03:00/03:07/03:14/03:21 stagger (owner DSM), CAT local backup 03:30 ICT + offsite
      04:15 ICT, CB1 zombie count (ACTION-08 watch cron 06:17), UA memory guard every 5min
      (ACTION-01), Mac cleanup 21:00 + dry-run 04:00 preserved]
  weekly: [C2 Sunday 05:00 prune preserved, Sunday 06:00 review TLS/log/version/backup alerts,
      C2 netdata sustained CPU review, Mac DERP path review, price router false-positive review
      (first 4 weeks)]
  monthly: [DirectAdmin isolated single-account restore drill, owner lifecycle review
      (ESM/Windows/PHP/MariaDB), firewall false-positive review, CSF country lists stay empty]
  restricted_window: LiteLLM restart only 03:00-06:00 ICT after 2-minute drain; AM4/i9 Ollama
    same window
historical_residuals_v10:
- OWUI exit-137 chronic flap risk unchanged; restart=always is the live mitigation; boot->healthy
  25-80 min under load
- Open WebUI forbids rolling two versions against one DB — single-container replace only after
  verified Postgres backup
- ASCII 90s duration ambiguity, stale music busy-check URL, ffmpeg 60s stage messaging — zcode
  source lanes
- Mac/UA cannot form direct tailscale path until owner NAT/firewall work
- chart-overlay remains offloaded KEEP_PENDING_OWNER_REVIEW
- no paid z.ai/Anthropic/Moonshot calls were made
verification:
  live_changes_by_this_task: NONE
  ssh_by_this_task: NONE
  inputs: [art#56608 atom survey (read-only, 8/8 machines, 225 files, 54600 lines, 32 findings),
    art#56564 GOD CONFIG v10, art#56565 GOD BLUEPRINT v6, art#56543 previous K3 report,
    art#56578 mega implement report]
  script_validation: all 23 action scripts are syntax-valid bash; fleet execution deferred to
    owner windows; CAT scripts OWNER_EXECUTE
  acceptance: every apply has paired verify/rollback or is explicitly read-only
artifact_ids:
  god_config_v10_previous: 56564
  god_blueprint_v6_previous: 56565
  atom_survey: 56608
  mega_implement: 56578
  previous_k3: 56543
residual_risks:
- UA memory relief is blocked on owner workload/capacity selection; alert-only does not create
  headroom
- C2 single OWUI worker remains the architectural chokepoint the ACTION-02 fix works around but
  does not remove
- Price router v2 needs a live false-positive watch week; disable path = OWUI toggle
- live-router recreate touches a production loopback service; auto-rollback covers health failure
- AM4 ufw enable carries SSH-lockout risk until the port-99 rule is proven from a second session
- Mac DERP repair is owner-network-dependent; tailscaled bounce may not help
- CAT changes all await owner execution; backup staleness is actively tripped
- CB1 zombies will grow until the owner recycles n8n
- i9 admission gate and ESU decision remain owner-blocked
- NAS swap clear remains root-blocked (margin healthy, no urgency)

thai_e2e_probe_20261113:
  when_utc: '2026-11-13T02:15-02:19'
  path: 'C2 LiteLLM localhost:4000 /v1/chat/completions -> bom-thai-chat -> Mac
    100.118.133.38:11434 qwen38-uni (route: keep_alive 24h, num_ctx 8192, think false,
    timeout 180)'
  auth: 'master key from container env LITELLM_MASTER_KEY on C2 (key loaded, length 51,
    never printed, never left C2)'
  probes:
    p1_cold: {http: 200, time_total_s: 83.45, regime: 'cold — Mac /api/ps empty before probe,
      includes model load', thai_chars: 18, latin_chars: 0, content_len: 22, total_tokens: 427,
      answer: 'ประเทศไทยมี 77 จังหวัด'}
    p2_warm: {http: 200, time_total_s: 23.90, regime: warm, thai_chars: 5, latin_chars: 0,
      content_len: 8, total_tokens: 423, answer: '50 อำเภอ'}
    p3_warm: {http: 200, time_total_s: 87.98, regime: warm, thai_chars: 15, latin_chars: 0,
      content_len: 15, total_tokens: 428, answer: 'แม่น้ำเจ้าพระยา'}
  stats: {probes: 3, median_s: 83.45, p90_s: 87.98, p90_method: nearest-rank n=3,
    thai_chars_median: 15, english_contamination: none, timeouts: 0}
  cache_observation: 'identical Thai prompt repeated within the cache ttl returned a cached
    copy in 0.08s with the SAME response id (litellm_settings.cache on valkey, ttl 300,
    completion cached) — E2E freshness requires prompt variation while probing.'
  history: 'R11 Thai probe (queue full): 85s, 111 Thai chars. R13 EN probe (hello): 4s,
    0 Thai chars, PROBE_FAIL recorded. v12 = first post-fix Thai measurement set: Thai output
    confirmed healthy.'
ollama_num_parallel_v12:
  current: 1
  current_evidence: '~/Library/LaunchAgents/com.bomai.ollama.plist EnvironmentVariables pins
    OLLAMA_NUM_PARALLEL=1 plus OLLAMA_HOST=127.0.0.1:11434, OLLAMA_MODELS=/Users/bom/BOM-AI/models,
    OLLAMA_MAX_LOADED_MODELS=1, OLLAMA_KEEP_ALIVE=-1, OLLAMA_CONTEXT_LENGTH=8192,
    OLLAMA_MAX_QUEUE=512, OLLAMA_LOAD_TIMEOUT=5m, OLLAMA_FLASH_ATTENTION=1,
    OLLAMA_KV_CACHE_TYPE=f16, OLLAMA_GPU_OVERHEAD=0. No /Users/bom/.ollama/env file; no system
    launchctl parallel key; the RUNNING fleet process env was not introspectable (NOT_COVERED).'
  recommendation: KEEP_AT_1
  reason: 'gate for raising to 2 requires ALL Mac-bound routes num_ctx <= 16384 AND free
    memory > 10GB. Live gate FAILS on context: C2 routes qwen38-think num_ctx 24576 and
    qwen38-deep num_ctx 32768 both target 100.118.133.38:11434 (verified in live config.yaml).
    Mac hw.memsize 48GB with qwen38-uni 31.02GB resident leaves free+inactive ~13.6GB;
    doubling KV at 32768 ctx with f16 KV cache risks pressure while OLLAMA_MAX_LOADED_MODELS=1,
    and a second slot would halve per-slot throughput on the DERP-relayed C2<->Mac path.
    Opus estimate "2 is safe if num_ctx <= 16384" is NOT met. NO SETTING WAS CHANGED.'
  revisit_when: 'if qwen38-think/qwen38-deep are re-pinned to <= 16384 or retired AND free
    memory stays > 10GB, revisit raising to 2.'
key_expiry_registry_v12:
  source: 'C2 bomllm-postgres-1, db litellm, table LiteLLM_VerificationToken (read 2026-11-13)'
  kw-engine-nas: '2027-02-10 21:39:04.426 (R13 renewal)'
  cctv_runner_flood_runner_p044: '2027-02-10 21:39:04.426 (R13 renewal)'
  cctv_runner_flood_runner_vision_p048: '2026-11-11 05:23:18.433 — EXPIRED, zero presentations
    per R12, left in place'
  empty_alias_dashboard_keys: '3 rows expired 2026-09 (R12 record, left in place)'
  next_expiry_wave: '2026-11-28..12-05: bom-bom-wave1-test, bom-bom-litellm,
    bom-siamlancard-apitest, n8n_content_pipe, bom-siamlancard-chat, bom-fagoodlala-chat'
janitor_v2_fleet_and_hub_brain:
  fleet_live: '8 production machines (c2, ua, am4, nas, mac, i9, cat, contabo1) plus am5
    command station; roles per machines section above; c2/am4/mac surveyed live by this task,
    ua/nas/i9/cat/contabo1 carry v11+R13 records (NOT re-verified this round).'
  hub_brain_v2: 'agent-hub-v2 on AM4 (image agent-hub:webstats-v1-20261104_0301, bind
    192.168.1.249:8192->8000, restart_policy no, rule LIVE_NO_TOUCH); NAS relays hub 8191 ->
    AM4; public hub.siam2r.com flows cloudflared -> 100.111.221.102:8191.'
  note: 'summary only; no janitor or hub process/config change by this task.'
extra_drift_v12:
- 'C2 config.yaml model_list = 24 entries; R11 health reported 27 models (DB-added models
  make up the difference).'
- 'litellm_settings also pins: request_timeout 60, retry_after 2, allowed_fails 3,
  cooldown_time 60, drop_params true, enable_pre_call_checks true.'
- 'bom-thai-chat route live: keep_alive 24h, num_ctx 8192, think false, timeout/stream_timeout
  180 — matches locked v11 params.'
- 'C2 ufw/netdata/disk states from v11 NOT re-verified this round (NOT_COVERED).'
- 'AM4 ollama version 0.40.13 from v11 NOT re-verified this round (NOT_COVERED).'
verification_v12:
  live_changes_by_this_task: NONE
  live_changes_note: 'documents only — no restart, no config write, no service touch on any host'
  ssh_read_only_hosts: ['c2 bom@109.123.233.171:99', 'am4 bom@192.168.1.249:99',
    'mac bom@192.168.1.254:22']
  litellm_probe_budget: '5 of 10 used (1 auth-test 401 + 3 fresh Thai probes + 1 cache-hit
    repeat)'
  evidence_logs: [p1_c2_config.log, p1_c2_cron.log, p1_c2_keys.log, p1_c2_keys2.log,
    p1_am4_thaiprod.log, p1_am4_thaiprod_full.log, p1_am4_hubimg.log, p1_mac_ps.log,
    p1_mac_env.log, p3_mac_ps.log, p3_mac_mem.log, p3_mac_multi.log, p3_mac_procinfo.log,
    p3_mac_launchagents.log, p2_probe_1.log, p2_probe_2.log, p2_probe_2b.log, p2_probe_3.log]
artifact_ids_v12:
  god_config_v11: 56686
  r11_report: 59888
  r12_report: 59917
  r13_report: 59929
  god_config_v12: THIS_ARTIFACT
residual_risks_v12:
- 'Thai E2E warm latency spans 23.9-88.0s for tiny answers on the DERP-relayed single-serialized
  slot path; direct-path work (v11 ACTION-06) or a slot increase after ctx re-pin would help.'
- 'The Mac FLEET ollama process runs a binary whose path differs from com.bomai.ollama.plist;
  which config source actually governs it is NOT_COVERED.'
- 'cctv_runner_flood_runner_vision_p048 expired key remains in the LiteLLM DB.'
- 'Identical prompts within ttl 300s serve cached copies — any latency SLO check must vary
  prompts.'
