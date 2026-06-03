# create SNS topic
aws --endpoint-url=http://localhost:4566 sns create-topic --name bike-files-topic

# create SNS subscription of Lambda
aws --endpoint-url=http://localhost:4566 sns subscribe --topic-arn arn:aws:sns:eu-north-1:000000000000:bike-files-topic --protocol lambda --notification-endpoint arn:aws:lambda:eu-north-1:000000000000:function:process-bike-file

# add permission for processing of SNS
aws --endpoint-url=http://localhost:4566 lambda add-permission `
  --function-name process-bike-file `
  --statement-id sns-trigger `
  --action lambda:InvokeFunction `
  --principal sns.amazonaws.com `
  --source-arn arn:aws:sns:eu-north-1:000000000000:bike-files-topic