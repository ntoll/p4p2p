# -*- coding: utf-8 -*-
"""
Defines a peer node on the network.
"""
from utils import long_to_hex


class PeerNode(object):
    """
    Represents another node on the network.
    """

    def __init__(self, network_id, ip_address, port, version, last_seen=0):
        """
        Initialise the peer node with a unique id within the network, IP
        address, port, the p4p2p version the contact is running and a
        timestamp indicating when the last connection was made with the
        contact (defaults to 0). The network id, if passed in as a numeric
        value, will be converted into a hexadecimal string.
        """
        if isinstance(network_id, long) or isinstance(network_id, int):
            self.network_id = long_to_hex(network_id)
        else:
            self.network_id = network_id
        self.ip_address = ip_address
        self.port = port
        self.version = version
        self.last_seen = last_seen
        # failed_RPCs keeps track of the number of failed RPCs to this peer.
        # If this number reaches a threshold then it is evicted from a
        # bucket and replaced with another node that is more reliable.
        self.failed_RPCs = 0

    def __eq__(self, other):
        """
        Override equals to work with a string representation of the contact's
        id.
        """
        if isinstance(other, PeerNode):
            return self.network_id == other.network_id
        elif isinstance(other, basestring):
            return self.network_id == other
        else:
            return False

    def __ne__(self, other):
        """
        Override != to work with a string representation of the contact's id.
        """
        return not self == other

    def __repr__(self):
        """
        Returns a tuple containing information about this contact.
        """
        return str((self.network_id, self.ip_address, self.port, self.version,
                    self.last_seen, self.failed_RPCs))

    def __str__(self):
        """
        Override the string representation of the object to be something
        useful.
        """
        return self.__repr__()
