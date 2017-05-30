import unittest
import time
from configInterface import readConfig
from LocalDatabase import createDatabase
from LocalDatabase import dropDatabase
from LocalDatabase import readFromDatabase
from LocalDatabase import addToDatabase
from LocalDatabase import changeChannelName
from LocalDatabase import resetChannel


class TestLocalDatabase(unittest.TestCase):

    def test_create_database(self):
        exp = readConfig(file='config.cfg', section='Test')
        res1 = createDatabase(exp)
        self.assertEqual(res1, True)
        self.assertRaises(TypeError, lambda: createDatabase, 'Wrong type')
        dropDatabase(exp)


    def test_add_to_database(self):
        exp = readConfig(file='config.cfg', section='Test')
        createDatabase(exp)
        list = {}
        for i in range(1, 61):
            list[i] = [i, 'Kg', 'tolerant']
        for ii in range(0, 2):
                res = addToDatabase(databaseValues=exp, listOfItems=list)
                self.assertEqual(res, True)
        dropDatabase(exp)

    def test_read_from_database(self):
        exp = readConfig(file='config.cfg', section='Test')
        createDatabase(exp)
        list = {}
        fromtime = time.strftime('%H:%M:%S')
        fromdate = time.strftime('%Y-%m-%d')
        for i in range(1, 61):
            list[i] = [i, 'Kg', 'tolerant']
        for ii in range(0, 2):
            addToDatabase(listOfItems=list, databaseValues=exp)

        totime = time.strftime('%H:%M:%S')
        todate = time.strftime('%Y-%m-%d')
        parameterlist = {'fromtime': fromtime, 'fromdate': fromdate, 'totime': totime, 'todate': todate}

        for index in range(1, 61):
            parameterlist['id'] = index
            res = readFromDatabase(databaseValues=exp, readParameters=parameterlist)
            self.assertEqual(len(res), 2)
        dropDatabase(exp)

    def test_change_channel_name(self):
        exp = readConfig(file='config.cfg', section='Test')
        createDatabase(exp)
        res = changeChannelName(exp, 'Newname', 59)
        self.assertEqual(res, True)
        dropDatabase(exp)

    def test_reset_channel(self):
        exp = readConfig(file='config.cfg', section='Test')
        createDatabase(exp)
        list = {}

        for i in range(1,61):
            list[i] = [20 + i, 'Placeholder', 'Placeholder']

        fromtime = time.strftime('%H:%M:%S')
        fromdate = time.strftime('%Y-%m-%d')
        addToDatabase(databaseValues=exp, listOfItems=list)
        totime = time.strftime('%H:%M:%S')
        todate = time.strftime('%Y-%m-%d')
        id = 5
        resetChannel(databaseValues=exp, id=id)
        readparam = {'id': id, 'fromdate': fromdate, 'fromtime': fromtime, 'todate': todate, 'totime': totime}
        self.assertTupleEqual(readFromDatabase(databaseValues=exp, readParameters=readparam), ())






if __name__ == '__main__':
    unittest.main()