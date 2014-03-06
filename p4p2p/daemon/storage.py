# -*- coding: utf-8 -*-
"""
Contains class definitions that define the local data store for the node.
"""

from collections import MutableMapping
import time


class DataStore(MutableMapping):
    """
    Base class for implementations of the storage mechanism for local nodes.

    Values are actually stored along with meta-data:

    * a timestamp indicating the last update in local data store.
    * the publisher's public key.
    * the original creation / publication timestamp according to the
      publisher.

    Regular Python dict operations work "as expected" but additional
    updated, publisher and pub_time methods allow access to metadata for
    a specific key.

    The __get_item__ and __setitem__ methods silently handle the metadata
    requirements and actually call the _get_item and _set_item methods in
    which the storage and retrieval of items should be handled / overridden.
    """

    def __delitem__(self, key):
        '''
        Remove an item from the data store.
        '''
        raise NotImplementedError('del needs implementing.')

    def __getitem__(self, key):
        '''
        Return a value for a given key.
        '''
        return self._get_item(key)[0]

    def __iter__(self):
        """
        Iterate over the data store.
        """
        raise NotImplementedError('Iteration needs implementing.')

    def __len__(self):
        """
        Determine the number of items in the data store.
        """
        raise NotImplementedError('len(obj) needs implementing.')

    def __setitem__(self, key, value):
        """
        Associate a key with a specified value.
        """
        updated_on = time.time()
        self._set_item(key, (value, updated_on))

    def keys(self):
        """
        Return a list of the keys in this data store.
        """
        raise NotImplementedError('keys() method needs implementing.')

    def updated(self, key):
        """
        Get the timestamp when a key/value pair identified by the key were
        last updated in this data store.
        """
        return self._get_item(key)[1]

    def publisher(self, key):
        """
        Get the public key of the original publisher of the key/value pair
        identified by "key".
        """
        return self._get_item(key)[0]['_p4p2p']['public_key']

    def created(self, key):
        """
        Get the time that an item identified by the key was originally
        created / published according to the publisher.
        """
        return self._get_item(key)[0]['_p4p2p']['timestamp']

    def _set_item(self, key, value):
        """
        Set the value of the key/value pair identified by "key"; this should
        set the "last published" value for the key/value pair to the current
        time.
        """
        raise NotImplementedError('_set_item(key, value) to be implemented.')

    def _get_item(self, key):
        """
        Get the value (a tuple containing the original value and a timestamp)
        for the given key.
        """
        raise NotImplementedError('_get_item(key) needs implementing.')


class DictDataStore(DataStore):
    """
    A datastore using Python's in-memory dictionary.
    """

    def __init__(self):
        self._dict = {}

    def __delitem__(self, key):
        """
        Delete the specified key (and its value)
        """
        del self._dict[key]

    def __iter__(self):
        """
        Iterates over the content of the data store.
        """
        return self._dict.__iter__()

    def __len__(self):
        """
        Returns the number of items in the data store.
        """
        return len(self._dict)

    def keys(self):
        """
        Return a view object of the keys in this data store.
        """
        return self._dict.keys()

    def _set_item(self, key, value):
        """
        Set the value of the key/value pair identified by key.
        """
        self._dict[key] = value

    def _get_item(self, key):
        """
        Get a named value from the data store.
        """
        return self._dict[key]
