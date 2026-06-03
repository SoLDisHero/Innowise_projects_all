# Create bucket

aws --endpoint-url=http://localhost:4566 s3 mb s3://helsinki-bike-data 2>$null

# Create Lambda because it does not reatained after reloading the system. Run .\create_lambda.ps1 in the Bash

aws --endpoint-url=http://localhost:4566 lambda create-function `
  --function-name process-bike-file `
  --runtime python3.13 `
  --handler lambda_handler.lambda_handler `
  --zip-file fileb://include/handlers/lambda_function.zip `
  --role arn:aws:iam::000000000000:role/lambda-role

# # Allow S3 to invoke Lambda

# aws --endpoint-url=http://localhost:4566 lambda add-permission `
#   --function-name process-bike-file `
#   --statement-id s3-trigger `
#   --action lambda:InvokeFunction `
#   --principal s3.amazonaws.com `
#   --source-arn arn:aws:s3:::helsinki-bike-data

# Attach S3 trigger

aws --endpoint-url=http://localhost:4566 s3api put-bucket-notification-configuration `
  --bucket helsinki-bike-data `
  --notification-configuration file://include/handlers/notification.json

# verify the function
# aws --endpoint-url=http://localhost:4566 lambda list-functions
# verify logs after DAG has been triggered
# aws --endpoint-url=http://localhost:4566 --region eu-north-1 logs tail /aws/lambda/process-bike-file
# verify bucket exist
# aws --endpoint-url=http://localhost:4566 s3 ls

# HOW TO RUN:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# .\create_lambda.ps1