<!-- GOD BLUEPRINT v6.0 — supersedes v5.2 (retained in git history and hub art#55907). Raw artifact: hub art#56565. -->

# GOD BLUEPRINT v6.0 — BOMLLM Fleet
# Full survey/baseline update; performance evidence is labeled by source.
project: bom-llm
step: fleet_optimization_blueprint
version: '6.0'
previous: '5.2'
base_document: art#55907 GOD BLUEPRINT v5.2 and art#55651 GOD CONFIG v9.0
date: '2026-11-06'
author: Kimi K3-256k /auto, spec art#56488
recommendation: INSPECT
references:
- 56483
- 56488
- 55651
- 55907
- 55908
- 56352
- 56456
v6.0 changes vs v5.2:
  1: Full 2026-11-06 eight-machine survey incorporated; no roles changed and no live command was executed by this task.
  2: UA memory pressure is the sole critical item; admission is frozen while gpt-oss-120b/ComfyUI/FX28 remain untouched.
  3: C2 production OWUI 0.13.0/Alembic e42c8f710a36 and short digest 549badb7b84d confirmed; load-average interpretation corrected.
  4: Ollama/OWUI/LiteLLM/n8n version matrix updated; LiteLLM remains 1.106.4 and independent UI/n8n versions are not force-aligned.
  5: 'Netdata history reconciled: 190-300% baseline, later 56-68/94/73.9% samples. Spec-supplied 42.8% is labeled unverified,
    not current.'
  6: New per-machine bind, cleanup, log, backup, lifecycle and security targets with rollback and owner gates.
  7: CAT backup path corrected to DirectAdmin default /home/admin/admin_backups; absence is not assumed.
  8: Maintenance schedule, alert contract and implementation waves added without creating new cron herds.
fleet_overview:
  machines: 8
  gpus: 7
  vram_gib: 96
  survey_window_ict: 2026-11-06 03:00-03:15
  reachable_machines: 8
  issues: 28
  critical_issues: 1
  roles_changed: false
  command_station: AM5 recorded separately; not counted among the eight production machines
architecture:
  diagram: "Users / owner apps\n  -> Cloudflare -> C2 OWUI 0.13.0 -> C2 LiteLLM 1.106.4\n       -> Mac qwen38-uni 0.40.14\
    \ server (PRIMARY, currently DERP sin)\n       -> UA gpt-oss-120b / bomai-safe (LIVE_NO_TOUCH; memory admission frozen)\n\
    \       -> AM4 Qdrant 1.20.0 + Infinity + business services through existing relays\n  -> NAS hub/docs/service relays\
    \ (n8n 2.31.2 unchanged)\nContabo1 monitoring/n8n 2.10.3/Browserless (independent)\nCAT DirectAdmin hosting (OWNER_EXECUTE\
    \ only)\ni9 ComfyUI/YuE2/bomai-pro (GPU attribution gate)"
  updates: No role migration. v6 overlays UA admission freeze, explicit-bind targets, Mac DERP remediation and CAT backup
    evidence.
  production_dependencies:
  - C2 tailscaled is load-bearing for hub/docs/chart, Qdrant, embeddings and Mac generation; do not stop.
  - C2 rag-lb-relay-am4 and qdrant-relay-am4 are production-critical; never remove during cleanup.
  - C2 chart-overlay_offloaded_to_am4 remains KEEP_PENDING_OWNER_REVIEW.
  - NAS n8n and Contabo1 n8n are independent owner-held instances; no restart or forced alignment.
performance_deltas:
  c2_netdata:
    initial_combined_cpu_pct: 190-300 (art56352)
    after_first_tune_combined_pct: 56-68 (art56352)
    after_final_tune_one_core_pct: 94.0
    latest_survey_one_core_pct: 73.9
    target_one_core_pct: <50 sustained
    spec_supplied_historical_delta:
      before_pct: 300
      after_pct: 42.8
      verified_by_supplied_artifacts: false
      use: Historical task input only; not current baseline
  ua_netdata:
    art56456_cpu_pct: 5.22
    latest_cpu_pct: 10.05
    verdict: CPU healthy; rebind only
  am4_netdata:
    restart_spike_cpu_pct: 43.96
    art56456_settling_cpu_pct: 25.78
    latest_cpu_pct: 0.96
    verdict: CPU solved; persistence remains
  c2_external_v5_2:
    api_ttfb_median_s:
    - 0.103
    - 0.093
    api_ttfb_p90_s:
    - 0.171
    - 0.182
    favicon_ttfb_median_s:
    - 0.181
    - 0.118
    ssh_connect_median_s:
    - 4.679
    - 1.048
    gate: AM5 median <0.5s and p90 <1.0s; localhost/hairpin is not public evidence
  c2_load: 14.26/19.06 historical high-load snapshot vs 12.54 latest under different workload; no causal improvement percentage
    claimed.
  mac_mlx_topk: 0.40.14 improvement applies to qwen38-uni, but no published or surveyed speed delta; measure after direct-path
    repair.
machine_baselines:
  c2:
    hostname: contabo2-bom-llm
    role: Public OWUI/LiteLLM control plane, search, relays and live router
    state: Debian 12, 12 vCPU, 47 GiB RAM, no GPU; RAM 6.3 GB used, disk 28%, load not saturation
    versions:
      owui: 0.13.0
      alembic: e42c8f710a36
      image_short: 549badb7b84d
      litellm: 1.106.4-pil2
      searxng: 2026.11.2
      postgres: '16.15'
      valkey: 9.1.2
    issues:
    - Netdata 73.9% one core
    - OWUI wide-bind candidate
    - five exited containers and old build cache
    - two unnamed zombies
    targets:
    - Optional 15s Netdata after sustained threshold
    - Archive four exited containers; keep chart-overlay and relays
    - Compose/Cloudflare-gated explicit OWUI bind
  ua:
    hostname: ubuntu-ai
    role: GPU inference, gpt-oss-120b, LiteLLM, ComfyUI and FX28
    state: 'CRITICAL memory: 16.304 GB available, 16.513 GB swap used, swap-out observed; both GPUs nearly full and idle'
    versions:
      ollama: 0.40.14
      owui_host: 0.12.4
      litellm: 1.106.4
      librechat: 0.8.8
    issues:
    - Memory pressure
    - wide binds
    - Netdata wide bind
    - two unnamed zombies
    targets:
    - Freeze new placements; read-only memory guard
    - Rebind Netdata and LiteLLM separately after consumer proof
    - No gpt-oss-120b/ComfyUI/FX28 mutation
  am4:
    hostname: ubuntu
    role: ComfyUI router/workers, embeddings, Qdrant, agent hub, LiteLLM and business services
    state: Load 16.78 is intentional FX28/Ollama work; 70.824 GB RAM available; no capacity emergency
    versions:
      ollama: 0.40.13
      owui_host: 0.11.4
      litellm: 1.106.4-pil2
      qdrant: 1.20.0
    issues:
    - Netdata config not persistent
    - Netdata host-network wide bind
    - kern.log >100 MB
    - one exited agent-hub backup
    targets:
    - Persist and explicitly bind Netdata
    - Dedicated kern.log rotation
    - Ollama 0.40.14 only after FX28 stops
    - Preserve all burn workloads
  nas:
    hostname: DS725_PLUS
    role: Storage, backups, tunnels, relays, monitoring and owner-held n8n
    state: RAID healthy; RAM available 13.817 GB; residual swap 38%; USB 65%; 03:00 herd on four threads
    versions:
      n8n: 2.31.2
      mariadb_agent_hub: '11.4'
      vaultwarden: 1.37.4
    issues:
    - 03:00 stacking
    - scripts.d enabled
    - old node_exporter wide bind
    - residual swap
    targets:
    - DSM stagger 03:00/03:07/03:14/03:21
    - Disable scripts.d only
    - Stop old exporter after scrape proof
    - Memory-gated swap cycle
    - Never restart n8n
  mac:
    hostname: macmini-ai
    role: Primary qwen38-uni MLX inference and embeddings
    state: Quiet M4 Pro, 48 GB unified memory; system disk 26%; simulator volumes 98%; DERP sin primary path
    versions:
      ollama_server: 0.40.14
      ollama_cli: 0.40.10
      netdata: 2.12.0
      qwen38_uni: 30 GB MLX resident, 7/7 locked
    issues:
    - DERP latency
    - CLI skew
    - full simulator volumes
    - MagicSock ReceiveIPv4 down
    targets:
    - Owner UDP/NAT direct-path repair and measured completion
    - Pinned CLI-only update
    - Backup-gated simulator review
    - No Docker start
  i9:
    hostname: DESKTOP-G3MKH6J
    role: YuE2/ComfyUI, bomai-pro and owner GPU services
    state: Windows 10 22H2 EOL, ESU unknown; RAM 66.339 GB available; GPUs hold 12.361/11.066 GB with Ollama empty
    versions:
      ollama: 0.40.13
      comfyui: 0.43.0
      python: 3.13.14
      pytorch: 2.14.0+cu130
    issues:
    - OS support
    - unattributed VRAM
    - wide Python/RDP/SMB candidates
    targets:
    - Owner ESU/OS decision
    - Read-only GPU attribution before placement
    - Signed Ollama 0.40.14 installer after owner window
    - ComfyUI stays LAN-only
  cat:
    hostname: server-122-155-168-7.da.direct
    role: DirectAdmin production hosting; OWNER_EXECUTE only
    state: Ubuntu 20.04.6, low load, 50.647 GB RAM available; ESM unknown; CSF enforcing; failed iptables-restore/maldet
    versions:
      directadmin: '1.713'
      nginx: 1.29.4
      php_cli: 8.3.33
      php1: '7.4'
      mariadb: 10.6.22
      csf: '15.05'
    issues:
    - EOL PHP slots/binaries
    - backup coverage unproven
    - DB metrics unavailable
    - OS support unverified
    - failed units
    - TLS inventory incomplete
    targets:
    - Verify ESM and backup first
    - Zero-reference PHP retirement
    - Metric-driven DB/PHP/nginx candidates
    - Evidence-gated CSF only; country lists empty
    - TLS audit without private-key reads
  contabo1:
    hostname: vmi3108393
    role: Monitoring, alerting, independent n8n and exporters
    state: Idle eight-core host with 20.701 GB RAM available; 79 Browserless zombies; MariaDB 10.4.13 EOL
    versions:
      n8n: 2.10.3
      mariadb: 10.4.13
      uptime_kuma: 2.5.6
      prometheus: '3.14'
      grafana: '13.2'
      netdata_binary: 2.12.0-405-nightly not running
    issues:
    - Chromium zombie leak
    - EOL MariaDB
    - n8n version skew (not an outage)
    - unsafe Netdata config if started
    targets:
    - Browserless-only planned recycle
    - Separate blue/green MariaDB migration
    - No n8n/Kuma change
    - Preconfigure safe Netdata but leave stopped
security_audit_summary:
  critical:
  - UA memory pressure
  high:
  - Mac DERP primary route
  - Contabo1 zombies
  - CAT backup recovery unproven
  - Windows/PHP/MariaDB lifecycle
  - wide-bind candidates after consumer proof
  no_change:
  - C2 ssh guard and owner ISP NEVER-BLOCK
  - working CSF SYNFLOOD/LF rules
  - healthy n8n instances
  - C2/UA/AM4 LiteLLM 1.106.4
  - AM4 FX28 and all ComfyUI
  forbidden:
  - sshd/PasswordAuthentication/PermitRootLogin edits or recommendations
  - DNS/resolv.conf changes
  - IRON exemptions
  - CAT agent execution
  - NAS n8n restart/upgrade
  - LiteLLM 1.107.0
policies:
  ssh_guard_list_maintenance:
    rule: C2 blocks only through /etc/c2-ssh-guard.list and c2-ssh-guard.service; never Docker chains or iptables-persistent.
    add_cidr_gate: '>=100 Invalid/Failed lines in 24h, zero Accepted in full journal, no NEVER-BLOCK overlap; cap 10 entries.'
    never_block:
    - 180.183.0.0/16
    - 122.155.168.7
    - 109.205.176.7
    - 171.6.136.143
    - 100.64.0.0/10
    - 192.168.0.0/16
  litellm_db_load: Keep v9 general_settings. Prune SpendLogs only >1M rows or >2GB after pg_dump, rows older than 30d, 50k
    batches + VACUUM ANALYZE; no VACUUM FULL. Restart only 03:00-06:00 ICT after 2-minute drain.
  poller_min_interval: No :3000/:4000/docker-exec probing more often than 5 minutes; opshub timers target 15 minutes via drop-ins;
    GOD warm-pin/keep-alive pipelines preserved.
  retry_contract:
    max_attempts: 2
    cooldown_s: 10
  production_locks:
  - gpt-oss-120b LIVE_NO_TOUCH
  - ComfyUI HTTP_API_ONLY
  - AM4 FX28 untouched
  - CAT OWNER_EXECUTE
  - n8n OWNER_HOLD
  - No sshd or DNS changes
phase_P_v5_2_evidence:
  hypotheses:
    H1_litellm_pg_loop: NOT SUPPORTED (tps=0, idle conns, tables below prune gates)
    H2_poller_pressure: NOT SUPPORTED
    H3_edge_vs_box: SUPPORTED (localhost ~0.01s vs external ~0.10s)
    H4_other_subnets: PARTIAL; owner ISP NEVER-BLOCK
    H5_static_files: SUPPORTED as missing files; heroes delivered
  ssh_guard: c2-ssh-guard.service persisted; one /22 DROP; owner ISP never blocked.
  litellm: Config already at target; SpendLogs about 153k rows/773MB; no prune/restart.
  squid: tailscaled.service.d/squid-rebind-v52.conf installed; tailscaled not restarted.
  residuals_carried:
  - KN1 phantom CPU accounting
  - single OWUI worker architecture
  - EU origin latency floor
  - owner-ISP failed-auth investigation
  - OWUI exit-137 historical flap
phase_O_v5_1_evidence:
  root_cause: C2 pre-auth brute-force plus KVM contention delayed SSH; sshd UseDNS/GSSAPI were clean and were not edited.
  fix: 102.220.160.0/22 DROP persisted; connects improved to about 1-3s in the measured window.
  tailscale_dependency: C2 has no LAN route; hub/docs/chart/Qdrant/embeddings/Mac generation depend on tailscaled. Boot-enabled
    retained.
  squid: Authenticated ncsa proxies on C2/Contabo1 kept; C2 must retain both listeners.
maintenance_schedule:
  daily:
  - NAS 03:00/03:07/03:14/03:21 stagger
  - CAT local backup 03:30 ICT, offsite 04:15 ICT after verification
  - Contabo1 zombie count comparison every 24h
  - Mac existing cleanup 21:00 and dry-run 04:00 preserved
  weekly:
  - C2 existing Sunday 05:00 prune preserved; inspect chart-overlay separately
  - Sunday 06:00 review TLS/log/version/backup alerts without auto-upgrades
  - Review C2 Netdata sustained CPU and Mac DERP path
  monthly:
  - Isolated DirectAdmin single-account restore drill
  - Owner review of ESM/Windows/PHP/MariaDB lifecycle and GPU capacity
  - Review firewall false positives and CSF country lists remain empty
  restricted_window: LiteLLM restart only 03:00-06:00 ICT after two-minute zero-completion drain; AM4/i9 Ollama use the same
    conservative inference window.
verification:
  analysis_inputs: Five mandated artifacts plus art56456 reconciliation and official vendor documentation
  live_changes_by_this_task: NONE
  ssh_by_this_task: NONE
  script_validation: 38 Bash/Python scripts parsed and syntax-checked locally; fleet execution is deferred
  acceptance: Every apply has a paired verify/rollback or is explicitly read-only; CAT scripts are OWNER_EXECUTE.
  residual_evidence_gap: No fleet post-change metrics exist yet; do not mark optimization targets DONE until the owner-authorized
    scripts produce them.
artifact_ids:
  god_config_v10: embedded_in_fleet_optimization_artifact
  god_blueprint_v6: embedded_in_fleet_optimization_artifact
  survey: 56483
  spec: 56488
