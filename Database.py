"""
This module can be used to create and interact with the system databases
"""

import pymysql
import datetime
import configInterface


def remoteGetPiid(databaseValues, uuid):
    try:
        conn = pymysql.connect(user=databaseValues['user'],  # Establishes connection to the database
                               host=databaseValues['host'],
                               password=databaseValues['password'],
                               database=databaseValues['name'],
                               port=int(databaseValues['port']))
        cursor = conn.cursor()

        sql = "select id_pis from pis where uniquekey = '%s'" % (uuid, )
        cursor.execute(sql)
        result = cursor.fetchone()[0]
        return result
    except TypeError as T:
        print('remote_add_new_pi Testerror: ')
        print(T)
        raise T
    except pymysql.err.Error as E:                                             # Raise exception if MySQL gives one
        print('remote_add_new_pi, MySQL Error')
        print(E)
        raise E


def remotePiExists(databaseValues, uuid):
    try:
        conn = pymysql.connect(user=databaseValues['user'],  # Establishes connection to the database
                               host=databaseValues['host'],
                               password=databaseValues['password'],
                               database=databaseValues['name'],
                               port=int(databaseValues['port']))
        cursor = conn.cursor()

        sql = "select * from pis where uniquekey = '%s'" % (uuid, )
        cursor.execute(sql)
        result = cursor.fetchone()
        if result == ():
            return False
        else:
            return True
    except TypeError as T:
        print('remote_add_new_pi Testerror: ')
        print(T)
        raise T
    except pymysql.err.Error as E:                                             # Raise exception if MySQL gives one
        print('remote_add_new_pi, MySQL Error')
        print(E)
        raise E




def remoteAddNewPi(databaseValues):
    """
    Adds a new pi to the remote database, this includes updating the channels table
    :param databaseValues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'} 
    :param name: a string containing the name of the pi to be stored in the database
    :return: the id given to the pi by the database or none if something went wrong
    """
    try:
        conn = pymysql.connect(user=databaseValues['user'],  # Establishes connection to the database
                               host=databaseValues['host'],
                               password=databaseValues['password'],
                               database=databaseValues['name'],
                               port=int(databaseValues['port']))
        cursor = conn.cursor()

        trigger = "create trigger save_uuid after insert on pis for each row set @last_uuid = new.uniquekey"
        cursor.execute(trigger)

        insertToPis = "insert into pis(uniquekey) values(UUID())"        # SQL query for inserting pi to the table
        cursor.execute(insertToPis)

        sql = "select last_insert_id() from pis"                               # Retrieves the id given to the pi
        cursor.execute(sql)
        piid = cursor.fetchone()[0]

        sql2 = "select @last_uuid"  # Retrieves the id given to the pi
        cursor.execute(sql2)
        unique = cursor.fetchone()[0]

        droptrigger = "drop trigger save_uuid"
        cursor.execute(droptrigger)

        insertValues = ""
        for index in range(1, 61):
            insertValues = insertValues + " ('%s')," % (unique, )                  # creates a string with the insertvalues
        insertValues = insertValues[:-1]                                       # Formats the string to query format

        insertToChannels = "insert into channels(fk_pis_channels) " \
            "values " + insertValues                                           # Insert query for the channels table
        cursor.execute(insertToChannels)

        identifiers = {'piid': str(piid), 'uuid': unique}


        conn.commit()
        conn.close()
        return identifiers
    except TypeError as T:
        print('remote_add_new_pi Testerror: ')
        print(T)
        raise T
    except pymysql.err.Error as E:                                             # Raise exception if MySQL gives one
        print('remote_add_new_pi, MySQL Error')
        print(E)
        raise E




def remoteStartNewSession(databaseValues, name, channels, piid):
    """
    Adds a new session to the database
    :param databaseValues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'} 
    :param name: a string containging the name of the session to be stored in the database
    :param channels: a dictionary containing the channel values to be added to the session
    Example: {1: '['Temperature', 'celsius', 2.2], 2: ['Force', 'Newton', 4.3]'}
    :return: The session id of the session created 
    """
    try:
        conn = pymysql.connect(user=databaseValues['user'],  # Establishes connection to the database
                               host=databaseValues['host'],
                               password=databaseValues['password'],
                               database=databaseValues['name'],
                               port=int(databaseValues['port']))

        cursor = conn.cursor()

        start = datetime.datetime.now()
        startFractions = start.microsecond

        insertSession = "insert into " \
            "sessions(name_sessions, start_sessions, fk_pis_sessions, startfractions_sessions) " \
            "values('%s', '%s', '%s', %f)" % (name, start, piid, startFractions)           # Insertion query for the sessions table

        cursor.execute(insertSession)

        readSession = "select last_insert_id()"                                # Retrieves the id given to the session
        cursor.execute(readSession)
        sessionid = cursor.fetchone()[0]


        tempList = []
        print(channels)
        for index in channels:
            print(index)
            #channels[index] = ast.literal_eval(channels[index])

            tempList.append((sessionid,
                             int(channels[index][0]),
                             index,
                             channels[index][1],
                             float(channels[index][2])))                       # Creates a list with all insertvalues
        insertValues = str(tempList)                                           # Turns the list into a string
        insertValues = insertValues[1:-1]                                      # Formats the string to query format

        insert = "insert into " \
            "session_channels(fk_sessions_session_channels, " \
            "fk_channels_session_channels, " \
            "channelname_session_channels, " \
            "unit_session_channels, tolerance_session_channels) " \
            "values" + insertValues                                            # Inserts into session_channels table
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

def startNewSession(databaseValues, name, channels):
    """
    Adds a new session to the database
    :param databaseValues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'} 
    :param name: a string containging the name of the session to be stored in the database
    :param channels: a dictionary containing the channel values to be added to the session
    Example: {1: '['Temperature', 'celsius', 2.2], 2: ['Force', 'Newton', 4.3]'}
    :return: The session id of the session created 
    """
    try:
        conn = pymysql.connect(user=databaseValues['user'],  # Establishes connection to the database
                               host=databaseValues['host'],
                               password=databaseValues['password'],
                               database=databaseValues['name'],
                               port=int(databaseValues['port']))

        cursor = conn.cursor()

        start = datetime.datetime.now()
        startFractions = start.microsecond

        insertSession = "insert into " \
            "sessions(name_sessions, start_sessions, startfractions_sessions) " \
            "values('%s', '%s', %f)" % (name, start, startFractions)           # Insertion query for the sessions table

        cursor.execute(insertSession)

        readSession = "select last_insert_id()"                                # Retrieves the id given to the session
        cursor.execute(readSession)
        sessionId = cursor.fetchone()[0]


        tempList = []
        print(channels)
        for index in channels:
            #channels[index] = ast.literal_eval(channels[index])

            tempList.append((sessionId,
                             int(channels[index][0]),
                             index,
                             channels[index][1],
                             float(channels[index][2])))                       # Creates a list with all insertvalues
        insertValues = str(tempList)                                           # Turns the list into a string
        insertValues = insertValues[1:-1]                                      # Formats the string to query format

        insert = "insert into " \
            "session_channels(fk_sessions_session_channels, " \
            "fk_channels_session_channels, " \
            "channelname_session_channels, " \
            "unit_session_channels, tolerance_session_channels) " \
            "values" + insertValues                                            # Inserts into session_channels table
        cursor.execute(insert)

        conn.commit()
        conn.close()
        return sessionId
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


def endCurrentSession(databaseValues, sessionId):
    """
    Adds an end value to a specified session 
    :param databaseValues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
    :param sessionId: an int representing the id of the session to be ended
    :return: an int representing the number of rows affected
    """
    try:
        conn = pymysql.connect(user=databaseValues['user'],  # Establishes connection to the database
                               host=databaseValues['host'],
                               password=databaseValues['password'],
                               database=databaseValues['name'],
                               port=int(databaseValues['port']))
        cursor = conn.cursor()

        end = datetime.datetime.now()                                   # Time used as end time for the session
        endFractions = end.microsecond
        setEnd = "update sessions set end_sessions = '%s', " \
            "endfractions_sessions = %f " \
            "where id_sessions = %d" % (end, endFractions, sessionId)
        affectedRows = cursor.execute(setEnd)                                 # Sets the end time of the session

        conn.commit()
        conn.close()
        return affectedRows
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


def createRemoteDatabase(databaseValues):
    """
    Creates a database with the structure of the 'remote database'
    :param databaseValues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
    :return: True if a database was created, false otherwise
    """
    try:
        conn = pymysql.connect(user=databaseValues['user'],  # Establishes connection to the database
                               host=databaseValues['host'],
                               password=databaseValues['password'],
                               port=int(databaseValues['port']))
        cursor = conn.cursor()

        sql = "show databases like '%s'" % (databaseValues['name'])
        result = cursor.execute(sql)                                           # Checks if the database exists

        if result == 0:                                                        # If the database doesnt exist
            sql2 = "Create database %s" % (databaseValues['name'])
            cursor.execute(sql2)
            sql3 = "use %s" % (databaseValues['name'])
            cursor.execute(sql3)                                               # Creates and uses the database

            createPis = "create table " \
                "pis(id_pis int primary key auto_increment, " \
                "uniquekey varchar(50) unique)" \
                                                                               # Creates the 'pis' table

            createChannels = "create table " \
                "channels(id_channels int primary key auto_increment, " \
                "fk_pis_channels varchar(50), " \
                "foreign key (fk_pis_channels) " \
                "references pis(uniquekey))"                                  # Creates the 'channels' table

            createSession = "create table " \
                "sessions(id_sessions int primary key auto_increment, " \
                "name_sessions varchar(50), " \
                "fk_pis_sessions varchar(50), " \
                "start_sessions datetime, " \
                "startfractions_sessions float, " \
                "end_sessions datetime," \
                "endfractions_sessions float, " \
                "foreign key (fk_pis_sessions) " \
                "references pis(uniquekey))"                                 # Creates the 'sessions' table

            createMeasurements = "create table " \
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

            createSessionChannel = "create table " \
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

            cursor.execute(createPis)
            cursor.execute(createChannels)
            cursor.execute(createSession)
            cursor.execute(createMeasurements)
            cursor.execute(createSessionChannel)                               # Executes the creation queries

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


def createLocalDatabase(databaseValues):
    """
    Creates a database with the structure of the 'local database'
    :param databaseValues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
    :return: True if a database was created, false otherwise
    """
    try:
        conn = pymysql.connect(user=databaseValues['user'],
                               host=databaseValues['host'],
                               password=databaseValues['password'],
                               port=int(databaseValues['port']))                     # Establishes connection to the database
        cursor = conn.cursor()

        sql = "show databases like '%s'" % (databaseValues['name'])
        result = cursor.execute(sql)                                           # Checks if the database exists

        if result == 0:                                                        # If the database doesnt exist
            sql2 = "Create database %s" % (databaseValues['name'])
            cursor.execute(sql2)
            sql3 = "use %s" % (databaseValues['name'])
            cursor.execute(sql3)                                               # Creates and uses the database

            createChannels = "create table " \
                "channels(id_channels int primary key)"                        # Creates the 'channels' table

            createSession = "create table " \
                "sessions(id_sessions int primary key auto_increment, " \
                "name_sessions varchar(50), " \
                "start_sessions datetime, " \
                "startfractions_sessions float, " \
                "end_sessions datetime, " \
                "endfractions_sessions float)"                                       # Creates the 'sessions' table

            createMeasurements = "create table " \
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

            createSessionChannel = "create table " \
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

            cursor.execute(createChannels)
            cursor.execute(createSession)
            cursor.execute(createMeasurements)
            cursor.execute(createSessionChannel)                               # Executes the creation queries





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


def dropDatabase(databaseValues):
    """
    Deletes a specified database 
    :param databaseValues: a python dictionary containing MySQL connection values for the database to be deleted
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
    :return: True if the database was deleted, False otherwise
    """
    try:
        conn = pymysql.connect(user=databaseValues['user'],  # Establishes connection to the database
                               host=databaseValues['host'],
                               password=databaseValues['password'],
                               port=int(databaseValues['port']))
        cursor = conn.cursor()

        sql = "drop database if exists %s" % (databaseValues['name'],)               # Deletes the database
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


def getChannelsList(databaseValues):
    """
    Retrieves a list of all the channels currently in the database
    :param databaseValues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
    :return: a tuple consisting of tuples containing the row values tretrieved 
    Example: ((1, 'Living room'), (2, 'Kitchen'))
    """
    try:
        conn = pymysql.connect(user=databaseValues['user'],  # Establishes connection to the database
                               host=databaseValues['host'],
                               password=databaseValues['password'],
                               database=databaseValues['name'],
                               port=int(databaseValues['port']))

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


def getSessionInformation(databaseValues, sessionId):
    """
    Retrieves inofrmation about a specified session from the database
    :param databaseValues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
    :param sessionId: an int representing the id of the session 
    :return: a tuple containing all available information about a session
    Example: {'name': 'session one', 'start': '2017-07-03 15:23:12', 'startfractions': 142, 'end': '2017-12-12 16:23:45', 'endfractions': 23423}
    """
    try:
        conn = pymysql.connect(user=databaseValues['user'],  # Establishes connection to the database
                               host=databaseValues['host'],
                               password=databaseValues['password'],
                               database=databaseValues['name'],
                               port=int(databaseValues['port']))

        cursor = conn.cursor()
        sql = "select * from sessions " \
              "where id_sessions = %d" % (sessionId,)
        cursor.execute(sql)                                                    # Retrieves information from 'sessions'

        queryResult = cursor.fetchall()
        result = {'id': queryResult[0][0], 'name': queryResult[0][1], 'start': queryResult[0][2],
                  'startfractions': queryResult[0][3], 'end': queryResult[0][4], 'endfractions': queryResult[0][5]}

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


def remoteGetPiList(databaseValues):
    """
    Retrieves a list of all the pis currently in the remote database
    :param databaseValues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
    :return: a tuple consisting of tuples containing Pi id and name or None if something went wrong
    Example: ((1, 'Living room'), (2, 'Kitchen'))
    """
    try:
        conn = pymysql.connect(user=databaseValues['user'],  # Establishes connection to the database
                               host=databaseValues['host'],
                               password=databaseValues['password'],
                               database=databaseValues['name'],
                               port=int(databaseValues['port']))

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


def getSessionList(databaseValues):
    """
    Retrieves a list of all the pis currently in the remote database
    :param databaseValues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
    :return: a tuple consisting of tuples containing Pi id and name or None if something went wrong
    Example: ((1, 'Living room'), (2, 'Kitchen'))
    """
    try:
        conn = pymysql.connect(user=databaseValues['user'],  # Establishes connection to the database
                               host=databaseValues['host'],
                               password=databaseValues['password'],
                               database=databaseValues['name'],
                               port=int(databaseValues['port']))

        cursor = conn.cursor()
        sql = "select id_sessions, name_sessions from sessions"                 # Retrieves all sessions from 'sessions'
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


def getSessionChannelList(databaseValues, sessionId):
    """    
    Retrieves a list of all channels in a session
    :param databaseValues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
    :param sessionId: an int representing the id of the session
    :return: a tuple containing channel id and channel name of all the channels connected to the session
    Example: ((1, 'channel1'), (2, 'channel2'))
    """
    try:
        conn = pymysql.connect(user=databaseValues['user'],  # Establishes connection to the database
                               host=databaseValues['host'],
                               password=databaseValues['password'],
                               database=databaseValues['name'],
                               port=int(databaseValues['port']))
        cursor = conn.cursor()

        sql = "select fk_channels_session_channels, " \
            "channelname_session_channels, unit_session_channels, tolerance_session_channels " \
            "from session_channels " \
            "where fk_sessions_session_channels = '%d'" % (sessionId,)        # Retrieves the channels of the sessionid
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


def getMeasurements(databaseValues, sessionId, channelId, startTime, endTime):
    """
    Retrieves measurements from the database using the arguments as search parameters
    :param databaseValues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
    :param sessionId: an int representing the session id 
    :param channelId: an int representing the channel id 
    :param startTime: a string representing the start date and time of the search 
    :param endTime: a string representing the end date and time of the search
    :return: the result of the database read
    Example: 
    """
    try:
        conn = pymysql.connect(user=databaseValues['user'],  # Establishes connection to the database
                               host=databaseValues['host'],
                               password=databaseValues['password'],
                               database=databaseValues['name'],
                               port=int(databaseValues['port']))
        cursor = conn.cursor()

        if startTime == None and endTime == None:
            if channelId == None:
                readsql = "SELECT * FROM measurements " \
                          "WHERE fk_sessions_measurements = %d" \
                          % (sessionId,)  # Searches the database
            else:
                readsql = "SELECT * FROM measurements " \
                          "WHERE fk_sessions_measurements = %d " \
                          "AND fk_channels_measurements = %d" \
                          % (sessionId,
                             channelId)
        else:
            if channelId == None:
                readsql = "SELECT * FROM measurements " \
                          "WHERE fk_sessions_measurements = %d AND " \
                          "timestamp_measurements >= '%s' AND " \
                          "timestamp_measurements <= '%s'" \
                          % (sessionId, startTime, endTime)  # Searches the database
            else:
                readsql = "SELECT * FROM measurements " \
                          "WHERE fk_sessions_measurements = %d AND " \
                          "timestamp_measurements >= '%s' AND " \
                          "timestamp_measurements <= '%s' AND " \
                          "fk_channels_measurements = %d" \
                          % (sessionId,
                             startTime,
                             endTime,
                             channelId)



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


def addToDatabase(databaseValues, listOfItems, sessionId):
    """
    Adds measurements to the database from a list of values
    :param databaseValues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
    :param listOfItems: a dictionary containing channel id's as keys and measurements as values
    Example: {1: 25.6, 2: 22.3}
    :param sessionId: an int representing the id of the session that collected the measurements
    :return: True if something was added to the database, false otherwise
    """
    try:
        conn = pymysql.connect(user=databaseValues['user'],  # Establishes connection to the database
                               host=databaseValues['host'],
                               password=databaseValues['password'],
                               database=databaseValues['name'],
                               port=int(databaseValues['port']))
        curs = conn.cursor()

        rawTimestamp = datetime.datetime.now()                                      # Gets the time of the addition
        timestamp = rawTimestamp.strftime('%Y-%m-%d %H:%M:%S')
        timestampFractions = rawTimestamp.microsecond                               # Gets the date of the addition

        print('Addition timestamp')
        print(timestamp)
        tempList = []
        for index in listOfItems:
            channelId = index
            measurementValue = listOfItems[index]
            tempList.append((sessionId,
                             channelId,
                             timestamp,
                             timestampFractions,
                             measurementValue))                                # Creates a list of values to be added

        addValues = str(tempList)
        addValues = addValues[1:-1]                                            # Creates a string formatted for MySQL

        sql1 = "Insert INTO " \
            "measurements(fk_sessions_measurements, " \
            "fk_channels_measurements, " \
            "timestamp_measurements, timestampfractions_measurements, " \
            "data_measurements) " \
            "VALUES" + addValues                                                # Adds the values to the database
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

def remoteAddToDatabase(databaseValues, listOfItems):
    """
    Adds measurements to the database from a list of values
    :param databaseValues: a python dictionary containing MySQL connection values
    Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
    :param listOfItems: a dictionary containing channel id's as keys and measurements as values
    Example: {1: 25.6, 2: 22.3}
    :param sessionid: an int representing the id of the session that collected the measurements
    :return: True if something was added to the database, false otherwise
    """
    try:
        conn = pymysql.connect(user=databaseValues['user'],  # Establishes connection to the database
                               host=databaseValues['host'],
                               password=databaseValues['password'],
                               database=databaseValues['name'],
                               port=int(databaseValues['port']))
        curs = conn.cursor()

        addValues = str(listOfItems)
        addValues = addValues[1:-1]                                            # Creates a string formatted for MySQL

        sql = "INSERT INTO " \
            "measurements(fk_sessions_measurements, " \
            "fk_channels_measurements, " \
            "timestamp_measurements, timestampfractions_measurements, " \
            "data_measurements) " \
            "VALUES" + addValues                                               # Adds the values to the database
        curs.execute(sql)

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

def convertToRemoteInsert(values, newsession, piid):
    for row in values:
        row['fk_sessions_measurements'] = newsession
        row['fk_channels_measurements'] = row['fk_channels_measurements']+60*(piid-1)
    return values

if __name__ == '__main__':
    db = configInterface.readConfig('config.cfg', 'default')
    createLocalDatabase(db)
