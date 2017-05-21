import unittest
import base


class TestStack(unittest.TestCase):
    def test_cases(self):
        self.assertEqual(base.stack('a b'), ['a b'])
        self.assertEqual(base.stack('a;b;c'), ['a', 'b', 'c'])
        self.assertEqual(base.stack('a;;b;c'), ['a;b', 'c'])
        self.assertEqual(base.stack('a;;;b;c'), ['a;;b', 'c'])


if __name__ == '__main__':
    unittest.main()
