#!/usr/bin/env python3
"""Combine per-chunk angular histogram templates into one pooled template,
optionally producing a 4-curve (gen/reco x CPV/SM) comparison plot.

Single-template usage (unchanged):
    python3 scripts/combine_angular_templates.py \
        --pattern "outputs/angular_lr/angular/O_W/O_W_all_gen_electron_chunk{chunk}_bins.csv" \
        --chunks 1-10 \
        --out outputs/angular_lr/angular/O_W/O_W_all_gen_electron_combined_bins.csv

4-curve comparison usage:
    python3 scripts/combine_angular_templates.py \
        --chunks 1-10 \
        --compare-plot \
        --reco-cpv-pattern "outputs/angular_lr/angular/O_W/O_W_all_reco_electron_chunk{chunk}_bins.csv" \
        --reco-sm-pattern  "outputs/angular_lr/angular/O_W/O_W_all_sm_reco_electron_chunk{chunk}_bins.csv" \
        --gen-cpv-pattern  "outputs/angular_lr/angular/O_W/O_W_all_gen_electron_chunk{chunk}_bins.csv" \
        --gen-sm-pattern   "outputs/angular_lr/angular/O_W/O_W_all_sm_gen_electron_chunk{chunk}_bins.csv" \
        --out-dir outputs/angular_lr/angular/O_W \
        --tag O_W_electron
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ilc_tth_cpv.histograms import SignedHistogram  # noqa: E402
from ilc_tth_cpv.io import read_table, write_table  # noqa: E402
from ilc_tth_cpv.plotting import import_plotting, plot_signed_histogram  # noqa: E402


# Chunk range parsing 

def parse_chunk_spec(spec: str) -> List[int]:
    chunks = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            low_s, high_s = part.split("-", 1)
            low, high = int(low_s), int(high_s)
            if low > high:
                raise SystemExit(f"Invalid chunk range '{part}': start > end")
            chunks.update(range(low, high + 1))
        else:
            chunks.add(int(part))
    if not chunks:
        raise SystemExit(f"No chunks parsed from --chunks '{spec}'")
    return sorted(chunks)

def get_chunk_label(chunk_ids: List[int]) -> str:
    """Format chunk list into a filename-friendly tag like 'chunk0-10' or 'chunk1_3_5'."""
    if len(chunk_ids) == 1:
        return f"chunk{chunk_ids[0]}"
    if chunk_ids == list(range(chunk_ids[0], chunk_ids[-1] + 1)):
        return f"chunk{chunk_ids[0]}-{chunk_ids[-1]}"
    return "chunk" + "_".join(str(c) for c in chunk_ids)


# Loading 

def meta_path_for(bins_csv_path: Path) -> Path:
    return Path(str(bins_csv_path).rsplit(".", 1)[0] + ".meta.json")


def load_chunk_template(pattern: str, chunk: int) -> dict:
    bins_path = Path(pattern.format(chunk=chunk))
    if not bins_path.exists():
        raise SystemExit(f"Missing chunk {chunk} bins CSV: {bins_path}")

    meta_path = meta_path_for(bins_path)
    if not meta_path.exists():
        raise SystemExit(f"Missing chunk {chunk} metadata: {meta_path}")

    rows = read_table(bins_path)
    with meta_path.open() as stream:
        meta = json.load(stream)

    n_k = meta.get("n_read")
    if n_k is None:
        n_k = meta.get("n_events_filled")
    if n_k is None:
        kinfit_report = meta.get("kinfit_report") or {}
        n_k = kinfit_report.get("n_read")
    if n_k is None:
        raise SystemExit(
            f"Chunk {chunk}: could not find an event count in {meta_path}. "
            f"Available top-level keys: {sorted(meta.keys())}"
        )

    return {
        "chunk": chunk, "bins_path": bins_path, "meta_path": meta_path,
        "rows": rows, "meta": meta, "n_k": float(n_k),
    }


def validate_consistent(templates: List[dict]) -> None:
    first = templates[0]
    first_meta = first["meta"]
    first_edges = _edges_from_rows(first["rows"])
    for tpl in templates[1:]:
        meta = tpl["meta"]
        for key in ("observable", "frame", "weight_column"):
            if meta.get(key) != first_meta.get(key):
                raise SystemExit(
                    f"Chunk {tpl['chunk']} metadata mismatch on '{key}': "
                    f"{meta.get(key)!r} != {first_meta.get(key)!r}"
                )
        edges = _edges_from_rows(tpl["rows"])
        if edges != first_edges:
            raise SystemExit(
                f"Chunk {tpl['chunk']} has different binning than "
                f"chunk {first['chunk']}"
            )


def _edges_from_rows(rows: list) -> List[float]:
    edges = [float(r["bin_low"]) for r in rows]
    edges.append(float(rows[-1]["bin_high"]))
    return edges


# Combination (unchanged, now a reusable building block)

def combine_templates(templates: List[dict]) -> dict:
    n_total = sum(tpl["n_k"] for tpl in templates)
    if n_total <= 0.0:
        raise SystemExit("N_total <= 0; cannot combine (check n_read values)")

    n_bins = len(templates[0]["rows"])
    edges = _edges_from_rows(templates[0]["rows"])

    signed_combined = [0.0] * n_bins
    abs_combined = [0.0] * n_bins
    entries_combined = [0] * n_bins

    for tpl in templates:
        weight = tpl["n_k"] / n_total
        for i, row in enumerate(tpl["rows"]):
            signed_combined[i] += weight * float(row["signed_weight_fb"])
            abs_combined[i] += weight * float(row["abs_weight_fb"])
            entries_combined[i] += int(row["entries"])

    local_signed_fraction = [
        (s / a) if a > 0.0 else 0.0
        for s, a in zip(signed_combined, abs_combined)
    ]

    frame = templates[0]["meta"].get("frame", "")
    observable = templates[0]["meta"].get("observable", "")

    rows = []
    for i in range(n_bins):
        rows.append({
            "frame": frame, "observable": observable, "bin_index": i,
            "bin_low": edges[i], "bin_high": edges[i + 1],
            "bin_center": 0.5 * (edges[i] + edges[i + 1]),
            "signed_weight_fb": signed_combined[i],
            "abs_weight_fb": abs_combined[i],
            "local_signed_fraction": local_signed_fraction[i],
            "entries": entries_combined[i],
        })

    return {
        "rows": rows, "edges": edges, "signed": signed_combined,
        "absw": abs_combined, "entries": entries_combined,
        "n_total": n_total, "frame": frame, "observable": observable,
        "weight_column": templates[0]["meta"].get("weight_column"),
    }


def combine_one(pattern: str, chunk_ids: List[int]) -> dict:
    """Load, validate, and combine one pattern's chunks. The single-pattern
    workhorse reused by both single-output mode and --compare-plot mode."""
    templates = [load_chunk_template(pattern, c) for c in chunk_ids]
    validate_consistent(templates)
    return combine_templates(templates)


def write_combined(combined: dict, out_path: Path, chunk_ids: List[int], pattern: str) -> None:
    per_chunk_n = {}  # not reconstructable here without templates; caller can extend if needed
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_table(out_path, combined["rows"], metadata={
        "observable": combined["observable"],
        "frame": combined["frame"],
        "weight_column": combined["weight_column"],
        "combination_method": (
            "event-count-weighted average across chunks: "
            "H_i = sum_k (N_k/N_total) * H_i^(k); entries summed directly; "
            "local_signed_fraction recomputed from combined signed/abs"
        ),
        "contributing_chunks": chunk_ids,
        "n_total": combined["n_total"],
        "n_read": combined["n_total"],
        "source_pattern": pattern,
    })
    print(f"bins   -> {out_path}  (N_total={combined['n_total']:.1f})")


# 4-curve comparison plot, built directly from combined in-memory data

def plot_four_curve_comparison(
    reco_cpv: dict, reco_sm: dict, gen_cpv: dict, gen_sm: dict,
    out_path: Path, observable: str, category_label: str,
) -> None:
    plt = import_plotting()
    fig, ax = plt.subplots(figsize=(8.0, 5.0))

    curves = {
        "reco CPV":      (reco_cpv, "#2458a4", "-",  1.0),
        "reco SM / 10":  (reco_sm,  "#2458a4", "--", 0.1),
        "gen CPV":       (gen_cpv,  "#b34d2e", "-",  1.0),
        "gen SM / 10":   (gen_sm,   "#b34d2e", "--", 0.1),
    }

    for label, (combined, color, linestyle, scale) in curves.items():
        edges = combined["edges"]
        signed = [s * scale for s in combined["signed"]]
        ax.step(edges, signed + [signed[-1]], where="post",
                color=color, linewidth=1.4, linestyle=linestyle, label=label)

    ax.axhline(0.0, color="#222222", linewidth=0.8)
    ax.set_xlabel(f"{observable} [rad]")
    ax.set_ylabel("signed weight [fb]")
    ax.set_title(f"{observable}, {category_label}: gen vs reco, CPV vs SM "
                 f"(all chunks combined)")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"plot   -> {out_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunks", required=True)
    parser.add_argument("--compare-plot", action="store_true",
                         help="combine 4 patterns and overlay gen/reco x CPV/SM")

    # single-template mode
    parser.add_argument("--pattern", default=None)
    parser.add_argument("--out", default=None)
    parser.add_argument("--no-plot", action="store_true")

    # compare-plot mode
    parser.add_argument("--reco-cpv-pattern", default=None)
    parser.add_argument("--reco-sm-pattern", default=None)
    parser.add_argument("--gen-cpv-pattern", default=None)
    parser.add_argument("--gen-sm-pattern", default=None)
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--tag", default=None, help="filename tag, e.g. O_W_electron")

    args = parser.parse_args()
    chunk_ids = parse_chunk_spec(args.chunks)
    chunk_label = get_chunk_label(chunk_ids)
    print(f"Combining {len(chunk_ids)} chunks: {chunk_ids}")

    if args.compare_plot:
        required = {
            "--reco-cpv-pattern": args.reco_cpv_pattern,
            "--reco-sm-pattern": args.reco_sm_pattern,
            "--gen-cpv-pattern": args.gen_cpv_pattern,
            "--gen-sm-pattern": args.gen_sm_pattern,
            "--out-dir": args.out_dir,
            "--tag": args.tag,
        }
        
        missing = [k for k, v in required.items() if v is None]
        if missing:
            raise SystemExit(f"--compare-plot requires: {', '.join(missing)}")

        reco_cpv = combine_one(args.reco_cpv_pattern, chunk_ids)
        reco_sm = combine_one(args.reco_sm_pattern, chunk_ids)
        gen_cpv = combine_one(args.gen_cpv_pattern, chunk_ids)
        gen_sm = combine_one(args.gen_sm_pattern, chunk_ids)

        out_dir = Path(args.out_dir) / chunk_label
        full_tag = f"{args.tag}_{chunk_label}"

        write_combined(reco_cpv, out_dir / f"{full_tag}_reco_combined_bins.csv", chunk_ids, args.reco_cpv_pattern)
        write_combined(reco_sm, out_dir / f"{full_tag}_sm_reco_combined_bins.csv", chunk_ids, args.reco_sm_pattern)
        write_combined(gen_cpv, out_dir / f"{full_tag}_gen_combined_bins.csv", chunk_ids, args.gen_cpv_pattern)
        write_combined(gen_sm, out_dir / f"{full_tag}_sm_gen_combined_bins.csv", chunk_ids, args.gen_sm_pattern)

        plot_four_curve_comparison(
            reco_cpv, reco_sm, gen_cpv, gen_sm,
            out_path=out_dir / f"{full_tag}_gen_vs_reco_cpv_vs_sm_combined.png",
            observable=reco_cpv["observable"],
            category_label=f"{args.tag} ({chunk_label})",
        )
        return 0

    # single-template mode (original behavior)
    if not args.pattern or not args.out:
        raise SystemExit("Non-compare mode requires --pattern and --out")

    out_str = args.out
    if "{chunks}" in out_str:
        out_str = out_str.format(chunks=chunk_label)
    elif "{chunk_label}" in out_str:
        out_str = out_str.format(chunk_label=chunk_label)

    combined = combine_one(args.pattern, chunk_ids)
    out_path = Path(out_str)

    # Automatically insert the chunk folder into the target path if not already present
    if chunk_label not in out_path.parts:
        out_path = out_path.parent / chunk_label / out_path.name

    write_combined(combined, out_path, chunk_ids, args.pattern)
    if not args.no_plot:
        hist = SignedHistogram(edges=combined["edges"])
        hist.signed = combined["signed"]
        hist.absw = combined["absw"]
        hist.entries = combined["entries"]
        plot_signed_histogram(
            hist, out_path.with_suffix(".png"),
            title=f"{combined['observable']} [{combined['frame']}] combined",
            xlabel=f"{combined['observable']} [rad]",
        )
        print(f"plot   -> {out_path.with_suffix('.png')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())