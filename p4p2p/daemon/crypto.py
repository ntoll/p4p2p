# -*- coding: utf-8 -*-
"""
Functions for signing and verifying items sent between peers. Items are
represented by dict objects.
"""
import time
import base64
import copy
from Crypto.Hash import SHA512
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from ..version import get_version


def get_signed_item(item, public_key, private_key, expires=None):
    """
    Returns a copy of the passed in item that has been signed using the
    private_key and annotated with metadata under the "_p4p2p" key (a
    timestamp indicating when the message was signed, a timestamp indicating
    when the item should expire, the p4p2p version that created the item, the
    public_key and the signature).

    The expiration timestamp is derived by adding the (optional) expires
    number of seconds to the timestamp. If no expiration is specified then the
    "expires" value is set to 0.0 (expiration is expressed as a float).
    """
    signed_item = item.copy()
    timestamp = time.time()
    expires_at = 0.0  # it's a float, dammit
    t = type(expires)
    if expires and (t == int or t == float) and expires > 0:
        expires_at = timestamp + expires
    signed_item['_p4p2p'] = {
        'timestamp': timestamp,
        'expires': expires_at,
        'version': get_version(),
        'public_key': public_key
    }
    root_hash = _get_hash(signed_item)
    key = RSA.importKey(private_key)
    signer = PKCS1_v1_5.new(key)
    sig = base64.encodebytes(signer.sign(root_hash)).decode('utf-8')
    signed_item['_p4p2p']['signature'] = sig
    return signed_item


def verify_item(item):
    """
    Returns a boolean to indicate if the message can be verified.
    """
    try:
        item_no_sig = copy.deepcopy(item)
        raw_sig = item_no_sig['_p4p2p']['signature']
        signature = base64.decodebytes(raw_sig.encode('utf-8'))
        public_key = RSA.importKey(item_no_sig['_p4p2p']['public_key'])
        del item_no_sig['_p4p2p']['signature']
        root_hash = _get_hash(item_no_sig)
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
