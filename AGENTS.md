# bomllm AGENTS.md — safety constraints (survive compaction)

安全约束 (存活 compaction):
- 禁止修改 sshd/authorized_keys/PasswordAuthentication/DNS/resolv.conf
- 禁止重启 gpt-oss-120b/ComfyUI/FX28/n8n/LiteLLM
- LiteLLM v1.107.0 禁止; i9 D: 不可触碰; 禁止打印密钥
- IRON 40: 正常工作的不要动; 禁止 enable ufw

范围: 仅 6 phases
证据: 需真实命令输出 — 不接受 self-report
Compact Instructions: compaction 后重读 AGENTS.md + /tmp/k3_report.yaml
