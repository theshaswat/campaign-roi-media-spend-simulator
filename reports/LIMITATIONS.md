# Limitations

- **CPM is derived, not disclosed.** No source in this project directly publishes a CPM figure for
  either channel; it's computed as `CPC × CTR% × 1000` and should be read as an internally-consistent
  derivation, not an independently-benchmarked number.
- **Two inputs are illustrative assumptions, not sourced figures**: the INR 75,000 fixed campaign
  cost and the 30% incrementality haircut. Replace both with real figures (a rate card, or a real
  holdout-test result) before using this for an actual campaign decision.
- **Benchmarks are national/global averages**, not specific to Tata CLiQ, any single brand, or any
  single product category — real CTR/CVR vary hugely by category and creative quality.
- **Shopping CVR (1.91%) is a global figure**; no India-specific Shopping conversion-rate benchmark
  was found for this build.
- **The funnel is linear** (no diminishing returns as spend scales, no auction-price escalation at
  higher spend) — real campaigns see CPMs rise with scale; this model does not capture that.
- **Nothing here is current by default.** Benchmark rates move; re-read this file and re-check the
  source register before quoting any figure from this project.
