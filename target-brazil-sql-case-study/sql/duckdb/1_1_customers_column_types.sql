-- Q1.1 | Data type of all columns in the customers table
-- Section : 1. Initial exploration: structure & characteristics
-- Question: Data type of all columns in the "customers" table.
-- Dialect : DuckDB (schema `target`, see scripts/build_db.py)

SELECT
  column_name,
  data_type
FROM information_schema.columns
WHERE table_schema = 'target' AND table_name = 'customers'
ORDER BY ordinal_position;
