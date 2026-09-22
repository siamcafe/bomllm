# Screenshots — curated set lands before Show HN

Tracking: `docs/show-hn.md` (launch checklist items M-1..M-5).

Rules for every screenshot in this folder:

1. **Vision-verified before commit** — a screenshot nobody looked at is
   not evidence. Open it, check it, then commit.
2. **Sanitized** — no real API keys (blur/crop key fields), no real user
   emails, no internal IPs or Tailscale addresses, no real account
   numbers. Chat content must use the staged demo conversations.
3. **Naming:** `01_webui_thai_chat.png`, `02_line_bot_phone.png`,
   `03_litellm_spend_dashboard.png`, `04_mac_mini_desk_meter.png`,
   `05_architecture_diagram.png`.
4. **Format:** PNG, ≤ 1600 px wide, ≤ 500 KB. Dark UI preferred.
5. **Video:** `walkthrough_90s.mp4` lives on the release page, not in git
   (repo size). Link from README once uploaded.

Captured 2026-09-12 (headless, vision-verified — not yet curated to the
naming/width rules above):

- `webui_thai_chat.png` — Thai question + Thai answer visible (vision-checked)
- `litellm_spend.png` — LiteLLM usage/spend dashboard, Sep 5–12 window
- `mac_dashboard.png` — monitoring dashboard substitute (Netdata: CPU /
  memory / disk / network, multi-node) — **wall-meter photo pending**;
  the desk shot with the plug meter still needs a physical capture
- Not captured (physical): LINE bot phone photo, 90 s walkthrough video

Planned shots (from the README placeholders):

- [ ] WebUI answering a Thai gold-price question with web search citations
- [ ] LINE bot conversation (phone, Thai)
- [ ] LiteLLM spend dashboard: $0.31–$2.76/day fallback spend
- [ ] The Mac Mini on the desk next to the plug meter (the $0.54 receipt)
- [ ] Architecture diagram (mermaid render or the dark-theme PNG)
