# Overview

This project implements a complete local AWS-like data platform using LocalStack. The pipeline processes the Helsinki City Bikes dataset (2016–2020), stores files in an emulated S3 environment, performs analytical transformations with Apache Spark, triggers serverless processing through AWS Lambda and SNS, stores aggregated results in DynamoDB, and visualizes the results in Tableau.

The solution demonstrates an end-to-end modern data engineering workflow using orchestration, distributed processing, event-driven architecture, NoSQL storage, and business intelligence tools.

# Architecture

Dataset → Airflow → S3 (LocalStack) → SNS → Lambda → DynamoDB → Tableau

Technologies
Apache Airflow (Astro Runtime)
Apache Spark (PySpark)
LocalStack (AWS Cloud Emulation)
Amazon S3 (LocalStack)
Amazon SNS (LocalStack)
AWS Lambda (LocalStack)
Amazon DynamoDB (LocalStack)
Pandas
Boto3
Tableau Public
Docker & Docker Compose

# Dataset

The project uses the Helsinki City Bikes dataset containing bike ride information from 2016 to 2020.

The original dataset is split into monthly CSV files. Each file contains ride information including:

Departure time
Return time
Departure station
Return station
Distance
Duration
Average speed
Temperature
Geographic coordinates

# Pipeline Steps

1. Load Monthly Files to S3

An Airflow DAG automatically scans a local folder containing monthly CSV files and uploads them to an S3 bucket hosted in LocalStack.

2. Spark Data Processing

Apache Spark processes the uploaded files and generates analytical metrics.

Calculated metrics:

Number of rides grouped by departure station
Number of rides grouped by return station
Output files are written to:

processed_by_spark/

and uploaded back to S3.

3. Event-Driven Processing

When new files are uploaded:

S3 generates an event.
SNS receives the notification.
Lambda function is triggered.
Lambda processes incoming data using Pandas.

This architecture simulates a production-grade event-driven AWS workflow. 4. DynamoDB Storage

Three DynamoDB tables are used.

- original_rides

Stores raw ride-level data.

Primary key: ride_id

- daily_rides

Stores daily aggregated metrics.

Primary key: ride_date

Metrics:

Average distance
Average duration
Average speed
Average temperature

- monthly_rides

Stores monthly aggregated metrics.

Primary key: month

Metrics:

Average distance
Average duration
Average speed
Average temperature

# Running the Project

Start Airflow
astro dev start

Start LocalStack
docker compose up -d

! You need to download a dataset and place it include/datasets/original folder and run main.py for splitting the data

Create AWS Resources
.\create_lambda.ps1
.\create_lambda_panda.ps1
.\create_dynamodb.ps1
Execute DAG

Run the Airflow DAG: file_to_s3 from the Airflow UI.

# Dashboards

![Tableau](include/pictures/image_daily.png)
![Tableau](include/pictures/image_monthly.png)
