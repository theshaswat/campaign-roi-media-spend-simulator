# Data Dictionary

## `data/raw/ad_benchmarks.csv`

| Field | Description |
|---|---|
| `channel` | Display, Shopping, FX, Market, or Assumption |
| `metric` | The specific figure — e.g. `CTR`, `CVR`, `CPC_global_usd` |
| `value` | The numeric value |
| `unit` | pct, USD, INR, or rate |
| `source` | Citing report |
| `notes` | Scope/derivation notes |
| `confidence` | `source_confirmed` or `assumption_illustrative` |

## `outputs/tables/funnel_and_sensitivity.csv`

| Field | Description |
|---|---|
| `channel` | Display or Shopping |
| `lever` | CTR, CVR, or Incrementality haircut |
| `direction` | low (-20%) or high (+20%) |
| `lever_value` | The lever's value at that perturbation |
| `incremental_roas` | Resulting incremental ROAS |
| `delta_vs_base_roas` | Change vs. the base-case ROAS |

## `excel_model/Campaign_ROI_Simulator.xlsx`

Three sheets: `Assumptions` (every sourced input, yellow-highlighted cells are the editable
assumptions), `Funnel_Model` (the full funnel per channel, every cell a live formula), `Sensitivity`
(the tornado, also live formulas referencing Assumptions).
