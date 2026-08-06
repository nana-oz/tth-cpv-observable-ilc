import csv
import argparse

from ilc_tth_cpv.plotting import import_plotting
from ilc_tth_cpv.histograms import SignedHistogram


def load_signed_histogram(path) -> SignedHistogram:
    """Load a CSV file into a SignedHistogram object."""
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))

    edges = [float(r["bin_low"]) for r in rows] + [float(rows[-1]["bin_high"])]
    signed = [float(r["signed_weight_fb"]) for r in rows]

    return SignedHistogram(edges=edges, signed=signed)


def plot_four_curves(
    observable: str, 
    lepton: str, 
    base_dir="outputs/angular_lr"):

    obs_dir = f"{base_dir}/angular/{observable}/joint_likelihood"
    curves = {
        "reco CPV": (f"{obs_dir}/{observable}_all_reco_{lepton}_bins.csv", "#2458a4", "-"),
        "reco SM":  (f"{obs_dir}/{observable}_all_sm_reco_{lepton}_bins.csv", "#2458a4", "--"),
        "gen CPV":  (f"{obs_dir}/{observable}_all_gen_{lepton}_bins.csv", "#b34d2e", "-"),
        "gen SM":   (f"{obs_dir}/{observable}_all_sm_gen_{lepton}_bins.csv", "#b34d2e", "--"),
    }

    plt = import_plotting()
    fig, ax = plt.subplots(figsize=(8.0, 5.0))

    for label, (path, color, linestyle) in curves.items():
        hist = load_signed_histogram(path)

        ax.step(
            hist.edges, 
            hist.signed + [hist.signed[-1]], 
            where="post",
            color=color, 
            linewidth=1.4, 
            linestyle=linestyle, 
            label=label,
        )

    ax.axhline(0.0, color="#222222", linewidth=0.8)
    ax.set_xlabel(f"{observable} [rad]")
    ax.set_ylabel("signed weight [fb]")
    ax.set_title(f"{observable}, {lepton}: gen vs reco, CPV vs SM")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()

    out_path=f"{obs_dir}/{observable}_all_sm_vs_cpv_gen_vs_reco_{lepton}_bins.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved plot: {out_path}")

def main():
    parser = argparse.ArgumentParser(description="Plot 4 curves for a given observable and lepton type.")
    parser.add_argument("--observable", choices=("O_W", "O_lD"), default="O_W")

    args = parser.parse_args()

    for lepton in ("electron", "muon"):
        plot_four_curves(
            observable=args.observable,
            lepton=lepton,
        )

if __name__ == "__main__":
    main()