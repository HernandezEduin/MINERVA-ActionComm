#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
manifest="experiment_logs/cap_sensitivity_manifest.tsv"
out="experiment_logs/cap_sensitivity"
mkdir -p experiment_logs
rm -f "$manifest"
for config in configs/mquake_st_single.yaml configs/mquake_st_multi.yaml; do
  bash scripts/run_paper_eval.sh cap "$config" 42 42 100 true "$manifest"
  bash scripts/run_paper_eval.sh cap "$config" 42 42 100 true "$manifest" --rate_max_num_actions_override 512
done
python scripts/aggregate_paper_results.py cap --manifest "$manifest" --output-dir "$out"
echo "Cap-sensitivity summaries written to $out"
