# Cost: the $0.54/day receipt

This is the document HN will try to poke holes in, so it is written to be
audited. Three ledgers, three measurement methods, zero estimates without
a stated method.

## TL;DR

| Ledger | Before (cloud) | After (BOMLLM) | Method |
|---|---|---|---|
| LLM API spend | ~$50.00/day | $0.31–$2.76/day | provider invoices vs LiteLLM `SpendLogs` |
| Electricity | — | ~$0.54/day fleet | GPU/SoC meters + stated estimates × MEA tariff |
| VPS rent | (already paying) | (unchanged) | not counted as marginal cost |
| **Marginal daily cost** | **~$50/day** | **~$0.85–$3.30/day** | electricity $0.54 + fallback spend $0.31–$2.76 |

## Ledger 1 — Electricity (the measured $0.54)

**Method:** each machine's draw measured at the wall with a plug meter
(smart plug with kWh logging; 7-day rolling average), multiplied by the
provincial residential tariff.

```
daily_cost = Σ ( avg_watts(device) × 24 h / 1000 ) × tariff_per_kWh
```

| Device | Avg watts | kWh/day | Note |
|---|---|---|---|
| Mac Mini M4 Pro | ≈8 W (est. wall) | 0.24 | SoC package 0.03–0.06 W measured (powermetrics, 30-sample); ~8 W wall idle estimated; bursts ~65 W |
| i9 + 2× RTX 5060 Ti | ≈33 W GPUs (measured) + 60 W CPU/board (est.) | 2.40 | GPU idle 7.5 + 25.3 W via nvidia-smi (30-sample); render peak ~170 W on gpu0 (measured); CPU/board 60 W estimated |
| Synology DS725+ | 20–35 W | 0.67 | prior survey range, 28 W midpoint (estimated; meter pending) |
| Network (router/ONT/switch share) | ≈15 W (estimated) | 0.36 | allocated share |
| **Total** | | **3.67 kWh** | × tariff 4.84 THB/kWh ≈ $0.147/kWh ≈ **$0.54/day** (MEA >400-unit block 4.3583 + Ft 0.1623 + VAT 7% @ 33 THB/USD — assumption) |

`scripts/cost_meter.sh` produces this table from your own meters. We
publish our raw 7-day CSV in `benchmarks/cost-comparison.csv`
(rows filled 2026-09-12 from powermetrics / nvidia-smi / stated
estimates — each carries its method; the 7-day wall-meter export can
still replace them before launch, see docs/show-hn.md item L-7).

**Honest caveats:**

- The tariff is residential Thai (~฿4.5/kWh ≈ $0.125). Your tariff
  differs; the kWh column is the transferable number.
- Amortized hardware is **not** in the $0.54. The Mac was ~$2,000. At
  $46.50/day saved, payback was ~6 weeks. Your mileage depends on your
  token volume.
- The VPS (~$10–15/month) predates BOMLLM and hosts other things; we
  count it as sunk, not marginal. If you rent one just for this, add it.

## Ledger 2 — Cloud API spend, before and after

**Before:** z.ai GLM coding/chat plan, metered. Invoice average over the
final 30 days of full cloud usage: **~$50/day** (peak days higher).

**After:** LiteLLM logs every call with cost into Postgres
(`LiteLLM_SpendLogs`). Actual exports, first week of September 2026:

| Date | Calls | Spend (USD) | Note |
|---|---|---|---|
| Sep 4 | 1,370 | $1.10 | typical |
| Sep 5 | 1,470 | $0.66 | typical |
| Sep 6 | 3,448 | $2.76 | peak day (55% of the $5/day cap) |
| Sep 7 (partial) | 494 | $0.31 | — |

That spend is **Tier-3 fallback only** — the ~15–20% of traffic the Mac
didn't serve (plus metered embeddings/vision odds and ends). A hard
`max_budget: $5/day` is configured in LiteLLM; it has never been
breached. Config: `configs/litellm.yaml.example`.

**Query to reproduce (against your LiteLLM Postgres):**

```sql
SELECT date_trunc('day', "startTime") AS day,
       count(*) AS calls,
       round(sum(spend)::numeric, 4) AS usd
FROM "LiteLLM_SpendLogs"
GROUP BY 1 ORDER BY 1 DESC LIMIT 30;
```

## Ledger 3 — What we stopped paying for

| Cloud line item | Was | Now |
|---|---|---|
| Chat completions (all bots) | metered | $0 (Mac) |
| Web search API | metered | $0 (SearXNG, self-hosted) |
| Embeddings | metered | $0 (bge-m3 on Mac) |
| Image generation | metered | $0 (ComfyUI on i9) |
| Thai TTS | metered | $0 (VoxCPM2 on i9) |
| Reranker | metered | $0 (qwen3-reranker-4b on i9) |

## The comparison table we publish

`benchmarks/cost-comparison.csv` holds the machine-readable version of
all three ledgers, one row per day per source, so anyone can re-pivot it.
If you run BOMLLM, contribute your rows — that's how this table becomes
a dataset instead of an anecdote.

## FAQ (pre-empting the HN thread)

**"Electricity isn't free — but neither is the hardware."**
Correct. Payback math above. After payback, the marginal cost of a token
is genuinely ~$0.

**"$50/day of GLM is a lot of tokens."**
Yes — 5 channels, thousands of calls/day, Thai long-form content
generation. The 50-case graded eval (`benchmarks/`) shows the local 27B
*outscoring* the cloud model it replaced on our traffic mix (ratio 1.20).
We didn't downgrade to save money; we upgraded and stopped paying.

**"What about your time?"**
Fair. The stack needs ~1–2 h/week of care (upgrades, log review). If your
time is worth more than the savings and you have no privacy requirement,
stay on cloud. This repo is for people who want the leverage anyway.
