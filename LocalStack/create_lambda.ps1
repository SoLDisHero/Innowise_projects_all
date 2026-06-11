# HOW TO RUN IF NEEDED:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# .\create_lambda.ps1

# Create Bucket
aws --endpoint-url=http://localhost:4566 s3api create-bucket `
  --bucket helsinki-bike-data `
  --create-bucket-configuration LocationConstraint=eu-north-1 `
  --region eu-north-1

# Create Lambda because it does not reatained after reloading the system. Run .\create_lambda.ps1 in the Bash

aws --endpoint-url=http://localhost:4566 lambda create-function `
  --function-name process-bike-file `
  --runtime python3.13 `
  --handler lambda_handler.lambda_handler `
  --zip-file fileb://include/handlers/lambda_function.zip `
  --role arn:aws:iam::000000000000:role/lambda-role

# Create SNS Topic

aws --endpoint-url=http://localhost:4566 sns create-topic `
  --name bike-files-topic


# Add permission for processing of SNS
aws --endpoint-url=http://localhost:4566 lambda add-permission `
  --function-name process-bike-file `
  --statement-id sns-trigger `
  --action lambda:InvokeFunction `
  --principal sns.amazonaws.com `
  --source-arn arn:aws:sns:eu-north-1:000000000000:bike-files-topic

# Subscribe Lambda to SNS

aws --endpoint-url=http://localhost:4566 sns subscribe `
  --topic-arn arn:aws:sns:eu-north-1:000000000000:bike-files-topic `
  --protocol lambda `
  --notification-endpoint arn:aws:lambda:eu-north-1:000000000000:function:process-bike-file

# Configure S3 -> SNS notification

aws --endpoint-url=http://localhost:4566 s3api put-bucket-notification-configuration `
  --bucket helsinki-bike-data `
  --notification-configuration file://include/handlers/notification.json

# verify the function
# aws --endpoint-url=http://localhost:4566 lambda list-functions
# verify logs after DAG has been triggered
# aws --endpoint-url=http://localhost:4566 --region eu-north-1 logs tail /aws/lambda/process-bike-file
# verify bucket exist
# aws --endpoint-url=http://localhost:4566 s3 ls