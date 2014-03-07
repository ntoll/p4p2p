# -*- coding: utf-8 -*-
"""
Ensures the cryptographic signing and related functions work as expected.
"""
from p4p2p.dht.crypto import get_signed_item, verify_item, _get_hash
from hashlib import sha512
from .keys import PRIVATE_KEY, PUBLIC_KEY, BAD_PUBLIC_KEY
import unittest
import uuid


class TestGetSignedItem(unittest.TestCase):
    """
    Ensures the p4p2p.daemon.crypto._get_signed_item function works as
    expected.
    """

    def test_expected_metadata(self):
        """
        Ensure the item (dict) returned from the function contains the
        expected metadata.
        """
        item = {
            'foo': 'bar',
            'baz': [1, 2, 3]
        }
        signed_item = get_signed_item(item, PUBLIC_KEY, PRIVATE_KEY)
        self.assertIn('_p4p2p', signed_item)
        metadata = signed_item['_p4p2p']
        self.assertIn('timestamp', metadata)
        self.assertIsInstance(metadata['timestamp'], float)
        self.assertIn('expires', metadata)
        self.assertIsInstance(metadata['expires'], float)
        self.assertIn('version', metadata)
        self.assertIsInstance(metadata['version'], str)
        self.assertIn('public_key', metadata)
        self.assertIsInstance(metadata['public_key'], str)
        self.assertIn('signature', metadata)
        self.assertIsInstance(metadata['signature'], str)
        self.assertEqual(5, len(metadata))

    def test_expires(self):
        """
        Ensure the expires argument is handled and checked appropriately.

        * If it's not passed the expires metadata defaults to 0.0.
        * It must be a number (int or float).
        * It must be > 0
        * The "expires" metadata must == timestamp + passed in expires arg.
        """
        item = {
            'foo': 'bar',
            'baz': [1, 2, 3]
        }
        signed_item = get_signed_item(item, PUBLIC_KEY, PRIVATE_KEY)
        self.assertEqual(0.0, signed_item['_p4p2p']['expires'])
        signed_item = get_signed_item(item, PUBLIC_KEY, PRIVATE_KEY, 'foo')
        self.assertEqual(0.0, signed_item['_p4p2p']['expires'])
        signed_item = get_signed_item(item, PUBLIC_KEY, PRIVATE_KEY, 123)
        self.assertEqual(signed_item['_p4p2p']['timestamp'] + 123,
                         signed_item['_p4p2p']['expires'])
        signed_item = get_signed_item(item, PUBLIC_KEY, PRIVATE_KEY, 123.456)
        self.assertEqual(signed_item['_p4p2p']['timestamp'] + 123.456,
                         signed_item['_p4p2p']['expires'])
        signed_item = get_signed_item(item, PUBLIC_KEY, PRIVATE_KEY, -1)
        self.assertEqual(0.0, signed_item['_p4p2p']['expires'])

    def test_original_item_unaffected(self):
        """
        Ensure the item (dict) passed into the function is not changed.
        """
        item = {
            'foo': 'bar',
            'baz': [1, 2, 3]
        }
        get_signed_item(item, PUBLIC_KEY, PRIVATE_KEY)
        self.assertNotIn('_p4p2p', item)
        self.assertEqual(2, len(item))
        self.assertIn('foo', item)
        self.assertIn('baz', item)
        self.assertEqual(item['foo'], 'bar')
        self.assertEqual(item['baz'], [1, 2, 3])

    def test_signed_item_is_verifiable(self):
        """
        Check that the resulting item is able to be verified.
        """
        item = {
            'foo': 'bar',
            'baz': [1, 2, 3]
        }
        signed_item = get_signed_item(item, PUBLIC_KEY, PRIVATE_KEY)
        self.assertTrue(verify_item(signed_item))


class TestVerifyItem(unittest.TestCase):
    """
    Ensures the p4p2p.daemon.crypto.verify_item function works as expected.
    """

    def test_good_item(self):
        """
        The good case should pass.
        """
        item = {
            'foo': 'bar',
            'baz': [1, 2, 3]
        }
        signed_item = get_signed_item(item, PUBLIC_KEY, PRIVATE_KEY)
        self.assertTrue(verify_item(signed_item))

    def test_malformed_item(self):
        """
        Does not contain the expected _p4p2p metadata.
        """
        item = {
            'foo': 'bar',
            'baz': [1, 2, 3]
        }
        self.assertFalse(verify_item(item))

    def test_modified_item(self):
        """
        The content of the item does not match the hash / signature.
        """
        item = {
            'foo': 'bar',
            'baz': [1, 2, 3]
        }
        signed_item = get_signed_item(item, PUBLIC_KEY, PRIVATE_KEY)
        signed_item['_p4p2p']['public_key'] = BAD_PUBLIC_KEY
        self.assertFalse(verify_item(item))


class TestGetHashFunction(unittest.TestCase):
    """
    Ensures the p4p2p.daemon.crypto._get_hash function works as expected.
    """

    def test_get_hash_dict(self):
        """
        Ensures that the dict is hashed in such a way that the keys are
        sorted so the resulting leaf hashes are used in the correct order.
        """
        to_hash = {}
        for i in range(5):
            k = str(uuid.uuid4())
            v = str(uuid.uuid4())
            to_hash[k] = v

        seed_hashes = []
        for k in sorted(to_hash):
            v = to_hash[k]
            seed_hashes.append(sha512(k.encode('utf-8')).hexdigest())
            seed_hashes.append(sha512(v.encode('utf-8')).hexdigest())
        seed = ''.join(seed_hashes)
        expected = sha512(seed.encode('utf-8'))
        actual = _get_hash(to_hash)
        self.assertEqual(expected.hexdigest(), actual.hexdigest())

    def test_get_hash_list(self):
        """
        Ensure all the items in a list are hashed in the correct order.
        """
        to_hash = []
        for i in range(5):
            to_hash.append(str(uuid.uuid4()))

        seed_hashes = []
        for item in to_hash:
            seed_hashes.append(sha512(item.encode('utf-8')).hexdigest())
        seed = ''.join(seed_hashes)
        expected = sha512(seed.encode('utf-8'))
        actual = _get_hash(to_hash)
        self.assertEqual(expected.hexdigest(), actual.hexdigest())

    def test_get_hash_none(self):
        """
        Ensure the hash of Python's None is actually a hash of 'null' (since
        this is the null value for JSON).
        """
        expected = sha512(b'null')
        actual = _get_hash(None)
        self.assertEqual(expected.hexdigest(), actual.hexdigest())

    def test_get_hash_boolean_true(self):
        """
        Ensure hash of Python's True boolean value is a hash of 'true' (since
        this is the true value in JSON).
        """
        expected = sha512(b'true')
        actual = _get_hash(True)
        self.assertEqual(expected.hexdigest(), actual.hexdigest())

    def test_get_hash_boolean_false(self):
        """
        Ensure hash of Python's False boolean value is a hash of 'false'
        (since this is the false value in JSON).
        """
        expected = sha512(b'false')
        actual = _get_hash(False)
        self.assertEqual(expected.hexdigest(), actual.hexdigest())

    def test_get_hash_float(self):
        """
        Ensure float values are hashed correctly.
        """
        expected = sha512(b'12345.6789')
        actual = _get_hash(12345.6789)
        self.assertEqual(expected.hexdigest(), actual.hexdigest())

    def test_get_hash_int(self):
        """
        Ensure integer values are hashed correctly.
        """
        expected = sha512(b'1234567890987654321234567890987654321')
        actual = _get_hash(1234567890987654321234567890987654321)
        self.assertEqual(expected.hexdigest(), actual.hexdigest())

    def test_get_hash_str(self):
        """
        Strings are hashed correctly
        """
        expected = sha512(b'foo')
        actual = _get_hash('foo')
        self.assertEqual(expected.hexdigest(), actual.hexdigest())

    def test_get_hash_nested_structure(self):
        """
        Ensure a tree like object is recursively hashed to produce a root-hash
        value.
        """
        child_list = ['bar', 1, 1.234, ]
        child_dict = {
            'b': False,
            'a': None,
            'c': True
        }
        to_hash = {
            'foo': child_list,
            'baz': child_dict
        }
        seed_hashes = []
        # REMEMBER - in this algorithm the keys to a dict object are ordered.
        seed_hashes.append(sha512(b'baz').hexdigest())
        seed_hashes.append(_get_hash(child_dict).hexdigest())
        seed_hashes.append(sha512(b'foo').hexdigest())
        seed_hashes.append(_get_hash(child_list).hexdigest())
        seed = ''.join(seed_hashes)
        expected = sha512(seed.encode('utf-8'))
        actual = _get_hash(to_hash)
        self.assertEqual(expected.hexdigest(), actual.hexdigest())
