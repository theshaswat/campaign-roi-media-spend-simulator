# Campaign ROI & Media Spend Simulator — Recommendation Memo

## Why this project

Built for the Tata CLiQ Monetization Intern application, whose two stated goals are optimizing
revenue streams and improving advertiser ROI — measured on pitch conversion, new revenue, and
campaign renewals. This is, literally, the tool a retail-media team runs before greenlighting spend:
at what point does a campaign clear its own cost.

## Methodology

1. **Benchmark sourcing** (`data/raw/ad_benchmarks.csv`) — CTR, CVR, CPC from WebFX's 2026 Google
   Ads Benchmarks (global) and OwlClaw's PPC Benchmarks India 2026 (India-specific search/shopping
   figures); India blended AOV from a 2026 order-level analysis; USD:INR from the Fed's H.10 release.
2. **CPM derivation** — not directly disclosed by any source, so derived as `CPC × CTR% × 1000` and
   shown as a formula in both the Python model and the Excel workbook, never asserted as a benchmark.
3. **Funnel** — Spend → Impressions → Clicks (CTR) → Orders (CVR) → Gross Revenue (AOV) →
   Incremental Revenue (haircut) → Incremental ROAS.
4. **Break-even solver** — `fixed_cost / (incremental_ROAS - 1)` when ROAS > 1; explicitly returns
   "NEVER" when ROAS ≤ 1, rather than a misleading negative or infinite number.
5. **Sensitivity tornado** — CTR, CVR, and incrementality haircut each moved ±20%, the three
   assumptions most likely to move a real decision.

## Results

At INR 500,000 test spend: Display returns 0.9430x incremental ROAS (never breaks even at any spend
level under these assumptions); Shopping/Sponsored returns 4.2908x (breaks even at just INR 22,791 of
spend, derived from full-precision ROAS — matches the Excel workbook's live-formula result exactly).
Full sensitivity table: `outputs/tables/funnel_and_sensitivity.csv`.

## What I learned

CTR and CVR sensitivity produce *identical* ROAS deltas (±0.1886 for a ±20% move in either lever) —
not a bug, but a direct consequence of the funnel being multiplicatively linear in both. Worth
stating plainly in an interview: in this model shape, which lever "matters more" isn't a modelling
question — it's whichever lever is operationally cheaper to move in a real campaign (creative/targeting
for CTR vs. landing-page/offer for CVR).

## Cross-validation

The Excel workbook (`excel_model/Campaign_ROI_Simulator.xlsx`) mirrors the Python model's logic as
live formulas referencing an Assumptions sheet — no pasted values anywhere in Funnel_Model or
Sensitivity. Recalculated headlessly via LibreOffice and compared line-for-line against the Python
output: both agree to the cent (Display 0.9430x, Shopping 4.2908x). This is the same
build-two-independent-paths-and-reconcile discipline used elsewhere in the portfolio.

## Limitations

See `LIMITATIONS.md`. In short: CPM is derived, not disclosed; fixed cost and incrementality
haircut are stated illustrative assumptions; benchmarks are national/global averages, not
category-specific or Tata-CLiQ-specific.

## What this demonstrates for the role

Direct evidence of the exact analytical tool the JD describes — a break-even/ROAS model built to
Excel-fluency standard (live formulas, not pasted values) — plus the honesty to report a channel that
doesn't work under real assumptions rather than only showing the flattering number.
