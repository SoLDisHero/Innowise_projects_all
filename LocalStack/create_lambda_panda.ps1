# need to create zip first

# create lambda function
aws lambda create-function `
  --function-name lambda_panda `
  --runtime python3.13 `
  --handler lambda_panda.lambda_handler `
  --zip-file fileb://include/handlers/lambda_panda.zip `
  --role arn:aws:iam::000000000000:role/lambda-role `
  --endpoint-url http://localhost:4566 `
  --region eu-north-1


  # give permission
  aws lambda add-permission `
  --function-name lambda_panda `
  --statement-id s3invoke `
  --action lambda:InvokeFunction `
  --principal s3.amazonaws.com `
  --source-arn arn:aws:s3:::helsinki-bike-data `
  --endpoint-url http://localhost:4566 `
  --region eu-north-1

  # attach an event
  aws --endpoint-url=http://localhost:4566 s3api put-bucket-notification-configuration `
  --bucket helsinki-bike-data `
  --notification-configuration file://include/handlers/panda_notification.json `
  --region eu-north-1