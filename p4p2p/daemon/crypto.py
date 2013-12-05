# -*- coding: utf-8 -*-
"""
Functions for signing and verifying messages sent between peers. Messages are
represented by dict objects.
"""
import time
from Crypto.Hash import SHA512
from types import NoneType
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA


def get_signed_message(message, public_key, private_key):
    """
    Returns a copy of the passed in message that has been signed using the
    private_key and annotated with metadata under the "_p4p2p" key (a
    timestamp indicating when the message was signed, the public_key and the
    signature).
    """
    signed_message = message.copy()
    signed_message['_p4p2p'] = {
        'timestamp': time.time(),
        'public_key': public_key
    }
    root_hash = _get_hash(signed_message)
    key = RSA.importKey(private_key)
    signer = PKCS1_v1_5.new(key)
    signed_message['_p4p2p']['signature'] = signer.sign(root_hash)
    return signed_message


def verify_message(message):
    """
    Returns a boolean to indicate if the message can be verified.
    """
    try:
        msg_no_sig = message.copy()
        signature = msg_no_sig['_p4p2p']['signature']
        public_key = RSA.importKey(msg_no_sig['_p4p2p']['public_key'])
        del msg_no_sig['_p4p2p']['signature']
        root_hash = _get_hash(msg_no_sig)
        verifier = PKCS1_v1_5.new(public_key)
        return verifier.verify(root_hash, signature)
    except:
        # TODO: do something with this..? (Probably not - tbc)
        pass
    return False


def _get_hash(obj):
    """
    Returns a SHA512 object for the given object. Works in a similar fashion
    to a Merkle tree (see https://en.wikipedia.org/wiki/Merkle_tree) should
    the object be tree like in structure - but only returns the "root" hash.
    """
    obj_type = type(obj)
    if obj_type is dict:
        hash_list = []
        for k in sorted(obj):
            hash_list.append(_get_hash(k).hexdigest())
            hash_list.append(_get_hash(obj[k]).hexdigest())
        seed = ''.join(hash_list)
        return SHA512.new(seed)
    elif obj_type is list:
        hash_list = []
        for item in obj:
            hash_list.append(_get_hash(item).hexdigest())
        seed = ''.join(hash_list)
        return SHA512.new(seed)
    elif obj_type is NoneType:
        return SHA512.new('null')
    elif obj_type is bool:
        return SHA512.new(str(obj).lower())
    else:
        return SHA512.new(str(obj))
