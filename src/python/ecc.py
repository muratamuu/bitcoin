#!/usr/bin/env python3
""" 楕円曲線関連モジュール
"""

import unittest
import hashlib
import hmac
from random import randint
from helper import hash160

class FieldElement:
    """単一の有限体要素
    """

    def __init__(self, num, prime):
        if num >= prime or num < 0:
            error = f'Num {num} not in field range 0 to {prime - 1}'
            raise ValueError(error)
        self.num = num
        self.prime = prime

    def __repr__(self):
        return f'FieldElement_{self.prime}({self.num})'

    def __eq__(self, other):
        if other is None:
            return False
        return self.num == other.num and self.prime == other.prime

    def __ne__(self, other):
        if other is None:
            return False
        return not self == other

    def __add__(self, other):
        if other is None:
            raise ValueError('other is None')
        if self.prime != other.prime:
            raise TypeError('Cannot add two numbers in different Fields')
        num = (self.num + other.num) % self.prime
        return self.__class__(num, self.prime)

    def __sub__(self, other):
        if other is None:
            raise ValueError('other is None')
        if self.prime != other.prime:
            raise TypeError('Cannot subtraction two numbers in different Fields')
        num = (self.num - other.num) % self.prime
        return self.__class__(num, self.prime)

    def __mul__(self, other):
        if other is None:
            raise ValueError('other is None')
        if self.prime != other.prime:
            raise TypeError('Cannot multiply two numbers in different Fields')
        num = (self.num * other.num) % self.prime
        return self.__class__(num, self.prime)

    def __rmul__(self, coefficient):
        num = (self.num * coefficient) % self.prime
        return self.__class__(num, self.prime)

    def __pow__(self, exponent):
        n = exponent % (self.prime - 1)
        num = pow(self.num, n, self.prime)
        return self.__class__(num, self.prime)

    def __truediv__(self, other):
        if other is None:
            raise ValueError('other is None')
        if self.prime != other.prime:
            raise TypeError('Cannot divide two numbers in different Fields')
        num = pow(other.num, self.prime - 2, self.prime)
        num = (self.num * num) % self.prime
        return self.__class__(num, self.prime)

class TestFieldElement(unittest.TestCase):
    """test class of FieldElement
    """

    def test_equality(self):
        a = FieldElement(7, 13)
        b = FieldElement(7, 13)
        c = FieldElement(6, 13)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_repr(self):
        a = FieldElement(7, 13)
        expected = 'FieldElement_13(7)'
        self.assertEqual(expected, str(a))

    def test_add(self):
        a = FieldElement(7, 13)
        b = FieldElement(12, 13)
        c = FieldElement(6, 13)
        self.assertEqual(c, a + b)

    def test_sub(self):
        a = FieldElement(9, 57)
        b = FieldElement(29, 57)
        c = FieldElement(37, 57)
        self.assertEqual(c, a - b)

    def test_mul(self):
        a = FieldElement(95, 97)
        b = FieldElement(45, 97)
        c = FieldElement(7, 97)
        self.assertEqual(c, a * b)

    def test_pow(self):
        a = FieldElement(3, 13)
        b = FieldElement(1, 13)
        self.assertEqual(b, a ** 3)

    def test_neg_pow(self):
        a = FieldElement(7, 13)
        b = FieldElement(8, 13)
        self.assertEqual(b, a ** -3)

    def test_div(self):
        a = FieldElement(3, 31)
        b = FieldElement(24, 31)
        c = FieldElement(4, 31)
        self.assertEqual(c, a / b)

class Point:
    """楕円曲線上の点
    """

    def __init__(self, x, y, a, b):
        self.a = a
        self.b = b
        self.x = x
        self.y = y
        if self.x is None and self.y is None:
            return
        if self.y ** 2 != self.x ** 3 + a * x + b:
            raise ValueError(f'({x}, {y}) is not on the curve')

    def __repr__(self):
        if self.x is None:
            return 'Point(infinity)'
        if isinstance(self.x, FieldElement):
            return f'Point({self.x.num},{self.y.num})_{self.a.num}_{self.b.num} FieldElement({self.x.prime})'
        else:
            return f'Point({self.x},{self.y})_{self.a}_{self.b}'

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y \
                and self.a == other.a and self.b == other.b

    def __ne__(self, other):
        return not self == other

    def __add__(self, other):
        if self.a != other.a or self.b != other.b:
            raise TypeError(f'Points {self}, {other} are not on the same curve')

        if self.x is None:
            return other

        if other.x is None:
            return self

        if self.x == other.x and self.y != other.y:
            return self.__class__(None, None, self.a, self.b)

        if self.x != other.x:
            s = (other.y - self.y) / (other.x - self.x)
            x = s ** 2 - self.x - other.x
            y = s * (self.x - x) - self.y
            return self.__class__(x, y, self.a, self.b)

        if self == other and self.y == 0 * self.x:
            return self.__class__(None, None, self.a, self.b)

        if self == other:
            s = (3 * self.x ** 2 + self.a) / (2 * self.y)
            x = s ** 2 - 2 * self.x
            y = s * (self.x - x) - self.y
            return self.__class__(x, y, self.a, self.b)

    def __rmul__(self, coefficient):
        coef = coefficient
        current = self
        result = self.__class__(None, None, self.a, self.b)
        while coef:
            if coef & 1:
                result += current
            current += current
            coef >>= 1
        return result

class TestPoint(unittest.TestCase):
    """test class of Point
    """

    def test_init(self):
        Point(-1, -1, 5, 7)

    def test_init_errror(self):
        with self.assertRaises(ValueError):
            Point(-1, -2, 5, 7)

    def test_equality(self):
        p1 = Point(-1, -1, 5, 7)
        p2 = Point(-1, -1, 5, 7)
        p3 = Point(18, 77, 5, 7)
        self.assertEqual(p1, p2)
        self.assertNotEqual(p1, p3)

    def test_add(self):
        p1 = Point(-1, -1, 5, 7)
        p2 = Point(-1, 1, 5, 7)
        inf = Point(None, None, 5, 7)
        self.assertEqual(p1 + inf, p1)
        self.assertEqual(inf + p2, p2)
        self.assertEqual(p1 + p2, inf)

    def test_add_x1_isnot_x2(self):
        p1 = Point(2, 5, 5, 7)
        p2 = Point(-1, -1, 5, 7)
        ans = Point(3, -7, 5, 7)
        self.assertEqual(p1 + p2, ans)

    def test_add_p1_and_p2_are_same(self):
        p1 = Point(-1, -1, 5, 7)
        p2 = Point(-1, -1, 5, 7)
        ans = Point(18, 77, 5, 7)
        self.assertEqual(p1 + p2, ans)

P = 2 ** 256 - 2 ** 32 - 977
A = 0
B = 7
N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

class S256Field(FieldElement):

    def __init__(self, num, prime=None):
        super().__init__(num=num, prime=P)

    def __repr__(self):
        return f'{self.num:064x}'

    def sqrt(self):
        return self**((P + 1) // 4)

class S256Point(Point):

    def __init__(self, x, y, a=None, b=None):
        a, b = S256Field(A), S256Field(B)
        if type(x) == int:
            super().__init__(x=S256Field(x), y=S256Field(y), a=a, b=b)
        else:
            super().__init__(x=x, y=y, a=a, b=b)

    def __repr__(self):
        if self.x is None:
            return 'S256Point(infinity)'
        else:
            return f'S256Point({self.x}, {self.y})'

    def __rmul__(self, coefficient):
        coef = coefficient % N
        return super().__rmul__(coef)

    def verify(self, z, sig):
        s_inv = pow(sig.s, N - 2, N)
        u = z * s_inv % N
        v = sig.r * s_inv % N
        total = u * G + v * self
        return total.x.num == sig.r

    def sec(self, compressed=True):
        '''SECフォーマットをバイナリ形式にて返す'''
        if compressed:
            if self.y.num % 2 == 0:
                return b'\x02' + self.x.num.to_bytes(32, 'big')
            else:
                return b'\x03' + self.x.num.to_bytes(32, 'big')
        else:
            return b'\x04' + self.x.num.to_bytes(32, 'big') + \
                self.y.num.to_bytes(32, 'big')

    @classmethod
    def parse(self, sec_bin):
        '''SECバイナリ(16進数ではない)からPointオブジェクトを返す'''
        if sec_bin[0] == 4:
            x = int.from_bytes(sec_bin[1:33], 'big')
            y = int.from_bytes(sec_bin[33:65], 'big')
            return S256Point(x=x, y=y)
        is_even = sec_bin[0] == 2
        x = S256Field(int.from_bytes(sec_bin[1:], 'big'))
        # 式 y^2 = x^3 + 7 の右辺
        alpha = x**3 + S256Field(B)
        # 左辺を解く
        beta = alpha.sqrt()
        if beta.num % 2 == 0:
            even_beta = beta
            odd_beta = S256Field(P - beta.num)
        else:
            even_beta = S256Field(P - beta.num)
            odd_beta = beta
        if is_even:
            return S256Point(x, even_beta)
        else:
            return S256Point(x, odd_beta)

    def hash160(self, compressed=True):
        return hash160(self.sec(compressed))

    def address(self, compressed=True, testnet=False):
        '''アドレスの文字列を返す'''
        h160 = self.hash160(compressed)
        if testnet:
            prefix = b'\x6f'
        else:
            prefix = b'\x00'
        return encode_base58_checksum(prefix + h160)

G = S256Point(
    0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
    0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8)

class TestS256Point(unittest.TestCase):
    """test class of Point with FieldElement
    """

    def test_point_with_FieldElement(self):
        prime = 223
        a = FieldElement(0, prime)
        b = FieldElement(7, prime)
        valid_points = [(192, 105), (17, 56), (1, 193)]
        invalid_points = [(200, 119), (42, 99)]
        for x_raw, y_raw in valid_points:
            x = FieldElement(x_raw, prime)
            y = FieldElement(y_raw, prime)
            Point(x, y, a, b)
        for x_raw, y_raw in invalid_points:
            x = FieldElement(x_raw, prime)
            y = FieldElement(y_raw, prime)
            with self.assertRaises(ValueError):
                Point(x, y, a, b)

    def test_add(self):
        prime = 223
        a = FieldElement(0, prime)
        b = FieldElement(7, prime)
        points = [((170, 142), (60, 139), (220, 181)),
                  ((47, 71), (17, 56), (215, 68)),
                  ((143, 98), (76, 66), (47, 71))]
        for (x1, y1), (x2, y2), (x3, y3) in points:
            p1 = Point(FieldElement(x1, prime), FieldElement(y1, prime), a, b)
            p2 = Point(FieldElement(x2, prime), FieldElement(y2, prime), a, b)
            p3 = Point(FieldElement(x3, prime), FieldElement(y3, prime), a, b)
            self.assertEqual(p1 + p2, p3)

    def test_scaler_add(self):
        prime = 223
        a = FieldElement(0, prime)
        b = FieldElement(7, prime)
        points = [((2, 192, 105), (49, 71)),
                  ((2, 143, 98), (64, 168)),
                  ((2, 47, 71), (36, 111)),
                  ((4, 47, 71), (194, 51)),
                  ((8, 47, 71), (116, 55)),
                  ((21, 47, 71), (None, None))]
        for (s, x1, y1), (x2, y2) in points:
            p = Point(FieldElement(x1, prime), FieldElement(y1, prime), a, b)
            sum = p
            for i in range(1, s):
                sum = sum + p
            ans = Point(None, None, a, b)
            if not x2 is None:
                ans = Point(FieldElement(x2, prime), FieldElement(y2, prime), a, b)
            self.assertEqual(sum, ans)

    def test_s256point_verify(self):
        z = 0xbc62d4b80d9e36da29c16c5d4d9f11731f36052c72401a76c23c0fb5a9b74423
        r = 0x37206a0610995c58074999cb9767b87af4c4978db68c06e8e6e81d282047a7c6
        s = 0x8ca63759c1157ebeaec0d03cecca119fc9a75bf8e6d0fa65c841c8e2738cdaec
        px = 0x04519fac3d910ca7e7138f7013706f619fa8f033e6ec6e09370ea38cee6a7574
        py = 0x82b51eab8c27c66e26c858a079bcdf4f1ada34cec420cafc7eac1a42216fb6c4
        point = S256Point(px, py)
        s_inv = pow(s, N-2, N)
        u = z * s_inv % N
        v = r * s_inv % N
        self.assertEqual((u*G + v*point).x.num, r)

    def test_s256point_verify_2(self):
        z = 0xec208baa0fc1c19f708a9ca96fdeff3ac3f230bb4a7ba4aede4942ad003c0f60
        r = 0xac8d1c87e51d0d441be8b3dd5b05c8795b48875dffe00b7ffcfac23010d3a395
        s = 0x68342ceff8935ededd102dd876ffd6ba72d6a427a3edb13d26eb0781cb423c4
        px = 0x887387e452b8eacc4acfde10d9aaf7f6d9a0f975aabb10d006e4da568744d06c
        py = 0x61de6d95231cd89026e286df3b6ae4a894a3378e393e93a0f45b666329a0ae34
        point = S256Point(px, py)
        s_inv = pow(s, N-2, N)
        u = z * s_inv % N
        v = r * s_inv % N
        self.assertEqual((u*G + v*point).x.num, r)

    def test_s256point_verify_3(self):
        z = 0x7c076ff316692a3d7eb3c3bb0f8b1488cf72e1afcd929e29307032997a838a3d
        r = 0xeff69ef2b1bd93a66ed5219add4fb51e11a840f404876325a1e8ffe0529a2c
        s = 0xc7207fee197d27c618aea621406f6bf5ef6fca38681d82b2f06fddbdce6feab6
        px = 0x887387e452b8eacc4acfde10d9aaf7f6d9a0f975aabb10d006e4da568744d06c
        py = 0x61de6d95231cd89026e286df3b6ae4a894a3378e393e93a0f45b666329a0ae34
        point = S256Point(px, py)
        sig = Signature(r, s)
        self.assertEqual(point.verify(z, sig), True)

    def test_s256point_signature(self):
        e = 12345
        z = int.from_bytes(hash256(b'Programming Bitcoin!'), 'big')

        k = 123456790
        r = (k*G).x.num
        k_inv = pow(k, N-2, N)
        s = (z+r*e) * k_inv % N
        point = e*G
        #print(point)

class Signature:

    def __init__(self, r, s):
        self.r = r
        self.s = s

    def __repr__(self):
        return f'Signature({self.r:x},{self.s:x})'

    def der(self):
        rbin = self.r.to_bytes(32, byteorder='big')
        # 先頭のnullバイトを全て取り除く
        rbin = rbin.lstrip(b'\x00')
        # rbinの最上位ビットが1の場合、\x00を追加する
        if rbin[0] & 0x80:
            rbin = b'\x00' + rbin
        result = bytes([2, len(rbin)]) + rbin
        sbin = self.s.to_bytes(32, byteorder='big')
        # 先頭のnullバイトを全て取り除く
        sbin = sbin.lstrip(b'\x00')
        # sbinの最上位ビットが1の場合、\x00を追加する
        if sbin[0] & 0x80:
            sbin = b'\x00' + sbin
        result += bytes([2, len(sbin)]) + sbin
        return bytes([0x30, len(result)]) + result

class TestSignature(unittest.TestCase):

    def test_der(self):
        r = 0x37206a0610995c58074999cb9767b87af4c4978db68c06e8e6e81d282047a7c6
        s = 0x8ca63759c1157ebeaec0d03cecca119fc9a75bf8e6d0fa65c841c8e2738cdaec

        sig = Signature(r=r, s=s)
        #print(sig.der().hex())

def hash256(s):
    '''two rounds of sha256'''
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()

class PrivateKey:

    def __init__(self, secret):
        self.secret = secret
        self.point = secret * G

    def hex(self):
        return f'{self.secret:064x}'

    def sign(self, z):
        #k = randint(0, N-1)
        k = self.deterministic_k(z)
        r = (k*G).x.num
        k_inv = pow(k, N-2, N)
        s = (z + r*self.secret) * k_inv % N
        if s > N/2:
            s = N - s
        return Signature(r, s)

    def deterministic_k(self, z):
        k = b'\x00' * 32
        v = b'\x01' * 32
        if z > N:
            z -= N
        z_bytes = z.to_bytes(32, 'big')
        secret_bytes = self.secret.to_bytes(32, 'big')
        s256 = hashlib.sha256
        k = hmac.new(k, v + b'\x00' + secret_bytes + z_bytes, s256).digest()
        v = hmac.new(k, v, s256).digest()
        k = hmac.new(k, v + b'\x01' + secret_bytes + z_bytes, s256).digest()
        v = hmac.new(k, v, s256).digest()
        while True:
            v = hmac.new(k, v, s256).digest()
            candidate = int.from_bytes(v, 'big')
            if candidate >= 1 and candidate < N:
                return candidate
            k = hmac.new(k, v + b'\x00', s256).digest()
            v = hmac.new(k, v, s256).digest()

    def wif(self, compressed=True, testnet=False):
        secret_bytes = self.secret.to_bytes(32, 'big')
        if testnet:
            prefix = b'\xef'
        else:
            prefix = b'\x80'
        if compressed:
            suffix = b'\x01'
        else:
            suffix = b''
        return encode_base58_checksum(prefix + secret_bytes + suffix)

class TestPrivateKey(unittest.TestCase):

    def test_to_sec_format(self):
        key = PrivateKey(0xdeadbeef12345)
        #print(key.point.sec())

    def test_address_1(self):
        key = PrivateKey(5002)
        address = key.point.address(compressed=False, testnet=True)
        self.assertEqual(address, 'mmTPbXQFxboEtNRkwfh6K51jvdtHLxGeMA')

    def test_address_2(self):
        key = PrivateKey(2020 ** 5)
        address = key.point.address(testnet=True)
        self.assertEqual(address, 'mopVkxp8UhXqRYbCYJsbeE1h1fiF64jcoH')

    def test_address_3(self):
        key = PrivateKey(0x12345deadbeef)
        address = key.point.address()
        self.assertEqual(address, '1F1Pn2y6pDb68E5nYJJeba4TLg2U7B6KF1')

    def test_wif_1(self):
        key = PrivateKey(5003)
        wif = key.wif(testnet=True)
        self.assertEqual(wif, 'cMahea7zqjxrtgAbB7LSGbcQUr1uX1ojuat9jZodMN8rFTv2sfUK')

    def test_wif_2(self):
        key = PrivateKey(2021 ** 5)
        wif = key.wif(compressed=False, testnet=True)
        self.assertEqual(wif, '91avARGdfge8E4tZfYLoxeJ5sGBdNJQH4kvjpWAxgzczjbCwxic')

    def test_wif_3(self):
        key = PrivateKey(0x54321deadbeef)
        wif = key.wif()
        self.assertEqual(wif, 'KwDiBf89QgGbjEhKnhXJuH7LrciVrZi3qYjgiuQJv1h8Ytr2S53a')

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

if __name__ == "__main__":
    unittest.main()

