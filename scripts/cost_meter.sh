#!/usr/bin/env bash
# ============================================================================
# BOMLLM cost meter — turns wall-meter readings into the cost table.
#
# Two input modes:
#   1. Manual: edit the DEVICES block below with your smart-plug's
#      7-day average watts per device, then run the script.
#   2. CSV:    --csv your_meter_export.csv with columns: device,avg_watts
#
# Output: a Markdown table + a CSV row set ready to append to
# benchmarks/cost-comparison.csv
#
#   ./scripts/cost_meter.sh --tariff 0.125
#   ./scripts/cost_meter.sh --tariff 0.125 --csv my_meters.csv
# ============================================================================
set -euo pipefail

TARIFF="0.125"     # USD per kWh — Thai residential ~฿4.5/kWh ≈ $0.125
CSV=""
DAYS=7             # averaging window of your meter readings

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tariff) TARIFF="$2"; shift 2 ;;
    --csv)    CSV="$2";    shift 2 ;;
    --days)   DAYS="$2";   shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

# --- DEVICES: name|avg_watts  (EDIT THESE — [BENCH_DATA_PENDING] in git) ----
DEVICES=$(
  cat <<'EOF'
mac_mini_m4pro|BENCH_DATA_PENDING
i9_2x_rtx5060ti|BENCH_DATA_PENDING
synology_ds725|BENCH_DATA_PENDING
network_share|BENCH_DATA_PENDING
EOF
)

if [[ -n "$CSV" ]]; then
  [[ -f "$CSV" ]] || { echo "csv not found: $CSV" >&2; exit 1; }
  DEVICES=$(awk -F, 'NR>1 {print $1"|"$2}' "$CSV")
fi

if echo "$DEVICES" | grep -q BENCH_DATA_PENDING; then
  cat >&2 <<'EOF'
[cost_meter] Device watts are still BENCH_DATA_PENDING.
Measure each device with a plug meter for 7 days, then either:
  - edit the DEVICES block in this script, or
  - pass --csv with columns: device,avg_watts
Example row: mac_mini_m4pro,38.5
EOF
  exit 1
fi

echo "| Device | Avg watts | kWh/day | Cost/day (USD) |"
echo "|---|---|---|---|"
TOTAL_KWH=0
TOTAL_COST=0
DATE=$(date +%F)

while IFS='|' read -r name watts; do
  [[ -z "$name" ]] && continue
  kwh=$(awk "BEGIN{printf \"%.3f\", $watts*24/1000}")
  cost=$(awk "BEGIN{printf \"%.4f\", $kwh*$TARIFF}")
  TOTAL_KWH=$(awk "BEGIN{printf \"%.3f\", $TOTAL_KWH+$kwh}")
  TOTAL_COST=$(awk "BEGIN{printf \"%.4f\", $TOTAL_COST+$cost}")
  echo "| $name | $watts | $kwh | \$$cost |"
  # CSV rows for benchmarks/cost-comparison.csv (append manually after review)
  echo "$DATE,electricity,$name,$kwh,kwh_day,$TARIFF,$cost,cost_meter_sh,\"${DAYS}d avg\"" >> cost_meter_rows.csv
done <<< "$DEVICES"

echo "| **Fleet total** | | **$TOTAL_KWH** | **\$$TOTAL_COST** |"
echo
echo "CSV rows appended to: cost_meter_rows.csv — review, then merge into"
echo "benchmarks/cost-comparison.csv (never commit meter exports with"
echo "location-identifying metadata)."
