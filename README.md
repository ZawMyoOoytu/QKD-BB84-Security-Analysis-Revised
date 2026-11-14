# QKD-BB84-Security-Analysis

### Finite-Key Security Analysis of the BB84 Quantum Key Distribution Protocol Under Intercept-Resend Attacks and Channel Noise

[![Research](https://img.shields.io/badge/Research-Quantum_Cryptography-blue)](https://github.com/ZawMyoOoytu/QKD-BB84-Security-Analysis-Revised)
[![Protocol](https://img.shields.io/badge/Protocol-BB84-indigo)](https://doi.org/10.1103/PhysRevLett.70.1895)
[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-Pytest-orange?logo=pytest)](https://docs.pytest.org/)

## Overview

This repository presents a computational and analytical study of the finite-key security of the **BB84 Quantum Key Distribution (QKD) protocol** under intercept-resend (IR) attacks and channel noise.

The research combines finite-key security modelling, bit-level protocol simulation, analytical key-rate evaluation, Monte Carlo experimentation, and statistical validation. It is accompanied by an IEEE journal manuscript, simulation source code, experimental datasets, generated figures, LaTeX tables, and an automated test suite.

The implementation is designed to support reproducible computational experiments and facilitate further investigation into the relationship between channel noise, eavesdropping-induced errors, finite-size statistical fluctuations, and secure key generation.

## Research Scope and Contributions

The project focuses on the following research components:

- **Finite-Key Security Analysis:** Modelling finite-size effects and statistical fluctuations in BB84 secure key generation.
- **Intercept-Resend Attack Modelling:** Implementing an eavesdropping model in which Eve measures and resends quantum states using a uniformly random basis.
- **Quantum Channel Noise:** Analysing independent bit-flip noise and the composition of multiple channel error stages.
- **Secure Key-Length Evaluation:** Implementing binary entropy, finite-key fluctuation terms, key-length calculations, and Serfling-based tail analysis.
- **Analytical and Computational Evaluation:** Comparing analytical key-rate behaviour with bit-level Monte Carlo simulations.
- **Experimental Reproducibility:** Providing fixed-seed experiments, processed results, publication figures, LaTeX tables, and automated tests.

## Repository Structure

```text
QKD-BB84-Security-Analysis-Revised/
│
├── manuscript/
│   ├── main.tex
│   ├── references.bib
│   ├── sections/
│   │   ├── 01_*.tex
│   │   ├── 02_*.tex
│   │   ├── 03_*.tex
│   │   ├── 04_*.tex
│   │   ├── 05_*.tex
│   │   ├── 06_*.tex
│   │   ├── 07_*.tex
│   │   └── 08_*.tex
│   └── figures/
│
├── simulation/
│   ├── __init__.py
│   ├── statistics.py
│   ├── quantum_channel.py
│   ├── eavesdropper.py
│   ├── bb84_core.py
│   ├── experiments.py
│   └── results.py
│
├── data/
│   ├── raw/
│   │   └── mc_trials.csv
│   └── processed/
│       └── results.json
│
├── outputs/
│   ├── figures/
│   └── tables/
│
├── tests/
│
└── README.md
```

## Implementation Details

| Module | Description |
|---|---|
| `simulation/statistics.py` | Binary entropy, finite-key fluctuation term μ, secure key-length formulation, and Serfling tail verification |
| `simulation/quantum_channel.py` | Independent bit-flip channel and composition of sequential channel error stages |
| `simulation/eavesdropper.py` | BB84 intercept-resend attack implementation and induced quantum bit error rate (QBER) |
| `simulation/bb84_core.py` | Bit-level BB84 protocol, Monte Carlo simulation, analytical key rate, minimum sample size (N_min), and maximum tolerable error probability (p_max) |
| `simulation/experiments.py` | Execution of the experimental scenarios and generation of research datasets |
| `simulation/results.py` | Post-processing of experimental results and generation of publication-ready figures and LaTeX tables |

## Experimental Data and Outputs

The repository includes both trial-level experimental data and aggregated results.

| Artifact | Description |
|---|---|
| `data/raw/mc_trials.csv` | Per-trial Monte Carlo counts, including n, k, test errors, and key errors |
| `data/processed/results.json` | Aggregated experimental results |
| `outputs/figures/` | Generated figures in PDF and PNG formats |
| `outputs/tables/` | LaTeX table environments incorporated into the manuscript |
| `manuscript/figures/` | Figures used in the IEEE manuscript |
| `tests/` | Automated validation suite containing 35 tests |

## Reproducibility

All experiments are designed to be executed from the repository root.

### 1. Environment Requirements

- Python 3.x
- NumPy
- SciPy
- Matplotlib
- pytest

Install the required dependencies:

```bash
pip install numpy scipy matplotlib pytest
```

### 2. Execute the Experiments

```bash
python -m simulation.experiments
```

This command executes the experimental pipeline and generates the corresponding datasets.

- Fixed random seed: `20261111`
- Approximate execution time: 15 seconds under the original execution environment.

Execution time may vary depending on hardware and software configuration.

### 3. Generate Figures and LaTeX Tables

```bash
python -m simulation.results
```

This command processes `data/processed/results.json` and generates figures and LaTeX tables for the manuscript.

### 4. Execute the Automated Test Suite

```bash
python -m pytest -q tests
```

The test suite contains 35 tests covering the implemented protocol, channel, eavesdropping, and statistical components.

**Execution note:** Run the modules using `python -m` from the repository root. Direct execution of `simulation/statistics.py` may cause a module-name collision with Python's standard-library `statistics` module.

## IEEE Manuscript Compilation

The research manuscript is prepared using the IEEEtran LaTeX document class and BibTeX bibliography management.

From the repository root:

```bash
cd manuscript

pdflatex main
bibtex main
pdflatex main
pdflatex main
```

The manuscript references generated LaTeX tables from `../outputs/tables/`. Consequently, the repository directory structure must be preserved when compiling locally or transferring the project to Overleaf.

**Required typesetting environment:** IEEEtran-compatible LaTeX distribution, such as TeX Live or Overleaf.

## Security Model and Assumptions

The current implementation adopts the following idealised physical and protocol assumptions:

1. **Source and Detector Model:** Ideal single-photon source and ideal detectors are assumed.
2. **Channel Loss:** Channel loss, detector dark counts, and multi-photon pulse effects are excluded.
3. **Channel Noise:** An independent bit-flip channel is assumed, with an identical error probability in both BB84 bases.
4. **Eavesdropping Strategy:** Eve performs an intercept-resend attack and independently selects a uniformly random measurement basis.
5. **Error-Correction Model:** Error-correction information leakage is represented by:

   \[
   \mathrm{leak}_{EC}=f_{EC}\,n\,h(Q_{\mathrm{tol}})
   \]

   where:

   - \(f_{EC}=1.16\) is the assumed error-correction efficiency factor.
   - \(n\) denotes the relevant sifted-key length.
   - \(h(\cdot)\) denotes the binary entropy function.
   - \(Q_{\mathrm{tol}}\) denotes the tolerated quantum bit error rate.

These assumptions define the scope of the present analytical and computational framework. The results should therefore be interpreted within this model rather than as a complete security certification for practical QKD hardware.

## Validation and Publication Readiness

Before journal submission, the following items require verification:

- Replace author, journal, and publication-date placeholders in `manuscript/main.tex`.
- Independently verify all bibliographic entries in `manuscript/references.bib` against the original publisher records.
- Verify Equations (1)–(3) against the published version of Tomamichel et al., *Nature Communications*, **3**, 634 (2012).
- Validate the numerical implementation and confirm consistency between analytical predictions and simulation outputs.
- Review the manuscript against the formatting, referencing, and submission requirements of the selected IEEE journal.

If a target journal requires a different LaTeX template, the existing section files can be transferred into the required template while preserving their scientific content.

## References

- Bennett, C. H., and Brassard, G. (1984). *Quantum cryptography: Public key distribution and coin tossing*. Proceedings of IEEE International Conference on Computers, Systems and Signal Processing, Bangalore, India, 175–179.
- Tomamichel, M., Lim, C. C. W., Gisin, N., and Renner, R. (2012). *Tight finite-key analysis for quantum cryptography*. Nature Communications, **3**, 634. https://doi.org/10.1038/ncomms1631

## Research and Development

This repository is maintained as a research-oriented implementation for the computational analysis of finite-key BB84 security.

The project is intended to support scientific reproducibility, independent technical examination, and further research into quantum cryptographic security under realistic channel and adversarial conditions.

**Repository:** [QKD-BB84-Security-Analysis-Revised](https://github.com/ZawMyoOoytu/QKD-BB84-Security-Analysis-Revised)

**Research Area:** Quantum Cryptography · Quantum Key Distribution · Finite-Key Security · Quantum Channel Modelling · Cryptographic Security Analysis

---

*Research code and manuscript are provided for scientific study and independent validation. Publication or security certification should not be inferred solely from the presence of simulation results or automated tests.*
