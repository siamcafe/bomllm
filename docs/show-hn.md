# Show HN launch plan — BOMLLM

**Target:** Tuesday, 2026-10-07, 20:00 ICT (= 13:00 UTC = 09:00 EDT —
HN's front page turns over on US-morning traffic; Tuesday avoids the
Monday news flood and the Friday weekend drop).

**Title (locked):**
`Show HN: BOMLLM – I replaced $50/day cloud AI with a $3.50/day Mac Mini serving 5 bots`

Why this title: one unexpected number ($3.50/day), one concrete contrast
($50/day), one credibility signal (5 bots = production, not a demo).
Under 80 chars. No adjectives like "blazing".

---

## T-minus checklist

**Readiness note (2026-09-16, T-21d):** the 709-L cutover is baked into
the repo (README, docs/thai.md, configs/ollama-modelfile.example,
configs/sampling-recipe.yaml — Arm B paired-eval numbers in, sampling
pin t0.6/top_p0.95/pp0/rep1.05 documented verbatim from the production
Modelfile). L-7 status: Config G cells resolved-as-invalidated (note in
sampling-recipe.yaml), Arm B eval cells filled; meter CSV cells still
`[BENCH_DATA_PENDING]` until the post-cutover electricity re-run.

### L — Logistics (T-14d → T-1d)

- [ ] **L-1.** GitHub org `bomllm` created; repo `bomllm/bomllm` public;
  default branch `main`; MIT LICENSE + NOTICE committed.
- [ ] **L-2.** Push history is CLEAN — the security-audit gate
  (`docs/security-audit.md`) ran on the exact commit being pushed;
  `git log -p` spot-checked for secrets (not just the working tree).
- [ ] **L-3.** `security@` contact live (or GitHub private vulnerability
  reporting enabled) — SECURITY.md updated with the real address.
- [ ] **L-4.** HuggingFace org `bomllm` (account: siamcafe) created;
  repo `bomllm/turbo-thai-config` public with model card, recipe,
  system prompt, eval bank, scorer. No weights.
- [ ] **L-5.** Repo social preview image (1280×640) uploaded in GitHub
  settings — the architecture diagram, dark theme.
- [ ] **L-6.** Topics set: `self-hosted`, `llm`, `ollama`, `mlx`,
  `apple-silicon`, `thai`, `litellm`, `open-webui`, `homelab`.
- [ ] **L-7.** Fill every `[BENCH_DATA_PENDING]`: meter CSV into
  `benchmarks/cost-comparison.csv`; release-hardware rerun row in
  `benchmarks/thai-quality.csv`; watt table in `docs/hardware.md`;
  Config G verbatim prompt into `configs/sampling-recipe.yaml` + HF repo.
- [ ] **L-8.** `./scripts/bootstrap.sh` tested on a FRESH VPS (or fresh
  docker context) end-to-end. The README promise is one command; it must
  be true.
- [ ] **L-9.** Issue templates + PR template render correctly; Discussions
  enabled with categories: Q&A, Show and tell, Benchmarks.
- [ ] **L-10.** GitHub release `v1.0.0` drafted (not published) with
  changelog body.

### M — Media (T-7d → T-2d)

- [ ] **M-1.** Screenshot 1: WebUI Thai chat with web-search citations.
- [ ] **M-2.** Screenshot 2: LINE bot on a phone.
- [ ] **M-3.** Screenshot 3: LiteLLM spend dashboard ($0.31–$2.76/day).
- [ ] **M-4.** Screenshot 4: Mac Mini + plug meter on the desk.
- [ ] **M-5.** 90-second walkthrough video: terminal `git clone` →
  bootstrap → first Thai answer. Hosted (YouTube unlisted or GitHub
  release asset), linked from README. 90 s > 10 pages of docs.
- [ ] **M-6.** Every screenshot vision-verified + sanitized per
  `assets/screenshots/PLACEHOLDER.md` rules.

### C — Copy (T-3d)

- [ ] **C-1.** First comment finalized (draft below).
- [ ] **C-2.** Blog post on the personal site (Thai + English) telling the
  3-month story: the swap incident, the empty-reply bug, the $50 → $3.50
  cutover. Link ready but posted AFTER HN (don't split the discussion).
- [ ] **C-3.** Thai-language posts queued for Facebook/LINE OA —
  scheduled for T+4h, not T+0.

---

## First comment (post within 60 seconds of submission)

> Author here. The honest limits, since the README is required to be
> cheerful:
>
> - **It's one 27B model on one Mac.** If the Mac reboots, a small CPU
>   model on the VPS keeps the bots alive (slower, dumber), and true
>   cloud fallback costs us $0.31–$2.76 on days it fires. Single point
>   of failure? Yes. Acceptable for a 5-bot business? Also yes, so far.
> - **It's not a frontier model.** For hard novel coding I still pay for
>   a frontier API. BOMLLM covers the ~85% of traffic that is Thai Q&A,
>   content drafting, classification, and translation — and on our
>   50-case graded eval it actually outscored the cloud model it
>   replaced (ratio 1.20, dual-graded, methodology in the repo).
> - **Thai is the hard part, and it's not perfect.** ~15/100 replies
>   still leak a stray Chinese character. The eval harness, the prompt
>   bank, and the full negative results (what did NOT work) are all in
>   the repo.
> - **The $3.50 is electricity only.** Hardware was ~$2k for the Mac;
>   payback was ~6 weeks at our volume. The cost doc shows the meter
>   method and the LiteLLM spend-log queries so you can audit both
>   numbers.
> - **Not a trading bot** — the MT5 integration is a read-only analysis
>   panel. Nothing here places trades.
>
> Happy to answer anything about the MLX vs GGUF numbers (30.2 vs 7.9
> tok/s on the same box), the LiteLLM passthrough footguns, or running
> this on smaller Macs.

---

## Timing plan (launch day, ICT)

| Time | Action |
|---|---|
| 19:30 | Final push; verify GitHub renders README mermaid + tables |
| 19:45 | Post first comment text in a local draft; open HN submit page |
| 20:00 | Submit. Immediately paste first comment. |
| 20:00–23:00 | **Author at keyboard.** Answer every comment within 15 min. Honest > defensive. |
| 23:00 | Log position, upvotes, top objections into the retro file |
| T+1d 08:00 | Morning US wave: answer overnight comments |
| T+1d | Fix any doc bugs reported; tag `v1.0.1` if needed |
| T+2d | Publish the blog post; link the HN thread |
| T+7d | Retro: stars, forks, issues opened, what questions repeated (→ FAQ) |

## What we will NOT do

- No upvote rings, no alt accounts, no "please star". HN detects and
  punishes all of it, and the repo's whole pitch is receipts.
- No editing the README mid-thread to dodge a criticism — answer in the
  thread, fix in a commit, link the commit.
- No arguing about Thai quality claims without the harness — point to
  `benchmarks/README.md` and invite a rerun.

## Success criteria (ours, not HN's)

- Front page ≥ 4 h; ≥ 300 points is a win.
- ≥ 3 issues filed by people who actually ran `bootstrap.sh`.
- ≥ 1 external benchmark row contributed within 2 weeks.
- Zero credential-leak incidents from the launch (the audit gate holds).
