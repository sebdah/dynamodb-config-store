""" DynamoDB Config Store

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
import os.path
import time
from ConfigParser import SafeConfigParser

from boto.dynamodb2.exceptions import ItemNotFound
from boto.dynamodb2.fields import HashKey, RangeKey
from boto.dynamodb2.table import Table
from boto.exception import JSONResponseError

from dynamodb_config_store.config_stores.time_based import TimeBasedConfigStore
from dynamodb_config_store.exceptions import (
    MisconfiguredSchemaException,
    TableNotCreatedException,
    TableNotReadyException)

# Publish the module __version__
config_file = SafeConfigParser()
config_file.read(
    os.path.abspath(os.path.join(os.path.dirname(__file__), 'settings.conf')))
__version__ = config_file.get('general', 'version')


class DynamoDBConfigStore(object):
    """ DynamoDB Config Store instance """

    auto_update = None      # Turn on or off the auto updater
    config = None           # Instance of the a ConfigStore
    connection = None       # boto.dynamodb2.layer1.DynamoDBConnection instance
    option_key = None       # Key for the option (default: _option)
    read_units = None       # Number of read units to provision to new tables
    store_key = None        # Key for the store (default: _store)
    store_name = None       # Name of the Store
    table = None            # boto.dynamodb2.table.Table instance
    table_name = None       # Name of the DynamoDB table
    update_interval = None  # Update interval for the auto updater
    write_units = None      # Number of write units to provision to new tables

    def __init__(
            self, connection, table_name, store_name,
            store_key='_store', option_key='_option',
            read_units=1, write_units=1,
            auto_update=True, update_interval=300):
        """ Constructor for the config store

        :type connection: boto.dynamodb2.layer1.DynamoDBConnection
        :param connection: Boto connection object to use
        :type table_name: str
        :param table_name: Name of the DynamoDB table to use
        :type store_name: str
        :param store_name: Name of the DynamoDB Config Store
        :type store_key: str
        :param store_key: Key name for the store in DynamoDB. Default _store
        :type option_key: str
        :param option_key: Key name for the option in DynamoDB. Default _option
        :type auto_update: bool
        :param auto_update:
            Auto update the config option every update_interval seconds
        :type update_interval: int
        :param update_interval: How often, in seconds, to refresh the config
        :returns: None
        """
        self.auto_update = auto_update
        self.connection = connection
        self.option_key = option_key
        self.read_units = read_units
        self.store_key = store_key
        self.store_name = store_name
        self.table_name = table_name
        self.update_interval = update_interval
        self.write_units = write_units

        self._initialize()

    def _initialize(self):
        """ Initialize the store

        :returns: None
        """
        try:
            table = self.connection.describe_table(self.table_name)
            status = table[u'Table'][u'TableStatus']
            schema = table[u'Table'][u'KeySchema']

            # Validate that the table is in ACTIVE state
            if status not in ['ACTIVE', 'UPDATING']:
                raise TableNotReadyException

            # Validate schema
            hash_found = False
            range_found = False
            for key in schema:
                if key[u'AttributeName'] == self.store_key:
                    if key[u'KeyType'] == u'HASH':
                        hash_found = True

                if key[u'AttributeName'] == self.option_key:
                    if key[u'KeyType'] == u'RANGE':
                        range_found = True

            if not hash_found or not range_found:
                raise MisconfiguredSchemaException

        except JSONResponseError as error:
            if error.error_code == 'ResourceNotFoundException':
                table_created = self._create_table(
                    read_units=self.read_units,
                    write_units=self.write_units)

                if not table_created:
                    raise TableNotCreatedException

        self.table = Table(self.table_name, connection=self.connection)

        self.reload()

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

    def get(self, option=None, keys=None):
        """ Get a config item

        A query towards DynamoDB will always be executed when this
        method is called.

        An boto.dynamodb2.exceptions.ItemNotFound will be thrown if the config
        option does not exist.

        :type option: str
        :param option: Name of the configuration option, all options if None
        :type keys: list
        :param keys: List of keys to return (used to get subsets of keys)
        :returns: dict -- Dictionary with all data; {'key': 'value'}
        """
        if option:
            return self.get_option(option, keys=keys)

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

    def get_option(self, option, keys=None):
        """ Get a specific option from the store.

        A query towards DynamoDB will always be executed when this
        method is called.

        get_option('a') == get(option='a')
        get_option('a', keys=['b', 'c']) == get(option='a', keys=['b', 'c'])

        :type option: str
        :param option: Name of the configuration option
        :type keys: list
        :param keys: List of keys to return (used to get subsets of keys)
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

            if keys:
                return {
                    key: value
                    for key, value in item.items()
                    if key in keys
                }
            else:
                return {key: value for key, value in item.items()}

        except ItemNotFound:
            raise

    def reload(self):
        """ Reload the config object

        This issues an query towards DynamoDB in order to fetch the latest data
        from the store.

        :returns: None
        """
        if self.auto_update:
            self.config = TimeBasedConfigStore(
                self.table,
                self.store_name,
                self.store_key,
                self.option_key,
                update_interval=self.update_interval)

    def set(self, option, data):
        """ Upsert a config item

        A write towards DynamoDB will be executed when this method is called.

        :type option: str
        :param option: Name of the configuration option
        :type data: dict
        :param data: Dictionary with all option data
        :returns: bool -- True if the data was stored successfully
        """
        data[self.store_key] = self.store_name
        data[self.option_key] = option

        return self.table.put_item(data, overwrite=True)
