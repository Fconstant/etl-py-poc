# Teaching Notes

## User Preferences
- Fullstack dev background — bridge from Postgres mental model
- Wants to understand BigQuery before implementing (not just "how to call the API")
- ADRs already exist with concrete schema decisions — use those as teaching hooks
- Learning alongside implementation, not separate study period
- Budget-conscious — emphasize free tier and cost control

## Session Log
- 2026-07-19: First session. Set up workspace. Created Lesson 001 (What Is BigQuery?). User hasn't interacted yet — waiting for first response.
- 2026-07-19: Created Lesson 002 (GoogleSQL Basics). User feedback: not interested in GoogleSQL syntax deep-dives, wants platform capabilities that make them sound like an expert. Adjusted lesson plan.
- 2026-07-19: Created Lesson 003 (BigQuery Core Capabilities) — pricing, table types, partitioning, materialized views, federated queries, ecosystem, security. Trimmed to 7 focused sections per user request.
- 2026-07-19: Created Lesson 004 (Python Client & Loading Data) — ADC auth, Polars→Arrow→BigQuery flow, write dispositions, schema mapping, to_bigquery() function, error handling. Ties directly to ADR-001/002.
- 2026-07-19: Moved all learning files into `learning/` subfolder. Updated skill instructions.
