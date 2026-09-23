# MINERVA-ActionComm

Code for the manuscript:

**"Action Communication in Shared-Policy Multi-Hop Graph Navigation"**

This repository studies the communication associated with stochastic action realizations in shared-policy multi-hop graph navigation. It builds on the question-conditioned **MINERVA** adaptation used in [THESEUS](https://github.com/HalcyonSolutions/THESEUS) and evaluates fixed pretrained policies without retraining them for communication.

The main comparisons include:

- native deterministic MINERVA beam inference
- repeated greedy execution
- Top-`K` stochastic execution
- unrestricted stochastic execution
- single-trajectory and multi-candidate evaluation settings

The experiments cover **KINSHIP**, **MetaQA**, and **MQuAKE-ST**.

## Relationship to THESEUS

This project reuses the navigation-ready resources and question-conditioned MINERVA setup from:

> [**THESEUS: Theseus in the Graph: Towards Traceable Multi-Hop Graph Navigation**](https://github.com/HalcyonSolutions/THESEUS)  
> [arXiv:2609.14528](https://arxiv.org/abs/2609.14528)

Please use the **THESEUS repository as the canonical resource page for datasets and pretrained checkpoints**:

https://github.com/HalcyonSolutions/THESEUS

THESEUS provides the current dataset links and checkpoint release status. This repository contains the action-communication evaluation code and experiment wrappers built around those resources.

## Setup

Clone the repository and initialize the MINERVA submodule:

```bash
git clone --recurse-submodules https://github.com/HernandezEduin/MINERVA-ActionComm.git
cd MINERVA-ActionComm
```

If the repository was cloned without submodules, initialize them with:

```bash
git submodule update --init --recursive
```

Install the MINERVA requirements:

```bash
cd minerva
pip install -r requirements.txt
cd ..
```

## Datasets and Pretrained Checkpoints

Datasets and pretrained checkpoints are maintained through the [THESEUS resource page](https://github.com/HalcyonSolutions/THESEUS).

After obtaining the required resources, place them in the locations expected by the provided configs. The evaluation code uses the following top-level resource directories:

```text
.cache/
datasets/
saved_models/
```

Available evaluation configs are:

- `configs/kinshiphinton.yaml`
- `configs/metaqa.yaml`
- `configs/mquake_st_single.yaml`
- `configs/mquake_st_multi.yaml`

## Running the Evaluation

The main rate-sweep entry point evaluates existing checkpoints under greedy and stochastic action-selection modes without retraining.

Example:

```bash
bash run_rate_sweep.sh configs/mquake_st_single.yaml 0 \
  --rate_test_rollouts 100 \
  --rate_top_k 2 4 \
  --rate_include_numpy_policy true \
  --rate_seed 42
```

The first positional argument after the config is the checkpoint or training seed used by the configured model setup.

A legacy evaluation entry point is also retained:

```bash
bash run_infocost.sh configs/kinshiphinton.yaml
```

Some internal filenames retain the earlier `infocost` naming for reproducibility and compatibility with existing experiment outputs. These names do not denote a separate method.

## Paper Experiment Wrappers

Reproducibility scripts for the manuscript experiments are provided under `experiments/`:

```text
experiments/
├── 01_run_r1_all_datasets.sh
├── 02_run_mquake_cap512.sh
├── 03_run_kinship_multiseed_r100.sh
├── 04_run_metaqa_multiseed_r100.sh
├── 05_run_r100_diversity_all_datasets.sh
└── 06_run_mquake_beam_cap512.sh
```

These scripts cover the single-trajectory diagnostic, multi-checkpoint `R=100` evaluation, candidate-diversity analysis, and MQuAKE-ST action-cap sensitivity checks used in the manuscript.

## Outputs

Rate-sweep outputs are written under the corresponding timestamped run directory, including machine-readable CSV/JSON summaries and evaluation artifacts.

Typical outputs are stored under:

```text
saved_models/<dataset>/<run_name>/
```

with evaluation-specific subdirectories such as `rate_sweep/`, `policy_entropy/`, and `test_beam/`.

## Repository Structure

```text
MINERVA-ActionComm/
├── code/
│   ├── evaluation_infocost.py
│   ├── evaluation_rate_sweep.py
│   └── policy_entropy/
├── configs/
├── experiments/
├── minerva/                 # pinned MINERVA submodule
├── tests/
├── run_infocost.sh
└── run_rate_sweep.sh
```

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

Please also follow the dataset-specific citation guidance provided in the [THESEUS repository](https://github.com/HalcyonSolutions/THESEUS).
