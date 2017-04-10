import unittest
from Main import read_db_config
from LocalDatabase import create_database
from LocalDatabase import id_exists
from LocalDatabase import add_to_database
from LocalDatabase import establish_connection


class TestLocalDatabase(unittest.TestCase):

    def test_create_database(self):
        exp = read_db_config()
        res1 = create_database(exp)
        self.assertEqual(res1, True)
        res2 = create_database('Random')
        #self.assertRaises(TypeError, create_database, 'random')
    '''
    def test_id_exists(self):
        values = read_db_config()
        res1 = id_exists(1, values)
        self.assertEqual(res1, True)
        res2 = id_exists(61, values)
        self.assertEqual(res2, False)


    def test_add_to_database(self):
        exp = read_db_config()
        list = {}
        name = 'Channel'
        for ii in range(1, 2):
            for i in range(1, 61):
                tempname = name + "%d" % (i,)
                list[i] = [tempname, i]
            res = add_to_database(list, exp)
            self.assertEqual(res, True)

        cursor = establish_connection(exp)
        for i in range(1, 61):
            sql = "Select * from channels where id = '%d'" % (i,)
            res3 = cursor.execute(sql)
            self.assertEqual(res3, 1)
            sql2 = "Select * from measurements where id = '%d'" % (i,)
            res4 = cursor.execute(sql2)
            self.assertGreaterEqual(res4, 2)
        with self.assertRaises(TypeError):
            add_to_database({'1': [23, 'hej']}, exp)

        '''



if __name__ == '__main__':
    unittest.main()