# QKD-BB84-Security-Analysis

Finite-key security analysis of BB84 under intercept-resend attacks and channel noise
(manuscript for an IEEE journal, simulation code, data and tests).

## Layout

| Path | Content |
|---|---|
| `manuscript/main.tex`, `references.bib` | IEEEtran paper; `sections/01..08_*.tex` are `\input` by `main.tex` |
| `simulation/statistics.py` | binary entropy, fluctuation term mu, key-length formula, Serfling tail check |
| `simulation/quantum_channel.py` | bit-flip channel, composition of flip stages |
| `simulation/eavesdropper.py` | intercept-resend attack, IR-induced QBER |
| `simulation/bb84_core.py` | bit-level BB84, Monte Carlo, analytic key rate, N_min, p_max |
| `simulation/experiments.py` | runs all experiments, writes `data/` |
| `simulation/results.py` | builds figures and LaTeX tables from `data/processed/results.json` |
| `data/raw/mc_trials.csv` | per-trial counts (n, k, test errors, key errors) |
| `data/processed/results.json` | aggregated results |
| `outputs/figures`, `outputs/tables` | figures (pdf/png) and table environments used by the paper |
| `tests/` | pytest suite (35 tests) |

## Reproduce (run from the repository root)

    pip install numpy scipy matplotlib pytest
    python -m simulation.experiments      # about 15 s, fixed seed 20261111
    python -m simulation.results          # figures -> outputs/figures and manuscript/figures
    python -m pytest -q tests

Always use `python -m ...` from the root: `simulation/statistics.py` would otherwise shadow
the standard-library `statistics` module.

## Build the paper

    cd manuscript
    pdflatex main && bibtex main && pdflatex main && pdflatex main

Tables are read from `../outputs/tables/`, so keep the folder structure when uploading
(for example to Overleaf). Needs the `IEEEtran` class (included in TeX Live / Overleaf).

## Before submission
- Replace the author block, journal name and date placeholders in `main.tex`.
- Verify every entry of `references.bib` against the publisher record.
- Confirm Eqs. (1)-(3) against the published version of Tomamichel et al., Nat. Commun. 3, 634 (2012).
- If the target journal has its own template, move the section files into it unchanged.

## Model assumptions
Ideal single-photon source and detector (no loss, dark counts or multi-photon pulses),
independent bit-flip channel with the same rate in both bases, Eve in a uniformly random
basis, ideal error-correction model leak = f_EC * n * h(Q_tol) with f_EC = 1.16.
