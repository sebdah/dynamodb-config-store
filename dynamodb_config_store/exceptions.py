""" Exception definitions """


class TableNotCreatedException(Exception):
    """ Exception thrown if the table could not be created successfull """
    pass


class TableNotReadyException(Exception):
    """ Exception thrown if the table is not in ACTIVE or UPDATING state """
    pass


class MisconfiguredSchemaException(Exception):
    """ Exception thrown if the table does not match the configuration """
    pass
