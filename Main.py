'''
This is the main program of the system
'''

import configparser



def read_db_config():
    '''
    This function reads data from configuration file and returns a dictionary with useful mysql connection configurations
    :return: If nothing went wrong, returns a dictionary with keys: 'host', 'name', 'user' and 'password'
    '''
    try:
        reader = configparser.ConfigParser()                                                    #Reads from the configuration file
        reader.read('config.cfg')

        hostvalue = reader.get('default', 'host')
        uservalue = reader.get('default', 'user')                                               #Gets specific configurations from the configuration file
        passwordvalue = reader.get('default', 'password')
        namevalue = reader.get('default', 'name')

        values = {'host': hostvalue, 'user':uservalue, 'password': passwordvalue, 'name': namevalue}    #Insert the values into the dictionary
        return values
    except Warning as w:
        print(W)
        return None


