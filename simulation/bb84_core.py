"""BB84 (efficient, biased-basis) protocol: bit-level simulation and analytic key rates.

Alice and Bob choose X with probability qx and Z with 1-qx. X-X matched pulses form the
raw key (n bits); Z-Z matched pulses are used for parameter estimation (k bits).
"""
import numpy as np

from .eavesdropper import intercept_resend, qber_ir
from .quantum_channel import bit_flip, compose_flips
from .statistics import (F_EC, h2, key_length, q_tol_rule)

QX_GRID = np.concatenate([np.linspace(0.5, 0.9, 41), np.linspace(0.9, 0.999, 100)])


# ---------------------------------------------------------------- analytic -----
def qber_theory(p, e_ch):
    """Q = e_ch + (1 - 2 e_ch) p / 4."""
    return compose_flips(qber_ir(p), e_ch)


def best_rate_analytic(N, p, e_ch, qx_grid=QX_GRID):
    """Optimise the X-basis probability; return (rate l/N, best qx, l)."""
    q = qber_theory(p, e_ch)
    best = (0.0, np.nan, 0.0)
    for qx in qx_grid:
        n = N * qx ** 2
        k = N * (1 - qx) ** 2
        if k < 2 or n < 2:
            continue
        l = key_length(n, k, q_tol_rule(q, k))
        if l > best[2]:
            best = (l / N, qx, l)
    return best


def asymptotic_rate(p, e_ch, f=F_EC):
    """N -> infinity limit: 1 - (1 + f) h(Q)."""
    q = qber_theory(p, e_ch)
    return max(0.0, 1.0 - h2(q) - f * h2(q))


def asymptotic_q_threshold(f=F_EC):
    """Q* with 1 - (1 + f) h(Q*) = 0."""
    lo, hi = 0.0, 0.5
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if 1 - (1 + f) * float(h2(mid)) > 0 else (lo, mid)
    return lo


def asymptotic_p_max(e_ch, f=F_EC):
    """Largest p with positive asymptotic rate."""
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if asymptotic_rate(mid, e_ch, f) > 0 else (lo, mid)
    return lo


def ir_only_p_max(e_ch, f=F_EC):
    """Asymptotic tolerance if Eve is restricted to IR: 1 - p/2 - f h(Q) > 0."""
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        ok = 1 - mid / 2 - f * float(h2(qber_theory(mid, e_ch))) > 0
        lo, hi = (mid, hi) if ok else (lo, mid)
    return lo


def p_max(N, e_ch):
    """Largest attack fraction with a positive finite-key rate (None if none even at p=0)."""
    if best_rate_analytic(N, 0.0, e_ch)[0] <= 0:
        return None
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if best_rate_analytic(N, mid, e_ch)[0] > 0 else (lo, mid)
    return lo


def n_min(q, e_ch=0.0, lo=2e2, hi=1e11):
    """Smallest N with positive key when the QBER q is realised by IR with e_ch = 0 (p = 4q)."""
    p = 4.0 * q
    if p > 1 or best_rate_analytic(hi, p, e_ch)[0] <= 0:
        return None
    for _ in range(60):
        mid = np.sqrt(lo * hi)
        lo, hi = (lo, mid) if best_rate_analytic(mid, p, e_ch)[0] > 0 else (mid, hi)
    return float(hi)


# -------------------------------------------------------------- simulation -----
def run_protocol(N, p, e_ch, qx, rng):
    """One bit-level run. Returns (n, k, test_errors, key_errors)."""
    a_bit = rng.integers(0, 2, N, dtype=np.int8)
    a_bas = (rng.random(N) >= qx).astype(np.int8)      # 0 = X (key), 1 = Z (test)
    b_bas = (rng.random(N) >= qx).astype(np.int8)

    w_bit, w_bas = intercept_resend(rng, a_bit, a_bas, p)
    w_bit = bit_flip(rng, w_bit, e_ch)

    b_rand = rng.integers(0, 2, N, dtype=np.int8)
    b_bit = np.where(b_bas == w_bas, w_bit, b_rand)

    err = a_bit != b_bit
    xx = (a_bas == 0) & (b_bas == 0)
    zz = (a_bas == 1) & (b_bas == 1)
    return int(xx.sum()), int(zz.sum()), int(err[zz].sum()), int(err[xx].sum())


def monte_carlo(N, p, e_ch, qx, trials, rng, raw=None):
    """Repeat the protocol; abort if the Z-sample QBER exceeds Q_tol.

    If ``raw`` is a list, one tuple (trial, n, k, test_err, key_err) is appended per trial.
    """
    rates, qk_l, qn_l, aborts = [], [], [], 0
    q_exp = qber_theory(p, e_ch)
    for t in range(trials):
        n, k, et, ek = run_protocol(N, p, e_ch, qx, rng)
        if raw is not None:
            raw.append((t, n, k, et, ek))
        if k < 2 or n < 2:
            aborts += 1
            rates.append(0.0)
            continue
        qt, qn_ = et / k, ek / n
        qk_l.append(qt)
        qn_l.append(qn_)
        q_tol = q_tol_rule(q_exp, k)
        if qt > q_tol:
            aborts += 1
            rates.append(0.0)
            continue
        l = max(0.0, float(key_length(n, k, q_tol)))
        rates.append(l / N)
    return dict(N=N, p=p, e_ch=e_ch, qx=qx, trials=trials,
                qber_mean=float(np.mean(qn_l)), qber_std=float(np.std(qn_l)),
                qber_z_mean=float(np.mean(qk_l)),
                abort_prob=aborts / trials,
                rate_mean=float(np.mean(rates)), rate_std=float(np.std(rates)))
