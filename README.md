# MINERVA-ActionComm

Code for the manuscript:

**"Action Communication in Shared-Policy Multi-Hop Graph Navigation"**

This repository studies stochastic action communication in shared-policy multi-hop graph navigation. It builds on the question-conditioned **MINERVA** adaptation used in [THESEUS](https://github.com/HalcyonSolutions/THESEUS) and evaluates fixed pretrained policies without retraining them for communication.

The experiments compare native deterministic MINERVA beam inference with repeated greedy, Top-`K`, and unrestricted stochastic execution on **KINSHIP**, **MetaQA**, and **MQuAKE-ST**.

## Relationship to THESEUS

Datasets and pretrained checkpoints are maintained through the canonical [THESEUS resource page](https://github.com/HalcyonSolutions/THESEUS):

> [**Theseus in the Graph: Towards Traceable Multi-Hop Graph Navigation**](https://github.com/HalcyonSolutions/THESEUS)  
> [arXiv:2609.14528](https://arxiv.org/abs/2609.14528)

This repository contains the action-communication evaluation code and experiment wrappers built around those resources.

## Setup

```bash
git clone --recurse-submodules https://github.com/HernandezEduin/MINERVA-ActionComm.git
cd MINERVA-ActionComm

cd minerva
pip install -r requirements.txt
cd ..
```

If the repository was cloned without submodules:

```bash
git submodule update --init --recursive
```

The paper reproduction wrappers default to the Conda environment `minerva_tf2`, which was used for the reported experiments. Set `ACTIONCOMM_ENV` to another Conda environment name if needed, or set it to an empty string to use the currently active environment.

## Datasets and Pretrained Checkpoints

Obtain datasets and pretrained checkpoints from [THESEUS](https://github.com/HalcyonSolutions/THESEUS). Place them in the locations expected by the configs:

```text
.cache/
datasets/
saved_models/
```

Available configs:

- `configs/kinshiphinton.yaml`
- `configs/metaqa.yaml`
- `configs/mquake_st_single.yaml`
- `configs/mquake_st_multi.yaml`

## Running an Individual Evaluation

```bash
bash run_rate_sweep.sh configs/mquake_st_single.yaml 0 \
  --rate_test_rollouts 100 \
  --rate_top_k 2 4 \
  --rate_include_numpy_policy true \
  --rate_seed 42
```

The optional positional argument after the config is the **GPU ID**. In the example above, `0` selects GPU 0. Omit it for CPU execution.

The paper uses two distinct seeds:

- **checkpoint/training seed**: the `seed` field in the YAML config, which selects the pretrained checkpoint
- **execution seed**: `--rate_seed`, which controls stochastic action sampling during evaluation

A legacy entry point is retained for compatibility:

```bash
bash run_infocost.sh configs/kinshiphinton.yaml
```

Some internal filenames retain the earlier `infocost` naming for reproducibility and compatibility with historical outputs. These names do not denote a separate method.

## Reproducing the Paper

| Paper artifact | Reproduction entry point | Protocol |
| --- | --- | --- |
| Table 1: datasets and evaluation settings | configs plus Table 2 runs | fixed settings and Greedy truncation |
| Table 2: cross-dataset utility and realization payload | `experiments/reproduce_table2.sh` | checkpoint seeds 0, 42, 100; execution seed 42; R=1 and R=100 |
| Fig. 2(a): MetaQA payload versus MRR | `experiments/reproduce_fig2.sh` | checkpoint seeds 0, 42, 100; execution seeds 42-46 |
| Fig. 2(b): checkpoint robustness | `experiments/reproduce_fig2.sh` | checkpoint-level MRR after averaging stochastic execution seeds |
| MQuAKE-ST cap sensitivity | `experiments/reproduce_cap_sensitivity.sh` | checkpoint seed 42; execution seed 42; cap 200 versus 512 |

Run an individual artifact:

```bash
bash experiments/reproduce_table2.sh
bash experiments/reproduce_fig2.sh
bash experiments/reproduce_cap_sensitivity.sh
```

or the complete sequence:

```bash
bash experiments/reproduce_all.sh
```

These experiments are computationally expensive, especially MetaQA.

The wrappers write manifests and paper-facing CSV/JSON summaries under `experiment_logs/`. Raw evaluator outputs remain under `saved_models/<dataset>/<run_name>/rate_sweep/`.

See [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md) for the exact paper-to-code mapping.

## Lower-Level Experiment Wrappers

The original stage wrappers are retained for provenance:

```text
experiments/
├── 01_run_r1_all_datasets.sh
├── 02_run_mquake_cap512.sh
├── 03_run_kinship_multiseed_r100.sh
├── 04_run_metaqa_multiseed_r100.sh
├── 05_run_r100_diversity_all_datasets.sh
└── 06_run_mquake_beam_cap512.sh
```

Scripts 03 and 04 vary **execution seeds**, not checkpoint seeds. Use the paper-facing wrappers above for the reported Table 2 and Fig. 2 values.

## Outputs

Each rate-sweep directory contains:

- `rate_sweep_summary.csv`
- `rate_sweep_summary.json`
- `rate_sweep_metadata.json`
- evaluator diagnostic plots

## Citation

If you use this repository, please cite the manuscript:

```bibtex
@misc{hernandez2026actioncomm,
  author = {Hernandez, Eduin E. and Garcia, Luis F. and Askar, Nurassyl and Rini, Stefano},
  title  = {Action Communication in Shared-Policy Multi-Hop Graph Navigation},
  year   = {2026},
  note   = {Manuscript},
  url    = {https://github.com/HernandezEduin/MINERVA-ActionComm}
}
```

If you use the THESEUS datasets, pretrained checkpoints, or adapted MINERVA setup, please also cite:

```bibtex
@article{hernandez2026theseus,
  author  = {Hernandez, Eduin E. and Garcia, Luis F. and Askar, Nurassyl and Diaz, Sergio A. and Rini, Stefano},
  title   = {Theseus in the Graph: Towards Traceable Multi-Hop Graph Navigation},
  journal = {arXiv preprint arXiv:2609.14528},
  year    = {2026}
}
```

Please also follow the dataset-specific citation guidance in the [THESEUS repository](https://github.com/HalcyonSolutions/THESEUS).
