"""Builds the live-formula Excel workbook: Assumptions -> Funnel Model -> Sensitivity.

Every number in Funnel Model and Sensitivity is a formula referencing Assumptions,
never a pasted value — so the workbook can't drift from its own source inputs.
"""
from pathlib import Path
import csv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS_PATH = ROOT / "data" / "raw" / "ad_benchmarks.csv"
OUT_PATH = ROOT / "excel_model" / "Campaign_ROI_Simulator.xlsx"

HEADER_FILL = PatternFill("solid", fgColor="1B2430")
HEADER_FONT = Font(color="FFFFFF", bold=True)
LABEL_FONT = Font(bold=True)
ASSUMPTION_FILL = PatternFill("solid", fgColor="FFF2CC")


def load_benchmarks() -> dict:
    with open(BENCHMARKS_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {(r["channel"], r["metric"]): (float(r["value"]), r["source"], r["notes"], r["confidence"]) for r in rows}


def style_header(ws, row, n_cols):
    for c in range(1, n_cols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT


def build():
    b = load_benchmarks()
    wb = Workbook()

    # ---------- Assumptions ----------
    ws = wb.active
    ws.title = "Assumptions"
    ws.append(["Metric", "Value", "Unit", "Source", "Notes"])
    style_header(ws, 1, 5)
    named_rows = {}

    def add_row(name, value, unit, source, notes, is_input=True):
        ws.append([name, value, unit, source, notes])
        r = ws.max_row
        if is_input:
            ws.cell(row=r, column=2).fill = ASSUMPTION_FILL
        named_rows[name] = r
        return r

    add_row("USD:INR rate", b[("FX", "USDINR")][0], "rate", b[("FX", "USDINR")][1], b[("FX", "USDINR")][2])
    add_row("AOV — India blended, low", b[("Market", "AOV_india_overall_usd_low")][0], "USD",
            b[("Market", "AOV_india_overall_usd_low")][1], b[("Market", "AOV_india_overall_usd_low")][2])
    add_row("AOV — India blended, high", b[("Market", "AOV_india_overall_usd_high")][0], "USD",
            b[("Market", "AOV_india_overall_usd_high")][1], b[("Market", "AOV_india_overall_usd_high")][2])
    r = ws.max_row + 1
    ws.append(["AOV — India blended (INR, derived)",
               f"=AVERAGE(B{named_rows['AOV — India blended, low']}:B{named_rows['AOV — India blended, high']})*B{named_rows['USD:INR rate']}",
               "INR", "Derived", "= average($/order) x FX rate"])
    named_rows["AOV_INR"] = ws.max_row

    ws.append([])
    ws.append(["-- Display channel --"])
    ws.cell(row=ws.max_row, column=1).font = LABEL_FONT
    add_row("Display CTR", b[("Display", "CTR")][0], "%", b[("Display", "CTR")][1], b[("Display", "CTR")][2])
    add_row("Display CVR", b[("Display", "CVR")][0], "%", b[("Display", "CVR")][1], b[("Display", "CVR")][2])
    add_row("Display CPC — global", b[("Display", "CPC_global_usd")][0], "USD",
            b[("Display", "CPC_global_usd")][1], b[("Display", "CPC_global_usd")][2])
    add_row("India CPC discount — low", b[("Display", "India_CPC_discount_low")][0], "%",
            b[("Display", "India_CPC_discount_low")][1], b[("Display", "India_CPC_discount_low")][2])
    add_row("India CPC discount — high", b[("Display", "India_CPC_discount_high")][0], "%",
            b[("Display", "India_CPC_discount_high")][1], b[("Display", "India_CPC_discount_high")][2])
    ws.append(["Display CPC — India (derived)",
               f"=B{named_rows['Display CPC — global']}*(1-AVERAGE(B{named_rows['India CPC discount — low']}:B{named_rows['India CPC discount — high']})/100)*B{named_rows['USD:INR rate']}",
               "INR", "Derived", "global CPC x (1 - avg India discount) x FX"])
    named_rows["Display_CPC_INR"] = ws.max_row
    ws.append(["Display CPM (derived)",
               f"=B{named_rows['Display_CPC_INR']}*(B{named_rows['Display CTR']}/100)*1000",
               "INR", "Derived", "CPC x CTR_fraction x 1000"])
    named_rows["Display_CPM"] = ws.max_row

    ws.append([])
    ws.append(["-- Shopping / Sponsored channel --"])
    ws.cell(row=ws.max_row, column=1).font = LABEL_FONT
    add_row("Shopping CTR", b[("Shopping", "CTR")][0], "%", b[("Shopping", "CTR")][1], b[("Shopping", "CTR")][2])
    add_row("Shopping CVR", b[("Shopping", "CVR")][0], "%", b[("Shopping", "CVR")][1], b[("Shopping", "CVR")][2])
    add_row("Shopping CPC — India, low", b[("Shopping", "CPC_india_low_inr")][0], "INR",
            b[("Shopping", "CPC_india_low_inr")][1], b[("Shopping", "CPC_india_low_inr")][2])
    add_row("Shopping CPC — India, high", b[("Shopping", "CPC_india_high_inr")][0], "INR",
            b[("Shopping", "CPC_india_high_inr")][1], b[("Shopping", "CPC_india_high_inr")][2])
    ws.append(["Shopping CPC — India (mid, derived)",
               f"=AVERAGE(B{named_rows['Shopping CPC — India, low']}:B{named_rows['Shopping CPC — India, high']})",
               "INR", "Derived", "midpoint of disclosed range"])
    named_rows["Shopping_CPC_INR"] = ws.max_row
    ws.append(["Shopping CPM (derived)",
               f"=B{named_rows['Shopping_CPC_INR']}*(B{named_rows['Shopping CTR']}/100)*1000",
               "INR", "Derived", "CPC x CTR_fraction x 1000"])
    named_rows["Shopping_CPM"] = ws.max_row

    ws.append([])
    ws.append(["-- Campaign assumptions (illustrative — replace before any resume claim) --"])
    ws.cell(row=ws.max_row, column=1).font = LABEL_FONT
    add_row("Fixed campaign cost", b[("Assumption", "fixed_campaign_cost_inr")][0], "INR",
            "ASSUMPTION — not sourced", b[("Assumption", "fixed_campaign_cost_inr")][2])
    add_row("Incrementality haircut (base)", b[("Assumption", "incrementality_haircut_base_pct")][0], "%",
            "ASSUMPTION — not sourced", b[("Assumption", "incrementality_haircut_base_pct")][2])
    add_row("Test spend", 500000, "INR", "Illustrative", "Editable — drives Funnel Model")

    for col, width in zip("ABCDE", [34, 14, 8, 46, 46]):
        ws.column_dimensions[col].width = width

    # ---------- Funnel Model ----------
    fm = wb.create_sheet("Funnel_Model")
    headers = ["Channel", "Spend (INR)", "CPM (INR)", "Impressions", "CTR %", "Clicks",
               "CVR %", "Orders", "AOV (INR)", "Gross Revenue (INR)", "Haircut %",
               "Incremental Revenue (INR)", "Incremental ROAS", "Break-even Spend (INR)"]
    fm.append(headers)
    style_header(fm, 1, len(headers))

    def funnel_row(channel, cpm_ref, ctr_ref, cvr_ref):
        r = fm.max_row + 1
        fm.append([
            channel,
            f"=Assumptions!B{named_rows['Test spend']}",
            f"=Assumptions!B{cpm_ref}",
            f"=B{r}/C{r}*1000",
            f"=Assumptions!B{ctr_ref}",
            f"=D{r}*(E{r}/100)",
            f"=Assumptions!B{cvr_ref}",
            f"=F{r}*(G{r}/100)",
            f"=Assumptions!B{named_rows['AOV_INR']}",
            f"=H{r}*I{r}",
            f"=Assumptions!B{named_rows['Incrementality haircut (base)']}",
            f"=J{r}*(1-K{r}/100)",
            f"=L{r}/B{r}",
            f'=IF(M{r}>1,Assumptions!B{named_rows["Fixed campaign cost"]}/(M{r}-1),"NEVER")',
        ])
        return r

    funnel_row("Display", named_rows["Display_CPM"], named_rows["Display CTR"], named_rows["Display CVR"])
    funnel_row("Shopping", named_rows["Shopping_CPM"], named_rows["Shopping CTR"], named_rows["Shopping CVR"])

    for col, width in zip("ABCDEFGHIJKLMN", [11, 13, 11, 13, 8, 11, 8, 10, 11, 16, 9, 18, 15, 18]):
        fm.column_dimensions[col].width = width

    # ---------- Sensitivity tornado ----------
    sens = wb.create_sheet("Sensitivity")
    sens.append(["Channel", "Lever", "Direction", "Delta %", "Resulting Incremental ROAS", "vs Base ROAS"])
    style_header(sens, 1, 6)

    def sens_row(channel, lever, direction, delta_pct, cpm_ref, ctr_ref, cvr_ref, haircut_ref, base_roas_cell):
        r = sens.max_row + 1
        ctr_formula = f"Assumptions!B{ctr_ref}*(1+{delta_pct}/100)" if lever == "CTR" else f"Assumptions!B{ctr_ref}"
        cvr_formula = f"Assumptions!B{cvr_ref}*(1+{delta_pct}/100)" if lever == "CVR" else f"Assumptions!B{cvr_ref}"
        haircut_formula = f"Assumptions!B{haircut_ref}*(1+{delta_pct}/100)" if lever == "Haircut" else f"Assumptions!B{haircut_ref}"
        spend = f"Assumptions!B{named_rows['Test spend']}"
        impressions = f"({spend}/Assumptions!B{cpm_ref}*1000)"
        clicks = f"({impressions}*({ctr_formula})/100)"
        orders = f"({clicks}*({cvr_formula})/100)"
        gross_rev = f"({orders}*Assumptions!B{named_rows['AOV_INR']})"
        inc_rev = f"({gross_rev}*(1-({haircut_formula})/100))"
        roas = f"({inc_rev}/{spend})"
        sens.append([channel, lever, direction, delta_pct, f"={roas}", f"={roas}-{base_roas_cell}"])
        return r

    for channel, cpm_ref, ctr_ref, cvr_ref, funnel_r in [
        ("Display", named_rows["Display_CPM"], named_rows["Display CTR"], named_rows["Display CVR"], 2),
        ("Shopping", named_rows["Shopping_CPM"], named_rows["Shopping CTR"], named_rows["Shopping CVR"], 3),
    ]:
        base_roas_cell = f"Funnel_Model!M{funnel_r}"
        for lever, ctr_r, cvr_r in [("CTR", ctr_ref, cvr_ref), ("CVR", ctr_ref, cvr_ref)]:
            for direction, delta in [("low", -20), ("high", 20)]:
                sens_row(channel, lever, direction, delta, cpm_ref, ctr_ref, cvr_ref,
                         named_rows["Incrementality haircut (base)"], base_roas_cell)
        for direction, delta in [("low", -20), ("high", 20)]:
            sens_row(channel, "Haircut", direction, delta, cpm_ref, ctr_ref, cvr_ref,
                     named_rows["Incrementality haircut (base)"], base_roas_cell)

    for col, width in zip("ABCDEF", [11, 10, 10, 9, 24, 14]):
        sens.column_dimensions[col].width = width

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT_PATH)
    print(f"Workbook written -> {OUT_PATH}")


if __name__ == "__main__":
    build()
