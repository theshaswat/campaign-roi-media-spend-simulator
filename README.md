# Campaign ROI & Media Spend Simulator

**Status: Phase 1–4 complete.** Data sourced, model + Excel workbook built and cross-validated,
reports written and available as both Markdown and PDF
(`reports/00_EXECUTIVE_SUMMARY`, `01_RECOMMENDATION_MEMO`, `02_DATA_DICTIONARY`,
`03_SOURCE_REGISTER`, `LIMITATIONS`), dashboard built (`dashboards/dashboard.html`). Resume-ready
line is in `reports/00_EXECUTIVE_SUMMARY.pdf`.

## What this is

A break-even spend and ROAS simulator for Display vs. Shopping/Sponsored campaigns, built from
published 2026 ad-tech benchmarks rather than invented assumptions — the funnel a retail-media
team runs before greenlighting a campaign: Spend → Impressions → Clicks → Orders → Revenue →
Incremental ROAS → break-even spend.

## Headline finding

**At current India-benchmark assumptions, Display campaigns don't clear break-even; Shopping/Sponsored
campaigns clear it easily.** Incremental ROAS: Display 0.94x (below 1 — never recovers a fixed
campaign cost, at any spend level), Shopping 4.29x (recovers a ₹75,000 illustrative fixed cost at
just ~₹22,800 of spend). This isn't a modeling failure — it reflects the real, sourced gap between
low-intent display CTR/CVR and high-intent shopping/search CTR/CVR. **This is the kind of honest
null result the house standard treats as a finding, not a problem to hide.**

## Data — every number sourced or clearly labelled as an assumption

`data/raw/ad_benchmarks.csv` — CTR, CVR, CPC figures from WebFX's 2026 Google Ads Benchmarks
(global) and OwlClaw's PPC Benchmarks India 2026 (India-specific search/shopping CPC and CTR);
AOV from a 2026 order-level analysis (Social Samosa/Whalesbook); USD:INR from the Fed's H.10
release. **CPM is not directly disclosed anywhere — it's derived as `CPC × CTR% × 1000`, shown as
a formula, not asserted as a benchmark.** Two inputs are explicitly unsourced illustrative
assumptions (fixed campaign cost ₹75,000; incrementality haircut 30%) and are flagged
`assumption_illustrative` in the source file — replace both with real client/category figures
before any resume claim.

## How it works

1. `src/campaign_model.py` — pure-Python funnel, break-even solver, sensitivity tornado. Run it
   directly to see console output.
2. `src/build_excel_model.py` — builds `excel_model/Campaign_ROI_Simulator.xlsx` with **every cell
   a live formula referencing the Assumptions sheet**, not a pasted value — same discipline as the
   9-tab/227-formula models elsewhere in the portfolio.
3. **Cross-validated**: the Excel workbook was recalculated headlessly (LibreOffice) and its output
   compared line-for-line against the independent Python model. Both agree to the cent (Display ROAS
   0.9430x both ways, Shopping ROAS 4.2908x both ways) — two independent implementations of the same
   logic, reconciled.

## What I learned

CTR and CVR sensitivity produce *identical* ROAS deltas (±0.1886 for a ±20% move in either) — not a
bug. The funnel is multiplicatively linear in both, so a proportional change in either lever moves
revenue by the same proportion. Worth saying plainly in an interview: in this model shape, "which
lever matters more" isn't a modelling question, it's whichever lever is operationally cheaper to
move in a real campaign.

## Reports (Phase 3–4)

`reports/00_EXECUTIVE_SUMMARY.{md,pdf}`, `01_RECOMMENDATION_MEMO.{md,pdf}`,
`02_DATA_DICTIONARY.{md,pdf}`, `03_SOURCE_REGISTER.{md,pdf}`, `LIMITATIONS.{md,pdf}`. Dashboard:
`dashboards/dashboard.html` (Display vs. Shopping incremental ROAS against the break-even line).

## Not done

Replace the two illustrative assumptions (fixed campaign cost, incrementality haircut) with sourced
figures if a real client brief becomes available — see `reports/LIMITATIONS.pdf`.

## Author

**Shaswat Sharma** — [GitHub: theshaswat](https://github.com/theshaswat)

## License

MIT (see [`LICENSE`](LICENSE)).
