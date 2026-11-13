# Four saved cases

The pairs straddle cost transitions in the full curves. They explain particular saved solutions; no counterfactual search was performed.

## mlp-L13

| Quantity | Teacher baseline | CP-SAT |
|---|---:|---:|
| ordinary_ms | 17758.4997 | 16736.8324 |
| bootstrap1_ms | 5200.75 | 4160.60 |
| bootstrap2_ms | 5172.52 | 5172.52 |
| modswitch_ms | 0 | 0 |
| n_b1 | 5 | 4 |
| n_b2 | 4 | 4 |
| n_bootstrap | 9 | 8 |
| depth | 26 | 26 |
| budget | 135 | 121 |
| utilisation | 0.1925925925925926 | 0.21487603305785125 |
| Total estimated latency (ms) | 28131.7697 | 26069.9524 |

[Complete placement diagram](figures/placement-mlp-L13.svg), [PNG](figures/placement-mlp-L13.png), [drawn data](figures/placement-mlp-L13.data.json).

## mlp-L14

| Quantity | Teacher baseline | CP-SAT |
|---|---:|---:|
| ordinary_ms | 17758.6597 | 16739.0724 |
| bootstrap1_ms | 5200.75 | 0 |
| bootstrap2_ms | 5172.52 | 5172.52 |
| modswitch_ms | 0 | 0 |
| n_b1 | 5 | 0 |
| n_b2 | 4 | 4 |
| n_bootstrap | 9 | 4 |
| depth | 26 | 26 |
| budget | 136 | 66 |
| utilisation | 0.19117647058823528 | 0.3939393939393939 |
| Total estimated latency (ms) | 28131.9297 | 21911.5924 |

[Complete placement diagram](figures/placement-mlp-L14.svg), [PNG](figures/placement-mlp-L14.png), [drawn data](figures/placement-mlp-L14.data.json).

## attention-L05

| Quantity | Teacher baseline | CP-SAT |
|---|---:|---:|
| ordinary_ms | 33851.7818 | 24951.7264 |
| bootstrap1_ms | 9361.35 | 10401.50 |
| bootstrap2_ms | 10345.04 | 10345.04 |
| modswitch_ms | 0 | 0 |
| n_b1 | 9 | 10 |
| n_b2 | 8 | 8 |
| n_bootstrap | 17 | 18 |
| depth | 62 | 62 |
| budget | 235 | 249 |
| utilisation | 0.26382978723404255 | 0.24899598393574296 |
| Total estimated latency (ms) | 53558.1718 | 45698.2664 |

[Complete placement diagram](figures/placement-attention-L05.svg), [PNG](figures/placement-attention-L05.png), [drawn data](figures/placement-attention-L05.data.json).

## attention-L06

| Quantity | Teacher baseline | CP-SAT |
|---|---:|---:|
| ordinary_ms | 33851.7818 | 24951.7264 |
| bootstrap1_ms | 9361.35 | 6240.90 |
| bootstrap2_ms | 10345.04 | 10345.04 |
| modswitch_ms | 0 | 0 |
| n_b1 | 9 | 6 |
| n_b2 | 8 | 8 |
| n_bootstrap | 17 | 14 |
| depth | 62 | 62 |
| budget | 236 | 194 |
| utilisation | 0.2627118644067797 | 0.31958762886597936 |
| Total estimated latency (ms) | 53558.1718 | 41537.6664 |

[Complete placement diagram](figures/placement-attention-L06.svg), [PNG](figures/placement-attention-L06.png), [drawn data](figures/placement-attention-L06.data.json).
