# -*- coding: utf-8 -*-
"""
Ensures details of contacts (peer nodes on the network) are represented
correctly.
"""
from hashlib import sha512
from p4p2p.dht.contact import PeerNode
from p4p2p.version import get_version
from .keys import PUBLIC_KEY
import unittest


class TestPeerNode(unittest.TestCase):
    """
    Ensures the PeerNode class works as expected.
    """

    def test_init(self):
        """
        Ensures an object is created as expected.
        """
        address = '192.168.0.1'
        port = 9999
        version = get_version()
        last_seen = 123
        contact = PeerNode(PUBLIC_KEY, address, port, version, last_seen)
        hex_digest = sha512(PUBLIC_KEY.encode('ascii')).hexdigest()
        self.assertEqual(contact.network_id, '0x' + hex_digest)
        self.assertEqual(address, contact.ip_address)
        self.assertEqual(port, contact.port)
        self.assertEqual(version, contact.version)
        self.assertEqual(last_seen, contact.last_seen)
        self.assertEqual(0, contact.failed_RPCs)

    def test_eq(self):
        """
        Makes sure equality works between a string representation of an ID and
        a PeerNode object.
        """
        network_id = '0x' + sha512(PUBLIC_KEY.encode('ascii')).hexdigest()
        address = '192.168.0.1'
        port = 9999
        version = get_version()
        last_seen = 123
        contact = PeerNode(PUBLIC_KEY, address, port, version, last_seen)
        self.assertTrue(network_id == contact)

    def test_eq_other_peer(self):
        """
        Ensure equality works between two PeerNode instances.
        """
        address = '192.168.0.1'
        port = 9999
        version = get_version()
        last_seen = 123
        contact1 = PeerNode(PUBLIC_KEY, address, port, version, last_seen)
        contact2 = PeerNode(PUBLIC_KEY, address, port, version, last_seen)
        self.assertTrue(contact1 == contact2)

    def test_eq_wrong_type(self):
        """
        Ensure equality returns false if comparing a PeerNode with some other
        type of object.
        """
        address = '192.168.0.1'
        port = 9999
        version = get_version()
        last_seen = 123
        contact = PeerNode(PUBLIC_KEY, address, port, version, last_seen)
        self.assertFalse(12345 == contact)

    def test_ne(self):
        """
        Makes sure non-equality works between a string representation of an ID
        and a PeerNode object.
        """
        address = '192.168.0.1'
        port = 9999
        version = get_version()
        last_seen = 123
        contact = PeerNode(PUBLIC_KEY, address, port, version, last_seen)
        self.assertTrue('54321' != contact)

    def test_str(self):
        """
        Ensures the string representation of a PeerContact is something
        useful.
        """
        network_id = '0x' + sha512(PUBLIC_KEY.encode('ascii')).hexdigest()
        address = '192.168.0.1'
        port = 9999
        version = get_version()
        last_seen = 123
        contact = PeerNode(PUBLIC_KEY, address, port, version, last_seen)
        expected = str((network_id, PUBLIC_KEY, address, port, version,
                       last_seen, 0))
        self.maxDiff = None
        self.assertEqual(expected, str(contact))
