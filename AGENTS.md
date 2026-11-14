# bomllm AGENTS.md — safety constraints (survive compaction)

## Fleet state (2026-11-14, release v18.0.0)
- 8 machines: C2, UA, AM4, NAS, i9, Mac, CAT, CB1 (+ AM5 command station, not counted)
- RAM 1,200+ GB total; 8 GPUs (UA 5080+5060Ti, AM4 5080+iGPU, i9 5060Ti x2, AM5 4060)
- LiteLLM 1.108.8 LTS (C2/UA/AM4, applied 2026-11-14; 1.107.0 COMPROMISED/BANNED; 1.109.x forbidden)
- OWUI v0.13.3 (C2, UA, AM4, Mac); ComfyUI v0.45.0 fleet (i9:8189 upgraded 2026-11-14)
- Ollama 0.40.13-0.40.16 (unifying on 0.40.16; Mac fleet daemon 0.40.16)
- keep_alive "24h" everywhere — NEVER "-1" (incident #33)
- BOM AI v2.1.8 — Pro = 709-L 27B GGUF Q4_K_M all platforms (Mac keeps MLX nvfp4)
- Gateway rc3: stream resume, 0/272 Han-cut rate; web search default OFF
- Incidents 34 | IRON rules 57+ | Mac Studio M5 Ultra 512GB on order (Jan-Feb 2027)

## 安全约束 (存活 compaction)
- 禁止修改 sshd/authorized_keys/PasswordAuthentication/DNS/resolv.conf (IRON 38 ABSOLUTE)
- 禁止重启 gpt-oss-120b/ComfyUI/FX28/n8n/LiteLLM (除非 owner 明确下令)
- LiteLLM v1.107.0 禁止; i9 D: 不可触碰; 禁止打印密钥
- IRON 40: 正常工作的不要动; 禁止 enable ufw
- n8n 全部工作流 (Contabo 生产 + NAS 本地): 只有 owner 明确下令才动

证据: 需真实命令输出 — 不接受 self-report
Compact Instructions: compaction 后重读 AGENTS.md + D:\zcode\STATUS.md
