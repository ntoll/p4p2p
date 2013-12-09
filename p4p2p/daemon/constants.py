# -*- coding: utf-8 -*-
"""
Defines constants used by P4P2P. Usually these are based upon concepts from
the Kademlia DHT and where possible naming is derived from the original
Kademlia paper as are the suggested default values.
"""

#: Represents the degree of parallelism in network calls.
ALPHA = 3

#: The maximum number of contacts stored in a bucket. Must be an even number.
K = 20

#: The default maximum time a NodeLookup is allowed to take (in seconds).
LOOKUP_TIMEOUT = 600

#: The timeout for network connections (in seconds).
RPC_TIMEOUT = 5

#: The timeout for receiving complete message once a connection is made (in
#: seconds). Ensures there are no stale deferreds in the node's _pending
#: dictionary.
RESPONSE_TIMEOUT = 1800  # half an hour

#: How long to wait before an unused bucket is refreshed (in seconds).
REFRESH_TIMEOUT = 3600  # 1 hour

#: How long to wait before a node replicates any data it stores (in seconds).
REPLICATE_INTERVAL = REFRESH_TIMEOUT

#: How long to wait before a node checks whether any buckets need refreshing or
#: data needs republishing (in seconds).
REFRESH_INTERVAL = REFRESH_TIMEOUT / 6  # Every 10 minutes.

#: The number of failed remote procedure calls allowed for a peer node. If this
#: is equalled or exceeded then the contact is removed from the routing table.
ALLOWED_RPC_FAILS = 5

#: The number of nodes to attempt to use to store a value in the network.
DUPLICATION_COUNT = K

#: The duration (in seconds) that is added to a value's creation time in order
#: to work out its expiry timestamp. -1 denotes no expiry point.
EXPIRY_DURATION = -1

#: Defines the errors that can be reported between nodes in the network.
ERRORS = {
    # The message simply didn't make any sense.
    1: 'Bad message',
    # The message was parsed but not recognised.
    2: 'Unknown message type',
    # The message was parsed and recognised but the node encountered a problem
    # when dealing with it.
    3: 'Internal error',
    # The message was too big for the node to handle.
    4: 'Message too big',
    # Unsupported version of the protocol.
    5: 'Unsupported protocol',
    # The message could not be cryptographically verified.
    6: 'Unverifiable provenance'
}
