import boto3
import pandas as pd

dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url="http://localhost:4566",
    region_name="eu-north-1",
    aws_access_key_id="sold",
    aws_secret_access_key="sold"
)

table = dynamodb.Table("original_rides")

response = table.scan()
items = response["Items"]

df = pd.DataFrame(items)

df.to_csv("original_rides.csv", index=False)