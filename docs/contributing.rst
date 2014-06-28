Contributing
============

Creating pull requests
----------------------

If you want to open a pull request, please do it towards the ``develop`` branch. I'd also appreciate if the pull request contains tests for the added functionality.

Running tests
-------------

Requirements
~~~~~~~~~~~~

You must have `DynamoDB Local <http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Tools.DynamoDBLocal.html>`_ installed. It is a local version of DynamoDB that can be used for local development and test execution.

The test suite assumes that DynamoDB Local will be running at port ``8000``.

You can either run DynamoDB Local your self or install it under ``dynamodb-local`` in the project root. If you do this, you can simply start the database with ``make dynamodb_local``

Executing the test suite
~~~~~~~~~~~~~~~~~~~~~~~~

You can run the test suite via ``make tests`` or ``python test.py``.
