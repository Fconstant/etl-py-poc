# BigQuery & Data Engineering Resources

## Knowledge

- [BigQuery Overview — Google Cloud Docs](https://docs.cloud.google.com/bigquery/docs/introduction)
  Official overview of architecture, storage, compute separation, serverless model. Use for: understanding what BigQuery IS at a foundational level.
- [BigQuery Explained: Architecture — Google Cloud Blog](https://cloud.google.com/blog/products/data-analytics/new-blog-series-bigquery-explained-overview)
  Deep dive into Dremel (compute), Colossus (storage), Jupiter (network). Use for: understanding the internals that make BigQuery fast.
- [Introduction to SQL in BigQuery — Google Cloud Docs](https://cloud.google.com/bigquery/docs/introduction-sql)
  GoogleSQL dialect overview, legacy SQL differences. Use for: SQL syntax reference.
- [BigQuery Pricing — Google Cloud](https://cloud.google.com/bigquery/pricing)
  On-demand vs capacity pricing, free tier, storage costs. Use for: cost modeling and avoiding surprise bills.
- [Estimate and Control Costs — Google Cloud Docs](https://docs.cloud.google.com/bigquery/docs/best-practices-costs)
  Cost optimization strategies: partitioning, clustering, max bytes billed. Use for: writing cost-efficient queries.
- [BigQuery vs Postgres: 2026 Comparison — Yuki](https://yukidata.com/bigquery-vs-postgres/)
  OLTP vs OLAP comparison, row vs column storage explained. Use for: bridging fullstack dev knowledge to data engineering.
- [Load and Query Data — Google Cloud Docs](https://docs.cloud.google.com/bigquery/docs/quickstarts/load-data-console)
  Hands-on quickstart: create dataset, load CSV, query. Use for: first practical exercise.
- [Introduction to Tables — Google Cloud Docs](https://docs.cloud.google.com/bigquery/docs/tables-intro)
  Table types: standard, external, views, materialized views. Use for: understanding BigQuery data model.
- [Polars BigQuery Guide — Polars Docs](https://docs.pola.rs/user-guide/io/bigquery/)
  Reading/writing BigQuery from Polars via `google-cloud-bigquery` + PyArrow. Use for: implementing `to_bigquery()`.
- [Python Client for BigQuery — Google Cloud Docs](https://docs.cloud.google.com/python/docs/reference/bigquery/latest)
  Official Python SDK reference. Use for: `load_table_from_file`, `query`, client configuration.
- [Google BigQuery: The Definitive Guide — Lakshmanan & Tigani](https://www.oreilly.com/library/view/google-bigquery-the/9781492095385/)
  Comprehensive book covering warehousing, analytics, ML at scale. Use for: deep reference when needed.

## Wisdom (Communities)

- [r/dataengineering](https://reddit.com/r/dataengineering)
  Active community, career advice, tool comparisons. Use for: real-world experience, interview prep.
- [BigQuery tag on Stack Overflow](https://stackoverflow.com/questions/tagged/google-bigquery)
  Q&A with real solutions. Use for: troubleshooting specific errors.
- [Google Cloud Community](https://cloud.google.com/community)
  Official forums, tutorials, events. Use for: GCP-specific questions.

## Gaps

- No dedicated BigQuery + Polars integration guide (feature request open: googleapis/google-cloud-python#15710)
- No beginner-friendly BigQuery cost calculator walkthrough
- BigQuery SQL dialect differences from PostgreSQL not well documented in one place
