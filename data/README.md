# Datasets used in FoVer

Put datasets here. This folder is ignored by Git.

## ProofWriter

Download the dataset from [the Author's website](https://allenai.org/data/proofwriter). Saving to `proofwriter` folder.

- In the **Strict Evaluation**, the first 120 lines of `OWA/depth-5/meta-test.jsonl`, and all lines in `proofwriter-test-80.jsonl` are used.
- In the **Normal Evaluation**, lines in `proofwriter-owa-baseline-test.jsonl` and `proofwriter-owa-baseline-test-80.jsonl` are used.

`proofwriter-test-80.jsonl`, `proofwriter-owa-baseline-test.jsonl`, and `proofwriter-owa-baseline-test-80.jsonl` are available in [Release](https://github.com/peiyu-cn/FoVer/releases).

## FOLIO

The FOLIO dataset is embedded as a submodule. Run
```sh
git submodule init
git submodule update
```
to download from HuggingFace.
`folio_v2_validation.jsonl` is used.

## REVEAL

The REVEAL dataset is also embedded as a submodule.
The selected subset is hosted on https://huggingface.co/datasets/peiyu-cn/FoVer-Data-Reveal.
`eval/musique_test.csv` and `eval/strategyqa_test.csv` are used.

> [!Note]
> 
> According to the original REVEAL agreement, we have to use gated HuggingFace repository to avoid AI crawling.
> You need to request the access of the repository, then [set up SSH keys for Git](https://huggingface.co/docs/hub/security-git-ssh) to download the submodule.
