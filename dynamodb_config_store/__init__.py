""" DynamoDB Config Store

Example structure:

------------+----------------+----------------+----------------+----------------
_store*     | _option**      | host           | port           | secret-key
------------+----------------+----------------+----------------+----------------
prod        | db             | db-cluster.com | 27017          |
prod        | external-port  |                | 80             |
prod        | secret-key     |                |                | abcd1234
test        | db             | localhost      | 27017          |
test        | external-port  |                | 4000           |
prod        | secret-key     |                |                | test1234
------------+----------------+----------------+----------------+----------------

*) Hash key
**) Range key
"""
import time

from boto.dynamodb2.fields import HashKey, RangeKey
from boto.dynamodb2.table import Table
from boto.dynamodb2.exceptions import ItemNotFound
from boto.exception import JSONResponseError

from dynamodb_config_store.exceptions import TableNotCreatedException


class DynamoDBConfigStore(object):
    """ DynamoDB Config Store instance """
    connection = None   # boto.dynamodb2.layer1.DynamoDBConnection instance
    table_name = None   # Name of the DynamoDB table
    store_name = None   # Name of the Store
    store_key = None    # Key for the store (default: _store)
    option_key = None   # Key for the option (default: _option)
    table = None        # boto.dynamodb2.table.Table instance

    def __init__(
            self, connection, table_name, store_name,
            store_key='_store', option_key='_option'):
        """ Constructor for the config store

        :type connection: boto.dynamodb2.layer1.DynamoDBConnection
        :param connection: Boto connection object to use
        :type table_name: str
        :param table_name: Name of the DynamoDB table to use
        :type store_name: str
        :type store_name: Name of the DynamoDB Config Store
        :type store_key: str
        :type store_key: Key name for the store name in DynamoDB. Default _store
        :type option_key: str
        :type option_key: Key name for the option in DynamoDB. Default _option
        :returns: None
        """
        self.connection = connection
        self.table_name = table_name
        self.store_name = store_name
        self.store_key = store_key
        self.option_key = option_key

        self._initialize()

    def get(self, option=None):
        """ Get a config item

        An boto.dynamodb2.exceptions.ItemNotFound will be thrown if the config
        option does not exist.

        :type option: str
        :param option: Name of the configuration option, all options if None
        :returns: dict -- Dictionary with all data; {'key': 'value'}
        """
        if option:
            return self.get_option(option)

        else:
            try:
                items = {}
                query = {'{}__eq'.format(self.store_key): self.store_name}

                for item in self.table.query_2(**query):
                    option = item[self.option_key]

                    # Remove metadata
                    del item[self.store_key]
                    del item[self.option_key]

                    items[option] = {k: v for k, v in item.items()}

                return items

            except ItemNotFound:
                raise

    def get_option(self, option):
        """ Get a specific option from the store.

        get_option('a') == get(option='a')

        :type option: str
        :param option: Name of the configuration option
        :returns: dict -- Dictionary with all data; {'key': 'value'}
        """
        try:
            kwargs = {
                self.store_key: self.store_name,
                self.option_key: option
            }

            item = self.table.get_item(**kwargs)

            del item[self.store_key]
            del item[self.option_key]

            return {key: value for key, value in item.items()}

        except ItemNotFound:
            raise

    def set(self, option, data):
        """ Upsert a config item

        :type option: str
        :param option: Name of the configuration option
        :type data: dict
        :param data: Dictionary with all option data
        :returns: bool -- True if the data was stored successfully
        """
        data[self.store_key] = self.store_name
        data[self.option_key] = option

        return self.table.put_item(data, overwrite=True)

    def _initialize(self):
        """ Initialize the store """
        try:
            self.connection.describe_table(self.table_name)
        except JSONResponseError as error:
            if error.error_code == 'ResourceNotFoundException':
                table_created = self._create_table()
                if not table_created:
                    raise TableNotCreatedException

        self.table = Table(self.table_name, connection=self.connection)

    def _create_table(self, read_units=1, write_units=1):
        """ Create a new table

        :type read_units: int
        :param read_units: Number of read capacity units to provision
        :type write_units: int
        :param write_units: Number of write capacity units to provision
        :returns: bool -- Returns True if the table was created
        """
        self.table = Table.create(
            self.table_name,
            schema=[
                HashKey(self.store_key),
                RangeKey(self.option_key)
            ],
            throughput={
                'read': read_units,
                'write': write_units
            },
            connection=self.connection)

        # Wait for the table to get ACTIVE
        return self._wait_for_table(target_state='ACTIVE')

    def _wait_for_table(self, target_state, sleep_time=5, retries=30):
        """ Wait for the table to get to a certain state

        :type target_state: str
        :param target_state: The target state to wait for
        :type sleep_time: int
        :param sleep_time: Number of seconds to wait between the checks
        :type retries: int
        :param retries: Number of retries before giving up
        :returns: bool -- True if the target state was reached, else False
        """
        while retries > 0:
            desc = self.connection.describe_table(self.table_name)
            if desc[u'Table'][u'TableStatus'] == target_state.upper():
                return True

            time.sleep(sleep_time)
            retries -= 1

        return False
