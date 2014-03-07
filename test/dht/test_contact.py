# -*- coding: utf-8 -*-
"""
Ensures details of contacts (peer nodes on the network) are represented
correctly.
"""
from p4p2p.dht.contact import PeerNode
from p4p2p.version import get_version
import unittest


class TestPeerNode(unittest.TestCase):
    """
    Ensures the PeerNode class works as expected.
    """

    def test_init(self):
        """
        Ensures an object is created as expected.
        """
        network_id = '12345'
        address = '192.168.0.1'
        port = 9999
        version = get_version()
        last_seen = 123
        contact = PeerNode(network_id, address, port, version, last_seen)
        self.assertEqual(network_id, contact.network_id)
        self.assertEqual(address, contact.ip_address)
        self.assertEqual(port, contact.port)
        self.assertEqual(version, contact.version)
        self.assertEqual(last_seen, contact.last_seen)
        self.assertEqual(0, contact.failed_RPCs)

    def test_init_with_long_id(self):
        """
        If the ID is passed in as a long value ensure it's translated to the
        correct string representation of the hex version.
        """
        network_id = 12345
        address = '192.168.0.1'
        port = 9999
        version = get_version()
        last_seen = 123
        contact = PeerNode(network_id, address, port, version, last_seen)
        expected = hex(12345)
        self.assertEqual(expected, contact.network_id)
        self.assertEqual(12345, int(contact.network_id, 0))

    def test_init_with_int_id(self):
        """
        If the ID is passed in as an int value ensure it's translated to the
        correct string representation of the hex version.
        """
        network_id = 12345
        address = '192.168.0.1'
        port = 9999
        version = get_version()
        last_seen = 123
        contact = PeerNode(network_id, address, port, version, last_seen)
        expected = hex(12345)
        self.assertEqual(expected, contact.network_id)
        self.assertEqual(12345, int(contact.network_id, 0))

    def test_eq(self):
        """
        Makes sure equality works between a string representation of an ID and
        a PeerNode object.
        """
        network_id = '12345'
        address = '192.168.0.1'
        port = 9999
        version = get_version()
        last_seen = 123
        contact = PeerNode(network_id, address, port, version, last_seen)
        self.assertTrue(network_id == contact)

    def test_eq_other_peer(self):
        """
        Ensure equality works between two PeerNode instances.
        """
        network_id = '12345'
        address = '192.168.0.1'
        port = 9999
        version = get_version()
        last_seen = 123
        contact1 = PeerNode(network_id, address, port, version, last_seen)
        contact2 = PeerNode(network_id, address, port, version, last_seen)
        self.assertTrue(contact1 == contact2)

    def test_eq_wrong_type(self):
        """
        Ensure equality returns false if comparing a PeerNode with some other
        type of object.
        """
        network_id = '12345'
        address = '192.168.0.1'
        port = 9999
        version = get_version()
        last_seen = 123
        contact = PeerNode(network_id, address, port, version, last_seen)
        self.assertFalse(12345 == contact)

    def test_ne(self):
        """
        Makes sure non-equality works between a string representation of an ID
        and a PeerNode object.
        """
        network_id = '12345'
        address = '192.168.0.1'
        port = 9999
        version = get_version()
        last_seen = 123
        contact = PeerNode(network_id, address, port, version, last_seen)
        self.assertTrue('54321' != contact)

    def test_str(self):
        """
        Ensures the string representation of a PeerContact is something
        useful.
        """
        network_id = '12345'
        address = '192.168.0.1'
        port = 9999
        version = get_version()
        last_seen = 123
        contact = PeerNode(network_id, address, port, version, last_seen)
        expected = "('12345', '192.168.0.1', 9999, '%s', 123, 0)" % version
        self.assertEqual(expected, str(contact))
