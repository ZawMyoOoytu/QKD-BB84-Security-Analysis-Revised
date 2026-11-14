"""Information-theoretic and statistical building blocks of the finite-key analysis.

Key-length expression and fluctuation term follow Tomamichel, Lim, Gisin, Renner,
Nat. Commun. 3, 634 (2012), Eq. (2) with q = 1, eps = eps_sec/4, eps_bar = eps_sec/2.

NOTE: this module name shadows the standard-library ``statistics`` only when the
``simulation`` directory itself is on ``sys.path``. Always run from the repository
root (``python -m simulation.experiments``) so it is imported as ``simulation.statistics``.
"""
import numpy as np

# Default security / protocol parameters used throughout the paper
EPS_SEC = 1e-10      # secrecy parameter
EPS_COR = 1e-15      # correctness parameter
F_EC = 1.16          # error-correction efficiency
Z_TOL = 3.0          # Q_tol = Q_exp + Z_TOL * sigma_k (honest abort probability ~1e-3)


def h2(x):
    """Binary entropy in bits (clipped away from 0 and 1)."""
    x = np.clip(x, 1e-15, 1 - 1e-15)
    return -x * np.log2(x) - (1 - x) * np.log2(1 - x)


def h_trunc(x):
    """Binary entropy truncated to 1 for x >= 1/2, as in the finite-key theorem."""
    x = np.asarray(x, dtype=float)
    return np.where(x >= 0.5, 1.0, h2(np.minimum(x, 0.5)))


def mu_bound(n, k, eps_sec=EPS_SEC):
    """Statistical-fluctuation term mu obtained by inverting the Serfling-type bound."""
    return np.sqrt((n + k) / (n * k) * (k + 1) / k * np.log(4.0 / eps_sec))


def key_length(n, k, q_tol, eps_sec=EPS_SEC, eps_cor=EPS_COR, f=F_EC):
    """Secret key length l in bits (not floored; <= 0 means no key)."""
    mu = mu_bound(n, k, eps_sec)
    leak = f * n * h_trunc(q_tol)
    return (n * (1.0 - h_trunc(q_tol + mu)) - leak
            - 2.0 * np.log2(1.0 / eps_sec) - np.log2(2.0 / eps_cor))


def q_tol_rule(q_exp, k, z=Z_TOL):
    """Tolerance threshold fixed in advance: expected QBER plus z standard errors."""
    sigma = np.sqrt(q_exp * (1 - q_exp) / k)
    return q_exp + z * sigma


def serfling_bound(gamma, n, k):
    """Right-hand side of the Serfling-type tail bound used to define mu."""
    return float(np.exp(-gamma ** 2 * n * k ** 2 / ((n + k) * (k + 1))))


def tail_check(n, k, q, rng, trials=400_000, gammas=(0.02, 0.04, 0.06, 0.08, 0.10)):
    """Empirical Pr[Q_n - Q_k >= gamma] (hypergeometric split of i.i.d. errors) vs the bound."""
    ns = n + k
    total_err = rng.binomial(ns, q, trials)
    test_err = rng.hypergeometric(total_err, ns - total_err, k)
    diff = (total_err - test_err) / n - test_err / k
    return [dict(gamma=g,
                 empirical=float(np.mean(diff >= g)),
                 bound=serfling_bound(g, n, k)) for g in gammas]
