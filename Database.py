"""
This module can be used to create and interact with the system databases
"""

import pymysql
import datetime
import configinterface




def remote_add_new_pi(dbvalues, name):
    """
    Adds a new pi to the remote database, this includes updating the channels table
    :param dbvalues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'} 
    :param name: a string containing the name of the pi to be stored in the database
    :return: the id given to the pi by the database or none if something went wrong
    """
    try:
        conn = pymysql.connect(user=dbvalues['user'],                          # Establishes connection to the database
                               host=dbvalues['host'],
                               password=dbvalues['password'],
                               database=dbvalues['name'],
                               port=int(dbvalues['port']))
        cursor = conn.cursor()

        inserttopis = "insert into pis(name_pis) values('%s')" % (name,)       # SQL query for inserting pi to the table
        cursor.execute(inserttopis)

        sql = "select last_insert_id() from pis"                               # Retrieves the id given to the pi
        cursor.execute(sql)
        piid = cursor.fetchone()[0]

        insertvalues = ""
        for index in range(1, 61):
            insertvalues = insertvalues + " (%d)," % (piid, )                  # creates a string with the insertvalues
        insertvalues = insertvalues[:-1]                                       # Formats the string to query format

        inserttochannels = "insert into channels(fk_pis_channels) " \
            "values " + insertvalues                                           # Insert query for the channels table
        cursor.execute(inserttochannels)
        conn.commit()
        conn.close()
        return piid
    except TypeError as T:
        print('remote_add_new_pi Testerror: ')
        print(T)
        raise T
    except pymysql.err.Error as E:                                             # Raise exception if MySQL gives one
        print('remote_add_new_pi, MySQL Error')
        print(E)
        raise E




def remote_start_new_session(dbvalues, name, channels, piid):
    """
    Adds a new session to the database
    :param dbvalues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'} 
    :param name: a string containging the name of the session to be stored in the database
    :param channels: a dictionary containing the channel values to be added to the session
    Example: {1: '['Temperature', 'celsius', 2.2], 2: ['Force', 'Newton', 4.3]'}
    :return: The session id of the session created 
    """
    try:
        conn = pymysql.connect(user=dbvalues['user'],                          # Establishes connection to the database
                               host=dbvalues['host'],
                               password=dbvalues['password'],
                               database=dbvalues['name'],
                               port=int(dbvalues['port']))

        cursor = conn.cursor()

        start = datetime.datetime.now()
        startfractions = start.microsecond

        insertsession = "insert into " \
            "sessions(name_sessions, start_sessions, fk_pis_sessions, startfractions_sessions) " \
            "values('%s', '%s', %d, %f)" % (name, start, piid, startfractions)           # Insertion query for the sessions table

        cursor.execute(insertsession)

        readsession = "select last_insert_id()"                                # Retrieves the id given to the session
        cursor.execute(readsession)
        sessionid = cursor.fetchone()[0]


        templist = []
        print(channels)
        for index in channels:
            #channels[index] = ast.literal_eval(channels[index])

            templist.append((sessionid,
                             int(index),
                             channels[index][1],
                             channels[index][2],
                             float(channels[index][3])))                       # Creates a list with all insertvalues
        insertvalues = str(templist)                                           # Turns the list into a string
        insertvalues = insertvalues[1:-1]                                      # Formats the string to query format

        insert = "insert into " \
            "session_channels(fk_sessions_session_channels, " \
            "fk_channels_session_channels, " \
            "channelname_session_channels, " \
            "unit_session_channels, tolerance_session_channels) " \
            "values" + insertvalues                                            # Inserts into session_channels table
        cursor.execute(insert)

        conn.commit()
        conn.close()
        return sessionid
    except TypeError as T:
        print('start_new_session Typeerror: ')
        print(T)
        raise T
    except RuntimeError as R:
        print('Runtimeerror: ')
        print(R)
        raise R
    except pymysql.err.Error as E:
        print('start_new _session MySQL error: ')
        print(E)
        raise E

def start_new_session(dbvalues, name, channels):
    """
    Adds a new session to the database
    :param dbvalues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'} 
    :param name: a string containging the name of the session to be stored in the database
    :param channels: a dictionary containing the channel values to be added to the session
    Example: {1: '['Temperature', 'celsius', 2.2], 2: ['Force', 'Newton', 4.3]'}
    :return: The session id of the session created 
    """
    try:
        conn = pymysql.connect(user=dbvalues['user'],                          # Establishes connection to the database
                               host=dbvalues['host'],
                               password=dbvalues['password'],
                               database=dbvalues['name'],
                               port=int(dbvalues['port']))

        cursor = conn.cursor()

        start = datetime.datetime.now()
        startfractions = start.microsecond

        insertsession = "insert into " \
            "sessions(name_sessions, start_sessions, startfractions_sessions) " \
            "values('%s', '%s', %f)" % (name, start, startfractions)           # Insertion query for the sessions table

        cursor.execute(insertsession)

        readsession = "select last_insert_id()"                                # Retrieves the id given to the session
        cursor.execute(readsession)
        sessionid = cursor.fetchone()[0]


        templist = []
        print(channels)
        for index in channels:
            #channels[index] = ast.literal_eval(channels[index])

            templist.append((sessionid,
                             int(index),
                             channels[index][1],
                             channels[index][2],
                             float(channels[index][3])))                       # Creates a list with all insertvalues
        insertvalues = str(templist)                                           # Turns the list into a string
        insertvalues = insertvalues[1:-1]                                      # Formats the string to query format

        insert = "insert into " \
            "session_channels(fk_sessions_session_channels, " \
            "fk_channels_session_channels, " \
            "channelname_session_channels, " \
            "unit_session_channels, tolerance_session_channels) " \
            "values" + insertvalues                                            # Inserts into session_channels table
        cursor.execute(insert)

        conn.commit()
        conn.close()
        return sessionid
    except TypeError as T:
        print('start_new_session Typeerror: ')
        print(T)
        raise T
    except RuntimeError as R:
        print('Runtimeerror: ')
        print(R)
        raise R
    except pymysql.err.Error as E:
        print('start_new _session MySQL error: ')
        print(E)
        raise E


def end_current_session(dbvalues, sessionid):
    """
    Adds an end value to a specified session 
    :param dbvalues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
    :param sessionid: an int representing the id of the session to be ended
    :return: an int representing the number of rows affected
    """
    try:
        conn = pymysql.connect(user=dbvalues['user'],                          # Establishes connection to the database
                               host=dbvalues['host'],
                               password=dbvalues['password'],
                               database=dbvalues['name'],
                               port=int(dbvalues['port']))
        cursor = conn.cursor()

        end = datetime.datetime.now()                                   # Time used as end time for the session
        endfractions = end.microsecond
        setend = "update sessions set end_sessions = '%s', " \
            "endfractions_sessions = %f " \
            "where id_sessions = %d" % (end, endfractions, sessionid)
        affectedrows = cursor.execute(setend)                                 # Sets the end time of the session

        conn.commit()
        conn.close()
        return affectedrows
    except TypeError as T:
        print('Typeerror: ')
        print(T)
    except RuntimeError as R:
        print('Runtimeerror: ')
        print(R)
    except pymysql.err.Error as E:
        print('end_current_session MySQL Error')
        print(E)
        raise E


def create_remote_database(dbvalues):
    """
    Creates a database with the structure of the 'remote database'
    :param dbvalues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
    :return: True if a database was created, false otherwise
    """
    try:
        conn = pymysql.connect(user=dbvalues['user'],                          # Establishes connection to the database
                               host=dbvalues['host'],
                               password=dbvalues['password'],
                               port=int(dbvalues['port']))
        cursor = conn.cursor()

        sql = "show databases like '%s'" % (dbvalues['name'])
        result = cursor.execute(sql)                                           # Checks if the database exists

        if result == 0:                                                        # If the database doesnt exist
            sql2 = "Create database %s" % (dbvalues['name'])
            cursor.execute(sql2)
            sql3 = "use %s" % (dbvalues['name'])
            cursor.execute(sql3)                                               # Creates and uses the database

            createpis = "create table " \
                "pis(id_pis int primary key auto_increment, " \
                "name_pis varchar(50))"                                        # Creates the 'pis' table

            createchannels = "create table " \
                "channels(id_channels int primary key auto_increment, " \
                "fk_pis_channels int, " \
                "foreign key (fk_pis_channels) " \
                "references pis(id_pis))"                                      # Creates the 'channels' table

            createsession = "create table " \
                "sessions(id_sessions int primary key auto_increment, " \
                "name_sessions varchar(50), " \
                "fk_pis_sessions int, " \
                "start_sessions datetime, " \
                "startfractions_sessions float, " \
                "end_sessions datetime," \
                "endfractions_sessions float, " \
                "foreign key (fk_pis_sessions) " \
                "references pis(id_pis))"                                 # Creates the 'sessions' table

            createmeasurements = "create table " \
                "measurements(fk_sessions_measurements int, " \
                "fk_channels_measurements int, " \
                "timestamp_measurements datetime, " \
                "timestampfractions_measurements float, " \
                "data_measurements float, foreign key (fk_sessions_measurements) " \
                "references sessions(id_sessions), " \
                "foreign key (fk_channels_measurements) " \
                "references channels(id_channels), " \
                "primary key (fk_sessions_measurements, " \
                "fk_channels_measurements, " \
                "timestamp_measurements, timestampfractions_measurements))"    # Creates the 'measurements' table

            createsessionchannel = "create table " \
                "session_channels(fk_sessions_session_channels int, " \
                "fk_channels_session_channels int, " \
                "channelname_session_channels varchar(50), " \
                "unit_session_channels varchar(50), " \
                "tolerance_session_channels float, " \
                "foreign key (fk_sessions_session_channels) " \
                "references sessions(id_sessions), " \
                "unique key (fk_sessions_session_channels, channelname_session_channels), " \
                "foreign key (fk_channels_session_channels) " \
                "references channels(id_channels), " \
                "primary key (fk_sessions_session_channels, " \
                "fk_channels_session_channels))"                               # Creates the 'session_channels' table

            cursor.execute(createpis)
            cursor.execute(createchannels)
            cursor.execute(createsession)
            cursor.execute(createmeasurements)
            cursor.execute(createsessionchannel)                               # Executes the creation queries

            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
    except TypeError as T:
        print('Typeerror: ')
        print(T)
        raise T
    except pymysql.err.Error as dbe:
        print("create_remote_database MySQL Error: ")
        print(dbe)
        raise dbe


def create_local_database(dbvalues):
    """
    Creates a database with the structure of the 'local database'
    :param dbvalues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
    :return: True if a database was created, false otherwise
    """
    try:
        conn = pymysql.connect(user=dbvalues['user'],
                               host=dbvalues['host'],
                               password=dbvalues['password'],
                               port=int(dbvalues['port']))                     # Establishes connection to the database
        cursor = conn.cursor()

        sql = "show databases like '%s'" % (dbvalues['name'])
        result = cursor.execute(sql)                                           # Checks if the database exists

        if result == 0:                                                        # If the database doesnt exist
            sql2 = "Create database %s" % (dbvalues['name'])
            cursor.execute(sql2)
            sql3 = "use %s" % (dbvalues['name'])
            cursor.execute(sql3)                                               # Creates and uses the database

            createchannels = "create table " \
                "channels(id_channels int primary key)"                        # Creates the 'channels' table

            createsession = "create table " \
                "sessions(id_sessions int primary key auto_increment, " \
                "name_sessions varchar(50), " \
                "start_sessions datetime, " \
                "startfractions_sessions float, " \
                "end_sessions datetime, " \
                "endfractions_sessions float)"                                       # Creates the 'sessions' table

            createmeasurements = "create table " \
                "measurements(fk_sessions_measurements int, " \
                "fk_channels_measurements int, " \
                "timestamp_measurements datetime, " \
                "timestampfractions_measurements float, " \
                "data_measurements float, " \
                "foreign key (fk_sessions_measurements) " \
                "references sessions(id_sessions), " \
                "foreign key (fk_channels_measurements) " \
                "references channels(id_channels), " \
                "primary key (fk_sessions_measurements, " \
                "fk_channels_measurements, " \
                "timestamp_measurements, timestampfractions_measurements))"    # Creates the 'measurements' table

            createsessionchannel = "create table " \
                "session_channels(fk_sessions_session_channels int, " \
                "fk_channels_session_channels int, " \
                "channelname_session_channels varchar(50), " \
                "unit_session_channels varchar(50), " \
                "tolerance_session_channels float, " \
                "foreign key (fk_sessions_session_channels)" \
                "references sessions(id_sessions), " \
                "unique key (fk_sessions_session_channels, channelname_session_channels), " \
                "foreign key (fk_channels_session_channels) " \
                "references channels(id_channels), " \
                "primary key (fk_sessions_session_channels, " \
                "fk_channels_session_channels))"                               # Creates the 'session_channels' table

            cursor.execute(createchannels)
            cursor.execute(createsession)
            cursor.execute(createmeasurements)
            cursor.execute(createsessionchannel)                               # Executes the creation queries





            for i in range(1, 61):
                insert = "Insert into " \
                        "channels (id_channels) values(%d)" % (i)
                cursor.execute(insert)  # Populates the 'channels' table

            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
    except TypeError as T:
        print('Typeerror: ')
        print(T)
        raise T
    except pymysql.err.Error as dbe:
        print("create_local_database MySQL Error: ")
        print(dbe)
        raise dbe


def drop_database(dbvalues):
    """
    Deletes a specified database 
    :param dbvalues: a python dictionary containing MySQL connection values for the database to be deleted
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
    :return: True if the database was deleted, False otherwise
    """
    try:
        conn = pymysql.connect(user=dbvalues['user'],                          # Establishes connection to the database
                               host=dbvalues['host'],
                               password=dbvalues['password'],
                               port=int(dbvalues['port']))
        cursor = conn.cursor()

        sql = "drop database if exists %s" % (dbvalues['name'],)               # Deletes the database
        cursor.execute(sql)
        conn.commit()
        conn.close()
        return True
    except Warning as W:
        print(W)
    except TypeError as T:
        print('drop_database Typeerror: ')
        print(T)
        raise T
    except pymysql.err.Error as E:
        print('drop_database MySQL Error: ')
        print(E)
        raise E


def get_channels_list(dbvalues):
    """
    Retrieves a list of all the channels currently in the database
    :param dbvalues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
    :return: a tuple consisting of tuples containing the row values tretrieved 
    Example: ((1, 'Living room'), (2, 'Kitchen'))
    """
    try:
        conn = pymysql.connect(user=dbvalues['user'],                          # Establishes connection to the database
                               host=dbvalues['host'],
                               password=dbvalues['password'],
                               database=dbvalues['name'],
                               port=int(dbvalues['port']))

        cursor = conn.cursor()
        sql = "select * from channels"                                         # Retrieves all channels from 'channels'
        cursor.execute(sql)
        result = cursor.fetchall()
        conn.close()
        return result
    except TypeError as T:
        print('get_channels_list Typeerror: ')
        print(T)
        raise TypeError
    except RuntimeError as R:
        print('get_channels_list Runttimeerror: ')
        print(R)
        raise R
    except pymysql.err.Error as E:
        print('get_channels_list MySQL Error')
        print(E)
        raise E


def get_session_information(dbvalues, sessionid):
    """
    Retrieves inofrmation about a specified session from the database
    :param dbvalues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
    :param sessionid: an int representing the id of the session 
    :return: a tuple containing all available information about a session
    Example: {'name': 'session one', 'start': '2017-07-03 15:23:12', 'startfractions': 142, 'end': '2017-12-12 16:23:45', 'endfractions': 23423}
    """
    try:
        conn = pymysql.connect(user=dbvalues['user'],                          # Establishes connection to the database
                               host=dbvalues['host'],
                               password=dbvalues['password'],
                               database=dbvalues['name'],
                               port=int(dbvalues['port']))

        cursor = conn.cursor()
        sql = "select * from sessions " \
              "where id_sessions = %d" % (sessionid,)
        cursor.execute(sql)                                                    # Retrieves information from 'sessions'

        queyresult = cursor.fetchall()
        result = {'id': queyresult[0][0], 'name': queyresult[0][1], 'start': queyresult[0][2],
                  'startfractions': queyresult[0][3], 'end': queyresult[0][4], 'endfractions': queyresult[0][5]}

        conn.close()
        return result
    except TypeError as T:
        print('get_session_information Typeerror: ')
        print(T)
        raise TypeError
    except RuntimeError as R:
        print('get_session_information Runttimeerror: ')
        print(R)
        raise R
    except pymysql.err.Error as E:
        print('get_session_information MySQL Error')
        print(E)
        raise E


def remote_get_pi_list(dbvalues):
    """
    Retrieves a list of all the pis currently in the remote database
    :param dbvalues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
    :return: a tuple consisting of tuples containing Pi id and name or None if something went wrong
    Example: ((1, 'Living room'), (2, 'Kitchen'))
    """
    try:
        conn = pymysql.connect(user=dbvalues['user'],                          # Establishes connection to the database
                               host=dbvalues['host'],
                               password=dbvalues['password'],
                               database=dbvalues['name'],
                               port=int(dbvalues['port']))

        cursor = conn.cursor()
        sql = "select * from pis"                                              # Retrieves all pis from 'pis'
        cursor.execute(sql)

        result = cursor.fetchall()
        conn.close()
        return result
    except TypeError as T:
        print('remote_get_pi_list Typeerror: ')
        print(T)
        raise TypeError
    except RuntimeError as R:
        print('remote_get_pi_list Runttimeerror: ')
        print(R)
        raise R
    except pymysql.err.Error as E:
        print('remote_get_pi_list MySQL Error')
        print(E)
        raise E


def get_session_list(dbvalues):
    """
    Retrieves a list of all the pis currently in the remote database
    :param dbvalues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
    :return: a tuple consisting of tuples containing Pi id and name or None if something went wrong
    Example: ((1, 'Living room'), (2, 'Kitchen'))
    """
    try:
        conn = pymysql.connect(user=dbvalues['user'],                          # Establishes connection to the database
                               host=dbvalues['host'],
                               password=dbvalues['password'],
                               database=dbvalues['name'],
                               port=int(dbvalues['port']))

        cursor = conn.cursor()
        sql = "select id_sessions, name_sessions from sessions"                                         # Retrieves all sessions from 'sessions'
        cursor.execute(sql)

        result = cursor.fetchall()
        conn.close()
        return result
    except TypeError as T:
        print('get_session_list Typeerror: ')
        print(T)
        raise TypeError
    except RuntimeError as R:
        print('get_session_list Runttimeerror: ')
        print(R)
        raise R
    except pymysql.err.Error as E:
        print('get_session_list MySQL Error')
        print(E)
        raise E


def get_session_channel_list(dbvalues, sessionid):
    """    
    Retrieves a list of all channels in a session
    :param dbvalues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
    :param sessionid: an int representing the id of the session
    :return: a tuple containing channel id and channel name of all the channels connected to the session
    Example: ((1, 'channel1'), (2, 'channel2'))
    """
    try:
        conn = pymysql.connect(user=dbvalues['user'],                          # Establishes connection to the database
                               host=dbvalues['host'],
                               password=dbvalues['password'],
                               database=dbvalues['name'],
                               port=int(dbvalues['port']))
        cursor = conn.cursor()

        sql = "select fk_channels_session_channels, " \
            "channelname_session_channels " \
            "from session_channels " \
            "where fk_sessions_session_channels = '%d'" % (sessionid, )        # Retrieves the channels of the sessionid
        cursor.execute(sql)

        result = cursor.fetchall()
        conn.close()
        return result
    except TypeError as T:
        print('get_session_channel_list Typerror: ')
        print(T)
        raise T
    except RuntimeError as R:
        print(R)
        raise R
    except pymysql.err.Error as E:
        print('get_session_channel_list MySQL Error:')
        print(E)
        raise E


def get_measurements(dbvalues, sessionid, channelid, starttime, endtime):
    """
    Retrieves measurements from the database using the arguments as search parameters
    :param dbvalues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
    :param sessionid: an int representing the session id 
    :param channelid: an int representing the channel id 
    :param starttime: a string representing the start date and time of the search 
    :param endtime: a string representing the end date and time of the search
    :return: the result of the database read
    Example: 
    """
    try:
        conn = pymysql.connect(user=dbvalues['user'],                          # Establishes connection to the database
                               host=dbvalues['host'],
                               password=dbvalues['password'],
                               database=dbvalues['name'],
                               port=int(dbvalues['port']))
        cursor = conn.cursor()

        if starttime == None and endtime == None:
            if channelid == None:
                readsql = "SELECT * FROM measurements " \
                          "WHERE fk_sessions_measurements = %d" \
                          % (sessionid,)  # Searches the database
            else:
                readsql = "SELECT * FROM measurements " \
                          "WHERE fk_sessions_measurements = %d " \
                          "AND fk_channels_measurements = %d" \
                          % (sessionid,
                             channelid)
        else:
            if channelid == None:
                readsql = "SELECT * FROM measurements " \
                          "WHERE fk_sessions_measurements = %d AND " \
                          "timestamp_measurements >= '%s' AND " \
                          "timestamp_measurements <= '%s'" \
                          % (sessionid, starttime, endtime)  # Searches the database
            else:
                readsql = "SELECT * FROM measurements " \
                          "WHERE fk_sessions_measurements = %d AND " \
                          "timestamp_measurements >= '%s' AND " \
                          "timestamp_measurements <= '%s' AND " \
                          "fk_channels_measurements = %d" \
                          % (sessionid,
                             starttime,
                             endtime,
                             channelid)



        cursor.execute(readsql)
        result = cursor.fetchall()
        conn.close()
        return result
    except TypeError as T:
        print('get_measurements Typerror: ')
        print(T)
        raise T
    except pymysql.err.Error as E:
        print('get_measurements MySQL Error: ')
        print(E)
        raise E


def add_to_database(dbvalues, list_of_items, sessionid):
    """
    Adds measurements to the database from a list of values
    :param dbvalues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
    :param list_of_items: a dictionary containing channel id's as keys and measurements as values
    Example: {1: 25.6, 2: 22.3}
    :param sessionid: an int representing the id of the session that collected the measurements
    :return: True if something was added to the database, false otherwise
    """
    try:
        conn = pymysql.connect(user=dbvalues['user'],                          # Establishes connection to the database
                               host=dbvalues['host'],
                               password=dbvalues['password'],
                               database=dbvalues['name'],
                               port=int(dbvalues['port']))
        curs = conn.cursor()

        rawtimestamp = datetime.datetime.now()                                      # Gets the time of the addition
        timestamp = rawtimestamp.strftime('%Y-%m-%d %H:%M:%S')
        timestampfractions = rawtimestamp.microsecond                               # Gets the date of the addition

        print('Addition timestamp')
        print(timestamp)
        templist = []
        for index in list_of_items:
            channelid = index
            measurementvalue = list_of_items[index]
            templist.append((sessionid,
                             channelid,
                             timestamp,
                             timestampfractions,
                             measurementvalue))                                # Creates a list of values to be added

        addvalues = str(templist)
        addvalues = addvalues[1:-1]                                            # Creates a string formatted for MySQL

        sql1 = "Insert INTO " \
            "measurements(fk_sessions_measurements, " \
            "fk_channels_measurements, " \
            "timestamp_measurements, timestampfractions_measurements, " \
            "data_measurements) " \
            "VALUES" + addvalues                                                # Adds the values to the database
        curs.execute(sql1)

        conn.commit()
        conn.close()
        return True
    except TypeError as T:
        print('add_to_database Typerror: ')
        print(T)
        return False
    except pymysql.err.Error as E:
        print('add_to_database MySQL error: ')
        print(E)
        raise E
    except pymysql.err.IntegrityError as E2:
        print('add_to_database MySQL IntegrityError: ')
        print(E2)
        raise E2

def remote_add_to_database(dbvalues, list_of_items):
    """
    Adds measurements to the database from a list of values
    :param dbvalues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
    :param list_of_items: a dictionary containing channel id's as keys and measurements as values
    Example: {1: 25.6, 2: 22.3}
    :param sessionid: an int representing the id of the session that collected the measurements
    :return: True if something was added to the database, false otherwise
    """
    try:
        conn = pymysql.connect(user=dbvalues['user'],                          # Establishes connection to the database
                               host=dbvalues['host'],
                               password=dbvalues['password'],
                               database=dbvalues['name'],
                               port=int(dbvalues['port']))
        curs = conn.cursor()

        addvalues = str(list_of_items)
        addvalues = addvalues[1:-1]                                            # Creates a string formatted for MySQL

        sql1 = "INSERT INTO " \
            "measurements(fk_sessions_measurements, " \
            "fk_channels_measurements, " \
            "timestamp_measurements, timestampfractions_measurements, " \
            "data_measurements) " \
            "VALUES" + addvalues                                               # Adds the values to the database
        curs.execute(sql1)

        conn.commit()
        conn.close()
        return True
    except TypeError as T:
        print('add_to_database Typerror: ')
        print(T)
        return False
    except pymysql.err.Error as E:
        print('add_to_database MySQL error: ')
        print(E)
        raise E
    except pymysql.err.IntegrityError as E2:
        print('add_to_database MySQL IntegrityError: ')
        print(E2)
        raise E2

def convert_to_remote_insert(values, newsession, piid):
    for row in values:
        row['fk_sessions_measurements'] = newsession
        row['fk_channels_measurements'] = row['fk_channels_measurements']+60*(piid-1)
    return values

if __name__ == '__main__':
    db = configinterface.read_config('config.cfg', 'default')
    create_local_database(db)
