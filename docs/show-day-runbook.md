# Show Day Runbook — Oct 7 2026

## Pre-show checklist
- [ ] Pause burn cron: `ssh nas 'touch /tmp/burn_pause'` (guard checks this file)
- [ ] Verify Mac ollama running: `curl -s http://$MAC_LAN_IP:11434/api/tags | jq '.models | length'` (expect ≥1)
- [ ] Verify LiteLLM health: `curl -s https://llm.siam2r.com/health/liveliness` (expect 200)
- [ ] Verify live-router: `ssh -p $C2_SSH_PORT $C2_USER@$C2_HOST 'curl -s http://localhost:8090/healthz'` (expect ws_connected=true)
- [ ] Verify chart-overlay: `ssh -p $C2_SSH_PORT $C2_USER@$C2_HOST 'curl -s http://localhost:8091/healthz'` (expect 200)
- [ ] Confirm code.siam2r.com + ide.siam2r.com return 403

## Kuma monitor add (one-time)
- URL: http://kuma-host:3001
- Add monitor: type=http, name=live-router, url=http://100.x.y.z:8090/healthz, interval=60, retry=3
- Default Telegram notification auto-applies

## Mac power-loss recovery
- Proven Sep 20: ollama auto-starts, model prewarms, canary OK
- If Mini goes dark: wait 2 min for auto-boot → check ollama → if down: VNC via BetterDisplay → `ollama serve`
- UPS status: UNCONFIRMED (treat as no-UPS)

## LINE token renew
- Oct 1 03:10 ICT: cron fires LINE token refresh
- Verify: check log next morning for 200 response
- If fail: manual renew via LINE developer console (owner)

## Burn cron resume (post-show)
- Remove pause: `ssh nas 'rm /tmp/burn_pause'`

## Freeze-exception list (Sep 30 – Oct 7)
ALLOWED:
- Active security incidents (emergency patches)
- Service restart-only recovery (no config change)
- Oct 1 03:10 LINE renew log read
- Read-only monitoring
NOT ALLOWED:
- Any Mac config change
- Any new container deploy
- Any pipeline code change
- Any model swap

## Author-at-keyboard
- Owner available: 09:00–23:00 ICT Oct 7
- Studio hotkeys need real window focus (manual)
- Countdown timer: manual setup in Restream Studio

## mu-plugin disable checklist
Before disabling any mu-plugin:
1. Identify replacement behavior (who/what provides the function after disable)
2. Verify replacement is deployed and responding
3. curl the affected page(s) BEFORE disable
4. Disable (rename .php → .php.disabled)
5. curl the affected page(s) AFTER disable
6. If broken: rename back immediately
