""" Time based config store

This config store updates the configuration every x seconds
"""
import threading
import time

from boto.dynamodb2.exceptions import ItemNotFound

from dynamodb_config_store.config_stores import ConfigStore


class TimeBasedConfigStore(ConfigStore):
    """ Fetches Stores on a periodic interval from DynamoDB

    All internal variables and methods are private (with an leading _), as
    the configuration options from DynamoDB will be set as instance attributes.
    """

    _option_key = None      # Option key in DynamoDB
    _populated = False      # True when the first population has been done
    _store_key = None       # Store key in DynamoDB
    _store_name = None      # Name of the Store
    _table = None           # boto.dynamodb2.table.Table
    _update_interval = 300  # How often, in seconds, to fetch updates

    def __init__(
            self, table, store_name, store_key, option_key,
            update_interval=300):
        """ Constructor for the TimeBasedConfigStore

        :type table: boto.dynamodb2.table.Table
        :param table: Table instance
        :type store_name: str
        :param store_name: Name of the DynamoDB Config Store
        :type store_key: str
        :param store_key: Key name for the store in DynamoDB. Default _store
        :type option_key: str
        :param option_key: Key name for the option in DynamoDB. Default _option
        :type update_interval: int
        :param update_interval: How often, in seconds, to fetch updates
        :returns: None
        """
        self._option_key = option_key
        self._store_key = store_key
        self._store_name = store_name
        self._table = table
        self._update_interval = update_interval

        thread = threading.Thread(target=self._run, args=())
        thread.daemon = True
        thread.start()

        while not self._populated:
            time.sleep(0.5)

    def _run(self):
        """ Run periodic fetcher

        :returns: None
        """
        while True:
            # Get options from DynamoDB
            options = self._fetch_options()

            # Delete old attributes
            self._delete_instance_attributes()

            # Populate the attribute list with the new attributes
            self._attributes = [key for key in options.keys()]

            # Add new attributes
            self._set_instance_attributes(options)

            self._populated = True

            time.sleep(self._update_interval)

    def _fetch_options(self):
        """ Retrieve a dictionary with all options and values from DynamoDB

        :returns: dict -- Dict with {'option': {'key': 'value'}}
        """
        try:
            items = {}
            query = {'{}__eq'.format(self._store_key): self._store_name}

            for item in self._table.query_2(**query):
                option = item[self._option_key]

                # Remove metadata
                del item[self._store_key]
                del item[self._option_key]

                items[option] = {k: v for k, v in item.items()}

            return items

        except ItemNotFound:
            return {}
