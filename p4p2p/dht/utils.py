# -*- coding: utf-8 -*-
"""
Contains generic utillity functions used in various different parts of
Drogulus.
"""
from .constants import K


def distance(key_one, key_two):
    """
    Calculate the XOR result between two string representations of hex values.
    Returned as an int.
    """
    val_key_one = int(key_one, 0)
    val_key_two = int(key_two, 0)
    return val_key_one ^ val_key_two


def sort_peer_nodes(peer_nodes, target_key):
    """
    Given a list of peer nodes, efficiently sorts it so that the peers closest
    to the target key are at the head. If the list is longer than K then only
    the K closest contacts will be returned.
    """
    # Key function
    def node_key(node):
        """
        Returns the node's distance to the target key.
        """
        return distance(node.network_id, target_key)

    peer_nodes.sort(key=node_key)
    return peer_nodes[:K]
