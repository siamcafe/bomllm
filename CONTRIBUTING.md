# Contributing to BOMLLM

Thanks for considering a contribution. BOMLLM is an operations kit built
from production scars — contributions that add **receipts** (measurements,
repro scripts, honest failure reports) are valued above contributions that
add adjectives.

## Ground rules

1. **No secrets, ever.** PRs containing API keys, tokens, real IPs,
   webhook URLs, account numbers, or personal data are rejected on sight.
   See `docs/security-audit.md` for the never-commit list.
2. **One hypothesis per PR.** State it, change one thing, measure, record
   the verdict. Do not stack speculative changes.
3. **Receipts over claims.** "Faster" needs a before/after number, the
   hardware it ran on, and the command to reproduce.
4. **Do not edit benchmarks to make them pass.** If a gate is wrong,
   open an issue and argue for recalibration with data.
5. **License hygiene.** New third-party components must be added to
   `NOTICE` with their license in the same PR.

## What we especially want

- Thai (and other non-English) evaluation prompts and scorers.
- Cost-meter data from other hardware (M4 base, M4 Max, M2/M3 Ultra,
  PC GPU boxes) via `scripts/cost_meter.sh`.
- Sampling recipes for other 27B-class MLX models, with A/B numbers.
- Channel adapters beyond LINE/Telegram (Discord, Slack, WhatsApp).
- Translations of docs (Thai first, then anything).

## Development setup

```bash
git clone https://github.com/bomllm/bomllm.git
cd bomllm
cp configs/.env.example .env   # fill with YOUR test values
./scripts/bootstrap.sh --dry-run
```

Run the Thai bench harness against your own endpoint:

```bash
python3 scripts/bench_thai.py --endpoint http://localhost:4000/v1 \
  --model your-model --bank benchmarks/thai-quality.csv --dry-run
```

## PR checklist

- [ ] No secrets (run `git grep -nEi '(sk-|api[_-]?key|token|password|secret)' -- ':!*.example'` and eyeball the hits)
- [ ] Docs updated if behavior changed
- [ ] `NOTICE` updated if a component was added
- [ ] Benchmark numbers include hardware, date, and reproduce command
- [ ] Commit messages in English, imperative mood

## Code of conduct

Be direct, be kind, bring data. We follow the
[Contributor Covenant](https://www.contributor-covenant.org/) v2.1.
