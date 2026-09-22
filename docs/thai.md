# Thai language playbook

BOMLLM is Thai-first. This document is everything we learned making a
27B open model answer Thai customers well enough to replace a paid cloud
model — including the eval protocol, the winning config, and the bugs
that cost us nights.

## Model matrix (what we ran, what won)

| Model | Quant / backend | Thai verdict | Evidence |
|---|---|---|---|
| Qwen3.8-27B class, stock | GGUF Q4_K_M | good, slow (7.9 tok/s) | p13a bench |
| Same, MLX | nvfp4 MLX | good, **30.2 tok/s** | p13a bench |
| TURBO-Fable (DavidAU fine-tune) | nvfp4 MLX | no Thai regression vs stock, fewer think tokens | A/B below |
| 709-L (TURBO-Fable series tune) | nvfp4 MLX | **incumbent since 2026-09-16** — +0.225 publishable first-pass over 735 | Arm B below |
| Typhoon (Thai-specialized) | GGUF | retired — general model + good prompt beat it on our traffic | internal A/B |
| OpenThai / granite merges | various | evaluated, not promoted | internal |

**Current production (since 2026-09-16):** 709-L nvfp4 (MLX), ONE
manifest, ONE production alias (`qwen38-uni`) + a `-bak` pointer to the
735 incumbent for second-level rollback. The old chat / think / code /
deep / fast alias fan-out was retired — behavior differentiation lives
on the LiteLLM route only.

### The 709-L cutover (2026-09-16, Arm B paired eval)

Same 20 production articles run through both models on the same box,
same gates (G2/G3/G5/G7/G9), graded on publishable-first-pass:

| Metric | 709-L | 735 (ex-incumbent) |
|---|---|---|
| Publishable first-pass rate | **0.781** (25/32) | 0.600 (24/40) |
| Paired mean delta | **+0.225** | — |
| Paired W/L/T (20 articles) | **8 / 1 / 11** | |
| Wall time mean / max | **141 s / 302 s** | 439 s / 1569 s |
| Gate failures | G7×6, G2×1 | G2×3, G3×6, G7×5, G9×1, G5×1 |
| Hard errors | 0 | 5 (1 suspect-fast + 4 timeouts at 1400 s) |

Honest caveats: partial repetitions (1.6–2.0 per article vs 3 planned —
the eval was killed mid-run by a VRAM contention stall from a
concurrent production grind), so the +0.225 is directional, not final.
The 3× wall-time advantage was measured under real contention, which is
how production actually runs. Full harvest: ops artifact 36247.

### The turbo-vs-stock Thai question (settled with statistics)

60-prompt bank (30 general-short, 15 report-long, 15 code-mixed),
300 completions, paired bootstrap 10,000 resamples, 2026-09-11:

- `thai_ratio` turbo vs stock: Δ +0.0155, 95% CI [−0.021, +0.054] —
  **includes zero: no significant Thai regression from the fine-tune.**
- Chinese-character leakage (Han events per 100 replies): turbo **15**,
  stock **43** — the fine-tune leaks *less*.
- Thinking tokens: turbo thinks ~2.4× less than stock (faster walls).

## The validated sampling recipe

Shipped as `configs/sampling-recipe.yaml`. Two layers, both measured:

**Layer 1 — Config G (system prompt + few-shot).** A Thai-only system
prompt with an explicit Han-character ban and two few-shot exemplars.
Effect: +0.029 `thai_ratio` over a mirror prompt, CI excludes zero; Han
events halve (35→15 per 100 without it).

**Layer 2 — Sampling parameters (pinned 2026-09-12).**

| Parameter | Value | Why |
|---|---|---|
| temperature | 0.6 | pinned; 1.0 was only ever paired with Config G, since invalidated |
| top_p | 0.95 | |
| top_k | 20 | |
| repeat_penalty | 1.0 | v3 pin (MTP alignment, DavidAU); higher values break code blocks; 8.0 (a typo) destroyed output — yes, we tested it |
| presence_penalty | 0.0 | any value >0 causes language mixing — pinned at zero (2026-09-12 finding; the earlier n=23 A/B tested thai_ratio suppression, a different symptom) |
| num_ctx | 32768 | below 8192, long Thai reports truncate |
| num_predict | 8192 | **completion safety** — see below |
| think | route-dependent | `false` for bots, `true` for deep routes |

Pinned 2026-09-12: all 6 aliases (turbo + chat / think / code / deep /
fast) were rebuilt with explicit `PARAMETER` lines — `repeat_penalty 1.0 ·
temperature 0.6 · top_p 0.95 · top_k 20 · presence_penalty 0.0` — so the
values ship in the Modelfile itself, not just the LiteLLM route layer.

### The completion-safety finding (the big one)

Historical `thai_ratio` swung wildly (0.72–0.92) through the LiteLLM
chain. Root cause was **not** the prompt — it was completion failures:
empty replies and truncations from small `num_predict` (64/900/4096)
colliding with hidden thinking tokens. At `num_predict: 8192`,
`num_ctx: 32768`, all 300/300 completions finished cleanly and
`thai_ratio` collapsed into a 0.036-wide band across **all** prompt
styles. Fix the floor first; prompt-tune second.

### The thinking-budget trap (bot routes)

A reasoning-capable model with `think` enabled and a small
`num_predict` burns the entire budget on hidden reasoning and returns
**empty content** (`done_reason: length`). Our LINE bot hit this. Fix:
bot routes pin `think: false` + `num_predict` sized for the reply.
`configs/litellm.yaml.example` shows the `thai-chat-rt` route.

## Thai evaluation protocol (reproduce us)

Harness: `scripts/bench_thai.py`. Bank format and results:
`benchmarks/thai-quality.csv`.

1. **Bank:** 60 fixed prompts (30 general-short, 15 report-long,
   15 code-mixed), sha256-pinned. Prompts are Thai-first, production-
   derived (customer Q&A, gold/forex analysis, article writing, code).
2. **Scorer:** `thai_ratio = thai_chars / (thai_chars + latin_chars)`,
   reasoning stripped. Also tracked: Han-character events per 100
   replies, completion rate, finish-reason distribution, tok/s, TTFT.
3. **Statistics:** paired bootstrap, 10,000 resamples, 95% CI; a
   challenger must beat the incumbent with CI excluding zero.
4. **Contamination control:** single model resident; log every reload;
   discard rows from polluted windows (we quarantined 58 tainted rows
   once — the sidecar file is in the raw evidence).
5. **Gates:** completion_rate ≥ 0.95 to qualify; promotion requires
   CI-excluding-zero win.

## Known issues (honest list)

- **Han leakage is not zero.** ~15/100 replies contain a stray Chinese
  character even with Config G. Down from 43, not eliminated.
- **Edge cases:** strict-JSON + mixed-language prompts can exceed a 30 s
  bot timeout (2/50 in the graded eval). Route those to Tier 3 or trim
  prompts.
- **English technical questions:** the stock persona answers *everything*
  in Thai — including English coding questions. A prompt revision that
  routes EN technical to English flipped our Thai-purity gates. Owner
  decision: Thai-always stays default; per-route override exists.
- **Long-context raw callers:** routes that bypass the persona row run
  at `num_ctx 8192` unless the Modelfile floor sets 32768. Set it.
- **Web-search deflection:** with web search forced on, the model
  sometimes greets instead of answering current-price questions. Under
  investigation; tracked in the issue tracker.

## Contributing Thai evals

New prompts: open a PR adding rows to the bank with category tags.
New languages: the protocol is language-agnostic — swap the scorer's
character classes. We'd love Lao, Khmer, and Burmese banks.
