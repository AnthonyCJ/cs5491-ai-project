"""Independently compare derived tables and rendered SVG labels with T2 sources.

This is file verification, not placement validation or an experiment. It uses
no generation helper, optimizer, scorer or subprocess.
"""
import argparse
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results/T2-FORMAL-20261004-004"
SELECTED = ("mlp-L13", "mlp-L14", "attention-L05", "attention-L06")
COMPONENTS = ("ordinary_ms", "bootstrap1_ms", "bootstrap2_ms", "modswitch_ms")


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def equal(left, right, label):
    if left != right:
        raise ValueError(f"{label}: {left!r} != {right!r}")


def text_content(element):
    return " ".join(" ".join(e.text or "" for e in element.iter() if e.tag.endswith("}text")).split())


def verify(package):
    from PIL import Image
    generated = read(package / "generated.sha256.json")["files"]
    for relative, expected in generated.items():
        equal(digest(package / relative), expected, relative + " generated hash")
    provenance = read(package / "provenance.json")
    equal(digest(ROOT / provenance["generator"]), provenance["generator_sha256"], "generator hash")
    equal(digest(SOURCE / "artifacts.sha256.json"), provenance["source_manifest_sha256"], "source manifest")
    raw_rows = read(SOURCE / "summary.json")["numerical_results"]
    with (package / "comparison.csv").open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    output_rows = read(package / "comparison.json")["rows"]
    equal(len(csv_rows), 30, "CSV row count")
    equal(len(output_rows), 30, "JSON row count")
    raw = {r["case_id"]: r for r in raw_rows}
    output = {r["case_id"]: r for r in output_rows}
    equal(set(raw), set(output), "case set")
    case_map, source_checks = {}, {}
    for row in output_rows:
        cid = row["case_id"]
        source = raw[cid]
        check = read(ROOT / source["check"])
        case = read(ROOT / source["output"] / "cases" / (cid + ".json"))
        case_map[cid], source_checks[cid] = case, check
        equal(row["module"], source["module"], cid + " module")
        equal(row["l_init"], source["l_init"], cid + " input")
        equal(row["l_max"], 14, cid + " maximum")
        for prefix, cost, metrics in (("baseline", check["baseline_costs"], check["baseline_audit"]),
                                       ("optimized", check["current_costs"], case["validated"]["audit"])):
            equal(Decimal(row[prefix + "_estimated_latency_ms"]), Decimal(cost["total_ms"]), cid + " total")
            equal(sum(Decimal(cost[k]) for k in COMPONENTS), Decimal(cost["total_ms"]), cid + " component sum")
            for component in COMPONENTS:
                equal(Decimal(row[prefix + "_" + component]), Decimal(cost[component]), cid + " " + component)
            for key in ("n_b1", "n_b2", "n_bootstrap", "depth", "budget", "utilisation"):
                equal(row[prefix + "_" + key], metrics[key], cid + " " + prefix + " " + key)
        base, opt = Decimal(check["baseline_costs"]["total_ms"]), Decimal(check["current_costs"]["total_ms"])
        equal(Decimal(row["saving_ms"]), base - opt, cid + " savings")
        equal(Decimal(row["reduction_percent"]), (base - opt) * 100 / base, cid + " percentage")
        equal(row["solver_status"], source["solver_status"], cid + " optimality state")
        equal(Decimal(str(row["objective_scaled"])), opt * 10000, cid + " objective")
        equal(Decimal(str(row["best_bound_scaled"])), opt * 10000, cid + " bound")
        equal(row["relative_gap"], source["relative_gap"], cid + " gap")
        equal(row["saved_check_status"], check["status"], cid + " check")
    for csv_row in csv_rows:
        row = output[csv_row["case_id"]]
        equal(set(csv_row), set(row), "CSV columns")
        for key, value in row.items():
            if isinstance(value, (int, float)):
                equal(Decimal(csv_row[key]), Decimal(str(value)), csv_row["case_id"] + " CSV " + key)
            else:
                equal(csv_row[key], value, csv_row["case_id"] + " CSV " + key)
    for module in ("mlp", "attention"):
        data = read(package / "figures" / f"comparison-{module}.data.json")
        equal(data["points"], [r for r in output_rows if r["module"] == module], module + " curve data")
    costs = read(package / "figures/cost-components.data.json")
    equal(costs["cases"], [output[c] for c in SELECTED], "cost plot data")
    graph_checks = []
    for cid in SELECTED:
        case = case_map[cid]
        saved = case["validated"]
        graph = read(package / "figures" / f"placement-{cid}.data.json")
        equal(graph["nodes"], saved["nodes"], cid + " complete nodes")
        equal(graph["edges"], saved["edges"], cid + " complete edges")
        equal(graph["edge_levels"], saved["audit"]["edge_levels"], cid + " edge levels")
        equal(graph["node_input_levels"], saved["audit"]["l_in"], cid + " inputs")
        equal(graph["node_output_levels"], saved["audit"]["l_out"], cid + " outputs")
        for key, value in graph["metrics"].items():
            equal(value, saved["audit"][key], cid + " diagram metrics " + key)
        svg = ET.parse(package / "figures" / f"placement-{cid}.svg").getroot()
        elements = {e.attrib["id"]: e for e in svg.iter() if "id" in e.attrib}
        equal({k.removeprefix("node-") for k in elements if k.startswith("node-")},
              {n[0] for n in saved["nodes"]}, cid + " rendered node IDs")
        equal({k for k in elements if re.fullmatch(r"edge-\d{3}", k)},
              {f"edge-{i:03}" for i in range(len(saved["edges"]))}, cid + " rendered edge IDs")
        for node in graph["drawn_nodes"]:
            name = node["id"]
            equal(text_content(elements["label-node-" + name]), " ".join(node["display_name"].split()), cid + " visible node name")
            equal(text_content(elements["label-op-" + name]), node["op"], cid + " visible operator")
            expected = f"L_in={saved['audit']['l_in'][name]} L_out={saved['audit']['l_out'][name]}"
            equal(text_content(elements["label-levels-" + name]), expected, cid + " visible node levels")
        for index, (u, v, ct) in enumerate(saved["edges"]):
            level = saved["audit"]["l_out"][u]
            equal(text_content(elements[f"label-edge-{index:03}"]), f"L={level} ct={ct}", cid + " visible edge annotation")
            edge = graph["drawn_edges"][index]
            equal((edge["from"], edge["to"], edge["ciphertexts"], edge["level"]), (u, v, ct, level), cid + " drawn edge")
        graph_checks.append({"case_id": cid, "nodes": len(saved["nodes"]), "edges": len(saved["edges"]), "svg_ids_and_labels_match": True})
    images = []
    for path in sorted((package / "figures").glob("*.png")):
        with Image.open(path) as image:
            dimensions = image.size
            image.verify()
        images.append({"file": path.name, "width": dimensions[0], "height": dimensions[1]})
    equal(len(images), 7, "PNG count")
    equal(len(list((package / "figures").glob("*.svg"))), 7, "SVG count")
    resource_rows = read(package / "resource-observations.json")["observations"]
    equal(len(resource_rows), 30, "resource row count")
    for row in resource_rows:
        for key, value in row.items():
            equal(value, raw[row["case_id"]][key], row["case_id"] + " recorded resource " + key)
    equal(read(package / "resource-observations.json")["recorded_total_scope"],
          read(SOURCE / "summary.json")["resources"], "original resource scope")
    return {"status": "passed", "conditions": 30, "generated_files_hashed": len(generated),
            "numeric_and_csv_checks": "All rows, totals, components, counts, depth/budget/utilisation, savings, states and bounds match saved sources.",
            "figure_groups": 7, "placement_checks": graph_checks, "pngs": images,
            "resource_rows_match": 30, "solver_calls": 0, "scoring_calls": 0,
            "scope": "Derived-file/visible-SVG-content checks. Separate visual review checks layout; T2 scientific validity is inherited.",
            "checker_sha256": digest(Path(__file__)), "generator_sha256": provenance["generator_sha256"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    result = verify((ROOT / args.package).resolve())
    if args.receipt:
        path = (ROOT / args.receipt).resolve()
        if path.exists():
            raise FileExistsError("Refusing to replace a check receipt")
        path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
