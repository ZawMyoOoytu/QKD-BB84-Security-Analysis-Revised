import numpy as np
import pytest

from simulation.statistics import (EPS_SEC, h2, h_trunc, key_length, mu_bound,
                                   q_tol_rule, serfling_bound, tail_check)


def test_binary_entropy_values():
    assert h2(0.5) == pytest.approx(1.0)
    assert h2(0.11) == pytest.approx(0.4999, abs=1e-3)
    assert float(h2(0.0)) == pytest.approx(0.0, abs=1e-12)


def test_truncated_entropy_is_one_above_half():
    assert h_trunc(0.6) == 1.0
    assert h_trunc(0.1) == pytest.approx(float(h2(0.1)))


def test_mu_matches_closed_form():
    n = k = 10_000
    expected = np.sqrt((n + k) / (n * k) * (k + 1) / k * np.log(4 / EPS_SEC))
    assert mu_bound(n, k) == pytest.approx(expected)


def test_mu_decreases_with_sample_size():
    assert mu_bound(1e4, 1e4) > mu_bound(1e5, 1e5) > mu_bound(1e6, 1e6)


def test_key_length_increases_with_n_and_decreases_with_q():
    assert key_length(8e4, 2e4, 0.03) > key_length(4e4, 1e4, 0.03)
    assert key_length(8e4, 2e4, 0.01) > key_length(8e4, 2e4, 0.05)


def test_key_length_nonpositive_for_tiny_blocks_or_huge_qber():
    assert key_length(50, 50, 0.01) < 0
    assert key_length(1e6, 1e6, 0.2) < 0


def test_q_tol_rule_exceeds_expected_qber():
    assert q_tol_rule(0.03, 1000) > 0.03
    assert q_tol_rule(0.03, 1e6) - 0.03 < q_tol_rule(0.03, 1e3) - 0.03


def test_serfling_bound_is_probability_and_monotone():
    b1, b2 = serfling_bound(0.02, 500, 500), serfling_bound(0.06, 500, 500)
    assert 0 < b2 < b1 <= 1


def test_tail_bound_not_violated():
    rng = np.random.default_rng(1)
    for row in tail_check(500, 500, 0.03, rng, trials=100_000):
        assert row["empirical"] <= row["bound"]
