# -*- coding: utf-8 -*-
"""
Contains generic utillity functions used in various different parts of
Drogulus.
"""
from constants import K


def long_to_hex(raw):
    """
    Given a raw numeric value (like a node's network ID for example) returns
    it expressed as a hexadecimal string.
    """
    # Turn it into hex string (remembering to drop the '0x' at the start).
    as_hex = hex(raw)[2:]
    # If the integer is 'long' knock off the 'L'.
    if as_hex[-1] == 'L':
        as_hex = as_hex[:-1]
    # If required, correct length by appending 'padding' zeros.
    if len(as_hex) % 2 != 0:
        as_hex = '0' + as_hex
    as_hex = as_hex.decode('hex')
    return as_hex


def hex_to_long(raw):
    """
    Given a hexadecimal string representation of a number (like a key or
    node's ID for example) returns the numeric (long) value.
    """
    return long(raw.encode('hex'), 16)


def distance(key_one, key_two):
    """
    Calculate the XOR result between two string variables returned as a long
    type value.
    """
    val_key_one = hex_to_long(key_one)
    val_key_two = hex_to_long(key_two)
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
