import unittest
import modular


class TestStack(unittest.TestCase):
    def test_cases(self):
        self.assertEqual(modular.stack('a b'), ['a b'])
        self.assertEqual(modular.stack('a;b;c'), ['a', 'b', 'c'])
        self.assertEqual(modular.stack('a;;b;c'), ['a;b', 'c'])
        self.assertEqual(modular.stack('a;;;b;c'), ['a;;b', 'c'])


if __name__ == '__main__':
    unittest.main()
