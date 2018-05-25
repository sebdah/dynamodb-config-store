""" Setup script for PyPI """
import os
from setuptools import setup
import sys
if sys.version_info.major > 2:
    from configparser import ConfigParser as SafeConfigParser
else:
    from ConfigParser import SafeConfigParser

settings = SafeConfigParser()
settings.read(os.path.realpath('dynamodb_config_store/settings.conf'))

setup(
    name='dynamodb-config-store',
    version=settings.get('general', 'version'),
    license='Apache License, Version 2.0',
    description='Store configuration details in DynamoDB',
    author='Sebastian Dahlgren',
    author_email='sebastian.dahlgren@gmail.com',
    url='https://github.com/sebdah/dynamodb-config-store/',
    keywords="dynamodb aws config configuration amazon web services",
    platforms=['Any'],
    packages=['dynamodb_config_store'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'boto>=2.29.1'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ]
)
