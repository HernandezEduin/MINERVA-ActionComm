#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
manifest="experiment_logs/table2_manifest.tsv"
out="experiment_logs/table2"
mkdir -p experiment_logs
rm -f "$manifest"
configs=(configs/kinshiphinton.yaml configs/metaqa.yaml configs/mquake_st_single.yaml configs/mquake_st_multi.yaml)
for checkpoint_seed in 0 42 100; do
  for config in "${configs[@]}"; do
    bash scripts/run_paper_eval.sh table2 "$config" "$checkpoint_seed" 42 1 false "$manifest"
    bash scripts/run_paper_eval.sh table2 "$config" "$checkpoint_seed" 42 100 true "$manifest"
  done
done
python scripts/aggregate_paper_results.py table2 --manifest "$manifest" --output-dir "$out"
echo "Table 2 summaries written to $out"
