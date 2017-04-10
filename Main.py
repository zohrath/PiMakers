import configparser
import pymysql


def read_db_config():
    try:
        reader = configparser.ConfigParser()                                        #Reads from the configuration file
        reader.read('config.cfg')

        hostvalue = reader.get('default', 'host')
        uservalue = reader.get('default', 'user')                                            #Gets specific configurations from the configuration file
        passwordvalue = reader.get('default', 'password')
        namevalue = reader.get('default', 'name')

        print(hostvalue)
        values = {'host': hostvalue, 'user':uservalue, 'password': passwordvalue, 'name': namevalue}

        return values
    except Warning as w:
        print(w)
        return None


