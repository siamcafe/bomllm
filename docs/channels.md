# Channels: wiring LINE, Telegram, WebUI, and MT5 (sanitized)

Five production channels. All converge on one LiteLLM endpoint; each gets
its own **virtual key** with its own **budget and model allow-list**.
That is the whole trick: one proxy, many doors, every door metered.

> Sanitization note: real webhook URLs, bot tokens, key values, account
> numbers, and internal hostnames were removed. Placeholders look like
> `CHANGE_ME_*`. See `docs/security-audit.md`.

## Channel 1 — Web chat (Open WebUI)

- Users reach `https://chat.example.com` → Cloudflare Tunnel → Open WebUI.
- WebUI authenticates users locally (invite-only; 19 users in prod),
  then calls LiteLLM container-to-container with the master key.
- Model dropdown is curated: Chat / Deep Think / Code / Vision. Admin-only
  models are hidden from user roles.
- Features enabled in prod: web search (SearXNG), RAG (bge-m3 + Qdrant +
  reranker), image gen (ComfyUI), TTS/STT (i9).

## Channel 2 — LINE bot

```
LINE Messaging API → webhook → n8n (NAS) → LiteLLM (model=thai-chat-rt)
→ n8n formats → LINE reply API
```

- n8n workflow: verify signature → load conversation state → call LiteLLM
  → post-process (length guard, link formatting) → reply.
- Route pins: `think: false`, `num_predict` sized for chat, 30 s timeout.
  A 30 s+ reply is a UX failure on LINE even if the content is perfect —
  two edge-case categories in our eval hit this cap; they route to
  fallback now.
- Credentials live in n8n's credential store, never in workflow JSON
  (scanned weekly).

## Channel 3 — Telegram bot

Same pattern as LINE: platform webhook → n8n → LiteLLM → reply.
Differences: MarkdownV2 escaping in post-processing, and a state-change
alert bot (separate token) that pages the owner when probes flip
(up/down) — driven by Uptime Kuma on the NAS.

## Channel 4 — MT5 EA (read-only)

A MetaTrader 5 indicator panel that asks the LLM about the chart it is
looking at.

- **Read-only by construction.** The EA contains no trading calls
  (audited: zero order-send symbols in the source tree). It renders an
  analysis panel; it cannot and does not trade.
- Transport: HTTPS POST to a dedicated LiteLLM virtual key:
  - model allow-list: exactly one analysis model
  - `max_budget` per day, hard cap
  - no user-facing data leaves the box except the chart metrics the
    user explicitly sends
- This channel is why the repo's "What this is NOT" section exists.
  BOMLLM is not a trading system.

## Channel 5 — n8n content pipelines

Scheduled n8n workflows that draft Thai articles:

```
cron → n8n → LiteLLM (model=bom-writer, num_predict=8192)
→ staging folder → human review → publish (manual)
```

- Measured throughput on the writer route: see `benchmarks/` — the
  10-post generation drill is the canonical load test
  (`[BENCH_DATA_PENDING]` for posts/hour on your hardware).
- Nothing auto-publishes. Ever.

## Virtual key policy (the metering fabric)

| Key | Used by | Models allowed | Budget |
|---|---|---|---|
| `CHANGE_ME_key_line` | LINE bot | `thai-chat-rt` | $2/day |
| `CHANGE_ME_key_tg` | Telegram bot | `thai-chat-rt` | $2/day |
| `CHANGE_ME_key_mt5` | MT5 EA | one analysis model | $1/day |
| `CHANGE_ME_key_writer` | n8n pipelines | `bom-writer` | $5/day |
| `CHANGE_ME_key_webui` | Open WebUI | curated list | $10/day |

All keys: created via `POST /key/generate`, stored in `.env` (gitignored),
rotated on any suspicion. Spend is in `LiteLLM_SpendLogs`; the query is
in `docs/cost.md`.

## Adding your own channel

1. `POST /key/generate` with a budget and model allow-list.
2. Point your channel at `https://llm.example.com/v1` with that key.
3. Add a Kuma probe for the channel's health endpoint.
4. If the channel is user-facing and Thai, inherit the
   `thai-chat-rt` route pattern (`think:false`, sized `num_predict`,
   Config G system prompt from `configs/sampling-recipe.yaml`).
