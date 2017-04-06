"""
This module offers an interface to a local sqlite3 database
"""


import sqlite3
import time



def check_if_index_exist(index):
    """
    This function checks if a channel is already added to the database
    :param index: the id of the channel to be looked for
    :return: True, if the channel was found, False otherwise
    """
    try:                                                            #trying to establish connection to the database
        conn = sqlite3.connect('/home/felix/LocalDatabase.db')
        cur = conn.cursor()
    except:
        print("second connection didnt work")

    try:                                                            #check the database for the channel id
        replacement = (index,)
        sqlstatement = "select id from channels where id = ?"
        cur.execute(sqlstatement, replacement)
        value = cur.fetchone()
        conn.close()
    except:
        print("The select query didnt work")
    if value == None:
       return False
    else:
       return True

def add_to_database(list_of_items):
    """
    This function adds attributes from a list of items to the database
    :param list_of_items: a python dictionary were the key is a unique integer and the value is a list of the structure [channelname, measurementvalue]
    :return: True if the values were added to the database, false otherwise
    """
    date = time.strftime("%Y-%m-%d")                                #TODO: check if the date and time should be colected here or in main
    timeofvalue = time.strftime("%H:%M:%S")

    try:                                                            #Trying to establish connection to the database
        conn = sqlite3.connect('/home/felix/LocalDatabase.db')
        print("connected to database")
    except:
        print("Something went wrong1")

    try:                                                            #Gather the channel id, channel name and measurementvalue from the list_of_items
        for index in list_of_items:

            id = index
            list = list_of_items[index]
            name = list[0]
            measurementvalue = list[1]

            found = check_if_index_exist(id)                        #Check if the channel index and name needs to be added to the database


            if found:
                conn.execute("INSERT INTO measurements VALUES(?,?,?,?)", (id, date, timeofvalue, measurementvalue))     #Add the measurement value and timestamp to the database
            else:
                conn.execute("INSERT INTO channels VALUES(?, ?)", (id, name))
                conn.execute("INSERT INTO measurements VALUES(?,?,?,?)", (id, date, timeofvalue, measurementvalue))     #Add the channel id and channel name aswell as the measurement value and timestamp

        conn.commit()                                               #Commit the changes and close the connection to the database
        conn.close()
        return True
    except:
        print("wrong with adding")
        conn.rollback()                                             #If an exception is thrown the database changes is not commited
        return False


