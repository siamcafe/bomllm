## What & why

<!-- one hypothesis per PR: state it, change one thing, measure it -->

## Receipts

<!-- before/after numbers + hardware + reproduce command, if applicable -->

## Checklist

- [ ] No secrets (`git grep -nEi '(sk-|api[_-]?key|token|password|secret)' -- ':!*.example'` eyeballed)
- [ ] `.gitignore` updated FIRST if a new credential-bearing file type appears
- [ ] `NOTICE` updated if a third-party component was added
- [ ] Docs updated if behavior changed
- [ ] Benchmark claims include hardware + date + reproduce command
- [ ] No test/benchmark edited to make it pass
