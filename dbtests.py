import unittest
from LocalDatabase import check_if_index_exists
from LocalDatabase import add_to_database

class TestLocalDatabase(unittest.TestCase):



    def test_add_to_database(test):
        res = add_to_database({1:['Test', 345]})
        self.assertEqual(res, True)

    def test_add_to_database(self):
        res = add_to_database({1: ['Test', 345]})
        self.assertEqual(res, False)

    def test_check_if_index_exists(self):
        res = check_if_index_exists(1)
        self.assertEqual(res, True)

    def test_check_if_index_exists(self):
        res = check_if_index_exists(2)
        self.assertEqual(res, False)


if __name__ == '__main__':
    unittest.main()