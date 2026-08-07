#!/usr/bin/env python3
"""
Aggregate Fisher information and event counts across chunks.
Reads:
  - N from *.meta.json
  - I from *.fisher.json
Outputs individual CSV files per chunk into the observable directory.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import pandas as pd


def read_metric_pair(file_prefix: Path) -> tuple[float, float]:
    """
    Given a file path prefix (without extension), reads:
      - {file_prefix}.meta.json -> extracts N (event count)
      - {file_prefix}.fisher.json -> extracts I (Fisher information)
    Returns (N, I).
    """
    meta_path = Path(f"{file_prefix}.meta.json")
    fisher_path = Path(f"{file_prefix}.fisher.json")

    n_val = 0.0
    i_val = 0.0

    # 1. Read N from meta.json
    if meta_path.exists():
        try:
            with open(meta_path, "r") as f:
                data = json.load(f)
            if isinstance(data, dict):
                for k in ["N", "n_events", "num_events", "entries", "count", "total_events", "sum_weights"]:
                    if k in data:
                        n_val = float(data[k])
                        break
        except Exception as e:
            print(f"Warning: Failed to parse {meta_path}: {e}")

    # 2. Read I from fisher.json
    if fisher_path.exists():
        try:
            with open(fisher_path, "r") as f:
                data = json.load(f)
            if isinstance(data, dict):
                for k in ["I", "fisher_info", "fisher_information", "integral", "total_fisher_info"]:
                    if k in data:
                        i_val = float(data[k])
                        break
        except Exception as e:
            print(f"Warning: Failed to parse {fisher_path}: {e}")

    return n_val, i_val


def process_observable_directory(
    obs_dir: Path, obs_name: str, frame: str = "ttbar_rest", max_chunks: int = 10
) -> None:
    """Process all chunks for an observable and output CSV per chunk."""
    if not obs_dir.exists():
        print(f"Error: Directory {obs_dir} does not exist.")
        return

    print(f"\nProcessing directory: {obs_dir}")

    for chunk_id in range(1, max_chunks + 1):
        # Prefixes for file pairs
        e_gen_prefix = obs_dir / f"{obs_name}_all_gen_electron_chunk{chunk_id}_bins"
        e_reco_prefix = obs_dir / f"{obs_name}_all_reco_electron_chunk{chunk_id}_bins"
        mu_gen_prefix = obs_dir / f"{obs_name}_all_gen_muon_chunk{chunk_id}_bins"
        mu_reco_prefix = obs_dir / f"{obs_name}_all_reco_muon_chunk{chunk_id}_bins"

        # Read (N, I) for each combination
        n_gen_e, i_gen_e = read_metric_pair(e_gen_prefix)
        n_reco_e, i_reco_e = read_metric_pair(e_reco_prefix)
        n_gen_mu, i_gen_mu = read_metric_pair(mu_gen_prefix)
        n_reco_mu, i_reco_mu = read_metric_pair(mu_reco_prefix)

        # Skip chunk if no files found
        if all(x == 0.0 for x in [i_gen_e, i_reco_e, i_gen_mu, i_reco_mu]):
            continue

        # Ratios
        ratio_e = (i_reco_e / i_gen_e) if i_gen_e > 0 else 0.0
        ratio_mu = (i_reco_mu / i_gen_mu) if i_gen_mu > 0 else 0.0

        # Combined (e + mu)
        n_gen_comb = n_gen_e + n_gen_mu
        n_reco_comb = n_reco_e + n_reco_mu
        i_gen_comb = i_gen_e + i_gen_mu
        i_reco_comb = i_reco_e + i_reco_mu
        ratio_comb = (i_reco_comb / i_gen_comb) if i_gen_comb > 0 else 0.0

        # Build table rows
        rows = [
            {
                "Observable": obs_name,
                "Lepton category": "electron",
                "Frame": frame,
                "N_gen": n_gen_e,
                "N_reco": n_reco_e,
                "I_gen": i_gen_e,
                "I_reco": i_reco_e,
                "I_reco / I_gen": ratio_e,
            },
            {
                "Observable": obs_name,
                "Lepton category": "muon",
                "Frame": frame,
                "N_gen": n_gen_mu,
                "N_reco": n_reco_mu,
                "I_gen": i_gen_mu,
                "I_reco": i_reco_mu,
                "I_reco / I_gen": ratio_mu,
            },
            {
                "Observable": obs_name,
                "Lepton category": "combined likelihood (e+mu)",
                "Frame": frame,
                "N_gen": n_gen_comb,
                "N_reco": n_reco_comb,
                "I_gen": i_gen_comb,
                "I_reco": i_reco_comb,
                "I_reco / I_gen": ratio_comb,
            },
        ]

        df = pd.DataFrame(rows)

        # Output path: outputs/angular_lr/angular/<OBSERVABLE>/fisher_summary_chunk<chunk_id>.csv
        out_csv = obs_dir / f"fisher_summary_chunk{chunk_id}.csv"
        df.to_csv(out_csv, index=False)
        print(f"  Created: {out_csv}")


def main():
    parser = argparse.ArgumentParser(description="Summarize Fisher Info & Meta files into CSVs per chunk.")
    parser.add_argument(
        "--base-dir",
        type=str,
        default="outputs/angular_lr/angular",
        help="Base directory containing observable subdirectories",
    )
    parser.add_argument(
        "--observables",
        nargs="+",
        default=["O_lD", "O_W"],
        help="Observables to process (e.g. O_lD O_W)",
    )
    parser.add_argument("--chunks", type=int, default=10, help="Maximum number of chunks to process")
    args = parser.parse_args()

    base_dir = Path(args.base_dir)

    for obs in args.observables:
        obs_dir = base_dir / obs
        process_observable_directory(obs_dir, obs_name=obs, max_chunks=args.chunks)


if __name__ == "__main__":
    main()
