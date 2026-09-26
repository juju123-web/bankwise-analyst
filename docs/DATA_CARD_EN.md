**Source:** [UCI Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing), `bank-additional-full.csv`, 41,188 observations. Authors: S. Moro, P. Rita, P. Cortez. License: CC BY 4.0. The ingestion manifest records provenance and SHA-256 checksums.

**Grain and metric:** One row is a source marketing observation, not necessarily a unique customer. `subscribed=1` corresponds to `y=yes`. Conversion is subscribed observations divided by all observations within the query scope. `observation_id` is a generated row number, not a customer identifier.

| Fields | Meaning and interpretation |
|---|---|
| age, job, marital, education | Demographic categories. Keep `unknown` as a distinct category. |
| default, housing, loan | Reported credit default and loan status. This project does not make credit eligibility decisions. |
| contact | Contact channel: cellular or telephone. |
| month, day_of_week | Month and weekday of the last contact. Per-row years and exact dates are unavailable. |
| duration | Last call duration in seconds, known after the call. Using it for pre-contact prediction would introduce leakage. |
| campaign | Number of contacts during this campaign, including the last contact. |
| pdays | Days since a previous campaign contact; 999 means not previously contacted, not a literal duration. |
| previous, poutcome | Previous campaign contact count and outcome. |
| emp_var_rate, cons_price_idx, cons_conf_idx, euribor3m, nr_employed | Source macroeconomic indicators; periods in column names were replaced with underscores. |
| y, subscribed | Original yes/no subscription outcome and its derived 0/1 representation. |

**Unsupported questions:** Revenue, profit, ROI, unique-customer retention, reliable year/month changes, and causal effects. Monthly grouping pools years; it is not a consecutive time series. Historical Portuguese bank observations do not represent today's Chinese fintech market.

**Cleaning decisions:** Preserve all source observations. Matching feature combinations are not sufficient evidence of duplicate customers. Cast numeric fields explicitly, retain unknown categories, and validate 41,188 rows and 4,640 positive outcomes. No synthetic business facts are added.

**Business use:** Segment differences can inform hypotheses for further investigation. They do not establish that changing a channel will improve conversion.
