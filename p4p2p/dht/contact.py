# -*- coding: utf-8 -*-
"""
Defines a peer node on the network.
"""
from hashlib import sha512


class PeerNode(object):
    """
    Represents another node on the network.
    """

    def __init__(self, public_key, ip_address, port, version, last_seen=0):
        """
        Initialise the peer node with a unique id within the network (derived
        from its public key), IP address, port the p4p2p version the contact
        is running and a timestamp indicating when the last connection was
        made with the contact (defaults to 0).

        The network id is created as the hexdigest of the SHA512 of the public
        key.
        """
        hex_digest = sha512(public_key.encode('ascii')).hexdigest()
        self.network_id = '0x' + hex_digest
        self.public_key = public_key
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
        elif isinstance(other, str):
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
        return str((self.network_id, self.public_key, self.ip_address,
                    self.port, self.version, self.last_seen,
                    self.failed_RPCs))

    def __str__(self):
        """
        Override the string representation of the object to be something
        useful.
        """
        return self.__repr__()
