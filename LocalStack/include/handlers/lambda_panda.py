import pandas as pd
import boto3
import uuid
import json
from decimal import Decimal

# initialize DynamoDB
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url="http://localstack:4566",
    region_name="eu-north-1",
    aws_access_key_id="sold",
    aws_secret_access_key="sold"
)

table_original = dynamodb.Table("original_rides")
table_daily = dynamodb.Table("daily_rides")
table_monthly = dynamodb.Table("monthly_rides")

# initialize our lamba_handler function that will be triggered by S3 data upload via 'event'
def lambda_handler(event, context):

    s3 = boto3.client(
    "s3",
    endpoint_url="http://localstack:4566",
    region_name="eu-north-1",
    aws_access_key_id="sold",
    aws_secret_access_key="sold"
    )

    # Extract SNS message
    sns_message = json.loads(
        event["Records"][0]["Sns"]["Message"]
    )

    # Extract S3 info
    bucket_name = sns_message["Records"][0]["s3"]["bucket"]["name"]
    file_key = sns_message["Records"][0]["s3"]["object"]["key"]

    # Read file from S3
    obj = s3.get_object(
        Bucket=bucket_name,
        Key=file_key
    )

    # Create DataFrame from uploaded CSV
    df = pd.read_csv(obj["Body"])

    # Wraper if our values are NaN
    def safe_decimal(value):
        if pd.isna(value):
            return Decimal("0")
        return Decimal(str(value))
    
    # raw data
    with table_original.batch_writer() as batch:
        for index, row in df.iterrows():
            batch.put_item(
                Item={                
                    "ride_id": str(uuid.uuid4()),
                    "departure": str(row["departure"]),
                    "return": str(row["return"]),
                    "departure_id": str(row["departure_id"]),
                    "departure_name": str(row["departure_name"]),
                    "return_id": str(row["return_id"]),
                    "return_name": str(row["return_name"]),
                    "distance_m": safe_decimal(row.get("distance (m)")),
                    "duration_sec": safe_decimal(row.get("duration (sec.)")),
                    "avg_speed_kmh": safe_decimal(row.get("avg_speed (km/h)")),
                    "departure_latitude": safe_decimal(row.get("departure_latitude")),
                    "departure_longitude": safe_decimal(row.get("departure_longitude")),
                    "return_latitude": safe_decimal(row.get("return_latitude")),
                    "return_longitude": safe_decimal(row.get("return_longitude")),
                    "air_temperature_c": safe_decimal(row.get("Air temperature (degC)")),
                    "month": str(row["month"])
                }
            )

    # daily metrics
    df["ride_date"] = pd.to_datetime(df["departure"]).dt.date

    daily = df.groupby("ride_date").agg({
        "distance (m)": "mean",
        "duration (sec.)": "mean",
        "avg_speed (km/h)": "mean",
        "Air temperature (degC)": "mean",
    }).reset_index()
    
    with table_daily.batch_writer() as batch:
        for index, row in daily.iterrows():
            batch.put_item(Item={
                "ride_date": str(row["ride_date"]),
                "avg_distance": safe_decimal(row["distance (m)"]),
                "avg_duration": safe_decimal(row["duration (sec.)"]),
                "avg_speed_kmh": safe_decimal(row["avg_speed (km/h)"]),
                "avg_temp": safe_decimal(row["Air temperature (degC)"]),
            })

    # monthly metrics
    df["month"] = pd.to_datetime(df["month"]).dt.to_period("M").astype("str")

    month = df.groupby("month").agg({
        "distance (m)": "mean",
        "duration (sec.)": "mean",
        "avg_speed (km/h)": "mean",
        "Air temperature (degC)": "mean",
    }).reset_index()

    with table_monthly.batch_writer() as batch:
        for index, row in month.iterrows():
            batch.put_item(Item={
                "month": str(row["month"]),
                "avg_distance": safe_decimal(row["distance (m)"]),
                "avg_duration": safe_decimal(row["duration (sec.)"]),
                "avg_speed_kmh": safe_decimal(row["avg_speed (km/h)"]),
                "avg_temp": safe_decimal(row["Air temperature (degC)"]),
            })

    return {"statusCode": 200, "message": "All good"}