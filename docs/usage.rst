Usage
=====

Instanciate a Store
-------------------

A store can be instanciated like this:
::

    from dynamodb_config_store

    store = DynamoDBConfigStore(
        connection,                 # boto.dynamodb2.layer1.DynamoDBConnection
        table_name,                 # Table name to use
        store_name,                 # Store name to use
        store_key='_store',         # (Optional) value to store Store name in
        option_key='_option')       # (Optional) value to store Option name in

When the Store is instanciated it will create the table if it does not exist. Currently a table with 1 read unit and 1 write unit will be created.

If the Store is instanciated towards an existing table, it will check that the table schema matches the expected Store schema. In other words it will check that ``store_key`` is the table hash key and that ``option_key`` is the table range key.

Writing configuration
---------------------

You can insert new items in the configuration via the ``set`` method.
::

    # 'option' is the name of the option where you want to store the values
    store.set('option', {'key1': 'value', 'key2': 'value'})

``set`` takes an ``option`` (``str``) and a ``dict`` with keys and values.

Reading configuration
---------------------

DynamoDB Config Store implements a few different ways to retrieve configuration. Currently we support:

* Time based config store (``TimeBasedConfigStore``)
* Direct config store (``DirectConfigStore``)

The **Time based config store** read data from DynamoDB on a schedule. That approach reduces the read unit consumption, but is not "strongly" consistent as all configuration updates are not reflect until the next config reload.

The **Direct config store** will always query DynamoDB for the latest configuration option. This behavior will consume more reads, but in return you'll always get the latest configuration back.

Reading configuration - DirectConfigStore
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The implementations documented below here will always fetch the configuration options directly from DynamoDB. For each `get()` below an read towards DynamoDB will be executed.

Read a specific Option
""""""""""""""""""""""

Specific Options can be fetched like this:
::

    store.config.get('option')

You will get a ``dict`` with all Keys related to the given Option:
::

    {
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3',
        'key4': 'value4'
    }

Get specific Keys from an Option
""""""""""""""""""""""""""""""""

If you don't need all Keys in the response, you can select which Keys you want to retrieve by adding the ``keys`` parameter:
::

    store.config.get('option', keys=['key1', 'key4'])

Returns:
::

    {
        'key1': 'value1',
        'key4': 'value4'
    }

Fetching all Options in a Store
"""""""""""""""""""""""""""""""

If you want to retrieve all Options within a Store, simply omit the ``option`` in the request:
::

    store.config.get()

You will get an dictionary like this in return:
::

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

Load the DirectConfigStore
""""""""""""""""""""""""""

The ``DirectConfigStore`` is enabled by default, but you can explicitly load it like this:
::

    from dynamodb_config_store

    store = DynamoDBConfigStore(
        connection,
        table_name,
        store_name,
        store_type='DirectConfigStore')

Reading configuration - TimeBasedConfigStore
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The recommended (but not the default) way to read configuration is to let DynamoDB Config Store store all your configuration in an object from which you can fetch the latest configuration. If you have an option called ``db``, you would access that as
::

    store.config.db

And you would get a ``dict`` in return:
::

    {'host': '127.0.0.1', 'port': Decimal(8000)}

By default DynamoDB Config Store will re-read all configuration from DynamoDB every 5 minutes (300 seconds). Any changes in the configuration after an update will not be reflected in the configuration object until the next update has been executed.

The benefit with this over the *Reading configuration directly from DynamoDB* approach is that you will consume much less read capacity. The downside, however, is that the configuration is not always up to date.

Load the TimeBasedConfigStore
"""""""""""""""""""""""""""""

You can start using the ``TimeBasedConfigStore`` by calling ``DynamoDBConfigStore`` like this:
::

    from dynamodb_config_store

    store = DynamoDBConfigStore(
        connection,
        table_name,
        store_name,
        store_type='TimeBasedConfigStore')


Read an Option
""""""""""""""

You can fetch an Option like this:
::

    store.config.option

Where ``option`` is the name of your Option.

Force config update
"""""""""""""""""""

You can manually force a configuration update by issuing:
::

    store.reload()

Set update interval
"""""""""""""""""""

You can set the update interval when instanciating DynamoDB Config Store:
::

    from dynamodb_config_store

    store = DynamoDBConfigStore(
        connection,
        table_name,
        store_name,
        store_type='TimeBasedConfigStore',
        store_type_kwargs={'auto_reload': 60})

This will set the update interval to 60 seconds.

Table management
----------------

DynamoDB Config Store will automatically create a new DynamoDB table if the configured table does not exist. The new table will be provisioned with 1 read unit and 1 write unit. If you want another provisioning, please supply the ``read_units`` and ``write_units`` parameters when instanciating ``DynamoDBConfigStore``, e.g:
::

    store = DynamoDBConfigStore(
        'table_name',
        'store_name',
        read_units=10,
        write_units=5)

If the table already exists when ``DynamoDBConfigStore`` is instanciated, then the table will be left intact. DynamoDB Config Store will check that the table schema is compatible with the configuration. That is; it will check that the hash key is ``store_key`` and the ``option_key`` is the range key. An ``MisconfiguredSchemaException`` will be raised if the table schema is not correct.
