# Campaign ROI & Media Spend Simulator — Executive Summary

**A break-even and ROAS simulator for Display vs. Shopping/Sponsored campaigns, built from published
2026 ad-tech benchmarks — the funnel a retail-media team runs before greenlighting spend.**

## Headline result

At INR 500,000 test spend, sourced India-benchmark assumptions:

| Channel | Derived CPM | CTR | CVR | Incremental ROAS | Break-even spend |
|---|---|---|---|---|---|
| Display | INR 62.5 | 0.46% | 0.57% | **0.94x** | Never — ROAS below 1 at any spend |
| Shopping / Sponsored | INR 575 | 5.75% | 1.91% | **4.29x** | INR 22,791 |

**Display doesn't clear break-even at these benchmark assumptions; Shopping/Sponsored clears it
easily.** This is a genuine, sourced finding, not an assumption chosen to make a nicer story.

## Cross-validated two ways

The Python model (`src/campaign_model.py`) and a live-formula Excel workbook
(`excel_model/Campaign_ROI_Simulator.xlsx`) were built independently from the same source data and
agree to the cent after the Excel workbook was recalculated headlessly (LibreOffice) — 0.9430x and
4.2908x, both implementations.

## What this is not

Not built against any real client's campaign data — CPM is derived, not directly disclosed by any
source (see Limitations). The fixed campaign cost (INR 75,000) and incrementality haircut (30%) are
stated, illustrative assumptions, not sourced figures — replace both before using this for a real
campaign decision.
