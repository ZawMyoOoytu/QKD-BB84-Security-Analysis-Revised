"""Run all experiments of the paper.

    python -m simulation.experiments            (from the repository root)

Writes
    data/processed/results.json   aggregated results used by simulation/results.py
    data/raw/*.csv                per-trial counts (n, k, test errors, key errors)
"""
import csv
import json
from pathlib import Path

import numpy as np

from .bb84_core import (asymptotic_p_max, asymptotic_q_threshold, asymptotic_rate,
                        best_rate_analytic, ir_only_p_max, monte_carlo, n_min, p_max,
                        qber_theory)
from .statistics import EPS_COR, EPS_SEC, F_EC, Z_TOL, tail_check

ROOT = Path(__file__).resolve().parent.parent
SEED = 20261111


def exp_qber(rng, raw):
    """QBER versus attack fraction: Monte Carlo against Eq. (4)."""
    rows = []
    for e_ch in (0.0, 0.02):
        for p in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.75, 1.0):
            buf = []
            r = monte_carlo(100_000, p, e_ch, 0.8, 60, rng, raw=buf)
            r["qber_theory"] = float(qber_theory(p, e_ch))
            rows.append(r)
            raw += [("qber", 100_000, p, e_ch, 0.8) + b for b in buf]
    return rows


def exp_mc_rate(rng, raw):
    """Full-protocol key rate against the analytic prediction (e_ch = 0.01)."""
    rows = []
    for N, trials in ((10_000, 1500), (100_000, 200), (1_000_000, 30)):
        for p in (0.0, 0.1, 0.2, 0.3):
            rate_a, qx, _ = best_rate_analytic(N, p, 0.01)
            qx = 0.8 if np.isnan(qx) else float(qx)
            buf = []
            r = monte_carlo(N, p, 0.01, qx, trials, rng, raw=buf)
            r["rate_analytic"] = float(rate_a)
            rows.append(r)
            raw += [("mc_rate", N, p, 0.01, qx) + b for b in buf]
    return rows


def exp_analytic():
    """Deterministic sweeps (no randomness)."""
    out = {}
    n_grid = np.logspace(3.5, 8, 60)
    out["rate_vs_N"] = {
        str(p): dict(N=n_grid.tolist(),
                     rate=[best_rate_analytic(N, p, 0.01)[0] for N in n_grid],
                     asym=asymptotic_rate(p, 0.01))
        for p in (0.0, 0.1, 0.2, 0.3)}

    p_grid = np.linspace(0, 0.6, 61)
    out["rate_vs_p"] = {
        str(int(N)): dict(p=p_grid.tolist(),
                          rate=[best_rate_analytic(N, p, 0.01)[0] for p in p_grid],
                          asym=[asymptotic_rate(p, 0.01) for p in p_grid])
        for N in (1e4, 1e5, 1e6, 1e8)}

    e_grid = np.linspace(0, 0.10, 51)
    out["rate_vs_e"] = {
        str(int(N)): dict(e=e_grid.tolist(),
                          rate=[best_rate_analytic(N, 0.0, e)[0] for e in e_grid],
                          asym=[asymptotic_rate(0.0, e) for e in e_grid])
        for N in (1e4, 1e5, 1e6, 1e8)}

    q_grid = np.linspace(0.0, 0.10, 41)
    out["nmin_vs_q"] = dict(q=q_grid.tolist(), nmin=[n_min(q) for q in q_grid])

    out["pmax"] = {f"{e}_{int(N)}": p_max(N, e)
                   for e in (0.0, 0.01, 0.02) for N in (1e4, 1e5, 1e6, 1e8)}
    out["pmax_asym"] = {str(e): asymptotic_p_max(e) for e in (0.0, 0.01, 0.02)}
    out["pmax_ir_only"] = {str(e): ir_only_p_max(e) for e in (0.0, 0.01, 0.02)}
    out["q_star"] = asymptotic_q_threshold()
    return out


def exp_tail(rng):
    return {f"{n}_{k}": tail_check(n, k, 0.03, rng)
            for n, k in ((500, 500), (2000, 500), (5000, 1000))}


def main():
    rng = np.random.default_rng(SEED)      # RNG order below is part of reproducibility
    raw = []
    out = dict(params=dict(eps_sec=EPS_SEC, eps_cor=EPS_COR, f_ec=F_EC, z_tol=Z_TOL, seed=SEED))
    out["qber"] = exp_qber(rng, raw)
    out["mc_rate"] = exp_mc_rate(rng, raw)
    out.update(exp_analytic())
    out["tail"] = exp_tail(rng)

    (ROOT / "data/processed").mkdir(parents=True, exist_ok=True)
    (ROOT / "data/raw").mkdir(parents=True, exist_ok=True)
    with open(ROOT / "data/processed/results.json", "w") as fh:
        json.dump(out, fh, indent=1)
    with open(ROOT / "data/raw/mc_trials.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["experiment", "N", "p", "e_ch", "qx", "trial", "n", "k",
                    "test_errors", "key_errors"])
        w.writerows(raw)
    print("experiments done:", len(raw), "raw trials")


if __name__ == "__main__":
    main()
