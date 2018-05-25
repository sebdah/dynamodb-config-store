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
import sys
if sys.version_info.major > 2:
    from configparser import ConfigParser as SafeConfigParser
else:
    from ConfigParser import SafeConfigParser

from boto.dynamodb2.exceptions import (
    LimitExceededException,
    ProvisionedThroughputExceededException,
    ResourceInUseException,
    ResourceNotFoundException,
    ValidationException)
from boto.dynamodb2.fields import HashKey, RangeKey
from boto.dynamodb2.table import Table
from boto.exception import JSONResponseError

from dynamodb_config_store.config_stores.simple import SimpleConfigStore
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

    config = None           # Instance of the a ConfigStore
    connection = None       # boto.dynamodb2.layer1.DynamoDBConnection instance
    option_key = None       # Key for the option (default: _option)
    read_units = None       # Number of read units to provision to new tables
    store_key = None        # Key for the store (default: _store)
    store_name = None       # Name of the Store
    config_store = None       # Store type to use
    config_store_args = None  # Store type arguments
    config_store_kwargs = None  # Store type key word args
    table = None            # boto.dynamodb2.table.Table instance
    table_name = None       # Name of the DynamoDB table
    write_units = None      # Number of write units to provision to new tables

    def __init__(
            self, connection, table_name, store_name,
            store_key='_store', option_key='_option',
            read_units=1, write_units=1,
            config_store='SimpleConfigStore',
            config_store_args=[], config_store_kwargs={}):
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
        :type config_store: str
        :param config_store: Store type to use
        :type config_store_args: list
        :param config_store_args: Store type arguments
        :type config_store_kwargs: dict
        :param config_store_kwargs: Store type key word arguments
        :returns: None
        """
        self.connection = connection
        self.option_key = option_key
        self.read_units = read_units
        self.store_key = store_key
        self.store_name = store_name
        self.table_name = table_name
        self.write_units = write_units
        self.config_store = config_store
        self.config_store_args = config_store_args
        self.config_store_kwargs = config_store_kwargs

        self._initialize_table()
        self._initialize_store()

    def _initialize_store(self):
        """ Initialize the store to use """
        if self.config_store == 'TimeBasedConfigStore':
            self.config = TimeBasedConfigStore(
                self.table,
                self.store_name,
                self.store_key,
                self.option_key,
                *self.config_store_args,
                **self.config_store_kwargs)
        elif self.config_store == 'SimpleConfigStore':
            self.config = SimpleConfigStore(
                self.table,
                self.store_name,
                self.store_key,
                self.option_key,
                *self.config_store_args,
                **self.config_store_kwargs)
        else:
            raise NotImplementedError

    def _initialize_table(self):
        """ Initialize the table

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

    def reload(self):
        """ Reload the config store

        :returns: None
        """
        self._initialize_store()

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

        try:
            return self.table.put_item(data, overwrite=True)
        except LimitExceededException:
            raise
        except ProvisionedThroughputExceededException:
            raise
        except ResourceInUseException:
            raise
        except ResourceNotFoundException:
            raise
        except ValidationException:
            raise
        except Exception:
            raise
