# GOD CONFIG v7.0

Policy ID: `bomllm.policy/v7.0` · Status: **PRODUCTION with documented deviations** · Source: BomLLM Mega Tuning Report (art#54324, 2026-10-29) · Verified fleet-wide 2026-10-31.

## Locked Generation Defaults

| Parameter | Value | Reason |
|-----------|-------|--------|
| temperature | 0.6 | Thai quality gate — ≥0.7 fails |
| top_p | 0.95 | Balanced sampling |
| top_k | 20 | Focused vocabulary |
| repeat_penalty | 1.0 | No repetition bias |
| presence_penalty | 0.0 | ⛔ CRITICAL — 1.5 causes Han leak |
| num_predict | 4096 | Max generation length |
| num_ctx | 8192 | Context window |

⛔ **DO NOT change presence_penalty from 0.0** — values >0 cause Chinese character leakage in Thai responses.

```yaml
# locked_params (bomllm.policy/v7.0)
temperature: 0.6
top_p: 0.95
top_k: 20
repeat_penalty: 1.0
presence_penalty: 0.0
num_predict: 4096
num_ctx: 8192
```

## Per-Model Compliance Table

| model_name | machine | temp | top_p | top_k | rep_pen | pres_pen | num_pred | num_ctx | compliant | notes |
|------------|---------|------|-------|-------|---------|----------|----------|---------|-----------|-------|
| qwen38-uni | Mac | 0.6 | 0.95 | 20 | 1.0 | 0.0 | 4096 | 8192 | YES | Production; parameter-only manifest; reloaded |
| bomai-pro | Mac | 0.6 | 0.95 | 20 | 1.0 | 0.0 | 4096 | 8192 | YES | Unloaded |
| bomai-mini | Mac | 0.6 | 0.95 | 20 | 1.0 | 0.0 | 4096 | 8192 | YES | Unloaded |
| bomai-gemma3 | Mac | 0.6 | 0.95 | 20 | 1.0 | 0.0 | 4096 | 8192 | YES | Unloaded |
| nomic-embed-text | Mac | N/A | N/A | N/A | N/A | N/A | N/A | 8192 | N/A | Embedding only |
| bge-m3 | Mac | N/A | N/A | N/A | N/A | N/A | N/A | unset | N/A | Embedding only |
| qwen3-vl:2b | UA | 0.6 | 0.95 | 20 | 1.0 | 0.0 | 4096 | 8192 | YES | Reloaded; inference returned `OK` |
| bomai-safe | UA | 0.6 | 0.95 | 20 | 1.0 | 0.0 | 4096 | 8192 | YES | Existing compliant tag |
| bomai | UA | 0.6 | 0.95 | 20 | 1.0 | 0.0 | 4096 | 8192 | YES | Context/predict corrected |
| siamcafe/bom-ai:latest | UA | 0.6 | 0.95 | 20 | 1.0 | 0.0 | 16384 | 32768 | NO | Protected production tag; not modified |
| siamcafe/bom-ai:v0.3.1-rc.1 | UA | 0.6 | 0.95 | 20 | 1.0 | 0.0 | 16384 | 32768 | NO | Protected production tag; not modified |
| bom-ai r4d-prod | UA | 0.6 | 0.95 | 20 | 1.0 | 0.0 | 16384 | 32768 | NO | Protected prod tag; not modified |
| bom-ai r4c-prod | UA | 0.6 | 0.95 | 20 | 1.0 | 0.0 | 16384 | 32768 | NO | Protected prod tag; not modified |
| bom-ai r4d-eval | UA | 0.6 | 0.95 | 20 | 1.0 | 0.0 | 4096 | 8192 | YES | Unchanged |
| bom-ai r4c-eval | UA | 0.6 | 0.95 | 20 | 1.0 | 0.0 | 4096 | 8192 | YES | Unchanged |
| bomai-v3 | UA | server default | server default | server default | server default | 0 by llama.cpp default | 4096 | 8192 | DEVIATION | parallel 2; mmproj, grammar, jinja preserved |
| gpt-oss-120b | UA | server default | server default | server default | server default | 0 by llama.cpp default | default | 32768 | DEVIATION | Production `llm-smart`; no authorized recreate |
| bomai-safe | AM4 | 0.6 | 0.95 | 20 | 1.0 | 0.0 | 4096 | 8192 | YES | New tag from existing base; base ID unchanged |
| siamcafe/bom-ai:v0.3.1-rc.1 | AM4 | 0.6 | 0.95 | 20 | 1.0 | 0.0 | 16384 | 32768 | NO | Protected base tag; not modified |
| bomai-pro | i9 | server default | server default | server default | server default | 0 by llama.cpp default | default | 8192 | DEVIATION | parallel 1; NSSM Automatic; health 200 |

## Documented Deviations

1. **Protected production tags** (`siamcafe/bom-ai` tags, `bom-ai r4*-prod`): retain `num_ctx 32768` / `num_predict 16384` by owner ruling — never rewritten; new compliant workloads must use a **new tag** (e.g. `bomai-safe`).
2. **llama.cpp servers** (`bomai-v3`, `gpt-oss-120b`, i9 `bomai-pro`): sampler is server default; `presence_penalty` is 0 by llama.cpp default. `gpt-oss-120b` keeps ctx 32768 as a deliberate production deviation.
3. **Embedding-only models** (`nomic-embed-text`, `bge-m3`): no sampler block — exempt.

## Deploy a New Model (GOD-compliant Modelfile)

```dockerfile
FROM siamcafe/bom-ai:v0.3.1-rc.1
PARAMETER temperature 0.6
PARAMETER top_p 0.95
PARAMETER top_k 20
PARAMETER repeat_penalty 1.0
PARAMETER presence_penalty 0.0
PARAMETER num_predict 4096
PARAMETER num_ctx 8192
```

```bash
# Create a NEW tag; never overwrite the production base tag.
ollama create bomai-safe -f /tmp/Modelfile.bomai-safe
ollama show bomai-safe --modelfile | grep -E 'temperature|top_p|top_k|repeat_penalty|presence_penalty|num_predict|num_ctx'
```

Use only Q4_K_M for new GGUF deployments; never Q6_K.

## Compliance Check (fleet-wide)

```bash
O=ollama   # AM4: O=/home/bom/.local/share/BOM-AI/ollama-v0.40.13/bin/ollama
bad=0
for M in $($O list | awk 'NR>1 {print $1}'); do
  case "$M" in
    nomic-embed-text:*|bge-m3:*) echo "N/A $M (embedding only)"; continue ;;
    siamcafe/*|*-prod) echo "PROTECTED $M (compare with the documented deviation)"; continue ;;
  esac
  for KV in temperature=0.6 top_p=0.95 top_k=20 repeat_penalty=1.0 presence_penalty=0.0 num_predict=4096 num_ctx=8192; do
    K=${KV%%=*}; V=${KV#*=}
    if ! $O show "$M" --modelfile | awk -v k="$K" -v v="$V" \
      '$1=="PARAMETER" && $2==k && ($3+0)==v {found=1} END {exit !found}'; then
      echo "FAIL $M $K expected $V"; bad=1
    fi
  done
done
[ "$bad" -eq 0 ] && echo 'ALL_UNPROTECTED_GENERATION_MODELS_COMPLIANT'
```

## Audit Results (2026-10-31)

- GOD CONFIG `pp=0` verified on 15 models across all machines — **0 nonzero presence_penalty**.
- Breakdown: 6 fully compliant + 3 known protected deviations + 4 QC-owned samplers at pp=0 + 2 embeddings exempt.
- Mac: explicit `PARAMETER presence_penalty 0` appended to 6 non-protected models (modelfile backups in `/tmp/god_fix_backup_20261031/`).
- QC stack (AM4 :11440): 4/4 models pinned to `presence_penalty=0`.

## Change Policy

⛔ Parameters above are **locked**. Changing any value (especially `presence_penalty` > 0) requires an explicit owner ruling and a new policy version (`bomllm.policy/v7.x`).
