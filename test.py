""" Unit tests for DynamoDB Config Store """

import unittest

from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.exceptions import ItemNotFound
from boto.dynamodb2.table import Table

from dynamodb_config_store import DynamoDBConfigStore

connection = DynamoDBConnection(
    aws_access_key_id='foo',
    aws_secret_access_key='bar',
    host='localhost',
    port=8000,
    is_secure=False)


class TestGet(unittest.TestCase):

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

    def test_update_with_new_value_fields(self):
        """ Test that we can completely change the value fields """
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
    suite_builder.addTest(unittest.makeSuite(TestSet))
    suite_builder.addTest(unittest.makeSuite(TestGet))

    return suite_builder

if __name__ == '__main__':
    test_suite = suite()

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)
