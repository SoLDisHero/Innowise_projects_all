--  THE FOLLOWING CODE IS FROM SNOWFLAKE CLOUD PLATFORM. IT WAS WORKING THERE BUT HAS NOT TESTED HERE
-- Create a database
CREATE OR REPLACE DATABASE airline_db;
-- Create schemas
CREATE SCHEMA extract_schema;
CREATE SCHEMA transform_schema;
CREATE SCHEMA load_schema;
CREATE SCHEMA audit_schema;
-- Check the results
SELECT CURRENT_DATABASE(), CURRENT_SCHEMA();
-- 
CREATE OR REPLACE TABLE extract_schema.raw_data(
    passenger_id STRING,
    first_name STRING,
    last_name STRING,
    gender STRING,
    age INTEGER,
    nationality STRING,
    airport_name STRING,
    airport_country_code STRING,
    country_name STRING,
    airport_continent STRING,
    continents STRING,
    departure_date DATE,
    arrival_airport STRING,
    pilot_name STRING,
    flight_status STRING,
    ticket_type STRING,
    passenger_status STRING
);
SHOW TABLES IN SCHEMA airline_db.extract_schema;
-- Create a warehouse
CREATE OR REPLACE WAREHOUSE airflow_whs WITH
    WAREHOUSE_SIZE='X-SMALL'
    AUTO_SUSPEND=180
    AUTO_RESUME=TRUE
    INITIALLY_SUSPENDED=TRUE;

-- Retrieve the name of the warehouse
SELECT CURRENT_WAREHOUSE()

-- Upload files csv files to the table. Needs to be run in Snowsql
PUT file://S:\SoLD\Internship\Snowflake\include\datasets\Airline_Dataset_new.csv @airline_db.extract_schema.%raw_data;

-- Listing the staged files
LIST @airline_db.extract_schema.%raw_data

-- Load data into the tables
COPY INTO extract_schema.raw_data
    FROM @%raw_data
    FILE_FORMAT = (type = csv, skip_header=1, field_optionally_enclosed_by='"')
    ON_ERROR = 'skip_file';

-- Check the data
SELECT * 
FROM extract_schema.raw_data
LIMIT 5;

-- Create Stream
CREATE OR REPLACE STREAM raw_data_stream
ON TABLE extract_schema.raw_data;

SELECT *
FROM raw_data_stream
LIMIT 10;

-- Using time-travel features for DDL and DML
-- Example
DELETE FROM extract_schema.raw_data
WHERE flight_status = 'On Time';

SELECT COUNT(*)
FROM extract_schema.raw_data;

SELECT COUNT(*)
FROM extract_schema.raw_data
AT(OFFSET => -60*5);

-- Example
CREATE OR REPLACE TABLE extract_schema.raw_data_new AS
SELECT *
FROM extract_schema.raw_data
AT(OFFSET => -60*10);

-- Example
DROP TABLE extract_schema.raw_data_new;
UNDROP TABLE extract_schema.raw_data_new;

-- Example
ALTER TABLE extract_schema.raw_data_new
RENAME COLUMN ticket_type TO ticket_test;

SELECT *
FROM extract_schema.raw_data_new
AT(OFFSET => -60);
