"""Campaign funnel, break-even spend solver, and sensitivity tornado.

Funnel: Spend -> Impressions (via derived CPM) -> Clicks (CTR) -> Orders (CVR)
-> Gross Revenue (AOV) -> Incremental Revenue (haircut) -> Incremental ROAS.

CPM is not directly disclosed for either channel in the sourced benchmarks, so it
is derived from CPC and CTR: CPM = CPC * CTR_fraction * 1000. This keeps every
number traceable to something in data/raw/ad_benchmarks.csv, shown as a formula
rather than assumed.
"""
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS_PATH = ROOT / "data" / "raw" / "ad_benchmarks.csv"
OUT_TABLE = ROOT / "outputs" / "tables" / "funnel_and_sensitivity.csv"


def load_benchmarks() -> dict:
    with open(BENCHMARKS_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {(r["channel"], r["metric"]): float(r["value"]) for r in rows}


def channel_inputs(b: dict, channel: str) -> dict:
    ctr_pct = b[(channel, "CTR")]
    cvr_pct = b[(channel, "CVR")]
    if channel == "Display":
        cpc_global_usd = b[(channel, "CPC_global_usd")]
        discount_mid = (b[(channel, "India_CPC_discount_low")] + b[(channel, "India_CPC_discount_high")]) / 2
        cpc_inr = cpc_global_usd * (1 - discount_mid / 100) * b[("FX", "USDINR")]
    elif channel == "Shopping":
        cpc_inr = (b[(channel, "CPC_india_low_inr")] + b[(channel, "CPC_india_high_inr")]) / 2
    else:
        raise ValueError(channel)
    cpm_inr = cpc_inr * (ctr_pct / 100) * 1000
    # Full precision, not rounded here: this feeds run_funnel(), and rounding before
    # deriving downstream figures is what caused the earlier CPM/break-even drift
    # against the Excel workbook. Round only at display time (see __main__).
    return {"ctr_pct": ctr_pct, "cvr_pct": cvr_pct, "cpc_inr": cpc_inr, "cpm_inr": cpm_inr}


def aov_inr(b: dict) -> float:
    low = b[("Market", "AOV_india_overall_usd_low")]
    high = b[("Market", "AOV_india_overall_usd_high")]
    mid_usd = (low + high) / 2
    return round(mid_usd * b[("FX", "USDINR")], 2)


def run_funnel(spend_inr: float, ctr_pct: float, cvr_pct: float, cpm_inr: float,
               aov: float, haircut_pct: float) -> dict:
    impressions = spend_inr / cpm_inr * 1000
    clicks = impressions * (ctr_pct / 100)
    orders = clicks * (cvr_pct / 100)
    gross_revenue = orders * aov
    incremental_revenue = gross_revenue * (1 - haircut_pct / 100)
    incremental_roas = incremental_revenue / spend_inr if spend_inr else 0
    return {
        "spend_inr": spend_inr, "impressions": round(impressions),
        "clicks": round(clicks, 1), "orders": round(orders, 2),
        "gross_revenue_inr": round(gross_revenue, 2),
        "incremental_revenue_inr": round(incremental_revenue, 2),
        # Full precision, not rounded here: rounding before deriving break-even spend
        # produced a value ~1 INR off from the Excel workbook's live-formula result
        # (which carries full precision end to end). Round only at display time.
        "incremental_roas": incremental_roas,
    }


def breakeven_spend(incremental_roas: float, fixed_cost_inr: float) -> str:
    if incremental_roas <= 1:
        return "NEVER — incremental ROAS <= 1 at these assumptions; no spend level recovers the fixed cost"
    spend = fixed_cost_inr / (incremental_roas - 1)
    return f"{round(spend):,} INR"


def sensitivity_tornado(base_ctr, base_cvr, base_haircut, cpm, aov, spend, delta_pct=20) -> list[dict]:
    rows = []
    levers = {
        "CTR": base_ctr,
        "CVR": base_cvr,
        "Incrementality haircut": base_haircut,
    }
    base = run_funnel(spend, base_ctr, base_cvr, cpm, aov, base_haircut)
    for lever, base_val in levers.items():
        for direction, mult in [("low", 1 - delta_pct / 100), ("high", 1 + delta_pct / 100)]:
            ctr, cvr, haircut = base_ctr, base_cvr, base_haircut
            if lever == "CTR":
                ctr = base_val * mult
            elif lever == "CVR":
                cvr = base_val * mult
            else:
                haircut = min(base_val * mult, 99)
            result = run_funnel(spend, ctr, cvr, cpm, aov, haircut)
            rows.append({
                "lever": lever, "direction": direction,
                "lever_value": round(ctr if lever == "CTR" else cvr if lever == "CVR" else haircut, 3),
                "incremental_roas": round(result["incremental_roas"], 4),
                "delta_vs_base_roas": round(result["incremental_roas"] - base["incremental_roas"], 4),
            })
    return rows


if __name__ == "__main__":
    b = load_benchmarks()
    aov = aov_inr(b)
    fixed_cost = b[("Assumption", "fixed_campaign_cost_inr")]
    base_haircut = b[("Assumption", "incrementality_haircut_base_pct")]
    spend_test = 500_000  # INR — illustrative campaign spend for the base case

    OUT_TABLE.parent.mkdir(parents=True, exist_ok=True)
    all_rows = []
    for channel in ["Display", "Shopping"]:
        ci = channel_inputs(b, channel)
        base = run_funnel(spend_test, ci["ctr_pct"], ci["cvr_pct"], ci["cpm_inr"], aov, base_haircut)
        be = breakeven_spend(base["incremental_roas"], fixed_cost)
        print(f"\n=== {channel} ===")
        print(f"Derived CPM: INR {round(ci['cpm_inr'], 2)} | CPC: INR {round(ci['cpc_inr'], 2)} | "
              f"CTR: {ci['ctr_pct']}% | CVR: {ci['cvr_pct']}%")
        print(f"At spend INR {spend_test:,}: incremental ROAS = {round(base['incremental_roas'], 4)}x, "
              f"incremental revenue = INR {base['incremental_revenue_inr']:,.0f}")
        print(f"Break-even spend to recover INR {fixed_cost:,.0f} fixed cost: {be}")

        tornado = sensitivity_tornado(ci["ctr_pct"], ci["cvr_pct"], base_haircut, ci["cpm_inr"], aov, spend_test)
        for row in tornado:
            row["channel"] = channel
            all_rows.append(row)

    with open(OUT_TABLE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["channel", "lever", "direction", "lever_value",
                                                 "incremental_roas", "delta_vs_base_roas"])
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"\nSensitivity tornado written -> {OUT_TABLE}")
