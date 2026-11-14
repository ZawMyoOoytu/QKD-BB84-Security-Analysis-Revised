import numpy as np
import pytest

from simulation.bb84_core import qber_theory
from simulation.eavesdropper import info_fraction_ir, intercept_resend, qber_ir
from simulation.quantum_channel import bit_flip, compose_flips


def test_qber_ir_full_attack_is_25_percent():
    assert qber_ir(1.0) == 0.25
    assert qber_ir(0.0) == 0.0


def test_compose_flips_properties():
    assert compose_flips(0.1, 0.0) == pytest.approx(0.1)
    assert compose_flips(0.1, 0.2) == pytest.approx(compose_flips(0.2, 0.1))
    assert compose_flips(0.5, 0.123) == pytest.approx(0.5)


def test_qber_theory_formula():
    for p, e in [(0.0, 0.01), (0.3, 0.02), (1.0, 0.0), (0.5, 0.05)]:
        assert qber_theory(p, e) == pytest.approx(e + (1 - 2 * e) * p / 4)


def test_fully_noisy_channel_gives_half():
    assert qber_theory(0.7, 0.5) == pytest.approx(0.5)


def test_bit_flip_rate():
    rng = np.random.default_rng(2)
    bits = np.zeros(200_000, dtype=np.int8)
    rate = bit_flip(rng, bits, 0.03).mean()
    assert rate == pytest.approx(0.03, abs=5 * np.sqrt(0.03 * 0.97 / 200_000))


def test_no_attack_leaves_state_unchanged():
    rng = np.random.default_rng(3)
    bit = rng.integers(0, 2, 1000, dtype=np.int8)
    bas = rng.integers(0, 2, 1000, dtype=np.int8)
    wb, wbas = intercept_resend(rng, bit, bas, 0.0)
    assert np.array_equal(wb, bit) and np.array_equal(wbas, bas)


def test_full_attack_basis_is_uniform_and_bit_correct_when_basis_matches():
    rng = np.random.default_rng(4)
    n = 200_000
    bit = rng.integers(0, 2, n, dtype=np.int8)
    bas = rng.integers(0, 2, n, dtype=np.int8)
    wb, wbas = intercept_resend(rng, bit, bas, 1.0)
    assert wbas.mean() == pytest.approx(0.5, abs=0.01)
    match = wbas == bas
    assert match.mean() == pytest.approx(0.5, abs=0.01)
    assert np.array_equal(wb[match], bit[match])      # Eve knows the bit if her basis is right


def test_ir_information_fraction():
    assert info_fraction_ir(0.4) == pytest.approx(0.2)
