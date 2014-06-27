""" Config Store base class """


class ConfigStore(object):
    """ Base class for config stores """

    _attributes = []        # List of set instance attributes

    def _delete_instance_attributes(self):
        """ Delete all the instance attributes

        :returns: None
        """
        for attr in self._attributes:
            delattr(self, attr)

    def _set_instance_attributes(self, options):
        """ Set instance attributes

        :type options: dict
        :param options: Dict with {'option': {'key': 'value'}}
        :returns: None
        """
        [setattr(self, key, options[key]) for key in options.keys()]
