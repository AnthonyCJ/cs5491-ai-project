# Data dictionary

The comparison contains one row per `(module, l_init)`: MLP and Attention, each at levels 0–14, with maximum level 14. Both methods in a row use the same original graph, ciphertext counts, input condition and course cost functions.

| Field or field family | Meaning and unit |
|---|---|
| `case_id`, `module`, `l_init`, `l_max` | Saved condition identifier, graph, input level and maximum level. Levels are integers. |
| `baseline_estimated_latency_ms`, `optimized_estimated_latency_ms` | Total modeled cost in milliseconds. No measured inference time is implied. |
| `saving_ms` | Baseline total minus optimized total, in milliseconds. |
| `reduction_percent` | `100 × saving_ms / baseline_estimated_latency_ms`, the percentage reduction relative to that condition's baseline. |
| `baseline_*_ms`, `optimized_*_ms` | Components `ordinary`, `bootstrap1`, `bootstrap2`, `modswitch`; their sum equals that method's total. |
| `*_n_b1` | Bootstrap1 count in ciphertexts. Cost = count × 1040.15 ms; restored level = 14. |
| `*_n_b2` | Bootstrap2 count in ciphertext pairs. Cost = count × 1293.13 ms; restored level = 13. Allowed source ciphertext counts are 8 or 16. |
| `*_n_bootstrap` | The course's sum of the preceding two counts, which use different counting units. It is not the number of refresh boxes. |
| `*_depth` | Greatest accumulated ordinary-operation level consumption on a path in the original computation. Refresh restoration is not extra consumed depth. |
| `*_budget` | `14 × n_b1 + 13 × n_b2 + l_init`, the course-defined level budget. |
| `*_utilisation` | Depth divided by budget, a dimensionless ratio; not CPU utilisation. |
| `solver_status`, `best_bound_scaled`, `objective_scaled`, `relative_gap` | Saved solver status and bound evidence. Integer-objective scale is 10000 per millisecond. All formal rows are optimal with equal objective/bound and zero gap. |
| `saved_check_status` | Result of the original saved-solution check, inherited from the formal evidence. |

Costs and calculated decimal quantities use strings in JSON to preserve decimal precision. Exact finite source costs are retained. Percentage division uses Python Decimal's 28-digit precision; it is a high-precision quotient, not an exact rational encoding. Saved utilisation values retain their original floating-point representation. CSV uses the same values. Human tables round percentages to four decimals, utilisation to six decimals and resource times to six decimals; these displays do not replace the machine-readable values.

Ordinary-node costs are per operator and are not multiplied again by edge ciphertext count. A shared inserted operation is charged once. All Modswitch costs are zero in these inputs. Details are in the existing [objective and precision specification](../../docs/s2-method.md#objective-and-numerical-precision).

The resource files copy saved observations; they make no new measurements. Names ending in `_seconds` use seconds, names ending in `_bytes` use bytes, and MiB displays divide by 1048576. `solve_wall_seconds` is a measured wall interval; `solver_reported_wall_seconds` is the solver's own reported interval. Core intervals contain model construction and solving, and attempts include their process/control overhead. Check-body intervals are inside check attempts. CPU totals measure processor time and can exceed wall time. See [resource scope](README.md#computation-resources) before aggregation.

Placement data preserve all saved nodes, edges, input/output levels and metrics. `drawn_nodes` additionally records display labels and coordinates; `drawn_edges` gives the rendered label and source index. Coordinates convey layout only. Machine traceability paths are repository-relative in [provenance.json](provenance.json).
