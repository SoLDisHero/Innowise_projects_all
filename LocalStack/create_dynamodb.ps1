# CREATING TABLE FOR THE ALL COLUMNS OF RAW DATA
aws --endpoint-url=http://localhost:4566 dynamodb create-table `
--table-name original_rides `
--key-schema AttributeName=ride_id,KeyType=HASH `
--attribute-definitions AttributeName=ride_id,AttributeType=S `
--billing-mode PAY_PER_REQUEST `
--region eu-north-1

# CREATING TABLE FOR THE ALL COLUMNS OF DAILY DATA
aws --endpoint-url=http://localhost:4566 dynamodb create-table `
--table-name daily_rides `
--key-schema AttributeName=ride_date,KeyType=HASH `
--attribute-definitions AttributeName=ride_date,AttributeType=S `
--billing-mode PAY_PER_REQUEST `
--region eu-north-1

# CREATING TABLE FOR THE ALL COLUMNS OF MONTHLY DATA
aws --endpoint-url=http://localhost:4566 dynamodb create-table `
--table-name monthly_rides `
--key-schema AttributeName=month,KeyType=HASH `
--attribute-definitions AttributeName=month,AttributeType=S `
--billing-mode PAY_PER_REQUEST `
--region eu-north-1

# CHECK THE TABLE LIST
# aws --endpoint-url=http://localhost:4566 dynamodb list-tables