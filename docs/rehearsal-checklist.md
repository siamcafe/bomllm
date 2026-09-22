# Rehearsal Gate — Complete by Sep 29

Record-only rehearsal: run through each item, capture evidence (screenshot/curl output), do NOT fix anything during rehearsal.

## R0: Fleet health
- [ ] Mac ollama responding (curl tags)
- [ ] LiteLLM liveliness 200
- [ ] SearXNG responding
- [ ] All tunnel hostnames 200 (llm/webui/hub) + 403 (code/ide)

## R1: Chat path
- [ ] Send test message via webui.siam2r.com → receive response
- [ ] Response uses 709-L model (check LiteLLM log)

## R2: Live stream text path
- [ ] live-router healthz ws_connected=true
- [ ] Send test chat via Restream → response appears in overlay

## R3: Chart vision path
- [ ] chart-overlay healthz 200
- [ ] Send chart-intent message → vision response appears

## R4: Image generation
- [ ] Send image request → ComfyUI generates → response with image

## R5: Voice (SiangTTS)
- [ ] TTS responds with audio (reference-only mode)

## R6: n8n pipelines
- [ ] Social_Auto_Post workflow active
- [ ] bomLLM retry-on-429 tested

## R7: Monitoring
- [ ] Kuma dashboard: all green
- [ ] Beszel NAS metrics visible
- [ ] Mac netdata :19999 accessible

## R8: Security
- [ ] code.siam2r.com = 403
- [ ] ide.siam2r.com = 403
- [ ] ENABLE_SIGNUP = false on both webui instances

## R9: Content
- [ ] README $0.54 (not $3.50)
- [ ] Bot count = 4 BOM + LINE hybrid
- [ ] No stale version numbers

## R10: Burn cron
- [ ] burn_pause touch/rm cycle works
- [ ] Guard blocks burn during pause

## R11: Recovery
- [ ] Document: last known-good state of each service
- [ ] live-router restart=unless-stopped confirmed

## R12: Studio
- [ ] Browser source overlay visible
- [ ] Countdown timer manually configured
- [ ] Hotkeys tested with real window focus

---
Rehearsal PASS = all items checked with evidence captured.
Rehearsal FAIL on any item = fix BEFORE Sep 30 freeze.
After Sep 30: no Mac changes allowed regardless of rehearsal outcome.
