--  THE FOLLOWING CODE IS FROM SNOWFLAKE CLOUD PLATFORM. IT WAS WORKING THERE BUT HAS NOT TESTED HERE
-- Create procedure with 3 dimension and 1 fact tables. Populate them
CREATE OR REPLACE PROCEDURE load_schema.load_data_procedure()
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    row_count NUMBER;
BEGIN

    -- Create Passendger dimension table. Need to create a surrogate key
    CREATE OR REPLACE TABLE load_schema.dimension_passenger (
        passenger_key NUMBER IDENTITY(1,1),
        passenger_id STRING,
        first_name STRING,
        last_name STRING,
        gender STRING,
        age INTEGER,
        nationality STRING
    );
    INSERT INTO load_schema.dimension_passenger (
        passenger_id,
        first_name,
        last_name,
        gender,
        age,
        nationality
    )
    SELECT DISTINCT
        passenger_id,
        first_name,
        last_name,
        gender,
        age,
        nationality
    FROM transform_schema.transform_data;
    
    -- Create Airport dimension table. Need a surrogate key
    CREATE OR REPLACE TABLE load_schema.dimension_airport (
        airport_key NUMBER IDENTITY(1,1),
        airport_name STRING,
        airport_country_code STRING,
        country_name STRING,
        airport_continent STRING
    );
    INSERT INTO load_schema.dimension_airport (
        airport_name,
        airport_country_code,
        country_name,
        airport_continent
    )
    SELECT DISTINCT
        airport_name,
        airport_country_code,
        country_name,
        airport_continent
    FROM transform_schema.transform_data;
    
    -- Create Travel supplementary table
    CREATE OR REPLACE TABLE load_schema.dimension_travel (
        travel_key NUMBER IDENTITY(1,1),
        departure_date DATE,
        arrival_airport STRING,
        flight_status STRING,
        ticket_type STRING,
        passenger_status STRING
    );
    INSERT INTO load_schema.dimension_travel (
        departure_date,
        arrival_airport,
        flight_status,
        ticket_type,
        passenger_status
    )
    SELECT DISTINCT
        departure_date,
        arrival_airport,
        flight_status,
        ticket_type,
        passenger_status
    FROM transform_schema.transform_data;
    
    -- Create Fact Table and isert data
    CREATE OR REPLACE TABLE load_schema.fact_table_airline (
        flight_fact_key NUMBER IDENTITY(1,1),
        passenger_key NUMBER,
        airport_key NUMBER,
        travel_key NUMBER
    );
    
    INSERT INTO load_schema.fact_table_airline (
        passenger_key,
        airport_key,
        travel_key
    )
    SELECT
        p.passenger_key,
        a.airport_key,
        t.travel_key
    FROM transform_schema.transform_data td
    JOIN load_schema.dimension_passenger p
        ON td.passenger_id = p.passenger_id
    JOIN load_schema.dimension_airport a
        ON td.airport_name = a.airport_name
       AND td.airport_country_code = a.airport_country_code
    JOIN load_schema.dimension_travel t
        ON td.departure_date = t.departure_date
       AND td.arrival_airport = t.arrival_airport
       AND td.flight_status = t.flight_status
       AND td.ticket_type = t.ticket_type
       AND td.passenger_status = t.passenger_status;

    row_count := (
    SELECT COUNT(*)
    FROM load_schema.fact_table_airline
    );

    INSERT INTO audit_schema.audit_table
    VALUES (
        'TRANSFORM_PROCESS_LOADING',
        CURRENT_TIMESTAMP(),
        row_count
    );
    
    RETURN 'Loaded data successfully';

END;
$$;

CALL load_schema.load_data_procedure();

SELECT *
FROM load_schema.fact_table_airline
LIMIT 5;

-- Create Secure View on Fact table
CREATE SECURE VIEW load_schema.fact_table_secure AS
SELECT
    passenger_key,
    airport_key,
    travel_key
FROM load_schema.fact_table_airline


-- Then create Row Level Security for PUBLIC role access (under 10000) and restrictions to other roles
CREATE OR REPLACE ROW ACCESS POLICY load_schema.fact_table_rls 
AS (passenger_key NUMBER) RETURNS BOOLEAN ->
CASE
    WHEN 'ACCOUNTADMIN' = CURRENT_ROLE() THEN TRUE
    WHEN passenger_key <= 10000 AND 'PUBLIC' = CURRENT_ROLE() THEN TRUE
    ELSE FALSE
END;

-- Apply Row Level Security to the Secure View
ALTER VIEW load_schema.fact_table_secure ADD ROW ACCESS POLICY load_schema.fact_table_rls ON (passenger_key);

-- USE ROLE PUBLIC; For testing

SELECT MAX(passenger_key)
FROM load_schema.fact_table_secure;

