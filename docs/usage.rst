Usage
=====

Instanciate a Store
-------------------

A store can be instanciated like this:
::

    store = DynamoDBConfigStore(
        connection,                 # boto.dynamodb2.layer1.DynamoDBConnection
        table_name,                 # Table name to use
        store_name,                 # Store name to use
        store_key='_store',         # (Optional) value to store Store name in
        option_key='_option')       # (Optional) value to store Option name in

When the Store is instanciated it will create the table if it does not exist. Currently a table with 1 read unit and 1 write unit will be created.

If the Store is instanciated towards an existing table, it will check that the table schema matches the expected Store schema. In other words it will check that ``store_key`` is the table hash key and that ``option_key`` is the table range key.

Write configuration
-------------------

You can insert new items in the configuration via the ``set`` method.
::

    # 'option' is the name of the option where you want to store the values
    store.set('option', {'key1': 'value', 'key2': 'value'})

``set`` takes an ``option`` (``str``) and a ``dict`` with keys and values.

Reading configuration
~~~~~~~~~~~~~~~~~~~~~

Read a specific Option
""""""""""""""""""""""

Specific Options can be fetched like this:
::

    store.get('option')

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

    store.get('option', keys=['key1', 'key4'])

Returns:
::

    {
        'key1': 'value1',
        'key4': 'value4'
    }

Fetching all Options in a Store
"""""""""""""""""""""""""""""""

If you want to retrieve all Options within a Stor, simply omit the ``option`` in the request:
::

    store.get()

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
