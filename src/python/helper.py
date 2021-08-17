#!/usr/bin/env python3
""" ヘルパ関数群
"""

import unittest
import hashlib

def hash256(s):
    '''two rounds of sha256'''
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()

def hash160(s):
    '''sha256 の後にripemd160が続く'''
    return hashlib.new('ripemd160', hashlib.sha256(s).digest()).digest()

BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def encode_base58(s):
    count = 0
    for c in s:
        if c == 0:
            count += 1
        else:
            break
    num = int.from_bytes(s, 'big')
    prefix = '1' * count
    result = ''
    while num > 0:
        num, mod = divmod(num, 58)
        result = BASE58_ALPHABET[mod] + result
    return prefix + result

def encode_base58_checksum(b):
    return encode_base58(b + hash256(b)[:4])

class TestEncode(unittest.TestCase):

    def test_encode1(self):
        v = 0x7c076ff316692a3d7eb3c3bb0f8b1488cf72e1afcd929e29307032997a838a3d
        b = v.to_bytes(32, 'big')
        #print(encode_base58(b))

    def test_encode2(self):
        v = 0xeff69ef2b1bd93a66ed5219add4fb51e11a840f404876325a1e8ffe0529a2c
        b = v.to_bytes(31, 'big')
        #print(encode_base58(b))

    def test_encode3(self):
        v = 0xc7207fee197d27c618aea621406f6bf5ef6fca38681d82b2f06fddbdce6feab6
        b = v.to_bytes(32, 'big')
        #print(encode_base58(b))

def little_endian_to_int(b):
    return int.from_bytes(b, 'little')

def int_to_little_endian(i, length):
    return i.to_bytes(length, 'little')

if __name__ == "__main__":
    unittest.main()
