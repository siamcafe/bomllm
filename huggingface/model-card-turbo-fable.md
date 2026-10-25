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

# BOM LLM — TURBO-Fable 27.78B

🇹🇭 Thai AI Model — Free for Thai people

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

## Recommended Parameters

| Parameter | Value |
|-----------|-------|
| temperature | 0.6 |
| top_p | 0.95 |
| top_k | 20 |
| repeat_penalty | 1.0 |
| presence_penalty | 0.0 |
| num_ctx | 8192 |
| num_predict | 4096 |

## License

MIT / Apache-2.0
