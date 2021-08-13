#!/usr/bin/env python3
""" 楕円曲線関連モジュール
"""

import unittest

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

P = 2 ** 256 - 2 ** 32 - 977
A = 0
B = 7
N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

class S256Field(FieldElement):

    def __init__(self, num, prime=None):
        super().__init__(num=num, prime=P)

    def __repr__(self):
        return '{:x}'.format(self.num).zfill(64)

class S256Point(Point):

    def __init__(self, x, y, a=None, b=None):
        a, b = S256Field(A), S256Field(B)
        if type(x) == int:
            super().__init__(x=S256Field(x), y=S256Field(y), a=a, b=b)
        else:
            super().__init__(x=x, y=y, a=a, b=b)

    def __repl__(self):
        if self.x is None:
            return 'S256Point(infinity)'
        else:
            return f'S256Point({self.x}, {self.y})'

    def __rmul__(self, coefficient):
        coef = coefficient % N
        return super().__rmul__(coef)

G = S256Point(
    0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
    0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8)

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

class TestEllipticCurve(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()

