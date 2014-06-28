# DynamoDB Config Store

Store your configuration in DynamoDB using DynamoDB Config Store.

Using this Python class you'll be able to easily manage application configuration directly in DynamoDB. It works almost like any configuration file, except that an option can have multiple values. For example your configuration could look like this:

    ------------+----------------+----------------+----------------+----------------
    _store      | _option        | host           | port           | secret-key
    ------------+----------------+----------------+----------------+----------------
    prod        | db             | db-cluster.com | 27017          |
    prod        | external-port  |                | 80             |
    prod        | secret-key     |                |                | abcd1234
    test        | db             | localhost      | 27017          |
    test        | external-port  |                | 4000           |
    test        | secret-key     |                |                | test1234
    ------------+----------------+----------------+----------------+----------------

You can then retrieve configuration like this:

    store = DynamoDBConfigStore(
        connection,                 # dynamodb2 connection from boto
        'config',                   # DynamoDB table name
        'prod')                     # Store name

    # Get the 'db' option and all it's values
    store.config.get('db') # Returns {'host': 'db-cluster.com', 'port', Decimal(27017)}

In our lingo a **Store** is roughly equivivalent to a configuration file. And an **Option** is an key in the Store which holds zero or more **Keys**.

## Documentation

The project documentation is hosted at [http://dynamodb-config-store.readthedocs.org/](http://dynamodb-config-store.readthedocs.org/).

## Contributing

### Creating pull requests

If you want to open a pull request, please do it towards the `develop` branch. I'd also appreciate if the pull request contains tests for the added functionality.

### Running tests

#### Requirements

You must have [DynamoDB Local](http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Tools.DynamoDBLocal.html) installed. It is a local version of DynamoDB that can be used for local development and test execution.

The test suite assumes that DynamoDB Local will be running at port `8000`.

You can either run DynamoDB Local your self or install it under `dynamodb-local` in the project root. If you do this, you can simply start the database with `make dynamodb_local`

#### Executing the test suite

You can run the test suite via `make tests` or `python test.py`.

## License

    APACHE LICENSE 2.0
    Copyright 2014 Sebastian Dahlgren

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
