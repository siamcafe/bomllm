---
language:
  - th
  - en
license: mit
tags:
  - thai
  - qwen3
  - mlx
  - nvfp4
  - bom-llm
base_model: DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NM-DAU
pipeline_tag: text-generation
model-index:
  - name: TURBO-Fable-27B-BOM
    results:
      - task:
          type: text-generation
          name: Thai Language Generation
        metrics:
          - type: accuracy
            value: 1.0
            name: Thai Gate (20/20)
          - type: custom
            value: 0.0
            name: Han Leak (0/5)
---

# BOM LLM v0.8 — TURBO-Fable 27.78B

🇹🇭 Thai AI Model — Free for Thai people

## What's New in v0.8 (Oct 30, 2026)

- **GOD CONFIG v7.0** — 9 production config changes
- **Open WebUI v0.12.4** — upgraded from v0.11.3
- **LiteLLM v1.106.3** — security patched (v1.107.0 supply-chain compromise blocked)
- **Ollama 0.40.10** — upgraded from 0.40.1
- **Qdrant v1.20.0** — upgraded from 1.19

## Model Details

- **Base**: DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NM-DAU
- **Parameters**: 27.78B (27,781,081,984)
- **Layers**: 1,204
- **Quantization**: nvfp4 (MLX) / Q4_K_M (GGUF)
- **Size**: 21.58 GB (MLX) / 18.50 GB (GGUF)

## Benchmark Results

| Test | Score | Details |
|------|-------|---------|
| Thai Gate | 20/20 = 1.00 | 10 questions, all 2/2, thai chars 292-1064 |
| Han Leak | 0/5 = 0.00 | Zero Chinese character leakage |
| Street Test | 3/3 PASS | thai>50, han<3, bytes>200 |
| Speed | 18.5 tok/s | Range 17-20, Apple M4 Pro MLX |

## Recommended Parameters (GOD CONFIG v7.0)

| Parameter | Value |
|-----------|-------|
| temperature | 0.6 |
| top_p | 0.95 |
| top_k | 20 |
| repeat_penalty | 1.0 |
| presence_penalty | 0.0 |
| num_ctx | 8192 |
| num_predict | 4096 |

⚠️ **presence_penalty MUST be 0.0** — setting 1.5 causes Han (Chinese) character leakage.

## License

MIT / Apache-2.0
