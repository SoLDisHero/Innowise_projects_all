from airflow.sdk import dag, task
from pendulum import datetime
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from pyspark.sql import SparkSession
from decimal import Decimal
import pyspark.sql.functions as F
import os
import boto3
import uuid
import pandas as pd

bucket_name = "helsinki-bike-data"
months_folder = "include/datasets/by_months/"
processed_path = "include/datasets/processed_by_spark/"

@dag( 
    dag_id="file_to_s3",
    start_date=datetime(2026,5,1),
    description="Loading data to S3",
    tags=["s3","helsinki_bike"],
    schedule=None,
    catchup=False)
def file_to_s3():

    # CREATE A BUCKET IF IT DOES NOT EXISTS
    @task
    def creation_bucket_check():
        hook = S3Hook(aws_conn_id="localstack_s3")
        if not hook.check_for_bucket(bucket_name):
            hook.create_bucket(bucket_name)

    # LOAD THE MONTHLY RAW DATA INTO S3 BUCKET
    @task
    def monthly_data():
        hook = S3Hook(aws_conn_id="localstack_s3")

        for file in os.listdir(months_folder):
            if file.endswith(".csv"):
                hook.load_file(
                    filename=os.path.join(months_folder, file), 
                    key=f"by_months/{file}", 
                    bucket_name=bucket_name, 
                    replace=True)
                
    # USE SPARK TO MODIFY DATE
    @task
    def modify_by_spark():
        # remove garbage folders and clutter
        import shutil

        for item in os.listdir(processed_path):
            item_path = os.path.join(processed_path, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            elif item.endswith(".csv"):
                os.remove(item_path)        

        spark = SparkSession.builder.appName("localstack_project").getOrCreate()
        for file in os.listdir(months_folder):
            if file.endswith(".csv"):
                month_header = file.replace("_date.csv","") #for renaming modified file

                df = spark.read.csv(
                    path=os.path.join(months_folder, file),
                    header=True,
                    inferSchema=True
                )

                # Metric that will group how many times it was taken at one station (departure_name) and it was returned at one station (return_name)
                result = df.groupBy("departure_name", "return_name").agg(F.count("*").alias("count")).orderBy("departure_name", ascending=True)
                output_dir = os.path.join(processed_path, month_header) # it's a mediator for renaming file
                result.coalesce(1).write.mode("overwrite").csv(output_dir, header=True) # save as one file

                for file_modified in os.listdir(output_dir):
                    if file_modified.endswith(".csv"):
                        os.rename(
                            os.path.join(output_dir, file_modified),
                            os.path.join(processed_path, f"{month_header}_modified.csv")
                        )        
        spark.stop()
        
    # UPLOAD 1 MODIFIED FILE TO S3. THE LOOP HAS BEEN SET UP FOR MORE THAN 1 FILE CASE
    @task
    def upload_by_spark():
        hook = S3Hook(aws_conn_id="localstack_s3")
        
        for file in os.listdir(processed_path):
            if file.endswith(".csv"):
                hook.load_file(
                    filename=os.path.join(processed_path, file),
                    key=f"processed_by_spark/{file}",
                    bucket_name=bucket_name,
                    replace=True
                )

    # UPLOAD RAW DATA INTO DYNAMODB STORAGE
    @task
    def to_dynamodb():
        
        # reading one csv file for testing
        spark = SparkSession.builder.appName("dynamodb_loading").getOrCreate()
        df = spark.read.csv(
            path=f"{months_folder}2016-05_date.csv",
            header=True,
            inferSchema=True
        )
        print("Partitions:", df.rdd.getNumPartitions()) # number of partition to process
        
        def write_to_dynamo(partition):

            # configuring DynamoDB connection to LocalStack
            dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url="http://localstack-main:4566",
            region_name="eu-north-1",
            aws_access_key_id="sold",
            aws_secret_access_key="sold"
            )
            table_original = dynamodb.Table("original_rides")

            with table_original.batch_writer(overwrite_by_pkeys=['ride_id']) as batch: # send rows by batches 
                for row in partition:
                    r = row.asDict() # assign Spark row to Python dict
                    try:
                        batch.put_item(
                            Item={
                                "ride_id": str(uuid.uuid4()),
                                "departure": str(row["departure"]),
                                "return": str(row["return"]),
                                "departure_id": str(row["departure_id"]),
                                "departure_name": str(row["departure_name"]),
                                "return_id": str(row["return_id"]),
                                "return_name": str(row["return_name"]),
                                "distance_m": Decimal(str(r.get("distance (m)") or 0)),
                                "duration_sec": Decimal(str(r.get("duration (sec.)") or 0)),
                                "avg_speed_kmh": Decimal(str(r.get("avg_speed (km/h)") or 0)),
                                "departure_latitude": Decimal(str(r.get("departure_latitude") or 0)),
                                "departure_longitude": Decimal(str(r.get("departure_longitude") or 0)),
                                "return_latitude": Decimal(str(r.get("return_latitude") or 0)),
                                "return_longitude": Decimal(str(r.get("return_longitude") or 0)),
                                "air temperature_c": Decimal(str(r.get("Air temperature (degC)") or 0)),
                                "month": str(row["month"])
                            }
                        )  
                    except Exception as e:
                        print("Error: ", e)
                        continue

        df.foreachPartition(write_to_dynamo) # distribute rows between independent Spark workers in concurency
        spark.stop()
       
    # UPLOAD DAILY DATA INTO DYNAMODB STORAGE
    @task
    def to_dynamodb_daily():
        spark = SparkSession.builder.appName("dynamodb_loading_daily").getOrCreate()
        df = spark.read.csv(
            path=f"{months_folder}2016-05_date.csv",
            header=True,
            inferSchema=True
        )
        # creating new column for day
        df = df.withColumn("ride_date",F.to_date(F.col("departure")))
        # calculate daily metrics such as AVG Distance day, AVG Duration day, AVG Speed day, AVG Temperature
        daily = df.groupBy("ride_date").agg(
            F.avg(F.col("`distance (m)`")).alias("avg_distance"),
            F.avg(F.col("`duration (sec.)`")).alias("avg_duration"),
            F.avg(F.col("`avg_speed (km/h)`")).alias("avg_speed_kmh"),
            F.avg(F.col("`Air temperature (degC)`")).alias("avg_temp")
        )
        # converting to Pandas for speeding up the process
        daily_df = daily.toPandas()

        # configuring DynamoDB connection to LocalStack
        dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url="http://localstack-main:4566",
            region_name="eu-north-1",
            aws_access_key_id="sold",
            aws_secret_access_key="sold"
        )
        table_daily = dynamodb.Table("daily_rides")

        def safe_decimal(value):
            if pd.isna(value):
                return Decimal("0")
            return Decimal(str(value))

        with table_daily.batch_writer() as batch:            
            for index, row in daily_df.iterrows():                
                try:
                    batch.put_item(
                        Item={
                            "ride_date": str(row["ride_date"]),
                            "avg_distance": safe_decimal(row["avg_distance"]),
                            "avg_duration": safe_decimal(row["avg_duration"]),
                            "avg_speed_kmh": safe_decimal(row["avg_speed_kmh"]),
                            "avg_temp": safe_decimal(row["avg_temp"])
                        }
                    )
                except Exception as e:
                    print("Error: ", row)
                    print(e)
        spark.stop()

    # UPLOAD MONTHLY DATA INTO DYNAMODB STORAGE
    @task
    def to_dynamodb_monthly():
        spark = SparkSession.builder.appName("dynamodb_loading_monthly").getOrCreate()
        df = spark.read.csv(
            path=f"{months_folder}2016-05_date.csv",
            header=True,
            inferSchema=True
        )
        # calculate monthly metrics such as AVG Distance day, AVG Duration day, AVG Speed day, AVG Temperature
        monthly = df.groupBy("month").agg(
            F.avg(F.col("`distance (m)`")).alias("avg_distance"),
            F.avg(F.col("`duration (sec.)`")).alias("avg_duration"),
            F.avg(F.col("`avg_speed (km/h)`")).alias("avg_speed_kmh"),
            F.avg(F.col("`Air temperature (degC)`")).alias("avg_temp")
        )
        # converting to Pandas for speeding up the process
        monthly_df = monthly.toPandas()

        # configuring DynamoDB connection to LocalStack
        dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url="http://localstack-main:4566",
            region_name="eu-north-1",
            aws_access_key_id="sold",
            aws_secret_access_key="sold"
        )
        table_monthly = dynamodb.Table("monthly_rides")
        def safe_decimal(value):
            if pd.isna(value):
                return Decimal("0")
            return Decimal(str(value))

        with table_monthly.batch_writer() as batch:            
            for index, row in monthly_df.iterrows():                
                try:
                    batch.put_item(
                        Item={
                            "month": str(row["month"]),
                            "avg_distance": safe_decimal(row["avg_distance"]),
                            "avg_duration": safe_decimal(row["avg_duration"]),
                            "avg_speed_kmh": safe_decimal(row["avg_speed_kmh"]),
                            "avg_temp": safe_decimal(row["avg_temp"])
                        }
                    )
                except Exception as e:
                    print("Error: ", row)
                    print(e)
        spark.stop()

    creation_bucket_check() >> monthly_data() >> modify_by_spark() >> upload_by_spark() >> to_dynamodb() >> to_dynamodb_daily() >> to_dynamodb_monthly()
    # creation_bucket_check() >> to_dynamodb() >> to_dynamodb_daily() >> to_dynamodb_monthly()
    
file_to_s3()