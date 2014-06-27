API documentation
=================

This is the API documentation for DynamoDB Config Store.

DynamoDBConfigStore
-------------------

.. autoclass:: dynamodb_config_store.DynamoDBConfigStore
    :private-members:
    :members:

TimeBasedConfigStore
--------------------

The `TimeBasedConfigStore` is the Config Store used for fetching configuration from DynamoDB on a preset interval. All configuration options will be exposed using instance attributes such as ``store.config.option``, where ``option`` is the store option.

This class shall not be instanciated directly, it's called by ``DynamoDBConfigStore``.

.. autoclass:: dynamodb_config_store.config_stores.time_based.TimeBasedConfigStore
    :private-members:
    :members:

Exceptions
----------

.. automodule:: dynamodb_config_store.exceptions
    :members:
