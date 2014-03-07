# -*- coding: utf-8 -*-
"""
Ensures the generic functions used in various places within the daemon work
as expected.
"""
from p4p2p.dht.utils import distance, sort_peer_nodes
from p4p2p.dht.contact import PeerNode
from p4p2p.dht import constants
from p4p2p.version import get_version
from .keys import PUBLIC_KEY
import unittest


class TestUtils(unittest.TestCase):
    """
    Ensures the generic utility functions work as expected.
    """

    def setUp(self):
        """
        Common vars.
        """
        self.version = get_version()

    def test_distance(self):
        """
        Sanity check to ensure the XOR'd values return the correct distance.
        """
        key1 = '0xdeadbeef'
        key2 = '0xbeefdead'
        expected = int(key1, 0) ^ int(key2, 0)
        actual = distance(key1, key2)
        self.assertEqual(expected, actual)

    def test_sort_peer_nodes(self):
        """
        Ensures that the sort_peer_nodes function returns the list ordered in
        such a way that the contacts closest to the target key are at the head
        of the list.
        """
        contacts = []
        for i in range(512):
            contact = PeerNode(PUBLIC_KEY, "192.168.0.%d" % i, 9999,
                               self.version, 0)
            contact.network_id = hex(2 ** i)
            contacts.append(contact)
        target_key = hex(2 ** 256)
        result = sort_peer_nodes(contacts, target_key)

        # Ensure results are in the correct order.
        def key(node):
            return distance(node.network_id, target_key)
        sorted_nodes = sorted(result, key=key)
        self.assertEqual(sorted_nodes, result)
        # Ensure the order is from lowest to highest in terms of distance
        distances = [distance(x.network_id, target_key) for x in result]
        self.assertEqual(sorted(distances), distances)

    def test_sort_peer_nodes_no_longer_than_k(self):
        """
        Ensure that no more than constants.K contacts are returned from the
        sort_peer_nodes function despite a longer list being passed in.
        """
        contacts = []
        for i in range(512):
            contact = PeerNode(PUBLIC_KEY, "192.168.0.%d" % i, 9999,
                               self.version, 0)
            contact.network_id = hex(2 ** i)
            contacts.append(contact)
        target_key = hex(2 ** 256)
        result = sort_peer_nodes(contacts, target_key)
        self.assertEqual(constants.K, len(result))
