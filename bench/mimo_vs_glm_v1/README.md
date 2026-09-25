# MiMo-V2.6 Q4 vs GLM-5.3 Coding Benchmark

**Date:** 2026-09-25
**Platform:** BOM LLM (Mac mini M4 Pro, Ollama 0.34.4)

## Results

| Model | Score | Runnable | Avg Time |
|-------|-------|----------|----------|
| MiMo-V2.6 Q4 (9B local) | 49/72 | 2/8 | 66.3s |
| GLM-5.3 (cloud) | 71/72 | 8/8 | N/A |

## Task Breakdown

| # | Task | MiMo | GLM | Gap |
|---|------|------|-----|-----|
| T1 | Python deduplicate_list | 8 ✅ | 9 ✅ | 1 |
| T2 | Python CSV summary | 8 ✅ | 9 ✅ | 1 |
| T3 | MQL5 SMA indicator | 2 ❌ | 9 ✅ | 7 🔴 |
| T4 | MQL5 FormatLotSize | 8 ❌ | 9 ✅ | 1 |
| T5 | WordPress mu-plugin REST | 5 ❌ | 9 ✅ | 4 |
| T6 | bash recent-files | 5 ❌ | 9 ✅ | 4 |
| T7 | Node fetch retry | 6 ❌ | 9 ✅ | 3 |
| T8 | Python RateLimiter | 7 ❌ | 8 ✅ | 1 |

## Verdict

MiMo-V2.6 Q4 = fast local drafting tool, NOT a GLM replacement.
- **Safe:** Simple Python drafts with test assertions, scaffolding under review
- **Keep GLM:** MQL5/EA, WordPress/PHP, bash, timing-critical code, review-free deliverables
- **Failure mode:** Confident fictional APIs, silently-wrong scripts

## Files

- `report.yaml` — Full structured report
- `report.json` — JSON format
- `report.log.txt` — Execution log
- `bundle.zip` — Complete benchmark bundle (tasks, runs, verification)
