#!/usr/bin/env bash
set -euo pipefail
echo "WARNING: Full paper reproduction is computationally expensive."
bash experiments/reproduce_table2.sh
bash experiments/reproduce_fig2.sh
bash experiments/reproduce_cap_sensitivity.sh
