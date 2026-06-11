--  THE FOLLOWING CODE IS FROM SNOWFLAKE CLOUD PLATFORM. IT WAS WORKING THERE BUT HAS NOT TESTED HERE
-- Create Audit table
CREATE OR REPLACE TABLE audit_schema.audit_table(
    process_name STRING,
    process_time TIMESTAMP,
    rows_processed NUMBER
)
-- We need to incorporate it into Procedures sequal
SELECT *
FROM audit_schema.audit_table
ORDER BY process_time DESC;
