'''
This module acts as an interface to a local database
'''

import pymysql
import os
import time
import configparser


def create_database(dbvalues):
    '''
    This function creates a database using parameters specified in a configuration file
    :return: 
    '''
    try:
        conn = pymysql.connect(user=dbvalues['user'], host=dbvalues['host'], password=dbvalues['password'])
        cursor = conn.cursor()
        sql = "show databases like '%s'" % (dbvalues['name'])
        print(sql)
        result = cursor.execute(sql)
        print(result)
        if result == 0:
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
    :param cursorcopy: a connection.cursor() cursor to the database
    :return: True if the channel id was found, false otherwise
    '''
    try:
        conn = pymysql.connect(user = dbvalues['user'], host = dbvalues['host'], password = dbvalues['password'], database = dbvalues['name'])
        cursor = conn.cursor()
        sql = "SELECT id FROM channels WHERE id = '%d'"  % (id, )                               #Looks for the channel id in the database
        cursor.execute(sql)
        value = cursor.fetchone()
        if value != None:                                                           #Checks if any value was found
            return True
        else:
            return False
    except RuntimeError as err:
        print(err)

def establish_connection(dbvalues):
    try:
        conn = pymysql.connect(user=dbvalues['user'], host=dbvalues['host'], password=dbvalues['password'], database=dbvalues['name'])
        cursor = conn.cursor()
        return cursor
    except RuntimeError as err:
        print(err)
        return None


def add_to_database(list_of_items, dbvalues):
    '''
    This function adds values to the database from a list of items
    :param list_of_items: a python dictionary where the key is a 
    unique integer and the value is a list structured as:[channelname, measurementvalue] 
    :return: 
    '''


    try:
        conn = pymysql.connect(user = dbvalues['user'], host = dbvalues['host'], password = dbvalues['password'], database = dbvalues['name'])        # Connects to the database
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

            found = id_exists(id, dbvalues)                                             #Checks if the id already exists in the database

            sql1 = "INSERT INTO measurements VALUES(%d, '%s', '%s', %f)" % (id, datestamp, timestamp, measurementvalue)
            print(sql1)
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


