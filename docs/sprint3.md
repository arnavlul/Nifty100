Days: Day 15–21 | Target Story Points: 49 SP | Epics: Epics 03 & 04 — Screener + Peer Engine

SPRINT GOAL

By end of Sprint 3, the financial screener must be fully functional with 6 preset filters and custom threshold support.

Peer percentile rankings must be computed for all 11 peer groups across 10 metrics. screener_output.xlsx and

peer_comparison.xlsx must be generated and reviewed. All data quality unit tests must pass.

DAILY TASKS

Day 15 — Filter Engine Core

• Write src/screener/engine.py — load screener_config.yaml and apply threshold filters to financial_ratios

DataFrame

• Support all 15 filterable metrics: ROE min, D/E max, FCF min, Revenue CAGR 5yr min, PAT CAGR 5yr min,

OPM min, P/E max, P/B max, Dividend Yield min, ICR min, Market Cap min, Net Profit min, EPS CAGR min, Asset

Turnover min, Sales min

• D/E filter: automatically skip companies in Financials sector when D/E max filter is applied

• ICR filter: treat Debt Free label as ICR = infinity (always passes any ICR minimum threshold)

• Return sorted DataFrame with composite_quality_score column added

Day 16 — 6 Preset Screeners

• Implement Quality Compounder preset: ROE > 15%, D/E < 1.0, FCF > 0, Revenue CAGR 5yr > 10%

• Implement Value Pick preset: P/E < 20, P/B < 3.0, D/E < 2.0, Dividend Yield > 1%

• Implement Growth Accelerator preset: PAT CAGR 5yr > 20%, Revenue CAGR 5yr > 15%, D/E < 2.0

• Implement Dividend Champion preset: Dividend Yield > 2%, Dividend Payout < 80%, FCF > 0

• Implement Debt-Free Blue Chip preset: D/E = 0, ROE > 12%, Revenue > 5000 Crore

• Implement Turnaround Watch preset: Revenue CAGR 3yr > 10%, FCF positive in latest year, D/E declining

year-over-year

• Test each preset on full 92-company universe — verify each returns between 5 and 50 companies and results

make business sense

Day 17 — Composite Score & Export

• Implement composite quality score (0 to 100 scale): 35% Profitability (ROE 15% + ROCE 10% + NPM 10%) +

30% Cash Quality (FCF CAGR 15% + CFO/PAT ratio 10% + FCF positive flag 5%) + 20% Growth (Revenue

CAGR 10% + PAT CAGR 10%) + 15% Leverage (D/E score 10% + ICR score 5%)

• Normalise each metric using P10/P90 winsorisation — cap extreme values at 10th and 90th percentile before

scaling to 0-100

• Compute sector-relative composite score — normalise within each broad_sector so scores reflect performance vs

sector peers

• Generate output/screener_output.xlsx — one sheet per preset with 20 KPI columns, sorted by composite score

descending

• Colour-code cells: green fill for cells meeting the preset threshold, red fill for cells failing the threshold

Day 18 — Peer Percentile Rankings

• Write src/analytics/peer.py — load peer_groups.xlsx and compute PERCENT_RANK for 10 metrics within each

of 11 peer groups

• Metrics to rank: ROE, ROCE, Net Profit Margin, D/E (inverse — lower is better), FCF, PAT CAGR 5yr, Revenue

CAGR 5yr, EPS CAGR 5yr, Interest Coverage, Asset Turnover

• For D/E ranking: invert the percentile (1 - PERCENT_RANK) so that lower D/E = higher percentile rank

• Populate peer_percentiles table in SQLite with columns: company_id, peer_group_name, metric, value,

percentile_rank, year

• For companies not in any peer group: return message No peer group assigned — do not raise an error


Day 19 — Radar Charts

• Generate radar/polar chart for each company in a peer group — 8 axes: ROE, ROCE, NPM, D/E, FCF score,

PAT CAGR 5yr, Revenue CAGR 5yr, Composite Score

• Each chart shows: the company's values as a filled polygon, peer group average as a dashed outline overlay

• Export as PNG to reports/radar_charts/ — filename format: _radar.png

• For companies with no peer group: generate a single-metric standalone chart with Nifty 100 average as reference

• Use matplotlib polar plot or plotly radar chart — ensure font size is readable at standard viewing size

Day 20 — Peer Comparison Excel Report

• Generate output/peer_comparison.xlsx with 11 sheets — one per peer group

• Each sheet columns: company_id, company_name, + 20 metric columns, + percentile rank for each metric

• Colour-code percentile rank cells: green fill for >= 75th percentile, yellow for 25th to 75th, red for <= 25th

percentile

• Highlight benchmark company row in each sheet with a gold/amber background

• Add a summary row at the bottom showing peer group median for each metric

Day 21 — Tests & Sprint Review

• Run all 14 DQ rule unit tests — must pass with 0 failures

• Verify screener: Quality Compounder preset returns companies with ROE > 15% and D/E < 1 — manually verify

top 5 results

• Verify peer rankings: within IT Services peer group, the company with highest ROE should have the highest ROE

percentile rank

• Sprint 3 retrospective

• Demo screener_output.xlsx and peer_comparison.xlsx to team lead

DELIVERABLES

• output/screener_output.xlsx — 6 sheets, one per preset, colour-coded cells

• output/peer_comparison.xlsx — 11 sheets, one per peer group, percentile colour-coded

• reports/radar_charts/ — PNG radar chart for each company with peer group overlay

• peer_percentiles table in SQLite — percentile ranks for all 11 groups

• config/screener_config.yaml — all threshold definitions, analyst-editable

• src/screener/engine.py — filter engine and composite score

• src/analytics/peer.py — peer percentile computation

EXIT CRITERIA (Definition of Done)

• 6 preset screeners each return between 5 and 50 companies

• peer_comparison.xlsx has exactly 11 sheets covering all 11 peer groups

• Peer percentile ranks are correct — verified by spot-checking IT Services and FMCG groups

• All 14 DQ rule unit tests pass

• Sprint 3 review meeting completed and signed off by team lead