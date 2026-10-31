-- Q1.1 | Data type of all columns in the customers table
-- Section : 1. Initial exploration: structure & characteristics
-- Question: Data type of all columns in the "customers" table.
-- Dialect : BigQuery Standard SQL (dataset `target`)

SELECT
  column_name,
  data_type
FROM target.INFORMATION_SCHEMA.COLUMNS
WHERE table_name = 'customers'
ORDER BY ordinal_position;
