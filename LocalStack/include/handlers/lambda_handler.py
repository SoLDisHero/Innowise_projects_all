import json
import boto3

s3 = boto3.client("s3", endpoint_url="http://localstack-main:4566")

def lambda_handler(event, context):

    print("Event: ", json.dumps(event))
    #Extract SNS message
    sns_message = event["Records"][0]["Sns"]["Message"]

    # Convert SNS message into dict
    s3_event = json.loads(sns_message)
    if "Records" not in s3_event:
        print("Mistake")
        return{
            "statusCode": 200,
            "body": "Continue"
        }

    # get event information
    bucket = s3_event["Records"][0]["s3"]["bucket"]["name"]
    key = s3_event["Records"][0]["s3"]["object"]["key"]
    print(f"Uploaded Key: {key}")

    # get month data
    month = key.split("/")[-1].split("_")[0]
    uploaded_file = f"by_months/{month}_date.csv"
    modified_file = f"processed_by_spark/{month}_modified.csv"

    # Checking that both uploaded files exists
    try:
        s3.head_object(Bucket=bucket, Key=uploaded_file)
        s3.head_object(Bucket=bucket, Key=modified_file)
        print("Both files exist and ready.")     

        return {
            "statusCode": 200,
            "body": json.dumps("Everything is working as expected")
        }
    except Exception as e:
        return {
            "statusCode": 200,
            "body": json.dumps("Waiting for the second file")
        }