'''
This module acts as an interface to the local database
'''

import pymysql
import time
import datetime
import configInterface




def change_channel_name(dbvalues, name, id):
    '''
    This function changes the name connected to a channel id
    :param dbvalues: configuration values for the database
    Example: {'user': 'root', 'host':'127.0.0.1', 'password': '1234', 'name': 'EmployeeDatabase'}
    :param name: the new name of the channel
    :param id: the channel id
    :return: True if the name was changed, False otherwise
    '''
    try:
        conn = pymysql.connect(user=dbvalues['user'], host=dbvalues['host'], password=dbvalues['password'], database=dbvalues['name'])
        cursor = conn.cursor()
        sql = "update channels set name = '%s' where id = %d" % (name, id)
        cursor.execute(sql)
        conn.commit()
        conn.close()
        return True
    except RuntimeError as R:
        print(R)
    except TypeError as T:
        print(T)
        return False

def reset_channel(dbvalues, id):
    '''
    This function resets a channel and removes its measurements from the database
    :param dbvalues: configuration values for the database
    Example: {'user': 'root', 'host':'127.0.0.1', 'password': '1234', 'name': 'EmployeeDatabase'}
    :param id: the id of the channel to be reset
    :return: True, if the channel was reset
    '''
    try:
        conn = pymysql.connect(user=dbvalues['user'], host=dbvalues['host'], password=dbvalues['password'], database=dbvalues['name'])
        cursor = conn.cursor()
        sql = "delete from measurements where c_id = '%d'" % (id, )
        cursor.execute(sql)
        sql2 = "update channels set name = 'channel%d' where id = %d" % (id, id)
        cursor.execute(sql2)
        conn.commit()
        conn.close()
        return True
    except RuntimeError as R:
        print(R)
    except TypeError as T:
        print(T)
        return False


def create_database(dbvalues):
    '''
    This function creates a database using parameters specified in a configuration file
    :param: dbvalues : configuration values for the database
    Example: {'user': 'root', 'host':'127.0.0.1', 'password': '1234', 'name': 'EmployeeDatabase'}
    :return: True if a database was created, false otherwise
    '''
    try:
        conn = pymysql.connect(user=dbvalues['user'], host=dbvalues['host'], password=dbvalues['password'])  # Establish mysql connection
        cursor = conn.cursor()
        sql = "show databases like '%s'" % (dbvalues['name'])
        result = cursor.execute(sql)
        if result == 0:  # If the database does not exist, create a new database and tables
            sql2 = "Create database %s" % (dbvalues['name'])
            cursor.execute(sql2)
            sql3 = "use %s" % (dbvalues['name'])
            cursor.execute(sql3)
            sql4 = "create table channels(id int primary key, name text)"
            sql5 = "create table measurements(c_id int, date date, time time(6), measurementvalue float, unit varchar(50), tolerance varchar(50), foreign key (c_id) references channels(id), primary key(c_id, date, time))"
            cursor.execute(sql4)
            cursor.execute(sql5)
            for index in range(1, 61):
                tempname = "channel%d" % (index,)
                sql6 = "Insert into channels (id, name) values(%d, '%s')" % (index, tempname)
                cursor.execute(sql6)
            conn.commit()
            conn.close()
        return True
    except TypeError as T:
        print(T)
        return False
    except Warning as W:
        return False

def drop_database(dbvalues):
    '''
    This function deletes a database
    :param dbvalues: a dictionary containing configurations for the database to be deleted
    Example: {'user': 'root', 'host':'127.0.0.1', 'password': '1234', 'name': 'EmployeeDatabase'}
    :return: True if the database was deleted, False otherwise
    '''
    try:
        conn = pymysql.connect(user=dbvalues['user'], host=dbvalues['host'], password=dbvalues['password'])
        cursor = conn.cursor()
        sql = "drop database if exists %s" % (dbvalues['name'],)
        cursor.execute(sql)
        conn.commit()
        conn.close()
        return True
    except Warning as W:
        print(W)
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
        conn = pymysql.connect(user=dbvalues['user'], host=dbvalues['host'], password=dbvalues['password'], database=dbvalues['name'])      #Establish connection to database
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



def read_from_database(dbvalues, readparameters):
    '''
    This funtion reads a specified databse using specified parameters
    :param dbvalues: a dictionary containing mysql database configurations
    Example: {'user': 'root', 'host':'127.0.0.1', 'password': '1234', 'name': 'EmployeeDatabase'}
    :param readparameters: a dictionary containing the parameters to be used in the read. 
    Example: {'id': 1, 'fromdate': '2017-04-09', 'todate': '2017-04-10', 'fromtime': '15:00:00', 'totime': '16:00:00'}
    :return: A tuple where each item represents a row returned from the database
    Example: ((1, 'channel1', datetime.date(2017, 4, 9), datetime.timedelta(0, 41759), 28.4))
    '''
    try:
        conn = pymysql.connect(user=dbvalues['user'], host=dbvalues['host'], password=dbvalues['password'], database=dbvalues['name'])  # Establish connection to database
        cursor = conn.cursor()
        id = readparameters['id']

        fromdate = readparameters['fromdate']
        fromtime = readparameters['fromtime']

        todate = readparameters['todate']
        totime = readparameters['totime']

        if fromtime == totime:
            totime = totime + ".999999"

        nestedsql = "(SELECT * FROM measurements WHERE date >= '%s' AND date <= '%s' AND time >= '%s' AND time <= '%s' AND c_id = %d)" % (fromdate, todate, fromtime, totime, id)
        sql = "SELECT temp.c_id, name, date, time, measurementvalue FROM %s AS temp INNER JOIN channels ON channels.id = temp.c_id ORDER BY date, time" % (nestedsql,)
        cursor.execute(sql)
        result = cursor.fetchall()
        return result
    except RuntimeError as err:
        print(err)
        return None

def add_to_database(dbvalues, list_of_items):
    '''
    This function adds entries to a specified database using a provided list of entry values
    :param dbvalues: a dictionary containing mysql configurations
    Example: {'user': 'root', 'host':'127.0.0.1', 'password': '1234', 'name': 'EmployeeDatabase'}
    :param list_of_items: a dictionary containing containing the needed values to make an entry to the database
    Example: {1: [ 25.6, 'Kg', '20'], 2: [22.3, 'Celsius', '2']}
    :return: True if something was added to the database, false otherwise
    '''
    try:
        conn = pymysql.connect(user=dbvalues['user'], host=dbvalues['host'], password=dbvalues['password'], database=dbvalues['name'])        #Connects to the database
        curs = conn.cursor()

        rawtime = datetime.datetime.now()                                       #Gets time and date
        timestamp = "%d:%d:%d.%d" % (rawtime.hour, rawtime.minute, rawtime.second, rawtime.microsecond)
        datestamp = time.strftime("%Y-%m-%d")

        for index in list_of_items:                                                 #For each item in the list, gets the values to be added to the database
            id = index
            list = list_of_items[index]
            measurementvalue = list[0]
            unit = list[1]
            tolerance = list[2]

            #found = id_exists(id, dbvalues)

            sql1 = "INSERT INTO measurements (c_id, date, time, measurementvalue, unit, tolerance) VALUES(%d, '%s', '%s', %f, '%s', '%s')" % (id, datestamp, timestamp, measurementvalue, unit, tolerance)
            curs.execute(sql1)

        conn.commit()
        conn.close()
        return True
    except TypeError as err:
        print(err)
        print("Something went wrong, read the error message")
        return False


