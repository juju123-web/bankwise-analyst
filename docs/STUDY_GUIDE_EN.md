# Bankwise study guide

Use the working project first, then learn to explain, modify, and verify it. Progress by the completion criteria below, not a fixed number of days. The Chinese guide remains available as `STUDY_GUIDE.md`.

## 1. Explore the product

Run overall conversion, channel comparison, job ranking, and an unsupported revenue question. Expand the SQL and execution trace. Download a result.

The guided demo executes fixed SQL without a model. Live mode asks the configured model to produce a plan, validates SQL, and executes it. These modes are labeled separately. Changing the interface language does not call the model; new live explanations follow the selected language.

**Completion:** Explain the business problem, the dataset, and the two modes in 90 seconds.

## 2. Understand data grain before SQL

Read `docs/DATA_CARD_EN.md` and `bankwise/data.py`.

41,188 observations are not necessarily 41,188 customers. An artificial row ID cannot recover customer identity. Overall conversion is 4,640 / 41,188, approximately 11.27%. `unknown` is a category rather than SQL NULL. `pdays=999` is a sentinel. A month without a year is not a complete date. Call duration becomes available only after contact.

ETL reads the nested source ZIP, converts types, renames columns, derives the binary outcome, validates counts, and atomically replaces a staging database. The manifest supports traceability.

**Exercise:** Identify three incorrect cleaning choices that could distort conclusions. Explain why identical feature values do not justify deleting observations as duplicate customers.

**Completion:** Explain observation IDs, unknown categories, sentinel values, pooled months, and prediction leakage without notes.

## 3. Learn SQL from the catalog

Read `bankwise/catalog.py` and practice in the SQL workbench.

```sql
SELECT job, COUNT(*) AS observations,
       SUM(subscribed) AS subscriptions,
       ROUND(100.0 * AVG(subscribed), 4) AS conversion_pct
FROM bank_contacts
GROUP BY job
HAVING COUNT(*) >= 100
ORDER BY conversion_pct DESC, job;
```

The average of a 0/1 variable is its positive fraction. WHERE filters observations before grouping; HAVING filters groups afterward. Filtering to `subscribed=1` before calculating conversion would destroy the denominator and produce 100%.

Study CASE for age/frequency buckets and the `rank` query for CTEs and ROW_NUMBER. PARTITION BY ranks jobs separately within each channel. A secondary job sort makes ties deterministic. There is no invented customer table solely to demonstrate JOINs; practice joins separately until real relational data is introduced.

**Exercise:** Compare cellular conversion by education, exclude unknown education, and require at least 200 observations.

**Completion:** Write the query independently and explain the denominator, grouping, sample threshold, and ordering.

## 4. Use Python to verify findings

Read `bankwise/insights.py`, `bankwise/evaluate.py`, and `summarize()` in `agent.py`.

The evaluation oracle reads CSV and computes reference values independently of SQL templates. Repeating the same SQL would not be an independent check. Both implementations can still share a business misunderstanding, so metric definitions need review.

Compare `wilson(1,2)` and `wilson(500,1000)`: both point estimates are 50%, but uncertainty differs. Wilson intervals assume independent observations and do not correct selection bias, confounding, repeated customers, or multiple comparisons. The highest observed rate is not automatically the most reliable or commercially attractive segment.

**Completion:** Explain the difference between a high rate, statistical precision, and a sound budget decision.

## 5. Trace the bounded agent

Read `analyze()` and `OpenAIPlanner` in `bankwise/agent.py`.

The workflow validates the question, inspects schema, obtains a query/refusal/clarification plan, validates and executes SQL, then computes a summary. An invalid plan or query gets at most one repair attempt. Provider errors stop the request rather than substituting a demo answer.

Injecting the planner as a parameter lets tests simulate a failed query followed by a repair. This verifies orchestration without paid API calls, but does not measure real-model accuracy. The model sees the schema and question, not database rows; result summaries are generated locally.

**Exercise:** Trace `test_repair` in `tests/test_core.py`. Record the first error, repair input, and final result.

**Completion:** Draw the control flow and distinguish syntax failure, provider failure, and a valid query with incorrect business semantics.

## 6. Explain execution protection

Read `bankwise/sql.py` and its tests. AST validation restricts syntax and tables. SQLite opens read-only and uses an authorizer for operations/functions. A progress handler bounds VM work and elapsed time. Output is capped at 200 rows with a truncation warning.

A prompt asking the model to be careful is not an access control. LIMIT alone does not bound the work of an expensive aggregate. Read-only protection does not guarantee correct metric definitions. The application does not execute generated Python.

**Completion:** Explain what each protection layer addresses, and what it cannot guarantee.

## 7. Make an independent improvement

Add a question comparing previously contacted and never-contacted observations, using `pdays=999` as the definition. Return observation counts, subscriptions, and conversion. Add an English question in `i18n.py`, a catalog entry, and an independent CSV oracle result. Run tests and evaluation.

Verify that group sizes sum to 41,188 and subscriptions sum to 4,640. Explain why averaging group rates without weights usually differs from the overall rate. Do not claim previous contact causes conversion.

**Completion:** Implement and debug the change yourself, then commit it. Consult the Chinese `EXERCISE_HINTS.md` only after attempting it independently.

## 8. Present the project honestly

Demonstrate a question, SQL, verified numbers, a data limitation, and execution controls in three minutes. Explain AI assistance honestly and show your own independent modification. The fixed demo benchmark, mocked planner tests, and live-model smoke tests establish different things; never combine them into a claim of 100% natural-language accuracy.

**Final self-check:** Start the app, write a grouped query, explain a window function, identify four data limitations, trace repair, explain read-only controls, add an evaluated question, and describe remaining gaps.

## Troubleshooting

| Symptom | First check |
|---|---|
| Missing Python module | Use the same virtual-environment interpreter for installation and execution. |
| Missing database | Run `python -m bankwise.data` from the project root. |
| Unknown SQL column | Inspect the schema; periods in source column names became underscores. |
| Access code rejected | Enter the owner's model access code, not the API key. |
| API quota error | Check the API organization's credits and limits. Work/Codex credits are separate. |
| Query runs but looks wrong | Review grain, denominator, filters, and grouping before trusting it. |
