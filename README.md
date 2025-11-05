# FoVer: First-Order Logic Verification for Natural Language Reasoning

The official code repository for the paper: "FoVer: First-Order Logic Verification for Natural Language Reasoning"
in _Transactions of the Association for Computational Linguistics_, vol. 13. pp. 1340-1359, 2025.
https://doi.org/10.1162/TACL.a.41

**The paper as well as its LaTeX source is available in [Release](https://github.com/peiyu-cn/FoVer/releases)**.
This version of the paper is better formatted than the published one, as it is much better for accessibility.

The paper is not hosted on arXiv.org, because arXiv does not support LuaLaTeX,
and there were some problems when I uploaded the source bundle.

## Repository Structure
- [`dataset_utils/`](dataset_utils/): Code for loading and processing datasets.
- [`llm_utils/`](llm_utils/): Code for interacting with LLM APIs.
- [`data/`](data/): Datasets used in the paper. We also store requests and responses here. See [`data/README.md`](data/README.md) for details.
- [`demos/`](demos/): Few-shot prompt examples for FoVer, in Jupyter-style cells. See [`demos/README.md`](demos/README.md) for details.
- [`private/`](private/): Private files, including API keys. This directory is ignored by Git. See [`private/README.md`](private/README.md) for details.

## Usage

### Environments

To avoid unexpected API calls, I use separate environments for request and judgement.
[`requirements.request`](requirements.request) is for request, and [`requirements.verifier`](requirements.verifier) is for judgement.

Note that only core dependencies are listed in the requirements files,
so you may need to install other dependencies on your own.

### Entry Point

The entry point is [`main.py`](main.py).
However, the CLI interface is not very user-friendly, you'll have to modify code every time for different experiments.

It is recommended to use Jupyter Notebooks or Interactive Python to replace `main.py`.
They will provide type hints and better interactivity.

Or, if you like, submit a PR to improve the CLI interface.

## Cite the Paper

If you find this work useful, please consider citing it:

```bibtex
@article{peiyu2025fover,
  title={FoVer: First-Order Logic Verification for Natural Language Reasoning},
  author={Pei, Yu and Du, Yongping and Jin, Xingnan},
  journal={Transactions of the Association for Computational Linguistics},
  volume={13},
  pages={1340-1359},
  year={2025},
  publisher={MIT Press},
  doi={10.1162/TACL.a.41}
}
```

## Copyright Notice

### The Paper

Copyright of the MIT publication version is held by the Association for Computational Linguistics.

Copyright of the previous versions, including the one in [Release](https://github.com/peiyu-cn/FoVer/releases), is held by the authors.

Both versions are distributed under CC-BY 4.0 license.

### The Code Repository

Copyright © 2024-2025 Pei, Yu. All rights reserved.

Files in this repository\* are distributed under the Apache License 2.0, and the CC-BY 4.0 license.
You may choose either license to use.

\***Exceptions:**

- Files in [`demos/`](demos/) are distributed under the CC-BY 4.0 license only.
- Datasets in [`data/`](data/) are subject to their original licenses.
