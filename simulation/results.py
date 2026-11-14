"""Turn data/processed/results.json into paper figures and LaTeX tables.

    python -m simulation.results                (from the repository root)

Writes
    outputs/figures/*.pdf|png     (PDFs are also copied to manuscript/figures/)
    outputs/tables/tab_*.tex      complete table environments, \\input by the manuscript
"""
import json
import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "outputs/figures"
TAB = ROOT / "outputs/tables"
MS_FIG = ROOT / "manuscript/figures"

# colour-blind-safe order (Okabe-Ito subset); markers/line styles keep figures
# readable in greyscale print
COL = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00"]
MRK = ["o", "s", "^", "D", "v"]
LS = ["-", "--", "-.", ":", (0, (5, 1))]
N_LABEL = {"10000": r"$N=10^4$", "100000": r"$N=10^5$",
           "1000000": r"$N=10^6$", "100000000": r"$N=10^8$"}

plt.rcParams.update({
    "font.family": "serif", "font.size": 8, "axes.labelsize": 8,
    "legend.fontsize": 6.5, "xtick.labelsize": 7, "ytick.labelsize": 7,
    "axes.linewidth": 0.6, "lines.linewidth": 1.1, "lines.markersize": 3.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.linewidth": 0.3, "grid.alpha": 0.45,
    "savefig.bbox": "tight", "pdf.fonttype": 42,
})
W, H = 3.45, 2.5


def _save(fig, name):
    fig.savefig(FIG / f"{name}.pdf")
    fig.savefig(FIG / f"{name}.png", dpi=300)
    plt.close(fig)


def fig_qber(R):
    fig, ax = plt.subplots(figsize=(W, H))
    pp = np.linspace(0, 1, 101)
    for i, e in enumerate((0.0, 0.02)):
        rows = [r for r in R["qber"] if r["e_ch"] == e]
        ax.plot(pp, e + pp / 4 - 2 * e * pp / 4, color=COL[i], ls=LS[i],
                label=fr"theory, $e_{{ch}}={e}$")
        ax.errorbar([r["p"] for r in rows], [r["qber_mean"] for r in rows],
                    yerr=[2 * r["qber_std"] for r in rows], fmt=MRK[i], color=COL[i],
                    mfc="none", capsize=1.5, elinewidth=0.6,
                    label=fr"simulation, $e_{{ch}}={e}$")
    ax.axhline(R["q_star"], color="0.35", lw=0.7, ls=(0, (2, 2)))
    ax.text(0.44, 0.083, r"asymptotic abort threshold ($f_{EC}=1.16$)", fontsize=6)
    ax.set_xlabel(r"Attack fraction $p$")
    ax.set_ylabel("QBER $Q$ (sifted key)")
    ax.legend(frameon=False, loc="lower right", bbox_to_anchor=(1.0, -0.02))
    _save(fig, "fig_qber")


def fig_rate_vs_N(R):
    fig, ax = plt.subplots(figsize=(W, H))
    for i, (p, d) in enumerate(R["rate_vs_N"].items()):
        ax.plot(d["N"], d["rate"], color=COL[i], ls=LS[i], label=fr"$p={p}$")
        ax.axhline(d["asym"], color=COL[i], lw=0.5, ls=(0, (1, 2)))
    ax.set_xscale("log")
    ax.set_xlabel(r"Number of transmitted pulses $N$")
    ax.set_ylabel(r"Secret key rate $\ell/N$ (bit/pulse)")
    ax.set_ylim(0, 1.12)
    ax.legend(frameon=False, loc="upper left", ncol=2,
              title=r"$e_{ch}=0.01$ (dotted: asymptotic)", title_fontsize=6.5)
    _save(fig, "fig_rate_vs_N")


def fig_rate_vs_p(R):
    fig, ax = plt.subplots(figsize=(W, H))
    for i, (N, d) in enumerate(R["rate_vs_p"].items()):
        ax.plot(d["p"], d["rate"], color=COL[i], ls=LS[i], label=N_LABEL[N])
    d = next(iter(R["rate_vs_p"].values()))
    ax.plot(d["p"], d["asym"], color="0.3", lw=0.7, ls=(0, (1, 2)), label=r"$N\to\infty$")
    ax.set_xlabel(r"Attack fraction $p$")
    ax.set_ylabel(r"Secret key rate $\ell/N$ (bit/pulse)")
    ax.set_xlim(0, 0.6)
    ax.legend(frameon=False, loc="upper right", title=r"$e_{ch}=0.01$", title_fontsize=6.5)
    _save(fig, "fig_rate_vs_p")


def fig_rate_vs_e(R):
    fig, ax = plt.subplots(figsize=(W, H))
    for i, (N, d) in enumerate(R["rate_vs_e"].items()):
        ax.plot(np.array(d["e"]) * 100, d["rate"], color=COL[i], ls=LS[i], label=N_LABEL[N])
    d = next(iter(R["rate_vs_e"].values()))
    ax.plot(np.array(d["e"]) * 100, d["asym"], color="0.3", lw=0.7, ls=(0, (1, 2)),
            label=r"$N\to\infty$")
    ax.set_xlabel(r"Channel flip probability $e_{ch}$ (\%)")
    ax.set_ylabel(r"Secret key rate $\ell/N$ (bit/pulse)")
    ax.set_xlim(0, 10)
    ax.legend(frameon=False, loc="upper right", title=r"$p=0$", title_fontsize=6.5)
    _save(fig, "fig_rate_vs_e")


def fig_nmin(R):
    fig, ax = plt.subplots(figsize=(W, H))
    q = np.array(R["nmin_vs_q"]["q"]) * 100
    n = np.array([np.nan if v is None else v for v in R["nmin_vs_q"]["nmin"]], dtype=float)
    ax.semilogy(q, n, color=COL[0], marker=MRK[0], mfc="none", markevery=2)
    ax.axvline(R["q_star"] * 100, color="0.35", lw=0.7, ls=(0, (2, 2)))
    ax.text(R["q_star"] * 100 - 0.15, 4e3, "asymptotic limit", rotation=90, fontsize=6, ha="right")
    ax.set_xlabel("QBER $Q$ (%)")
    ax.set_ylabel(r"Minimum pulses $N_{\min}$ for $\ell>0$")
    ax.set_xlim(0, 10.2)
    _save(fig, "fig_nmin")


# ------------------------------------------------------------------ tables -----
def _sci(x):
    return rf"$10^{{{int(np.floor(np.log10(x)))}}}$"


def _table(name, caption, label, colspec, header, rows):
    body = "\n".join(rows)
    text = (r"\begin{table}[!t]" "\n"
            rf"\caption{{{caption}}}" "\n"
            rf"\label{{{label}}}" "\n"
            r"\centering" "\n" r"\small" "\n"
            rf"\begin{{tabular}}{{{colspec}}}" "\n"
            r"\toprule" "\n" f"{header}" "\n" r"\midrule" "\n"
            f"{body}\n"
            r"\bottomrule" "\n" r"\end{tabular}" "\n" r"\end{table}" "\n")
    (TAB / f"{name}.tex").write_text(text)


def tables(R):
    rows = [f"{_sci(r['N'])} & {r['p']:.1f} & {r['qx']:.2f} & {r['abort_prob']*100:.2f} & "
            rf"{r['rate_mean']:.4f} $\pm$ {r['rate_std']:.4f} & {r['rate_analytic']:.4f} \\"
            for r in R["mc_rate"]]
    _table("tab_mc",
           r"Monte Carlo versus analytic key rate ($\ech=0.01$, $\epssec=10^{-10}$, $\epscor=10^{-15}$)",
           "tab:mc", r"@{}cccccc@{}",
           r"$N$ & $p$ & $q_X$ & abort (\%) & simulated $\ell/N$ & analytic \\", rows)

    rows = []
    for e in ("0.0", "0.01", "0.02"):
        cells = ["--" if R["pmax"][f"{e}_{N}"] is None else f"{R['pmax'][f'{e}_{N}']:.3f}"
                 for N in (10000, 100000, 1000000, 100000000)]
        rows.append(f"{float(e):.2f} & " + " & ".join(cells) + f" & {R['pmax_asym'][e]:.3f} \\\\")
    _table("tab_pmax", r"Largest tolerable IR attack fraction $p_{\max}$ for a positive key",
           "tab:pmax", r"@{}cccccc@{}",
           r"$\ech$ & $N=10^4$ & $10^5$ & $10^6$ & $10^8$ & $N\to\infty$ \\", rows)

    rows = []
    for key, vals in R["tail"].items():
        n_, k_ = key.split("_")
        rows += [f"{n_} & {k_} & {v['gamma']:.2f} & {v['empirical']:.1e} & {v['bound']:.1e} \\\\"
                 for v in vals if v["gamma"] in (0.02, 0.04, 0.08)]
    _table("tab_tail",
           r"Empirical tail probability $\Pr[Q_n-Q_k\ge\gamma]$ versus bound \eqref{eq:serfling} ($Q=0.03$)",
           "tab:tail", r"@{}ccccc@{}",
           r"$n$ & $k$ & $\gamma$ & empirical & bound \\", rows)


def main():
    R = json.load(open(ROOT / "data/processed/results.json"))
    for d in (FIG, TAB, MS_FIG):
        d.mkdir(parents=True, exist_ok=True)
    for f in (fig_qber, fig_rate_vs_N, fig_rate_vs_p, fig_rate_vs_e, fig_nmin):
        f(R)
    tables(R)
    for pdf in FIG.glob("*.pdf"):
        shutil.copy(pdf, MS_FIG / pdf.name)
    print("figures and tables written")


if __name__ == "__main__":
    main()
