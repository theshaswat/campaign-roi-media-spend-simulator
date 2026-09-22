# Campaign ROI & Media Spend Simulator — Where Display Stops Paying

> The funnel a retail-media team runs before greenlighting a campaign — spend through
> impressions, clicks, orders and revenue to incremental ROAS and break-even spend —
> built from published 2026 ad-tech benchmarks rather than assumed rates. At those
> benchmarks Display never clears break-even at any spend level, and Shopping/Sponsored
> clears it at roughly ₹22,800.

## Question

At sourced India market benchmarks rather than invented ones, what spend does a campaign
need before it recovers its fixed cost, and does the answer differ enough by channel to
change where budget goes?

## Findings

At ₹500,000 test spend, on sourced India-benchmark assumptions:

| Channel | Derived CPM | CTR | CVR | Incremental ROAS | Break-even spend |
|---|---|---|---|---|---|
| Display | ₹62.5 | 0.46% | 0.57% | **0.94x** | **Never** — ROAS below 1 at any spend |
| Shopping / Sponsored | ₹575 | 5.75% | 1.91% | **4.29x** | **₹22,791** |

A channel returning less than 1.0x incremental ROAS does not have a high break-even
point — it has no break-even point at all, because every additional rupee of spend widens
the loss rather than amortising the fixed cost. That is the substantive difference between
the two rows, and it is a property of the sourced click-through and conversion rates, not
of the model: low-intent display inventory converts far below high-intent shopping and
search inventory, and the gap is wide enough to cross the line where scale stops helping.

**CTR and CVR produce identical ROAS deltas** — ±0.1886 for a ±20% move in either lever on
Display, ±0.8582 on Shopping. This is not a bug. The funnel is multiplicatively linear in
both, so a proportional change in either moves revenue by the same proportion. The
practical consequence is that "which lever matters more" is not a modelling question in
this funnel shape; it is a question of which lever is cheaper to move in a live campaign.

Full reasoning: [`reports/01_RECOMMENDATION_MEMO.md`](reports/01_RECOMMENDATION_MEMO.md).
One-page version: [`reports/00_EXECUTIVE_SUMMARY.md`](reports/00_EXECUTIVE_SUMMARY.md).

## Method

- Built the funnel as spend → impressions → clicks → orders → revenue → incremental ROAS,
  with a break-even solver and a sensitivity tornado over each lever
- Sourced CTR, CVR and CPC from published 2026 benchmarks rather than assuming them, and
  kept the India-specific and global figures distinguishable in the source file
- **Derived CPM rather than asserting it.** No source discloses CPM directly, so it is
  computed as `CPC × CTR% × 1000` and presented as a formula, not as a benchmark
- Flagged the two inputs that are not sourced — fixed campaign cost and incrementality
  haircut — as illustrative in the data file itself, so the distinction survives outside
  the prose
- Tested each lever at ±20% and recorded the deltas rather than reporting a single
  point estimate

## Cross-validation

The Python model (`src/campaign_model.py`) and the live-formula Excel workbook
(`excel_model/Campaign_ROI_Simulator.xlsx`) were built independently from the same source
data. The workbook was then recalculated headlessly under LibreOffice and compared
line-for-line against the Python output. Both agree to the cent — 0.9430x and 4.2908x
under each implementation.

Every cell in the workbook is a live formula referencing the Assumptions sheet, not a
pasted value, so changing an input propagates through the model rather than silently
disagreeing with it.

## Data and sources

`data/raw/ad_benchmarks.csv` — every figure carries its source:

| Input | Source |
|---|---|
| CTR, CVR, CPC (global) | WebFX, 2026 Google Ads Benchmarks |
| Search/Shopping CPC and CTR (India) | OwlClaw, PPC Benchmarks India 2026 |
| Average order value | 2026 order-level analysis (Social Samosa / Whalesbook) |
| USD:INR | US Federal Reserve H.10 release |
| CPM | Derived — `CPC × CTR% × 1000`, not disclosed by any source |
| Fixed campaign cost (₹75,000) | Illustrative assumption, flagged in source file |
| Incrementality haircut (30%) | Illustrative assumption, flagged in source file |

Full register: [`reports/03_SOURCE_REGISTER.md`](reports/03_SOURCE_REGISTER.md).
Field definitions: [`reports/02_DATA_DICTIONARY.md`](reports/02_DATA_DICTIONARY.md).

## Structure

```
campaign-roi-media-spend-simulator/
├── data/raw/              # ad_benchmarks.csv — every input with its source
├── src/
│   ├── campaign_model.py      # funnel, break-even solver, sensitivity tornado
│   ├── build_excel_model.py   # builds the live-formula workbook
│   └── build_pdf.py           # renders reports/*.md to PDF
├── excel_model/           # Campaign_ROI_Simulator.xlsx
├── outputs/tables/        # funnel_and_sensitivity.csv
├── dashboards/            # dashboard.html — ROAS against the break-even line
└── reports/               # executive summary, memo, data dictionary,
                           # source register, limitations (.md + .pdf)
```

## How to run

```bash
pip install -r requirements.txt
cd src
python3 campaign_model.py      # funnel + break-even + sensitivity, to console and CSV
python3 build_excel_model.py   # -> excel_model/Campaign_ROI_Simulator.xlsx
python3 build_pdf.py           # -> reports/*.pdf
```

## Limitations

Full detail in [`reports/LIMITATIONS.md`](reports/LIMITATIONS.md). Headline items:

- **Not built against any real campaign data.** The benchmarks are published market
  averages, not one advertiser's observed performance.
- **CPM is derived, not disclosed.** No source in the register publishes CPM directly.
- **Two inputs are illustrative, not sourced** — the ₹75,000 fixed campaign cost and the
  30% incrementality haircut. Both should be replaced with real category or client figures
  before the break-even numbers are used for an actual spend decision.
- Benchmarks blend global and India-specific sources where no India figure was published
  for a given metric; the source file records which is which.

## Author

**Shaswat Sharma** — [GitHub: theshaswat](https://github.com/theshaswat)

## License

MIT (see [`LICENSE`](LICENSE)).
