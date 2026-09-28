"""Preliminary English figures drawn only from verified S2 result records."""

from collections import defaultdict
from graphlib import TopologicalSorter
from pathlib import Path
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch
from matplotlib.path import Path as MplPath
from matplotlib.ticker import StrMethodFormatter

from .audit import require
from .s2_runner import ROOT, digest, read_json, write_json

INK = "#17324d"
BLUE = "#356dad"
TEAL = "#087f73"
ORANGE = "#ad601c"


def save_both(fig, stem):
    """Save a scalable diagram and a portable raster preview."""
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight", facecolor="white")
    fig.savefig(stem.with_suffix(".png"), dpi=120, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def draw_placement(case, stem, run_id):
    """Draw every inserted/original node and every edge level from a saved DAG.

    Long residual edges run outside the node columns. Their orthogonal routes
    occupy separate lanes; labels carry the saved level and ciphertext count.
    """
    checked = case["validated"]
    nodes, edges, audit = checked["nodes"], checked["edges"], checked["audit"]
    by_name = {n[0]: n for n in nodes}
    pred = defaultdict(list)
    for u, v, _ in edges:
        pred[v].append(u)
    order = list(TopologicalSorter({n: pred[n] for n in by_name}).static_order())
    rank = {}
    for n in order:
        rank[n] = max((rank[p] + 1 for p in pred[n]), default=0)
    layers = defaultdict(list)
    for n in order:
        layers[rank[n]].append(n)
    xpos = {}
    for layer in sorted(layers):
        names = sorted(layers[layer], key=lambda n: (sum(xpos[p] for p in pred[n]) / max(1, len(pred[n])), n))
        for i, n in enumerate(names):
            xpos[n] = (i - (len(names) - 1) / 2) * 4.4
    ystep, width, height = 1.65, 3.65, 0.94
    pos = {n: (xpos[n], -rank[n] * ystep) for n in order}
    long_edges = [(u, v, ct) for u, v, ct in edges if rank[v] - rank[u] > 1]
    side_lanes = {-1: [], 1: []}
    lane_for = {}
    for u, v, ct in sorted(long_edges, key=lambda e: (rank[e[0]], -rank[e[1]], e[0], e[1])):
        side = -1 if xpos[u] + xpos[v] <= 0 else 1
        intervals = side_lanes[side]
        chosen = next((i for i, end in enumerate(intervals) if end < rank[u]), len(intervals))
        if chosen == len(intervals):
            intervals.append(rank[v])
        else:
            intervals[chosen] = rank[v]
        lane_for[u, v] = (side, chosen)
    node_left, node_right = min(xpos.values()) - width / 2, max(xpos.values()) + width / 2
    xleft = node_left - 0.9 * (len(side_lanes[-1]) + 1)
    xright = node_right + 0.9 * (len(side_lanes[1]) + 1)
    bottom = -max(rank.values()) * ystep - 1.5
    fig, ax = plt.subplots(figsize=((xright - xleft) * 0.82, (1.9 - bottom) * 0.60))
    ax.set_xlim(xleft, xright)
    ax.set_ylim(bottom, 1.9)
    ax.set_aspect("equal")
    ax.axis("off")
    levels = {(e["from"], e["to"]): e["level"] for e in audit["edge_levels"]}
    for u, v, ct in edges:
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        start, end = (x0, y0 - height / 2), (x1, y1 + height / 2)
        label = f"L={levels[u, v]} | ct={ct}"
        if (u, v) in lane_for:
            side, lane = lane_for[u, v]
            outside = (node_left if side < 0 else node_right) + side * (0.7 + lane * 0.9)
            points = [start, (x0, start[1] - 0.18), (outside, start[1] - 0.18),
                      (outside, end[1] + 0.18), (x1, end[1] + 0.18), end]
            path = MplPath(points, [MplPath.MOVETO] + [MplPath.LINETO] * 5)
            arrow = FancyArrowPatch(path=path, arrowstyle="-|>", mutation_scale=9, color=ORANGE, lw=0.9, zorder=1)
            ax.text(outside + side * 0.10, (start[1] + end[1]) / 2, label, rotation=90,
                    ha="right" if side < 0 else "left", va="center", fontsize=7.5, color=ORANGE,
                    bbox={"facecolor": "white", "edgecolor": "none", "pad": 1}, zorder=2)
        else:
            arrow = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=9, color=INK, lw=0.9, zorder=1)
            ax.text((x0 + x1) / 2 + 0.10, (start[1] + end[1]) / 2, label,
                    ha="left", va="center", fontsize=7.5, color=INK,
                    bbox={"facecolor": "white", "edgecolor": "none", "pad": 1}, zorder=2)
        ax.add_patch(arrow)
    for name, op, depth, _ in nodes:
        x, y = pos[name]
        inserted = op in ("Bootstrap1", "Bootstrap2", "Modswitch")
        color = "#fff0d9" if op.startswith("Bootstrap") else "#edf0f3" if op == "Modswitch" else "#e7f4f1" if op.startswith("PolyEval") else "#eaf1fc" if "MM" in op else "#ffffff"
        edge_color = ORANGE if op.startswith("Bootstrap") else INK
        ax.add_patch(FancyBboxPatch((x - width / 2, y - height / 2), width, height,
                                    boxstyle="round,pad=0.03,rounding_size=0.06", fc=color, ec=edge_color, lw=1.0, zorder=3))
        short = name.removesuffix("_mlp").removesuffix("_attn")
        if inserted:
            short = short.removeprefix("s2_")
        short = "\n".join(textwrap.wrap(short.replace("_", " "), width=31))
        ax.text(x, y + 0.20, short, fontsize=8.5, fontweight="bold", ha="center", va="center", color=INK, zorder=4)
        ax.text(x, y - 0.05, op, fontsize=8, ha="center", va="center", color=INK, zorder=4)
        ax.text(x, y - 0.29, f"in {audit['l_in'][name]} -> out {audit['l_out'][name]}",
                fontsize=8, ha="center", va="center", color=INK, zorder=4)
    title = f"{case['module'].upper() if case['module'] == 'mlp' else case['module'].title()} placement | input level {case['l_init']}"
    ax.set_title(title + f"\nEstimated latency {float(audit['latency_decimal_ms']):,.4f} ms | B1 {audit['n_b1']} | B2 {audit['n_b2']}"
                 + f"\nDepth {audit['depth']} | budget {audit['budget']} | utilisation {audit['utilisation']:.6f}",
                 fontsize=12, color=INK, pad=24, linespacing=1.5)
    handles = [Patch(fc="#fff0d9", ec=ORANGE, label="Refresh"), Patch(fc="#edf0f3", ec=INK, label="Modswitch"),
               Patch(fc="#ffffff", ec=INK, label="Original operator")]
    ax.legend(handles=handles, loc="upper center", ncol=3, frameon=False, fontsize=8)
    ax.text((xleft + xright) / 2, bottom + 0.10,
            f"Source: {run_id} / {case['case_id']}\nB1 counts ciphertexts; B2 counts pairs. Shared operators are drawn and charged once.\nS2 preliminary placement; levels and ciphertext counts are shown on every edge.",
            ha="center", va="bottom", fontsize=8, color=INK)
    save_both(fig, stem)
    data = {"case_id": case["case_id"], "source_run": run_id, "nodes": nodes, "edges": edges,
            "edge_levels": audit["edge_levels"], "node_input_levels": audit["l_in"], "node_output_levels": audit["l_out"],
            "drawn_node_count": len(nodes), "drawn_edge_count": len(edges)}
    write_json(stem.with_suffix(".data.json"), data)


def make_figures(output, figures):
    """Create comparisons and two MLP placements in a new, versioned directory."""
    require(figures.is_relative_to(ROOT), "Figure directory must be inside this repository")
    figures.mkdir(parents=True, exist_ok=False)
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none", "axes.spines.top": False,
                         "axes.spines.right": False, "axes.labelcolor": INK, "text.color": INK,
                         "axes.edgecolor": "#9aa8b4", "xtick.color": INK, "ytick.color": INK})
    metadata = read_json(output / "run.json")
    cases = [read_json(p) for p in sorted((output / "cases").glob("*.json"))]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for ax, module, label in zip(axes, ("mlp", "attention"), ("MLP: all 15 input levels", "Attention: representative inputs only")):
        subset = sorted((c for c in cases if c["module"] == module), key=lambda c: c["l_init"])
        levels = [c["l_init"] for c in subset]
        baseline = [float(c["baseline_decimal_ms"]) for c in subset]
        estimated = [float(c["validated"]["audit"]["latency_decimal_ms"]) if c["validated"] else float("nan") for c in subset]
        ax.plot(levels, baseline, color=BLUE, linewidth=1.6, linestyle="--", label="Teacher baseline")
        ax.plot(levels, estimated, color=TEAL, linewidth=2, marker="o", markersize=4,
                linestyle="-" if module == "mlp" else "none", label="Shared-refresh CP-SAT")
        ax.set_title(label, fontsize=12, loc="left", pad=14)
        ax.set_xlabel("Input level")
        ax.set_ylabel("Estimated inference latency (ms)")
        ax.set_xticks(list(range(0, 15, 2)) if module == "mlp" else levels)
        ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
        ax.grid(axis="y", color="#e2e8ed", linewidth=0.7)
        ax.legend(frameon=False, fontsize=8.5)
    fig.suptitle("S2 preliminary optimisation results", x=0.06, ha="left", fontsize=16, fontweight="bold")
    fig.text(0.06, 0.02, f"Source: {metadata['run_id']}. Fitted latency scores; no actual FHE inference timing. Attention's remaining 12 inputs await S3.", fontsize=8)
    fig.tight_layout(rect=(0, 0.06, 1, 0.93))
    save_both(fig, figures / "latency-comparison")
    selected = [c for c in cases if c["module"] == "mlp" and c["l_init"] in (0, 14)]
    require(len(selected) == 2 and all(c["validated"] for c in selected), "Expected valid MLP levels 0 and 14")
    for case in selected:
        draw_placement(case, figures / ("placement-" + case["case_id"]), metadata["run_id"])
    examples = read_json(output / "tiny-examples.json")
    e = next(e for e in examples["examples"] if e["id"] == "shared-refresh-and-modswitch")
    draw_placement({"case_id": e["id"], "module": "tiny example", "l_init": e["level"], "validated": e["validated"]},
                   figures / "method-shared-prefix", metadata["run_id"])
    write_json(figures / "provenance.json", {
        "source_run": metadata["run_id"], "source_run_sha256": digest(output / "run.json"),
        "source_manifest_sha256": digest(output / "artifacts.sha256.json"),
        "generator_sha256": digest(Path(__file__)),
        "source_case_hashes": {c["case_id"]: digest(output / "cases" / (c["case_id"] + ".json")) for c in selected},
        "purpose": "S2 preliminary visual evidence; does not replace the S4 figure requirements",
    })
    write_json(figures / "artifacts.sha256.json", {p.name: digest(p) for p in sorted(figures.iterdir()) if p.is_file()})
    print(f"Saved preliminary figures: {figures.relative_to(ROOT).as_posix()}")
