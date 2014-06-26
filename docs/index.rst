.. DynamoDB Config Store index

.. toctree::
    :hidden:
    :maxdepth: 3

    installation
    usage
    api
    release_notes
    bug_reporting
    license

DynamoDB Config Store documentation
===================================

Overview
--------

Store your configuration in DynamoDB using DynamoDB Config Store.

Using this Python class you'll be able to easily manage application configuration directly in DynamoDB. It works almost like any configuration file, except that an option can have multiple values (it's NoSQL, right :)). For example your configuration could look like this:
::

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
::

    store = DynamoDBConfigStore(
        connection,                 # dynamodb2 connection from boto
        'config',                   # DynamoDB table name
        'prod')                     # Store name

    # Get the 'db' option and all it's values
    store.get('db') # Returns {'host': 'db-cluster.com', 'port', Decimal(27017)}

In our lingo a **Store** is roughly equivivalent to a configuration file. And an **Option** is an key in the Store which holds zero or more **Keys**.
