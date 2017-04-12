

import configparser



def read_config(file, section):
    '''
    This function reads the options for a specified section in a specified configuration file
    :param file: the file to read from
    :param section: the section to read from 
    :return: a dictionary containing the configuration options with corresponding value
    '''
    try:
        reader = configparser.ConfigParser()                                                    #Reads from the configuration file
        reader.read(file)
        values = {}
        if reader.has_section(section):
            list = reader.items(section)
            configs = {}
            for item in list:
                configs[item[0]] = item[1]
            return configs
    except:
        print('wrong')

def set_config(file, section, optionvaluepairs):
    '''
    This function updates a section in a configuration file
    :param file: the configuration file
    :param section: the section to be updated. If the section does not exist, a new section will be created
    :param optionvaluepairs: a dictionary with options as keys and optionsvalues as values
    Example: {'host': '127.0.0.1', 'user': 'root', 'password': '1234', 'name': Measurements}
    :return: True if the file was changed
    '''
    try:
        config = configparser.ConfigParser()
        config.read(file)
        if not config.has_section(section):
            config.add_section(section)
        for index in optionvaluepairs:
            config.set(section, index, optionvaluepairs[index])
        with open(file, 'w') as configfile:
            config.write(configfile)
        return True
    except RuntimeError as R:
        print(R)
        return False


