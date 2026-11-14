"""Noisy quantum channel: independent bit-flip with probability e_ch.

A depolarising channel with depolarising probability lambda produces the same
effective flip rate e_ch = lambda / 2 in the measurement bases.
"""
import numpy as np


def bit_flip(rng, bits, e_ch):
    """Flip each bit independently with probability e_ch."""
    return bits ^ (rng.random(bits.shape[0]) < e_ch).astype(np.int8)


def compose_flips(e1, e2):
    """Error probability of two independent bit-flip stages (XOR of Bernoulli variables)."""
    return e1 * (1 - e2) + (1 - e1) * e2
