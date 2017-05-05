

import configparser




def read_config(file, section):
    """
    Reads the options for a specified section in a specified configuration file
    :param file: a string containing the name of the file to be read
    :param section: a string containing the name of the section to be read 
    :return: a dictionary with configuration options as keys and optionvalues as values
    Example: {'host': '127.0.0.1', 'user': 'root', 'password': '1234', 'name': Measurements}
    """
    try:
        reader = configparser.ConfigParser()                                    # Reads from the configuration file
        reader.read(file)

        if reader.has_section(section):                                         # Checks if the section exists
            valuelist = reader.items(section)
            configs = {}
            for item in valuelist:                                              # Creates a dictionary of the values
                configs[item[0]] = item[1]
            return configs
    except TypeError as T:
        print('read_config Typerror:')
        print(T)
        raise T

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


