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
        return not (self == other)

    def __add__(self, other):
        if other is None:
            raise ValueError(f'other is None')
        if self.prime != other.prime:
            raise TypeError(f'Cannot add two numbers in different Fields')
        num = (self.num + other.num) % self.prime
        return self.__class__(num, self.prime)

    def __sub__(self, other):
        if other is None:
            raise ValueError(f'other is None')
        if self.prime != other.prime:
            raise TypeError(f'Cannot subtraction two numbers in different Fields')
        num = (self.num - other.num) % self.prime
        return self.__class__(num, self.prime)

    def __mul__(self, other):
        if other is None:
            raise ValueError(f'other is None')
        if self.prime != other.prime:
            raise TypeError(f'Cannot multiply two numbers in different Fields')
        num = (self.num * other.num) % self.prime
        return self.__class__(num, self.prime)

    def __pow__(self, exponent):
        n = exponent % (self.prime - 1)
        num = pow(self.num, n, self.prime)
        return self.__class__(num, self.prime)

    def __truediv__(self, other):
        if other is None:
            raise ValueError(f'other is None')
        if self.prime != other.prime:
            raise TypeError(f'Cannot divide two numbers in different Fields')
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
        else:
            return f'Point({self.x},{self.y})_{self.a}_{self.b}'

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y \
                and self.a == other.a and self.b == other.b

    def __ne__(self, other):
        return not (self == other)

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


if __name__ == "__main__":
    unittest.main()

