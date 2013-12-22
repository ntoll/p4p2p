# -*- coding: utf-8 -*-
"""
Code to implement routing tables.
"""

import time
import random
import constants
from bucket import BucketFull, Bucket
from utils import long_to_hex, hex_to_long, sort_peer_nodes


class RoutingTable(object):
    """
    From the original Kademlia paper:

    "The routing table is a binary tree whose leaves are k-buckets. Each
    k-bucket contains nodes with some common prefix in their ID. The prefix is
    the k-bucket's position in the the binary tree. Thus, each k-bucket covers
    some range of the ID space, and together the k-buckets cover the entire
    512-bit ID space with no overlap."
    """

    def __init__(self, parent_node_id):
        """
        The parent_node_id is the 512-bit ID of the node to which this routing
        table belongs.
        """
        # Create the initial (single) bucket covering the range of the
        # entire 512-bit ID space
        self._buckets = [Bucket(range_min=0, range_max=2 ** 512)]
        self._parent_node_id = parent_node_id
        # Cache containing nodes eligible to replace stale bucket entries
        self._replacement_cache = {}
        # Set of nodes (network_ids) that have been blacklisted due to "bad"
        # behaviour.
        self._blacklist = set()

    def _bucket_index(self, key):
        """
        Returns the index of the bucket responsible for the specified key
        string.
        """
        if isinstance(key, str):
            key = hex_to_long(key)
        # Bound check for key too small.
        if key < 0:
            raise ValueError('Key out of range')
        for i, bucket in enumerate(self._buckets):
            if bucket.key_in_range(key):
                return i
        # Key was too big given the key space.
        raise ValueError('Key out of range.')

    def _random_key_in_bucket_range(self, bucket_index):
        """
        Returns a random key in the specified bucket's range.
        """
        keyValue = random.randrange(self._buckets[bucket_index].range_min,
                                    self._buckets[bucket_index].range_max)
        return long_to_hex(keyValue)

    def _split_bucket(self, old_bucket_index):
        """
        Splits the specified bucket into two new buckets which together
        cover the same range in the key/ID space.
        """
        # Resize the range of the current (old) bucket.
        old_bucket = self._buckets[old_bucket_index]
        split_point = old_bucket.range_max - (
            old_bucket.range_max - old_bucket.range_min) / 2
        # Create a new bucket to cover the range split off from the old
        # bucket.
        new_bucket = Bucket(split_point, old_bucket.range_max)
        old_bucket.range_max = split_point
        # Now, add the new bucket into the routing table.
        self._buckets.insert(old_bucket_index + 1, new_bucket)
        # Finally, copy all nodes that belong to the new bucket into it...
        for contact in old_bucket._contacts:
            if new_bucket.key_in_range(contact.network_id):
                new_bucket.add_contact(contact)
        # ...and remove them from the old bucket
        for contact in new_bucket._contacts:
            old_bucket.remove_contact(contact)

    def blacklist(self, contact):
        """
        Marks the referenced contact as blacklisted because it has misbehaved
        in some way. For example, it may have attempted to propagate a non
        valid value or responded to a node lookup with an incorrect response.
        Once blacklisted a contact is never allowed to be in the routing
        table or replacement cache.
        """
        self.remove_contact(contact.network_id, forced=True)
        self._blacklist.add(contact.network_id)

    def add_contact(self, contact):
        """
        Add the given contact (PeerNode) to the correct bucket; if it already
        exists, its status will be updated.
        """
        if contact.network_id in self._blacklist:
            return
        if contact.network_id == self._parent_node_id:
            return
        # Initialize/reset the "failed RPC" counter since adding it to the
        # routing table is the result of a successful RPC.
        contact.failed_RPCs = 0
        bucket_index = self._bucket_index(contact.network_id)
        try:
            self._buckets[bucket_index].add_contact(contact)
        except BucketFull:
            # The bucket is full; see if it can be split (by checking if its
            # range includes the host node's id)
            if self._buckets[bucket_index].key_in_range(self._parent_node_id):
                self._split_bucket(bucket_index)
                # Retry the insertion attempt
                self.add_contact(contact)
            else:
                # We can't split the k-bucket
                #
                # NOTE: This implementation follows section 4.1 of the 13 page
                # version of the Kademlia paper (optimized contact accounting
                # without PINGs - results in much less network traffic, at the
                # expense of some memory)
                #
                # Put the new contact in our replacement cache for the
                # corresponding k-bucket (or update it's position if it exists
                # already).
                if not bucket_index in self._replacement_cache:
                    self._replacement_cache[bucket_index] = []
                if contact in self._replacement_cache[bucket_index]:
                    self._replacement_cache[bucket_index].remove(contact)
                elif len(self._replacement_cache[bucket_index]) >= constants.K:
                    # Use k to limit the size of the contact replacement cache.
                    self._replacement_cache[bucket_index].pop(0)
                self._replacement_cache[bucket_index].append(contact)

    def find_close_nodes(self, key, network_id=None):
        """
        Finds up to "K" number of known nodes closest to the node/value with
        the specified key. If network_id is supplied the referenced node will
        be excluded from the returned contacts.

        The result is a list of "K" node contacts of type PeerNode. Will only
        return fewer than "K" contacts if not enough contacts are known.

        The result is ordered from closest to furthest away from the target
        key.
        """
        bucket_index = self._bucket_index(key)
        closest_nodes = self._buckets[bucket_index].get_contacts(
            constants.K, network_id)
        # How far away to jump beyond the containing bucket of the given key.
        bucket_jump = 1
        number_of_buckets = len(self._buckets)
        # Flags that indicate if it's possible to jump higher or lower through
        # the buckets.
        can_go_lower = bucket_index - bucket_jump >= 0
        can_go_higher = bucket_index + bucket_jump < number_of_buckets
        while (len(closest_nodes) <
               constants.K and (can_go_lower or can_go_higher)):
            # Continue to fill the closestNodes list with contacts from the
            # nearest unchecked neighbouring buckets. Have chosen to opt for
            # readability rather than conciseness.
            if can_go_lower:
                # Neighbours lower in the key index.
                remaining_slots = constants.K - len(closest_nodes)
                jump_to_neighbour = bucket_index - bucket_jump
                neighbour = self._buckets[jump_to_neighbour]
                contacts = neighbour.get_contacts(remaining_slots, network_id)
                closest_nodes.extend(contacts)
                can_go_lower = bucket_index - (bucket_jump + 1) >= 0
            if can_go_higher:
                # Neighbours higher in the key index.
                remaining_slots = constants.K - len(closest_nodes)
                jump_to_neighbour = bucket_index + bucket_jump
                neighbour = self._buckets[jump_to_neighbour]
                contacts = neighbour.get_contacts(remaining_slots, network_id)
                closest_nodes.extend(contacts)
                can_go_higher = (bucket_index + (bucket_jump + 1) <
                                 number_of_buckets)
            bucket_jump += 1

        # Order the nodes from closest to furthest away from the target key and
        # ensure we only return K contacts (in certain circumstances K+1
        # results are generated).
        return sort_peer_nodes(closest_nodes, key)

    def get_contact(self, network_id):
        """
        Returns the (known) contact with the specified network ID. Will raise
        a ValueError if no contact with the specified ID is known.
        """
        bucket_index = self._bucket_index(network_id)
        contact = self._buckets[bucket_index].get_contact(network_id)
        return contact

    def get_refresh_list(self, start_index=0, force=False):
        """
        Finds all buckets that need refreshing, starting at the
        bucket with the specified index. This bucket and those further away
        from it will be refreshed. Returns network_ids to be searched for
        in order to refresh those buckets in the routing table. If the
        "force" parameter is True then all buckets with the specified range
        will be refreshed, regardless of the time they were last accessed.
        """
        bucket_index = start_index
        refresh_IDs = []
        now = int(time.time())
        for bucket in self._buckets[start_index:]:
            last_refreshed = now - bucket.last_accessed
            if force or last_refreshed >= constants.REFRESH_TIMEOUT:
                search_ID = self._random_key_in_bucket_range(bucket_index)
                refresh_IDs.append(search_ID)
            bucket_index += 1
        return refresh_IDs

    def remove_contact(self, network_id, forced=False):
        """
        Attempt to remove the contact (PeerNode) with the specified network_id
        from the routing table.

        The operation will only succeed if either the number of failed RPCs
        made against the contact is >= constants.ALLOWED_RPC_FAILS or the
        'forced' flag is set to True (defaults to False).

        If there are any contacts in the replacement cache for the affected
        bucket then the most up-to-date contact in the replacement cache will
        be used as a replacement.
        """
        bucket_index = self._bucket_index(network_id)
        try:
            contact = self._buckets[bucket_index].get_contact(network_id)
        except ValueError:
            # Fail silently since the contact isn't in the routing table
            # anyway.
            return
        contact.failed_RPCs += 1
        if forced or contact.failed_RPCs >= constants.ALLOWED_RPC_FAILS:
            # Remove the contact from the bucket.
            self._buckets[bucket_index].remove_contact(network_id)
            if bucket_index in self._replacement_cache:
                # If required, remove the old contact from the replacement
                # cache.
                if contact in self._replacement_cache[bucket_index]:
                    self._replacement_cache[bucket_index].remove(contact)
                # If possible, replace the stale contact with the most recent
                # contact stored in the replacement cache.
                if len(self._replacement_cache[bucket_index]) > 0:
                    self._buckets[bucket_index].add_contact(
                        self._replacement_cache[bucket_index].pop())

    def touch_bucket(self, key):
        """
        Update the lastAccessed timestamp of the bucket which covers
        the range containing the specified key string in the key/ID space.

        The lastAccessed field is used to ensure a bucket doesn't become
        stale.
        """
        bucket_index = self._bucket_index(key)
        self._buckets[bucket_index].last_accessed = int(time.time())
