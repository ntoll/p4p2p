# -*- coding: utf-8 -*-
"""
Ensures the cryptographic signing and related functions work as expected.
"""
from p4p2p.daemon.crypto import (get_signed_message, verify_message,
                                 _get_hash)
from hashlib import sha512
import unittest
import uuid


# Useful throw-away constants for testing purposes.
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIICXgIBAAKBgQC+n3Au1cbSkjCVsrfnTbmA0SwQLN2RbbDIMHILA1i6wByXkqEa
mnEBvgsOkUUrsEXYtt0vb8Qill4LSs9RqTetSCjGb+oGVTKizfbMbGCKZ8fT64ZZ
gan9TvhItl7DAwbIXcyvQ+b1J7pHaytAZwkSwh+M6WixkMTbFM91fW0mUwIDAQAB
AoGBAJvBENvj5wH1W2dl0ShY9MLRpuxMjHogo3rfQr/G60AkavhaYfKn0MB4tPYh
MuCgtmF+ATqaWytbq9oUNVPnLUqqn5M9N86+Gb6z8ld+AcR2BD8oZ6tQaiEIGzmi
L9AWEZZnyluDSHMXDoVrvDLxPpKW0yPjvQfWN15QF+H79faJAkEA0hgdueFrZf3h
os59ukzNzQy4gjL5ea35azbQt2jTc+lDOu+yjUic2O7Os7oxnSArpujDiOkYgaih
Dny+/bIgLQJBAOhGKjhpafdpgpr/BjRlmUHXLaa+Zrp/S4RtkIEkE9XXkmQjvVZ3
EyN/h0IVNBv45lDK0Qztjic0L1GON62Z8H8CQAcRkqZ3ZCKpWRceNXK4NNBqVibj
SiuC4/psfLc/CqZCueVYvTwtrkFKP6Aiaprrwyw5dqK7nPx3zPtszQxCGv0CQQDK
51BGiz94VAE1qQYgi4g/zdshSD6xODYd7yBGz99L9M77D4V8nPRpFCRyA9fLf7ii
ZyoLYxHFCX80fUoCKvG9AkEAyX5iCi3aoLYd/CvOFYB2fcXzauKrhopS7/NruDk/
LluSlW3qpi1BGDHVTeWWj2sm30NAybTHjNOX7OxEZ1yVwg==
-----END RSA PRIVATE KEY-----"""


PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+n3Au1cbSkjCVsrfnTbmA0SwQ
LN2RbbDIMHILA1i6wByXkqEamnEBvgsOkUUrsEXYtt0vb8Qill4LSs9RqTetSCjG
b+oGVTKizfbMbGCKZ8fT64ZZgan9TvhItl7DAwbIXcyvQ+b1J7pHaytAZwkSwh+M
6WixkMTbFM91fW0mUwIDAQAB
-----END PUBLIC KEY-----"""


BAD_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
HELLOA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+n3Au1cbSkjCVsrfnTbmA0SwQ
LN2RbbDIMHILA1i6wByXkqEamnEBvgsOkUUrsEXYtt0vb8Qill4LSs9RqTetSCjG
b+oGVTKizfbMbGCKZ8fT64ZZgan9TvhItl7DAwbIXcyvQ+b1J7pHaytAZwkSwh+M
6WixkMTbFM91fW0mUwIDAQAB
-----END PUBLIC KEY-----"""


class TestGetSignedMessage(unittest.TestCase):
    """
    Ensures the p4p2p.daemon.crypto._get_signed_message functoin works as
    expected.
    """

    def test_expected_metadata(self):
        """
        Ensure the message (dict) returned from the function contains the
        expected metadata.
        """
        message = {
            'foo': 'bar',
            'baz': [1, 2, 3]
        }
        signed_message = get_signed_message(message, PUBLIC_KEY, PRIVATE_KEY)
        self.assertIn('_p4p2p', signed_message)
        metadata = signed_message['_p4p2p']
        self.assertIn('timestamp', metadata)
        self.assertIsInstance(metadata['timestamp'], float)
        self.assertIn('public_key', metadata)
        self.assertIsInstance(metadata['public_key'], str)
        self.assertIn('signature', metadata)
        self.assertIsInstance(metadata['signature'], str)
        self.assertEqual(3, len(metadata))

    def test_original_message_unaffected(self):
        """
        Ensure the message (dict) passed into the function is not changed.
        """
        message = {
            'foo': 'bar',
            'baz': [1, 2, 3]
        }
        get_signed_message(message, PUBLIC_KEY, PRIVATE_KEY)
        self.assertNotIn('_p4p2p', message)
        self.assertEqual(2, len(message))
        self.assertIn('foo', message)
        self.assertIn('baz', message)
        self.assertEqual(message['foo'], 'bar')
        self.assertEqual(message['baz'], [1, 2, 3])

    def test_signed_message_is_verifiable(self):
        """
        Check that the resulting message is able to be verified.
        """
        message = {
            'foo': 'bar',
            'baz': [1, 2, 3]
        }
        signed_message = get_signed_message(message, PUBLIC_KEY, PRIVATE_KEY)
        self.assertTrue(verify_message(signed_message))


class TestVerifyMessage(unittest.TestCase):
    """
    Ensures the p4p2p.daemon.crypto.verify_message function works as expected.
    """

    def test_good_message(self):
        """
        The good case should pass.
        """
        message = {
            'foo': 'bar',
            'baz': [1, 2, 3]
        }
        signed_message = get_signed_message(message, PUBLIC_KEY, PRIVATE_KEY)
        self.assertTrue(verify_message(signed_message))

    def test_malformed_message(self):
        """
        Does not contain the expected _p4p2p metadata.
        """
        message = {
            'foo': 'bar',
            'baz': [1, 2, 3]
        }
        self.assertFalse(verify_message(message))

    def test_modified_message(self):
        """
        The content of the message do not match the hash / signature.
        """
        message = {
            'foo': 'bar',
            'baz': [1, 2, 3]
        }
        signed_message = get_signed_message(message, PUBLIC_KEY, PRIVATE_KEY)
        signed_message['_p4p2p']['public_key'] = BAD_PUBLIC_KEY
        self.assertFalse(verify_message(message))


class TestGetHashFunction(unittest.TestCase):
    """
    Ensures the p4p2p.daemon.crypto._get_hash function works as expected.
    """

    def test_get_hash_dict(self):
        """
        Ensures that the dict is hashed in such a way that the keys are
        sorted so the hashes used in the correct order.
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

    def test_get_hash_int(self):
        """
        Ensure int values are hashed correctly.
        """
        expected = sha512(b'12345')
        actual = _get_hash(12345)
        self.assertEqual(expected.hexdigest(), actual.hexdigest())

    def test_get_hash_float(self):
        """
        Ensure float values are hashed correctly.
        """
        expected = sha512(b'12345.6789')
        actual = _get_hash(12345.6789)
        self.assertEqual(expected.hexdigest(), actual.hexdigest())

    def test_get_hash_long(self):
        """
        Ensure long values are hashed correctly.
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

    def test_get_hash_unicode(self):
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
        # REMEMBER - dict objects are ordered by key.
        seed_hashes.append(sha512(b'baz').hexdigest())
        seed_hashes.append(_get_hash(child_dict).hexdigest())
        seed_hashes.append(sha512(b'foo').hexdigest())
        seed_hashes.append(_get_hash(child_list).hexdigest())
        seed = ''.join(seed_hashes)
        expected = sha512(seed.encode('utf-8'))
        actual = _get_hash(to_hash)
        self.assertEqual(expected.hexdigest(), actual.hexdigest())
