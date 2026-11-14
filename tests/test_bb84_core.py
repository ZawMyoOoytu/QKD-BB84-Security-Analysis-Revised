import json
from pathlib import Path

import numpy as np
import pytest

from simulation.bb84_core import (asymptotic_p_max, asymptotic_q_threshold, asymptotic_rate,
                                  best_rate_analytic, ir_only_p_max, monte_carlo, n_min,
                                  p_max, qber_theory, run_protocol)

RESULTS = Path(__file__).resolve().parent.parent / "data/processed/results.json"


# ------------------------------------------------------------ simulation -----
def test_run_protocol_counts_follow_basis_probabilities():
    rng = np.random.default_rng(5)
    N, qx = 200_000, 0.8
    n, k, _, _ = run_protocol(N, 0.0, 0.0, qx, rng)
    assert n / N == pytest.approx(qx ** 2, abs=0.005)
    assert k / N == pytest.approx((1 - qx) ** 2, abs=0.005)


def test_no_noise_no_attack_gives_zero_errors():
    rng = np.random.default_rng(6)
    _, _, et, ek = run_protocol(50_000, 0.0, 0.0, 0.7, rng)
    assert et == 0 and ek == 0


@pytest.mark.parametrize("p,e", [(0.4, 0.0), (0.2, 0.02), (1.0, 0.0)])
def test_simulated_qber_matches_theory_in_both_bases(p, e):
    rng = np.random.default_rng(7)
    r = monte_carlo(20_000, p, e, 0.6, 20, rng)
    q = qber_theory(p, e)
    assert r["qber_mean"] == pytest.approx(q, abs=0.004)      # key (X) basis
    assert r["qber_z_mean"] == pytest.approx(q, abs=0.006)    # test (Z) basis


def test_monte_carlo_is_reproducible_for_same_seed():
    a = monte_carlo(10_000, 0.1, 0.01, 0.7, 5, np.random.default_rng(8))
    b = monte_carlo(10_000, 0.1, 0.01, 0.7, 5, np.random.default_rng(8))
    assert a == b


def test_monte_carlo_raw_records_every_trial():
    raw = []
    monte_carlo(10_000, 0.1, 0.01, 0.7, 7, np.random.default_rng(9), raw=raw)
    assert len(raw) == 7 and all(len(t) == 5 for t in raw)


def test_full_attack_aborts_and_gives_no_key():
    r = monte_carlo(100_000, 1.0, 0.0, 0.7, 5, np.random.default_rng(10))
    # the expected-QBER-based threshold is 0.25+, so test passes, but the key length is zero
    assert r["rate_mean"] == 0.0


# --------------------------------------------------------------- analytic -----
def test_known_rate_value():
    assert best_rate_analytic(1e6, 0.0, 0.01)[0] == pytest.approx(0.4537, abs=1e-3)


def test_no_key_for_tiny_block():
    assert best_rate_analytic(1e3, 0.0, 0.01)[0] == 0.0


def test_rate_monotone_in_N_and_p():
    rates_n = [best_rate_analytic(N, 0.1, 0.01)[0] for N in (1e5, 1e6, 1e7, 1e8)]
    assert rates_n == sorted(rates_n)
    rates_p = [best_rate_analytic(1e6, p, 0.01)[0] for p in (0.0, 0.1, 0.2, 0.3)]
    assert rates_p == sorted(rates_p, reverse=True)


def test_rate_below_and_approaching_asymptote():
    asym = asymptotic_rate(0.0, 0.01)
    assert best_rate_analytic(1e8, 0.0, 0.01)[0] < asym
    assert best_rate_analytic(1e12, 0.0, 0.01)[0] > 0.97 * asym


def test_asymptotic_thresholds():
    assert asymptotic_q_threshold() == pytest.approx(0.0981, abs=2e-4)
    assert asymptotic_p_max(0.0) == pytest.approx(0.392, abs=2e-3)
    assert asymptotic_p_max(0.02) < asymptotic_p_max(0.01) < asymptotic_p_max(0.0)


def test_ir_only_tolerance_exceeds_general_tolerance():
    for e in (0.0, 0.01, 0.02):
        assert ir_only_p_max(e) > asymptotic_p_max(e) + 0.15


def test_p_max_grows_with_N_and_stays_below_asymptote():
    vals = [p_max(N, 0.01) for N in (1e4, 1e5, 1e6, 1e8)]
    assert vals == sorted(vals)
    assert vals[-1] < asymptotic_p_max(0.01)


def test_p_max_none_when_no_key_without_attack():
    assert p_max(1e3, 0.01) is None


def test_n_min_values():
    assert n_min(0.0) == pytest.approx(2.6e3, rel=0.05)
    assert n_min(0.05) == pytest.approx(2.4e4, rel=0.05)
    assert n_min(0.10) is None            # above the asymptotic threshold


# ------------------------------------------------ stored experiment output -----
@pytest.mark.skipif(not RESULTS.exists(), reason="run python -m simulation.experiments first")
def test_stored_monte_carlo_matches_analytic():
    R = json.load(open(RESULTS))
    for r in R["mc_rate"]:
        assert r["rate_mean"] == pytest.approx(r["rate_analytic"], abs=3e-4 + 3 * r["rate_std"])
    for r in R["qber"]:
        assert r["qber_mean"] == pytest.approx(r["qber_theory"], abs=3 * r["qber_std"] + 1e-3)
