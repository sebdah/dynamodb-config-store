tests:
	python test.py

dynamodb_local:
	java -Djava.library.path=./dynamodb-local/DynamoDBLocal_lib -jar ./dynamodb-local/DynamoDBLocal.jar --inMemory

install:
	python setup.py build
	python setup.py install

release:
	python setup.py register
	python setup.py sdist upload
