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

if __name__ == "__main__":
    unittest.main()

