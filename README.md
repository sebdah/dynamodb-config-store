# dynamodb-config-store

Store your configuration in DynamoDB

## Running tests

### Requirements

#### DynamoDB Local

You must have [DynamoDB Local](http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Tools.DynamoDBLocal.html) installed. It is a local version of DynamoDB that can be used for local development and test execution.

The test suite assumes that DynamoDB Local will be running at port `8000`.

You can either run DynamoDB Local your self or install it under `dynamodb-local` in the project root. If you do this, you can simply start the database with `make dynamodb_local`
