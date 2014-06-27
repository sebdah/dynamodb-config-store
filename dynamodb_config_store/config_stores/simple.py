""" The Simple Config Store implementation """
from boto.dynamodb2.exceptions import ItemNotFound

from dynamodb_config_store.config_stores import ConfigStore


class SimpleConfigStore(ConfigStore):
    """ SimpleConfigStore fetching configuration directly from DynamoDB

    This config store will always poll for the latest changes from DynamoDB.
    """

    _option_key = None      # Option key in DynamoDB
    _populated = False      # True when the first population has been done
    _store_key = None       # Store key in DynamoDB
    _store_name = None      # Name of the Store
    _table = None           # boto.dynamodb2.table.Table

    def __init__(self, table, store_name, store_key, option_key):
        """ Constructor for the SimpleConfigStore

        :type table: boto.dynamodb2.table.Table
        :param table: Table instance
        :type store_name: str
        :param store_name: Name of the DynamoDB Config Store
        :type store_key: str
        :param store_key: Key name for the store in DynamoDB. Default _store
        :type option_key: str
        :param option_key: Key name for the option in DynamoDB. Default _option
        :returns: None
        """
        self._option_key = option_key
        self._store_key = store_key
        self._store_name = store_name
        self._table = table

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
                query = {'{}__eq'.format(self._store_key): self._store_name}

                for item in self._table.query_2(**query):
                    option = item[self._option_key]

                    # Remove metadata
                    del item[self._store_key]
                    del item[self._option_key]

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
                self._store_key: self._store_name,
                self._option_key: option
            }

            item = self._table.get_item(**kwargs)

            del item[self._store_key]
            del item[self._option_key]

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
