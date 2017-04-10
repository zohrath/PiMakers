'''
This module acts as an interface to a local database
'''

import mysql.connector
import os
import time
import configparser


def create_database():
    '''
    This function creates a database using parameters specified in a configuration file
    :return: 
    '''
    reader = configparser.ConfigParser()                                        #Reads from the configuration file
    reader.read('config.cfg')

    host = reader.get('default', 'host')
    user = reader.get('default', 'user')                                            #Gets specific configurations from the configuration file
    password = reader.get('default', 'password')
    name = reader.get('default', 'name')

    expression = "mysql -h " + host + " -u " + user \
                 + " --password=" + password + \
                 " --execute='create database if not exists " + name + "'"          #Build the system command creates the database

    os.system(expression)


def id_exists(id, cursorcopy):
    '''
    This function checks if a channel id exists in the database
    :param id: channel id to look for 
    :param cursorcopy: a connection.cursor() cursor to the database
    :return: True if the channel id was found, false otherwise
    '''
    try:
        sql = "SELECT id FROM channels WHERE id = ?"                                #Looks for the channel id in the database
        cursorcopy.execute(sql, (id,))
        value = cursorcopy.fetchone()
        if value != None:                                                           #Checks if any value was found
            return True
        else:
            return False
    except mysql.connector.Error as err:
        print(err)


def add_to_database(list_of_items):
    '''
    This function adds values to the database from a list of items
    :param list_of_items: a python dictionary where the key is a 
    unique integer and the value is a list structured as:[channelname, measurementvalue] 
    :return: 
    '''
    reader = configparser.ConfigParser()                                        #Reads from the configuration file
    reader.read('config.cfg')

    user = reader.get('default', 'user')
    host = reader.get('default', 'host')                                            #Gets specific configurations from the configuration file
    password = reader.get('default', 'password')
    dbname = reader.get('default', 'name')

    try:
        conn = mysql.connector.connect(user = user, host = host, password = password, database = dbname)        # Connects to the database
        curs = conn.cursor(prepared=True)
        print("Connected to database succcessfully")
    except mysql.connector.Error as err:
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

            found = id_exists(id, curs)                                             #Checks if the id already exists in the database

            sql1 = "INSERT INTO measurements VALUES(?, ?, ?, ?)"
            sql2 = "INSERT INTO channels VALUES(?, ?)"

            if found:                                                               #If the channel id is already in the database only the measurement attributes gets added
                curs.execute(sql1, (id, datestamp, timestamp, measurementvalue))
            else:                                                                   #Otherwise, the channel id gets added aswell
                curs.execute(sql1, (id, datestamp, timestamp, measurementvalue))
                curs.execute(sql2, (id, name))

        conn.commit()
        conn.close()
    except mysql.connector.Error as err:
        print(err)
        print("Something went wrong, read the error message")


list = {1:['channel1', 28.4], 40:['channel40', 18.34]}
add_to_database(list)
