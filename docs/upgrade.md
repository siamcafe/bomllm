# Upgrade runbook

How we update the stack without waking up to a broken fleet. Rules first,
then per-component procedures.

## The rules

1. **Pin everything.** No `latest` tags anywhere. Dated or versioned
   tags only. (`code-server:latest` once drifted under us; never again.)
2. **One component per window.** Never stack upgrades. If two things
   change and it breaks, you have learned nothing.
3. **Backup before touch.** Postgres dump + config snapshot, verified
   restorable (a backup you haven't restored is a rumor).
4. **Rollback plan written *before* the upgrade command runs.**
5. **Smoke suite after.** The 6-probe smoke below, all green, or roll back.
6. **Off-peak.** Our window: after 23:00 local, never during the nightly
   restart window (03:45–04:30) or business hours.

## The 6-probe smoke suite (run after ANY change)

```bash
# 1. LiteLLM alive + DB connected
curl -sf https://llm.example.com/health/liveliness     # 200
curl -sf https://llm.example.com/health/readiness      # 200, db=connected

# 2. Unauth gate holds
curl -s -o /dev/null -w '%{http_code}' \
  -X POST https://llm.example.com/v1/chat/completions  # 401

# 3. Real chat through the whole chain (Thai)
curl -sf https://llm.example.com/v1/chat/completions \
  -H "Authorization: Bearer $SMOKE_KEY" \
  -d '{"model":"thai-chat-rt","messages":[{"role":"user","content":"สวัสดีครับ"}],"max_tokens":32}'

# 4. WebUI up
curl -sf -o /dev/null -w '%{http_code}' https://chat.example.com/  # 200

# 5. SearXNG local
curl -sf 'http://127.0.0.1:8888/search?q=test&format=json' -o /dev/null

# 6. Mac model resident, no swap growth
ssh mac 'ollama ps && vm_stat | grep -i swap'
```

## Ollama (Mac)

```bash
brew upgrade ollama            # or the pkg; note client/server version skew warnings
sudo launchctl kickstart -k system/ai.bomllm.ollama  # your label may differ
```

- Verify: `ollama --version` client == server; `ollama ps` shows the
  production model reloading; first warm chat < 5 s (Metal recompile can
  make the very first load slower — warm it before declaring done).
- Rollback: `brew` pin to the previous version; models are untouched by
  upgrades.
- Watch: MLX backend behavior changes (the alias-sharing finding in
  `docs/hardware.md` was version-specific — re-verify after upgrades).

## LiteLLM (VPS)

We run a lightly patched image. Procedure:

```bash
docker compose pull litellm           # new pinned tag
docker compose up -d litellm          # recreate
docker compose logs -f litellm        # watch boot: config parse, DB migrate
```

- Config is mounted read-only; `STORE_MODEL_IN_DB=True` means routes can
  also live in Postgres — after upgrades, diff `/model/info` against the
  pre-upgrade capture.
- Rollback: previous tag is kept locally (`litellm-prev` pattern);
  `docker compose up -d` with the old tag. DB migrations are the risk —
  dump Postgres *before* pulling.
- Known footgun: `drop_params` behavior and provider passthrough changed
  across versions; re-run the sampling-param passthrough probe
  (`benchmarks/README.md` §chain) after any LiteLLM bump.

## Open WebUI (VPS)

```bash
docker compose pull open-webui
docker compose up -d open-webui
```

- Settings live in its DB (key/value). Snapshot the DB first; diff
  `/api/config` after.
- Check the changelog for CVE fixes — we track them and bump promptly
  (0.11.0 fixed several; we run the fixed line).
- After upgrade: verify image-gen base URL, RAG reranker URL, and
  web-search engine survived (config drift between env and DB is a
  real, observed failure mode — DB wins).

## SearXNG / Qdrant / Valkey / Postgres

- SearXNG: dated tags only; config in `volumes/searxng`; rolling back is
  retagging.
- Qdrant: snapshot before upgrade (`POST /snapshots`); keep the previous
  image tag locally for rollback (we keep v1.19.0 alongside v1.19.1).
- Postgres: dump, upgrade within major 16, verify `pg_isready` + row
  counts. Major upgrades: `pg_dumpall` → new volume → restore.
- Valkey: AOF on; upgrades are low-risk; `PING` after.

## Mac OS

- Defer until a quiet week. Verify Ollama launchd job, pf rules, and
  Tailscale survive the reboot. Re-run the 6-probe suite.

## Upgrade log

Keep a table in your ops repo. Ours looks like:

| Date | Component | From → To | Smoke | Rollback needed |
|---|---|---|---|---|
| 2026-08-31 | Open WebUI | 0.10.x → v0.11.3 | 6/6 | no |
| YYYY-MM-DD | component (e.g. Ollama) | vX.Y → vX.Z | N/6 | no/yes |

## If it breaks at 2 a.m.

1. Don't debug forward — roll back to the pinned previous tag.
2. Capture `docker compose logs --since 30m` into the incident folder.
3. Post-mortem within 48 h: one page, root cause, the rule that would
  have prevented it. Add the rule here.
