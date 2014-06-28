Release notes
=============

0.2.2 (2014-06-28)
------------------

* Address common DynamoDB exceptions (`#17 <https://github.com/sebdah/dynamodb-config-store/issues/17>`_)

0.2.1 (2014-06-28)
------------------

* Throw exception if not implemented config store is used (`#16 <https://github.com/sebdah/dynamodb-config-store/issues/16>`_)
* Renamed ``store_type`` parameter to ``config_store``

0.2.0 (2014-06-27)
------------------

* Modular config store design implemented (`#15 <https://github.com/sebdah/dynamodb-config-store/issues/15>`_)
* Implement TimeBasedConfigStore for automatic config reloading (`#14 <https://github.com/sebdah/dynamodb-config-store/issues/14>`_)

0.1.1 (2014-06-26)
------------------

* Fixed broken reference to license in PyPI script (`#13 <https://github.com/sebdah/dynamodb-config-store/issues/13>`_)

0.1.0 (2014-06-26)
------------------

* Initial release of DynamoDB Config Store
* Support for ``get()``
* Support for ``get_object()``
* Support for ``set()``
* Table schema is validated upon instanciation
* Tables are created if the do not exist
* Full test suite implemented
