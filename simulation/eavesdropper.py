"""Intercept-resend (IR) eavesdropper.

Eve attacks each pulse independently with probability p. For an attacked pulse she
measures in a uniformly random basis and resends her result in that basis.
"""
import numpy as np


def qber_ir(p):
    """QBER on basis-matched pulses caused by IR alone: p * 1/2 (wrong basis) * 1/2 (random outcome)."""
    return p / 4.0


def intercept_resend(rng, a_bit, a_bas, p):
    """Return (bit, basis) of the states on the wire after Eve's attack."""
    n = a_bit.shape[0]
    attacked = rng.random(n) < p
    e_bas = rng.integers(0, 2, n, dtype=np.int8)
    e_rand = rng.integers(0, 2, n, dtype=np.int8)
    e_bit = np.where(e_bas == a_bas, a_bit, e_rand)
    return np.where(attacked, e_bit, a_bit), np.where(attacked, e_bas, a_bas)


def info_fraction_ir(p):
    """Fraction of sifted bits Eve knows exactly (attacked and basis matches Alice's)."""
    return p / 2.0
