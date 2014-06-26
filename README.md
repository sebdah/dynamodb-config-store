# dynamodb-config-store

Store your configuration in DynamoDB using DynamoDB Config Store.

Using this class you'll be able to easily manage application configuration directly in DynamoDB. It works almost like any configuration file, except that an option can have multiple values (it's NoSQL, right :)). For example your configuration could look like this:

    ------------+----------------+----------------+----------------+----------------
    _store      | _option        | host           | port           | secret-key
    ------------+----------------+----------------+----------------+----------------
    prod        | db             | db-cluster.com | 27017          |
    prod        | external-port  |                | 80             |
    prod        | secret-key     |                |                | abcd1234
    test        | db             | localhost      | 27017          |
    test        | external-port  |                | 4000           |
    prod        | secret-key     |                |                | test1234
    ------------+----------------+----------------+----------------+----------------

You can then retrieve configuration like this:

    store = DynamoDBConfigStore(
        connection,                 # dynamodb2 connection from boto
        'config',                   # DynamoDB table name
        'prod')                     # Store name

    # Get the 'db' option and all it's values
    store.get('db') # Returns {'host': 'db-cluster.com', 'port', Decimal(27017)}

In our lingo a **Store** is roughly equivivalent to a configuration file. And an **Option** is an key in the Store which holds zero or more **Values**.

## Usage

### Instanciate a Store

A store can be instanciated like this:

    store = DynamoDBConfigStore(
        connection,                 # boto.dynamodb2.layer1.DynamoDBConnection
        table_name,                 # Table name to use
        store_name,                 # Store name to use
        store_key='_store',         # (Optional) value to store Store name in
        option_key='_option')       # (Optional) value to store Option name in

When the Store is instanciated it will create the table if it does not exist. Currently a table with 1 read unit and 1 write unit will be created.

If the Store is instanciated towards an existing table, it will check that the table schema matches the expected Store schema. In other words it will check that `store_key` is the table hash key and that `option_key` is the table range key.

### Write configuration

You can insert new items in the configuration via the `set` method.

    # 'option' is the name of the option where you want to store the values
    store.set('option', {'key1': 'value', 'key2': 'value'})

`set` takes an `option` (`str`) and a `dict` with keys and values.

### Reading configuration

#### Read a specific Option

Specific Options can be fetched like this:

    store.get('option')

You will get a `dict` with all Values related to the given Option:

    {
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3',
        'key4': 'value4'
    }

#### Get specific Values from an Option

If you don't need all Values in the response, you can select which Values you want to retrieve by adding the `values` parameter:

    store.get('option', values=['value1', 'value4'])

Returns:

    {
        'key1': 'value1',
        'key4': 'value4'
    }

#### Fetching all Options in a Store

If you want to retrieve all Options within a Stor, simply omit the `option` in the request:

    store.get()

You will get an dictionary like this in return:

    {
        'option1': {
            'key1': 'value1',
            'key2': 'value2'
        },
        'option2': {
            'key1': 'value1',
            'key4': 'value2'
        }
    }

## Running tests

### Requirements

#### DynamoDB Local

You must have [DynamoDB Local](http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Tools.DynamoDBLocal.html) installed. It is a local version of DynamoDB that can be used for local development and test execution.

The test suite assumes that DynamoDB Local will be running at port `8000`.

You can either run DynamoDB Local your self or install it under `dynamodb-local` in the project root. If you do this, you can simply start the database with `make dynamodb_local`

### Executing the test suite

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
