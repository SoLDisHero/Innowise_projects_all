--  THE FOLLOWING CODE IS FROM SNOWFLAKE CLOUD PLATFORM. IT WAS WORKING THERE BUT HAS NOT TESTED HERE
-- Create Procedure for creating table and then loading date from Stage 1 (Raw) to Stage 2 (Transform)
CREATE OR REPLACE PROCEDURE transform_schema.transform_to_procedure()
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    row_count NUMBER;
BEGIN

    CREATE OR REPLACE TABLE transform_schema.transform_data AS
    SELECT
        passenger_id,
        UPPER(first_name) AS first_name,
        UPPER(last_name) AS last_name,
        gender,
        age,
        nationality,
        airport_name,
        airport_country_code,
        country_name,
        airport_continent,
        continents,
        departure_date,
        arrival_airport,
        pilot_name,
        flight_status,
        ticket_type,
        passenger_status
    FROM extract_schema.raw_data;

    row_count := (
    SELECT COUNT(*)
    FROM transform_schema.transform_data
    );

    INSERT INTO audit_schema.audit_table
    VALUES (
        'TRANSFORM_PROCESS_TRANSFORMING',
        CURRENT_TIMESTAMP(),
        row_count
    );
    
    RETURN 'Success';

END;
$$;


CALL transform_schema.transform_to_procedure();

-- Check the data
SELECT *
FROM transform_schema.transform_data
LIMIT 5
