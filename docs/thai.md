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
| TURBO-Fable (DavidAU fine-tune) | nvfp4 MLX | **incumbent** — no Thai regression vs stock, fewer think tokens | A/B below |
| Typhoon (Thai-specialized) | GGUF | retired — general model + good prompt beat it on our traffic | internal A/B |
| OpenThai / granite merges | various | evaluated, not promoted | internal |

**Current production:** TURBO-Fable nvfp4 (MLX), one manifest, five
aliases (chat / think / code / deep / fast) sharing one blob.

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

**Layer 2 — Sampling parameters.**

| Parameter | Value | Why |
|---|---|---|
| temperature | 1.0 (with Config G) / 0.6 (without) | measured equivalent on our bank; 0.6 is the simpler equal |
| top_p | 0.95 | |
| top_k | 20 | |
| repeat_penalty | 1.05 | >1.05 breaks code blocks; 8.0 (a typo) destroyed output — yes, we tested it |
| presence_penalty | 0.0 | hypothesis that 1.5 suppresses Thai: **refuted** (isolated A/B, n=23) |
| num_ctx | 32768 | below 8192, long Thai reports truncate |
| num_predict | 8192 | **completion safety** — see below |
| think | route-dependent | `false` for bots, `true` for deep routes |

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
