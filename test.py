""" Unit tests for DynamoDB Config Store """

import unittest

from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.exceptions import ItemNotFound
from boto.dynamodb2.table import Table

from dynamodb_config_store import DynamoDBConfigStore
from dynamodb_config_store.exceptions import MisconfiguredSchemaException

connection = DynamoDBConnection(
    aws_access_key_id='foo',
    aws_secret_access_key='bar',
    host='localhost',
    port=8000,
    is_secure=False)


class TestCustomStoreAndOptionKeys(unittest.TestCase):

    def setUp(self):

        # Configuration options
        self.table_name = 'conf'
        self.store_name = 'test'
        self.store_key = '_s'
        self.option_key = '_o'

        # Instanciate the store
        self.store = DynamoDBConfigStore(
            connection,
            self.table_name,
            self.store_name,
            store_key=self.store_key,
            option_key=self.option_key)

        # Get an Table instance for validation
        self.table = Table(self.table_name, connection=connection)

    def test_custom_store_and_option_keys(self):
        """ Test that we can set custom store and option keys """
        obj = {
            'host': '127.0.0.1',
            'port': 27017
        }

        # Insert the object
        self.store.set('db', obj)

        # Fetch the object directly from DynamoDB
        kwargs = {
            '_s': self.store_name,
            '_o': 'db'
        }
        item = self.table.get_item(**kwargs)

        self.assertEqual(item['_s'], self.store_name)
        self.assertEqual(item['_o'], 'db')
        self.assertEqual(item['host'], '127.0.0.1')
        self.assertEqual(item['port'], 27017)

    def tearDown(self):
        """ Tear down the test case """
        self.table.delete()


class TestGetOption(unittest.TestCase):

    def setUp(self):

        # Configuration options
        self.table_name = 'conf'
        self.store_name = 'test'

        # Instanciate the store
        self.store = DynamoDBConfigStore(
            connection,
            self.table_name,
            self.store_name)

        # Get an Table instance for validation
        self.table = Table(self.table_name, connection=connection)

    def test_get(self):
        """ Test that we can retrieve an object from the store """
        obj = {
            'endpoint': 'http://test.com',
            'port': 80,
            'username': 'test',
            'password': 'something'
        }

        # Insert the object
        self.store.set('api', obj)

        # Retrieve the object
        option = self.store.get('api')

        self.assertNotIn('_store', option)
        self.assertNotIn('_option', option)
        self.assertEqual(option['endpoint'], obj['endpoint'])
        self.assertEqual(option['port'], obj['port'])
        self.assertEqual(option['username'], obj['username'])
        self.assertEqual(option['password'], obj['password'])

    def test_get_item_not_found(self):
        """ Test that we can't retrieve non-existing items """
        with self.assertRaises(ItemNotFound):
            self.store.get('doesnotexist')

    def tearDown(self):
        """ Tear down the test case """
        self.table.delete()


class TestGetOptionAndKeysSubset(unittest.TestCase):

    def setUp(self):

        # Configuration options
        self.table_name = 'conf'
        self.store_name = 'test'

        # Instanciate the store
        self.store = DynamoDBConfigStore(
            connection,
            self.table_name,
            self.store_name)

        # Get an Table instance for validation
        self.table = Table(self.table_name, connection=connection)

    def test_get(self):
        """ Test that we can retrieve an object from the store """
        obj = {
            'endpoint': 'http://test.com',
            'port': 80,
            'username': 'test',
            'password': 'something'
        }

        # Insert the object
        self.store.set('api', obj)

        # Retrieve the object
        option = self.store.get('api', keys=['endpoint', 'port'])

        self.assertNotIn('_store', option)
        self.assertNotIn('_option', option)
        self.assertNotIn('username', option)
        self.assertNotIn('password', option)
        self.assertEqual(option['endpoint'], obj['endpoint'])
        self.assertEqual(option['port'], obj['port'])

    def tearDown(self):
        """ Tear down the test case """
        self.table.delete()


class TestGetFullStore(unittest.TestCase):

    def setUp(self):

        # Configuration options
        self.table_name = 'conf'
        self.store_name = 'test'

        # Instanciate the store
        self.store = DynamoDBConfigStore(
            connection,
            self.table_name,
            self.store_name)

        # Get an Table instance for validation
        self.table = Table(self.table_name, connection=connection)

    def test_get_of_full_store(self):
        """ Test that we can retrieve all objects in the store """
        objApi = {
            'endpoint': 'http://test.com',
            'port': 80,
            'username': 'test',
            'password': 'something'
        }
        objUser = {
            'username': 'luke',
            'password': 'skywalker'
        }

        # Insert the object
        self.store.set('api', objApi)
        self.store.set('user', objUser)

        # Retrieve all objects
        options = self.store.get()
        self.assertEquals(len(options), 2)
        optApi = options['api']
        optUser = options['user']

        self.assertNotIn('_store', optApi)
        self.assertNotIn('_option', optApi)
        self.assertEqual(optApi['endpoint'], objApi['endpoint'])
        self.assertEqual(optApi['port'], objApi['port'])
        self.assertEqual(optApi['username'], objApi['username'])
        self.assertEqual(optApi['password'], objApi['password'])

        self.assertNotIn('_store', optUser)
        self.assertNotIn('_option', optUser)
        self.assertEqual(optUser['username'], objUser['username'])
        self.assertEqual(optUser['password'], objUser['password'])

    def tearDown(self):
        """ Tear down the test case """
        self.table.delete()


class TestMisconfiguredSchemaException(unittest.TestCase):

    def setUp(self):

        # Configuration options
        self.table_name = 'conf'
        self.store_name = 'test'

        # Instanciate the store
        DynamoDBConfigStore(connection, self.table_name, self.store_name)

        # Get an Table instance for validation
        self.table = Table(self.table_name, connection=connection)

    def test_misconfigured_schema_store_key(self):
        """ Test that an exception is raised if the store key is not an hash """
        with self.assertRaises(MisconfiguredSchemaException):
            DynamoDBConfigStore(
                connection,
                self.table_name,
                self.store_name,
                store_key='test')

    def test_misconfigured_schema_option_key(self):
        """ Test that an exception is raised if the option key isn't a range """
        with self.assertRaises(MisconfiguredSchemaException):
            DynamoDBConfigStore(
                connection,
                self.table_name,
                self.store_name,
                option_key='test')

    def tearDown(self):
        """ Tear down the test case """
        self.table.delete()


class TestSet(unittest.TestCase):

    def setUp(self):

        # Configuration options
        self.table_name = 'conf'
        self.store_name = 'test'

        # Instanciate the store
        self.store = DynamoDBConfigStore(
            connection,
            self.table_name,
            self.store_name)

        # Get an Table instance for validation
        self.table = Table(self.table_name, connection=connection)

    def test_set(self):
        """ Test that we can insert an object """
        obj = {
            'host': '127.0.0.1',
            'port': 27017
        }

        # Insert the object
        self.store.set('db', obj)

        # Fetch the object directly from DynamoDB
        kwargs = {
            '_store': self.store_name,
            '_option': 'db'
        }
        item = self.table.get_item(**kwargs)

        self.assertEqual(item['_store'], self.store_name)
        self.assertEqual(item['_option'], 'db')
        self.assertEqual(item['host'], '127.0.0.1')
        self.assertEqual(item['port'], 27017)

    def test_update(self):
        """ Test that we can change values in an option """
        obj = {
            'username': 'luke',
            'password': 'skywalker'
        }

        # Insert the object
        self.store.set('user', obj)

        # Get the option
        option = self.store.get('user')
        self.assertEqual(option['username'], obj['username'])
        self.assertEqual(option['password'], obj['password'])

        # Updated version of the object
        updatedObj = {
            'username': 'anakin',
            'password': 'skywalker'
        }

        # Insert the object
        self.store.set('user', updatedObj)

        # Get the option
        option = self.store.get('user')
        self.assertEqual(option['username'], updatedObj['username'])
        self.assertEqual(option['password'], updatedObj['password'])

    def test_update_with_new_keys(self):
        """ Test that we can completely change the keys """
        obj = {
            'username': 'luke',
            'password': 'skywalker'
        }

        # Insert the object
        self.store.set('credentials', obj)

        # Get the option
        option = self.store.get('credentials')
        self.assertEqual(option['username'], obj['username'])
        self.assertEqual(option['password'], obj['password'])

        # Updated version of the object
        updatedObj = {
            'access_key': 'anakin',
            'secret_key': 'skywalker'
        }

        # Insert the object
        self.store.set('credentials', updatedObj)

        # Get the option
        option = self.store.get('credentials')
        self.assertEqual(option['access_key'], updatedObj['access_key'])
        self.assertEqual(option['secret_key'], updatedObj['secret_key'])
        self.assertNotIn('username', option)
        self.assertNotIn('password', option)

    def tearDown(self):
        """ Tear down the test case """
        self.table.delete()


def suite():
    """ Defines the test suite """
    suite_builder = unittest.TestSuite()
    suite_builder.addTest(unittest.makeSuite(TestMisconfiguredSchemaException))
    suite_builder.addTest(unittest.makeSuite(TestSet))
    suite_builder.addTest(unittest.makeSuite(TestGetOption))
    suite_builder.addTest(unittest.makeSuite(TestGetOptionAndKeysSubset))
    suite_builder.addTest(unittest.makeSuite(TestGetFullStore))
    suite_builder.addTest(unittest.makeSuite(TestCustomStoreAndOptionKeys))

    return suite_builder

if __name__ == '__main__':
    test_suite = suite()

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)
