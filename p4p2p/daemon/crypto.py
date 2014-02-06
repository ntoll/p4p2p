# -*- coding: utf-8 -*-
"""
Functions for signing and verifying messages sent between peers. Messages are
represented by dict objects.
"""
import time
import base64
import copy
from Crypto.Hash import SHA512
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
    sig = base64.encodebytes(signer.sign(root_hash)).decode('utf-8')
    signed_message['_p4p2p']['signature'] = sig
    return signed_message


def verify_message(message):
    """
    Returns a boolean to indicate if the message can be verified.
    """
    try:
        msg_no_sig = copy.deepcopy(message)
        raw_sig = msg_no_sig['_p4p2p']['signature']
        signature = base64.decodebytes(raw_sig.encode('utf-8'))
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
    elif obj_type is list:
        hash_list = []
        for item in obj:
            hash_list.append(_get_hash(item).hexdigest())
        seed = ''.join(hash_list)
    elif obj_type is bool:
        seed = str(obj).lower()
    elif obj_type is float:
        seed = repr(obj)
    elif obj is None:
        seed = 'null'
    else:
        seed = str(obj)
    return SHA512.new(seed.encode('utf-8'))
