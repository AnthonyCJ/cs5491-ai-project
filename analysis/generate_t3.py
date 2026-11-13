"""Generate formal-result tables and seven figures from immutable saved evidence.

Reads JSON/CSV and draws recorded graphs. Does not import the optimizer, run a
scorer, launch subprocesses, or modify a source experiment. Use the existing
requirements-s2.txt environment and a fresh output directory.
"""
import argparse
from collections import defaultdict
import csv
from decimal import Decimal
from graphlib import TopologicalSorter
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ID = "T2-FORMAL-20261004-004"
SOURCE = ROOT / "results" / SOURCE_ID
EXPECTED_SOURCE_MANIFEST = "0c465b0e11b76c417aa731da2863ad5739a24629e7246d9663559c154472e1f1"
SELECTED = ("mlp-L13", "mlp-L14", "attention-L05", "attention-L06")
COMPONENTS = ("ordinary_ms", "bootstrap1_ms", "bootstrap2_ms", "modswitch_ms")
INSERTED = {"Bootstrap1", "Bootstrap2", "Modswitch"}
INK, BLUE, TEAL, AMBER, PURPLE = "#17324d", "#356dad", "#087f73", "#bd721d", "#7859a1"
plt = None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def dec(value):
    return Decimal(str(value))


def checked_path(base, relative):
    path = (base / relative).resolve()
    require(path.is_relative_to(base), f"Source path escaped base: {relative}")
    return path


def load_inputs():
    """Reconcile saved identifiers, exact costs, CSV fields and fingerprints."""
    require(digest(SOURCE / "artifacts.sha256.json") == EXPECTED_SOURCE_MANIFEST, "Unexpected formal evidence manifest")
    manifest = read(SOURCE / "artifacts.sha256.json")["files"]
    for relative, expected in manifest.items():
        require(digest(checked_path(SOURCE, relative)) == expected, f"Changed evidence: {relative}")
    public_inputs = read(SOURCE / "inputs.sha256.json")
    for relative, expected in public_inputs.items():
        require(digest(checked_path(ROOT, relative)) == expected, f"Changed frozen input: {relative}")
    summary = read(SOURCE / "summary.json")
    raw_rows = summary["numerical_results"]
    with (SOURCE / "summary.csv").open(encoding="utf-8-sig", newline="") as handle:
        csv_rows = {r["case_id"]: r for r in csv.DictReader(handle)}
    expected_ids = {f"{m}-L{level:02}" for m in ("mlp", "attention") for level in range(15)}
    require(len(raw_rows) == 30 and {r["case_id"] for r in raw_rows} == expected_ids, "Incomplete formal coverage")
    require(set(csv_rows) == expected_ids, "CSV coverage differs")
    cases, checks, rows, sources, resource_rows = {}, {}, [], [], []
    for raw in raw_rows:
        cid = raw["case_id"]
        case_path = checked_path(ROOT, raw["output"]) / "cases" / f"{cid}.json"
        check_path = checked_path(ROOT, raw["check"])
        case, check = read(case_path), read(check_path)
        audit, baseline = case["validated"]["audit"], check["baseline_audit"]
        costs, base_costs = check["current_costs"], check["baseline_costs"]
        require(digest(case_path) == raw["case_sha256"] == check["case_sha256"], cid + " case fingerprint")
        require(digest(check_path) == raw["check_sha256"], cid + " check fingerprint")
        run_path = checked_path(ROOT, raw["output"]) / "run.json"
        require(digest(run_path) == raw["run_json_sha256"] == check["run_json_sha256"], cid + " run fingerprint")
        require(cid == case["case_id"] == check["case_id"], cid + " identity")
        require(raw["l_init"] == case["l_init"] and raw["l_max"] == case["l_max"] == 14, cid + " levels")
        require(raw["state"] == check["status"] == "passed", cid + " state")
        require(case["solution"]["status"] == raw["solver_status"] == "OPTIMAL", cid + " solver state")
        require(dec(raw["objective_scaled"]) == dec(raw["best_bound_scaled"]), cid + " bound")
        require(audit["structural_and_level_checks_passed"] and baseline["structural_and_level_checks_passed"], cid + " saved audit")
        require(check["solver_calls"] == 0 and check["saved_solution_verified_once_without_search"], cid + " saved check")
        for cost, metrics, total in ((costs, audit, raw["estimated_latency_ms"]), (base_costs, baseline, raw["baseline_estimated_latency_ms"])):
            require(sum(dec(cost[k]) for k in COMPONENTS) == dec(cost["total_ms"]) == dec(metrics["latency_decimal_ms"]) == dec(total), cid + " exact costs")
            require(metrics["n_bootstrap"] == metrics["n_b1"] + metrics["n_b2"], cid + " count")
            require(metrics["budget"] == metrics["n_b1"] * 14 + metrics["n_b2"] * 13 + raw["l_init"], cid + " budget")
            require(abs(metrics["depth"] / metrics["budget"] - metrics["utilisation"]) < 1e-14, cid + " utilisation")
        for key, value in raw.items():
            csv_value = csv_rows[cid][key]
            if isinstance(value, bool):
                require(csv_value.lower() == str(value).lower(), cid + " CSV boolean " + key)
            elif isinstance(value, (int, float)) or key in ("estimated_latency_ms", "baseline_estimated_latency_ms", "reduction_percent", *COMPONENTS):
                require(dec(csv_value) == dec(value), cid + " CSV number " + key)
            else:
                require(csv_value == value, cid + " CSV field " + key)
        saving = dec(base_costs["total_ms"]) - dec(costs["total_ms"])
        reduction = saving / dec(base_costs["total_ms"]) * 100
        require(saving > 0 and abs(reduction - dec(raw["reduction_percent"])) < Decimal("1e-22"), cid + " reduction")
        require(dec(costs["total_ms"]) * 10000 == dec(raw["objective_scaled"]), cid + " scaled objective")
        row = {"case_id": cid, "module": raw["module"], "l_init": raw["l_init"], "l_max": 14,
               "baseline_estimated_latency_ms": base_costs["total_ms"], "optimized_estimated_latency_ms": costs["total_ms"],
               "saving_ms": str(saving), "reduction_percent": str(reduction)}
        for prefix, metrics, cost in (("baseline", baseline, base_costs), ("optimized", audit, costs)):
            for key in COMPONENTS:
                row[f"{prefix}_{key}"] = cost[key]
            for key in ("n_b1", "n_b2", "n_bootstrap", "depth", "budget", "utilisation"):
                row[f"{prefix}_{key}"] = metrics[key]
        row.update({"solver_status": raw["solver_status"], "objective_scaled": raw["objective_scaled"],
                    "best_bound_scaled": raw["best_bound_scaled"], "relative_gap": raw["relative_gap"],
                    "saved_check_status": check["status"]})
        resources = {key: raw[key] for key in raw if key.endswith(("_seconds", "_bytes"))}
        resource_rows.append({"case_id": cid, "module": raw["module"], "l_init": raw["l_init"], **resources})
        sources.append({"case_id": cid, "case": case_path.relative_to(ROOT).as_posix(), "case_sha256": raw["case_sha256"],
                        "check": raw["check"], "check_sha256": raw["check_sha256"],
                        "run": run_path.relative_to(ROOT).as_posix(), "run_sha256": raw["run_json_sha256"],
                        "source_fingerprint": raw["source_fingerprint"],
                        "configuration": f"configs/t2-formal-20261004-r4/{cid}.json",
                        "configuration_sha256": digest(ROOT / f"configs/t2-formal-20261004-r4/{cid}.json")})
        cases[cid], checks[cid] = case, check
        rows.append(row)
    return summary, rows, cases, checks, sources, resource_rows, len(manifest), len(public_inputs)


def save_both(fig, stem):
    """Export vector text and a raster from one matplotlib figure."""
    fig.savefig(stem.with_suffix(".svg"), facecolor="white", bbox_inches="tight",
                metadata={"Date": None, "Creator": "Formal result analysis generator"})
    fig.savefig(stem.with_suffix(".png"), facecolor="white", bbox_inches="tight", dpi=140,
                metadata={"Software": "Formal result analysis generator"})
    plt.close(fig)


def draw_curve(rows, module, stem):
    from matplotlib.ticker import StrMethodFormatter
    subset = [r for r in rows if r["module"] == module]
    title = "MLP" if module == "mlp" else "Attention"
    levels = [r["l_init"] for r in subset]
    baseline = [float(r["baseline_estimated_latency_ms"]) for r in subset]
    optimized = [float(r["optimized_estimated_latency_ms"]) for r in subset]
    reduction = [float(r["reduction_percent"]) for r in subset]
    fig, axes = plt.subplots(2, 1, figsize=(9, 7.2), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    axes[0].plot(levels, baseline, color=BLUE, linestyle="--", marker="s", markersize=4, label="Teacher fixed-placement baseline")
    axes[0].plot(levels, optimized, color=TEAL, linewidth=2, marker="o", markersize=4, label="Shared-refresh CP-SAT")
    axes[0].set_ylabel("Estimated inference latency (ms)")
    axes[0].set_ylim(0, max(baseline) * 1.14)
    axes[0].yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    axes[0].legend(loc="lower left", frameon=False, fontsize=10)
    axes[1].plot(levels, reduction, color=TEAL, linewidth=2, marker="o", markersize=4)
    axes[1].set_ylabel("Reduction from baseline (%)")
    axes[1].set_ylim(0, 30)
    axes[1].set_xlabel("Input level (maximum level = 14)")
    axes[1].set_xticks(range(15))
    for ax in axes:
        ax.grid(axis="y", color="#dfe6eb", linewidth=0.7)
        ax.set_xlim(-0.4, 14.4)
    for r in subset:
        if r["case_id"] in SELECTED:
            level = r["l_init"]
            axes[1].annotate(f"L{level}: {float(r['reduction_percent']):.4f}%",
                             (level, float(r["reduction_percent"])), xytext=(-5 if level == 14 else 8, 12),
                             textcoords="offset points", ha="right" if level == 14 else "left", fontsize=9, color=INK)
    fig.suptitle(f"{title}: full input-level comparison", x=0.10, ha="left", fontsize=17, fontweight="bold")
    fig.text(0.10, 0.023, "One saved optimization run per condition. Costs follow the course model; lines connect discrete levels.\n"
             f"Reduction (%) = 100 x (baseline - optimized) / baseline. Source: {SOURCE_ID}.", fontsize=8.5, color=INK)
    fig.tight_layout(rect=(0.025, 0.08, 0.99, 0.94))
    save_both(fig, stem)
    write_json(stem.with_suffix(".data.json"), {"module": module, "source": SOURCE_ID, "points": subset})


def draw_costs(rows, stem):
    from matplotlib.patches import Patch
    colors = [BLUE, AMBER, PURPLE, "#87959e"]
    labels = ["Ordinary operations", "Bootstrap1", "Bootstrap2", "Modswitch (zero cost here)"]
    fig, axes = plt.subplots(2, 2, figsize=(13.2, 8.4))
    selected = [next(r for r in rows if r["case_id"] == cid) for cid in SELECTED]
    for ax, row in zip(axes.flat, selected):
        title = ("MLP" if row["module"] == "mlp" else "Attention") + f", input level {row['l_init']}"
        for y, prefix in ((1, "baseline"), (0, "optimized")):
            left = 0
            for component, color in zip(COMPONENTS, colors):
                value = float(row[f"{prefix}_{component}"])
                ax.barh(y, value, left=left, height=0.46, color=color)
                left += value
            total = float(row[f"{prefix}_estimated_latency_ms"])
            ax.text(total + 650, y, f"{total:,.4f}", va="center", fontsize=8.5, color=INK)
        ax.set_yticks([1, 0], ["Teacher baseline", "CP-SAT"])
        ax.set_ylim(-0.65, 1.65)
        ax.set_xlim(0, 69000)
        ax.set_xticks([0, 20000, 40000, 60000], ["0", "20,000", "40,000", "60,000"])
        ax.set_xlabel("Estimated latency (ms)")
        ax.set_title(title + f"\nReduction {float(row['reduction_percent']):.4f}%", loc="left", fontsize=12, pad=12)
        ax.grid(axis="x", color="#e4e9ee", lw=0.6)
        ax.set_axisbelow(True)
    fig.suptitle("Where the saved cost reductions come from", x=0.055, ha="left", fontsize=18, fontweight="bold")
    fig.legend([Patch(facecolor=c) for c in colors], labels, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 0.067), fontsize=9)
    fig.text(0.055, 0.022, "All ordinary operations and shared inserted operations are included once. Modswitch costs are exactly zero in these saved cases.\n"
             f"Source: {SOURCE_ID}, saved independent checks. Numerical components: cases.md.", fontsize=8.5)
    fig.tight_layout(rect=(0.025, 0.13, 0.99, 0.93), h_pad=2.2, w_pad=2.5)
    save_both(fig, stem)
    write_json(stem.with_suffix(".data.json"), {"source": SOURCE_ID, "components": COMPONENTS, "cases": selected})


def draw_placement(case, stem):
    """Draw all saved nodes/edges, retaining SVG IDs for separate checks.

    Layering and residual lanes adapt the repository's S3 renderer.
    No numeric-model module is imported; graph data are read, not rebuilt.
    """
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch
    from matplotlib.path import Path as MplPath
    checked = case["validated"]
    nodes, edges, audit = checked["nodes"], checked["edges"], checked["audit"]
    by_name = {n[0]: n for n in nodes}
    pred = defaultdict(list)
    for u, v, _ in edges:
        pred[v].append(u)
    order = list(TopologicalSorter({n: pred[n] for n in by_name}).static_order())
    rank, layers, xpos = {}, defaultdict(list), {}
    for name in order:
        rank[name] = max((rank[p] + 1 for p in pred[name]), default=0)
        layers[rank[name]].append(name)
    for layer in sorted(layers):
        names = sorted(layers[layer], key=lambda n: (sum(xpos[p] for p in pred[n]) / max(1, len(pred[n])), n))
        for i, name in enumerate(names):
            xpos[name] = (i - (len(names) - 1) / 2) * 5.3
    ystep, width, height = 1.85, 4.25, 1.10
    pos = {n: (xpos[n], -rank[n] * ystep) for n in order}
    long_edges = [(u, v, ct) for u, v, ct in edges if rank[v] - rank[u] > 1]
    side_lanes, lane_for = {-1: [], 1: []}, {}
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
    xleft = node_left - (len(side_lanes[-1]) + 1)
    xright = node_right + (len(side_lanes[1]) + 1)
    bottom = -max(rank.values()) * ystep - 3.3
    fig, ax = plt.subplots(figsize=((xright - xleft) * 0.80, (2.2 - bottom) * 0.59))
    ax.set(xlim=(xleft, xright), ylim=(bottom, 2.2), aspect="equal")
    ax.axis("off")
    levels = {(e["from"], e["to"]): e["level"] for e in audit["edge_levels"]}
    drawn_edges = []
    for index, (u, v, ct) in enumerate(edges):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        start, end = (x0, y0 - height / 2), (x1, y1 + height / 2)
        label = f"L={levels[u, v]}  ct={ct}"
        if (u, v) in lane_for:
            side, lane = lane_for[u, v]
            outside = (node_left if side < 0 else node_right) + side * (0.7 + lane)
            points = [start, (x0, start[1] - 0.20), (outside, start[1] - 0.20),
                      (outside, end[1] + 0.20), (x1, end[1] + 0.20), end]
            path = MplPath(points, [MplPath.MOVETO] + [MplPath.LINETO] * 5)
            arrow = FancyArrowPatch(path=path, arrowstyle="-|>", mutation_scale=9, color=AMBER, lw=0.9, zorder=1)
            text = ax.text(outside + side * 0.12, (start[1] + end[1]) / 2, label, rotation=90,
                           ha="right" if side < 0 else "left", va="center", fontsize=8, color=AMBER,
                           bbox={"facecolor": "white", "edgecolor": "none", "pad": 1}, zorder=2)
        else:
            arrow = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=9, color=INK, lw=0.9, zorder=1)
            text = ax.text((x0 + x1) / 2 + 0.12, (start[1] + end[1]) / 2, label,
                           ha="left", va="center", fontsize=8, color=INK,
                           bbox={"facecolor": "white", "edgecolor": "none", "pad": 1}, zorder=2)
        arrow.set_gid(f"edge-{index:03}")
        text.set_gid(f"label-edge-{index:03}")
        ax.add_patch(arrow)
        drawn_edges.append({"index": index, "from": u, "to": v, "ciphertexts": ct, "level": levels[u, v], "label": label})
    drawn_nodes = []
    for name, op, depth, description in nodes:
        x, y = pos[name]
        color = "#fff0d9" if op == "Bootstrap1" else "#f0e9fa" if op == "Bootstrap2" else "#edf0f3" if op == "Modswitch" else "#e7f4f1" if op.startswith("PolyEval") else "#eaf1fc" if "MM" in op else "#ffffff"
        edge_color = AMBER if op == "Bootstrap1" else PURPLE if op == "Bootstrap2" else INK
        box = FancyBboxPatch((x - width / 2, y - height / 2), width, height,
                            boxstyle="round,pad=0.03,rounding_size=0.06", fc=color, ec=edge_color, lw=1, zorder=3)
        box.set_gid("node-" + name)
        ax.add_patch(box)
        short = name.removesuffix("_mlp").removesuffix("_attn").removeprefix("s2_")
        short = "\n".join(textwrap.wrap(short.replace("_", " "), width=35))
        text = ax.text(x, y + 0.27, short, fontsize=9, fontweight="bold", ha="center", va="center", color=INK, zorder=4)
        text.set_gid("label-node-" + name)
        text = ax.text(x, y - 0.02, op, fontsize=8.5, ha="center", va="center", color=INK, zorder=4)
        text.set_gid("label-op-" + name)
        level_label = f"L_in={audit['l_in'][name]}  L_out={audit['l_out'][name]}"
        text = ax.text(x, y - 0.33, level_label, fontsize=8.5, ha="center", va="center", color=INK, zorder=4)
        text.set_gid("label-levels-" + name)
        drawn_nodes.append({"id": name, "op": op, "original_depth": depth, "description": description,
                            "display_name": short, "input_level": audit["l_in"][name],
                            "output_level": audit["l_out"][name], "level_label": level_label, "x": x, "y": y})
    title = "MLP" if case["module"] == "mlp" else "Attention"
    ax.set_title(f"{title} saved placement, input level {case['l_init']}\n"
                 f"Estimated latency {float(audit['latency_decimal_ms']):,.4f} ms   B1 {audit['n_b1']}   B2 {audit['n_b2']}\n"
                 f"Depth {audit['depth']}   Budget {audit['budget']}   Utilisation {audit['utilisation']:.6f}",
                 fontsize=13, color=INK, pad=30, linespacing=1.5)
    handles = [Patch(fc="#fff0d9", ec=AMBER, label="Bootstrap1"), Patch(fc="#f0e9fa", ec=PURPLE, label="Bootstrap2"),
               Patch(fc="#edf0f3", ec=INK, label="Modswitch"), Patch(fc="#eaf1fc", ec=INK, label="Matrix operation"),
               Patch(fc="#e7f4f1", ec=INK, label="Polynomial operation"), Patch(fc="white", ec=INK, label="Other original operation")]
    ax.legend(handles=handles, loc="upper center", ncol=3, frameon=False, fontsize=8)
    ax.text((xleft + xright) / 2, bottom + 0.1,
            f"Source: {SOURCE_ID}, {case['case_id']}. All {len(nodes)} nodes and {len(edges)} edges are shown.\n"
            "Edges: producer level L and ciphertext count ct. A merge receives the minimum incoming level.\n"
            "B1 counts ciphertexts; B2 counts pairs. Shared inserted operations are drawn and charged once.\n"
            "Open the SVG with zoom to inspect individual operations. Positions have no performance meaning.",
            ha="center", va="bottom", fontsize=8.5, color=INK)
    save_both(fig, stem)
    write_json(stem.with_suffix(".data.json"), {
        "case_id": case["case_id"], "source": SOURCE_ID, "nodes": nodes, "edges": edges,
        "edge_levels": audit["edge_levels"], "node_input_levels": audit["l_in"], "node_output_levels": audit["l_out"],
        "drawn_nodes": drawn_nodes, "drawn_edges": drawn_edges,
        "metrics": {k: audit[k] for k in ("latency_decimal_ms", "n_b1", "n_b2", "n_bootstrap", "depth", "budget", "utilisation")},
    })


def make_tables(output, rows, cases, checks, summary, resource_rows):
    write_csv(output / "comparison.csv", rows)
    write_json(output / "comparison.json", {"source": SOURCE_ID, "decimal_encoding": "Exact decimal quantities are strings; units appear in field names.", "rows": rows})
    write_csv(output / "resource-observations.csv", resource_rows)
    write_json(output / "resource-observations.json", {"source": SOURCE_ID, "recorded_total_scope": summary["resources"],
               "observations": resource_rows, "new_measurements": False,
               "note": "Per-condition core/solver/body intervals are nested in attempt windows. Do not add them to the outer totals."})
    resource_lines = ["# Recorded computation resources", "",
                      "These are the original formal-run observations, not new measurements or estimated inference latency.",
                      "All time columns use seconds. RSS uses MiB (1,048,576 bytes). Display values are rounded; CSV/JSON retain the source values.",
                      "Core, solve and check-body intervals are inside their attempt windows; do not add these columns together.", "",
                      "| Condition | Solve wall | Core wall | Core CPU | Sampled core RSS (MiB) | Run attempt wall | Check attempt wall | Check body wall |",
                      "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in resource_rows:
        resource_lines.append(f"| {r['case_id']} | {r['solve_wall_seconds']:.6f} | {r['core_pipeline_wall_seconds']:.6f} | {r['core_pipeline_cpu_seconds']:.6f} | {r['core_sampled_peak_rss_bytes']/1048576:.3f} | {r['run_attempt_wall_seconds']:.6f} | {r['verify_attempt_wall_seconds']:.6f} | {r['verify_body_wall_seconds']:.6f} |")
    resource_lines += ["", "The recorded RSS is a sampled maximum, not an exact or cross-device peak.",
                       "See [analysis and resource scope](README.md#computation-resources) for aggregate intervals and exclusions.",
                       "See [CSV](resource-observations.csv) / [JSON](resource-observations.json) for all saved timing fields and the original total-resource record."]
    (output / "resource-observations.md").write_text("\n".join(resource_lines) + "\n", encoding="utf-8")
    lines = ["# Full comparison", "", "Each row is one input level of one of the two fixed graphs. Estimated costs are in milliseconds.",
             "Reduction = (same-condition baseline - optimized) / baseline x 100. Display rounding does not replace exact CSV/JSON values.",
             "", "| Module | Input | Baseline (ms) | Optimized (ms) | Saved (ms) | Reduction (%) | Baseline B1/B2 | Optimized B1/B2 |",
             "|---|---:|---:|---:|---:|---:|---|---|"]
    for r in rows:
        lines.append(f"| {r['module']} | {r['l_init']} | {float(r['baseline_estimated_latency_ms']):.4f} | {float(r['optimized_estimated_latency_ms']):.4f} | {float(r['saving_ms']):.4f} | {float(r['reduction_percent']):.4f} | {r['baseline_n_b1']}/{r['baseline_n_b2']} | {r['optimized_n_b1']}/{r['optimized_n_b2']} |")
    lines += ["", "Every saved result is OPTIMAL with zero recorded gap and a passed saved-result check. Optimality is limited to the encoded course model.",
              "", "Exact fields are also available in the [CSV](comparison.csv) and [JSON](comparison.json).",
              "B1 counts ciphertexts; B2 counts pairs. Their sum is the course refresh count, not the number of boxes.",
              "Depth is the greatest accumulated ordinary-operation level consumption on a path. Budget = 14 x B1 + 13 x B2 + input level; utilisation = depth / budget.",
              "", "Source: [formal package](../T2-FORMAL-20261004-004/README.md); [per-row traceability](provenance.json).",
              "", "## Cost components", "", "All values are estimated milliseconds. Modswitch is zero for both methods in every condition.", "",
              "| Condition | Baseline ordinary | Optimized ordinary | Baseline B1 | Optimized B1 | Baseline B2 | Optimized B2 |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for r in rows:
        values = [r[f"{method}_{component}_ms"] for component in ("ordinary", "bootstrap1", "bootstrap2") for method in ("baseline", "optimized")]
        lines.append("| " + r["case_id"] + " | " + " | ".join(f"{float(value):.4f}" for value in values) + " |")
    lines += ["", "## Level metrics and saved status", "",
              "Utilisation is a depth-to-budget ratio, not CPU utilisation or a latency score. The input-level ceiling is 14 throughout.", "",
              "| Condition | Baseline depth | Optimized depth | Baseline budget | Optimized budget | Baseline utilisation | Optimized utilisation | Solver / saved check |",
              "|---|---:|---:|---:|---:|---:|---:|---|"]
    for r in rows:
        lines.append(f"| {r['case_id']} | {r['baseline_depth']} | {r['optimized_depth']} | {r['baseline_budget']} | {r['optimized_budget']} | {r['baseline_utilisation']:.6f} | {r['optimized_utilisation']:.6f} | {r['solver_status']} / {r['saved_check_status']} |")
    (output / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    evidence = []
    lines = ["# Four saved cases", "", "The pairs straddle cost transitions in the full curves. They explain particular saved solutions; no counterfactual search was performed.", ""]
    for cid in SELECTED:
        row = next(r for r in rows if r["case_id"] == cid)
        case, check = cases[cid], checks[cid]
        audit = case["validated"]["audit"]
        changes = []
        for name, op, _, _ in case["validated"]["nodes"]:
            if op not in INSERTED:
                base_cost = check["baseline_audit"]["node_latency_decimal_ms"][name]
                opt_cost = audit["node_latency_decimal_ms"][name]
                if dec(base_cost) != dec(opt_cost):
                    changes.append({"node": name, "op": op, "baseline_ms": base_cost, "optimized_ms": opt_cost,
                                    "saving_ms": str(dec(base_cost) - dec(opt_cost))})
        evidence.append({"case_id": cid, "baseline_costs": check["baseline_costs"], "optimized_costs": check["current_costs"],
                         "shared_refreshes": case["solution"]["shared_refreshes"],
                         "placement_chains": audit["placement_chains"], "ordinary_node_changes": changes})
        lines += [f"## {cid}", "", "| Quantity | Teacher baseline | CP-SAT |", "|---|---:|---:|"]
        for field in (*COMPONENTS, "n_b1", "n_b2", "n_bootstrap", "depth", "budget", "utilisation"):
            lines.append(f"| {field} | {row['baseline_' + field]} | {row['optimized_' + field]} |")
        lines += [f"| Total estimated latency (ms) | {row['baseline_estimated_latency_ms']} | {row['optimized_estimated_latency_ms']} |",
                  "", f"[Complete placement diagram](figures/placement-{cid}.svg), [PNG](figures/placement-{cid}.png), [drawn data](figures/placement-{cid}.data.json).", ""]
    (output / "cases.md").write_text("\n".join(lines), encoding="utf-8")
    write_json(output / "case-explanations.json", {"source": SOURCE_ID, "selected_cases": evidence})
    groups = []
    for module in ("mlp", "attention"):
        subset = [r for r in rows if r["module"] == module]
        for cost in dict.fromkeys(r["optimized_estimated_latency_ms"] for r in subset):
            group = [r for r in subset if r["optimized_estimated_latency_ms"] == cost]
            groups.append({"module": module, "input_levels": [r["l_init"] for r in group], "optimized_ms": cost,
                           "min_reduction_percent": str(min(dec(r["reduction_percent"]) for r in group)),
                           "max_reduction_percent": str(max(dec(r["reduction_percent"]) for r in group)),
                           "optimized_n_b1": sorted({r["optimized_n_b1"] for r in group}),
                           "optimized_n_b2": sorted({r["optimized_n_b2"] for r in group})})
    write_json(output / "analysis-summary.json", {"source": SOURCE_ID, "condition_count": len(rows),
               "all_strictly_improved": all(dec(r["saving_ms"]) > 0 for r in rows), "plateaus": groups,
               "counts_can_increase": [r["case_id"] for r in rows if r["optimized_n_bootstrap"] > r["baseline_n_bootstrap"]],
               "selected": SELECTED})


def generate(output):
    global plt
    require(not output.exists(), "Refusing to overwrite an existing output directory")
    require(not output.is_relative_to(SOURCE), "Output cannot be inside the source experiment")
    summary, rows, cases, checks, sources, resource_rows, count, input_count = load_inputs()
    output.mkdir(parents=True, exist_ok=False)
    figures = output / "figures"
    figures.mkdir()
    # This per-process temporary cache does not change persistent configuration.
    with tempfile.TemporaryDirectory(prefix="t3-matplotlib-") as cache:
        os.environ["MPLCONFIGDIR"] = cache
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as pyplot
        plt = pyplot
        plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none", "svg.hashsalt": "formal-analysis-v1",
                             "axes.spines.top": False, "axes.spines.right": False, "axes.labelcolor": INK,
                             "text.color": INK, "axes.edgecolor": "#9aa8b4", "axes.titlecolor": INK})
        make_tables(output, rows, cases, checks, summary, resource_rows)
        for module in ("mlp", "attention"):
            draw_curve(rows, module, figures / f"comparison-{module}")
        draw_costs(rows, figures / "cost-components")
        for cid in SELECTED:
            draw_placement(cases[cid], figures / f"placement-{cid}")
    write_json(output / "provenance.json", {
        "source": SOURCE_ID, "source_manifest_sha256": EXPECTED_SOURCE_MANIFEST,
        "source_files_checked": count, "frozen_public_inputs_checked": input_count,
        "source_summary_json_sha256": digest(SOURCE / "summary.json"), "source_summary_csv_sha256": digest(SOURCE / "summary.csv"),
        "generator": Path(__file__).relative_to(ROOT).as_posix(), "generator_sha256": digest(Path(__file__)),
        "recorded_experiment_HEAD": "aa89f7bb870b1f11d305946f007b1cbb76073b2f",
        "recorded_experiment_worktree_dirty": True, "case_sources": sources, "selected_placement_cases": SELECTED,
        "selection": "Adjacent saved conditions across each module's recorded cost transition.",
        "python_version": platform.python_version(), "matplotlib_version": importlib.metadata.version("matplotlib"),
        "solver_calls": 0, "scoring_calls": 0, "purpose": "Analysis and figures derived from saved formal results.",
        "renderer_origin": "Layered layout adapted from src/bootplacement/s3_figures.py; numeric modules are not imported.",
    })
    files = {p.relative_to(output).as_posix(): digest(p) for p in sorted(output.rglob("*")) if p.is_file()}
    write_json(output / "generated.sha256.json", {"scope": "Generated data, tables and figures; authored analysis and checks are separate.", "files": files})
    print(json.dumps({"output": str(output), "conditions": len(rows), "figure_groups": 7, "svg": 7, "png": 7,
                      "source_files_checked": count, "frozen_public_inputs_checked": input_count}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="Fresh directory; relative paths resolve from the repository root")
    args = parser.parse_args()
    generate((ROOT / args.output).resolve())
