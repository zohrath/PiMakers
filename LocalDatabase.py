'''
This module acts as an interface to a local database
'''

import pymysql
import time



def create_database(dbvalues):
    '''
    This function creates a database using parameters specified in a configuration file
    :return: True if a database was created, false otherwise
    '''
    try:
        conn = pymysql.connect(user=dbvalues['user'], host=dbvalues['host'], password=dbvalues['password'])                     #Establish mysql connection
        cursor = conn.cursor()
        sql = "show databases like '%s'" % (dbvalues['name'])

        result = cursor.execute(sql)
        if result == 0:                                                                                                         #If the database does not exist, create a new database and tables
            sql2 = "Create database %s" % (dbvalues['name'])
            cursor.execute(sql2)
            sql3 = "use %s" % (dbvalues['name'])
            cursor.execute(sql3)
            sql4 = "create table channels(id int primary key, name text)"
            sql5 = "create table measurements(id int, date date, time time, measurementvalue float, primary key(id, date, time))"
            cursor.execute(sql4)
            cursor.execute(sql5)
        return True
    except TypeError as T:
        print(T)
        return False

def id_exists(id, dbvalues):
    '''
    This function checks if a channel id exists in the database
    :param id: channel id to look for 
    :param dbvalues: a dictionary containing mysql connection configurations. 
    Example: {'user': 'root', 'host':'127.0.0.1', 'password': '1234', 'name': 'EmployeeDatabase'}
    :return: True if the channel id was found, false otherwise
    '''
    try:
        conn = pymysql.connect(user = dbvalues['user'], host = dbvalues['host'], password = dbvalues['password'], database = dbvalues['name'])      #Establish connection to database
        cursor = conn.cursor()
        sql = "SELECT id FROM channels WHERE id = '%d'"  % (id, )                                                                                   #Looks for the channel id in the database
        cursor.execute(sql)
        value = cursor.fetchone()
        if value != None:                                          #Checks if any value was found
            return True
        else:
            return False
    except RuntimeError as err:
        print(err)

def establish_connection(dbvalues):
    '''
    This function offers a cursor to a database
    :param dbvalues: a dictionary containing mysql database configurations.
    Example: {'user': 'root', 'host':'127.0.0.1', 'password': '1234', 'name': 'EmployeeDatabase'}
    :return: A cursor to the database, the cursor is a connection.cursor() object from the PyMySQL module
    '''
    try:
        conn = pymysql.connect(user=dbvalues['user'], host=dbvalues['host'], password=dbvalues['password'], database=dbvalues['name'])              #Establish connection to database
        cursor = conn.cursor()
        return cursor
    except RuntimeError as err:
        print(err)
        return None



def read_from_database(dbvalues, readparameters):
    '''
    This funtion reads a specified databse using specified parameters
    :param dbvalues: a dictionary containing mysql datbase configurations
    Example: {'user': 'root', 'host':'127.0.0.1', 'password': '1234', 'name': 'EmployeeDatabase'}
    :param readparameters: a dictionary containing the parameters to be used in the read. 
    Example: {'id': 1, 'fromdate': '2017-04-09', 'todate': '2017-04-10', 'fromtime': '15:00:00', 'totime': '16:00:00'}
    :return: A tuple containing the result of the read.
    Example: ((1, 'channel1', datetime.date(2017, 4, 9), datetime.timedelta(0, 41759), 28.4))
    '''
    try:
        cursor = establish_connection(dbvalues)                                             #Establishes connection to the database
        id = readparameters['id']

        fromdate = readparameters['fromdate']                                               #Sets the different parameters
        fromtime = readparameters['fromtime']

        todate = readparameters['todate']
        totime = readparameters['totime']

        nestedsql = "(SELECT * FROM measurements WHERE date BETWEEN '%s' AND '%s' AND time BETWEEN '%s' AND '%s' AND id = %d)" % (fromdate, todate, fromtime, totime, id)
        sql = "SELECT temp.id, name, date, time, measurementvalue FROM %s AS temp INNER JOIN channels ON channels.id = temp.id ORDER BY date, time" % (nestedsql,)

        cursor.execute(sql)                                                                 #Reads from the database using the above query
        result = cursor.fetchall()

        return result
    except RuntimeError as err:
        print(err)



def add_to_database(list_of_items, dbvalues):
    '''
    This function adds entries to a specified database using a provided list of entry values
    :param list_of_items: a dictionary containing containing the needed values to make an entry to the database
    Example: {1: ['Channel1', 25.6], 2: ['Channel2', 22.3]}
    :return: True if something was added to the database, false otherwise
    '''
    try:
        conn = pymysql.connect(user = dbvalues['user'], host = dbvalues['host'], password = dbvalues['password'], database = dbvalues['name'])        #Connects to the database
        curs = conn.cursor()
        print("Connected to database succcessfully")
    except RuntimeError as err:
        print(err)
        print("Something went wrong, read the error message")
    try:
        timestamp = time.strftime("%H:%M:%S")                                       #Gets time and date
        datestamp = time.strftime("%Y-%m-%d")

        for index in list_of_items:                                                 #For each item in the list, gets the values to be added to the database
            id = index
            list = list_of_items[index]
            name = list[0]
            measurementvalue = list[1]

            found = id_exists(id, dbvalues)                                         #Checks if the id already exists in the database

            sql1 = "INSERT INTO measurements VALUES(%d, '%s', '%s', %f)" % (id, datestamp, timestamp, measurementvalue)
            sql2 = "INSERT INTO channels VALUES(%d, '%s')" % (id, name)

            if found:                                                               #If the channel id is already in the database only the measurement attributes gets added
                curs.execute(sql1)
            else:                                                                   #Otherwise, the channel id gets added aswell
                curs.execute(sql1)
                curs.execute(sql2)

        conn.commit()
        conn.close()
        return True
    except TypeError as err:
        print(err)
        print("Something went wrong, read the error message")
        return False


