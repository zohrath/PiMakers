import sys
import threading
import pymysql
import configInterface
import configparser
import Database
import datetime
import UI
import random
import ast
import Communication
import copy

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from GraphWindowUI import DataDisplay


class Main(QtWidgets.QMainWindow):
    def __init__(self):
        """
        Creates the main window of the application
        """
        self.sessionRunning = False


        #Creates main GUI
        QtWidgets.QMainWindow.__init__(self)
        self.widgetList = UI.UIpages()                                      # Creates a stacked widget containing the UI pages of the application
        self.widgetList.setCurrentIndex(self.widgetList.mainMenuIndex)
        self.setCentralWidget(self.widgetList)                              # Displays the mainmenu

        #Sets up threading
        self.shouldEnd = threading.Event()
        self.shouldEndRemote = threading.Event()                            # Initialize events for communication with other threads
        self.programQuit = threading.Event()

        self.setConnections()                                              # Connects the main window to respond to user interactions

        self.checkForAbortedSession()                                       # Checks if the last program session was aborted before a measuring session was ended


    def setConnections(self):
        """
        Connects the signals of the UI pages to various slots. 
        This controls how the application responds to user interaction
        :return: 
        """
        w = self.widgetList.widget
        list = self.widgetList
        w(list.mainMenuIndex).quitSignal.connect(self.quit)
        w(list.mainMenuIndex).sessionSignal.connect(self.showChannelSettings)
        w(list.mainMenuIndex).helpSignal.connect(self.showHelpPage)
        w(list.mainMenuIndex).currentSignal.connect(self.endCurrentSession)
        w(list.mainMenuIndex).visualizeSignal.connect(self.showVisualizeSettings)            # Connects the signals emitted by the main menu buttons
        w(list.mainMenuIndex).warningPressed.connect(self.WarningRemoteDatabaseDown)

        w(list.currentSessionIndex).cancelPressed.connect(self.showMainMenu)                       # Connects the signal emitted by the 'Avsluta mätning' in the main menu

        w(list.databaseSettingsIndex).cancelPressed.connect(self.showChannelSettings)
        w(list.databaseSettingsIndex).okPressed.connect(self.startSession)                           # Connects the signals emitted by the databasesettings page

        w(list.helpPageIndex).cancelPressed.connect(self.showMainMenu)                       # Connects the signals emitted by the helppage

        w(list.channelSettingsIndex).backPressed.connect(self.showMainMenu)
        w(list.channelSettingsIndex).okPressed.connect(self.showDatabaseSettings)                   # Connects the signals emitted by channelsettings page

        w(list.visualizeDatabaseSettingsIndex).cancelPressed.connect(self.showMainMenu)
        w(list.visualizeDatabaseSettingsIndex).okPressed.connect(self.showSessionList)                        # Connects the signals emitted by the databasesettings page for visualizing a measuring session
        w(list.visualizeSessionSettingsIndex).backPressed.connect(self.showVisualizeSettings)
        w(list.visualizeSessionSettingsIndex).sessionChosen.connect(self.getSessionChannels)
        w(list.visualizeSessionSettingsIndex).okPressed.connect(self.visualizeData)                              # Connects the signals emitted by the visualize session page

    def WarningRemoteDatabaseDown(self):
        message = "Varning: Anslutningen till den databas som används i mätningen är nere. \n" \
                  "Mätningen kommer att fortsätta lokalt samtidigt som anslutningen försöker återuprättas. \n" \
                  "Varningssymbolen i startmenyn kommer att försvinna när anslutningen är återupprättad."
        self.messageToUser(messageText=message, yesbuttontext=None, closeButtonText="Stäng")


    def getSessionChannels(self, sessionId):
        """
        Uses a session id to fetch all channels connected to the id from a database
        :param sessionId: An int representing the session id to be used in the database search
        :return: 
        """

        useRemoteDatabase = \
            self.widgetList.\
                widget(self.widgetList.visualizeDatabaseSettingsIndex)\
                .useRemote()                                                # Checks if the local or a remote database should be searched
        if useRemoteDatabase:                                                       # If remote, get remote channels
            remoteDatabase = \
                configInterface.readConfig('config.cfg', 'remotevisual')
            channelList = \
                Database.getSessionChannelList(remoteDatabase, sessionId)
        else:                                                               # Else, get local channels
            localDatabase = \
                configInterface.readConfig('config.cfg', 'default')
            channelList = \
                Database.getSessionChannelList(localDatabase, sessionId)

        self.widgetList.widget(self.widgetList.visualizeSessionSettingsIndex)\
            .updateChannelList(channelList)                                 # Use the channels to update the channel list on the session settings for the visualize page



    def visualizeData(self, sessionId, channellist):
        """
        Uses a session id and a list of channels to display related data in a new window
        :param sessionId: An int representing the session id to fetch data from
        :param channellist: a dictionary where the keys are channel ids and the values 
        are lists where the first item should be the display name of the channel
        Example: {1: ['Temperature Room 1', 20.0, 'Celsius'], 2: ['Weight Room 2', 2.34, 'Kilograms']}
        :return: 
        """
        useRemote = \
            self.widgetList.\
                widget(self.widgetList.visualizeDatabaseSettingsIndex)\
                .useRemote()                                                # Checks the settings from the visualize page to see if local or remote database should be used in the visualization

        if useRemote:                                                       # If remote get remote database settings
            database = configInterface.readConfig('config.cfg', 'remotevisual')
        else:                                                               # Else, get local database settings
            database = configInterface.readConfig('config.cfg', 'default')

        self.dataDisplay = DataDisplay(databaseValues=database,
                                       sessionId=sessionId,
                                       channelList=channellist,
                                       ongoing=False,
                                       timeInterval=1)                     # Displays data from the database in a new window, change hard coded timeintervall
        self.dataDisplay.show()

    def checkForAbortedSession(self):
        """
        Continues a started session if the program was terminated without ending the session 
        :return: 
        """
        with open('config.cfg', 'r') as configfile:                        # Check if the configfile has a latestsession section
            parser = configparser.ConfigParser()
            parser.read_file(configfile)
            abortedSession = parser.has_section('latestsession')

        if abortedSession:                                                      # If the configfile has the section
            #Reads config file for the aborted session options
            hasRemote = parser.has_option('latestsession', 'remotedatabase')    # Check for remote option
            channels = configInterface.readConfig('config.cfg', 'channels')     # Fetch channels
            sessionSettings = configInterface.readConfig('config.cfg', 'latestsession')
            start = sessionSettings['start']
            end = sessionSettings['end']
            self.localDatabase = ast.literal_eval(sessionSettings['localdatabase'])
            self.localSessionId = int(sessionSettings['localsessionid'])
            timeInterval = float(sessionSettings['timeintervall'])

            channelDictionary = {}
            for index in channels:
                channelDictionary[index] = ast.literal_eval(channels[index])      # Formats the channel

            if not end:                                                     # If the session was not ended
                addThread = Addthread(localDatabase=self.localDatabase,
                                      sessionId=self.localSessionId,
                                      channelList=channelDictionary,
                                      shouldEnd=self.shouldEnd,
                                      timeInterval=timeInterval)
                addThread.start()                                           # Start a thread for adding values to local database

                if hasRemote:                                               # If a remote database is used in the session
                    self.useRemote = True
                    self.remoteDatabase = ast.literal_eval(sessionSettings['remotedatabase'])
                    self.remoteSessionId = int(sessionSettings['remotesessionid'])
                    remoteAddThread = AddRemoteThread(remoteDatabase=self.remoteDatabase,
                                                      remoteSessionId=self.remoteSessionId,
                                                      localDatabase=self.localDatabase,
                                                      sessionId=self.localSessionId,
                                                      shouldEnd=self.shouldEndRemote,
                                                      programQuit=self.programQuit,
                                                      timeInterval=timeInterval)
                    remoteAddThread.noConnection.connect(self.warnUser)
                    remoteAddThread.connectionEstablished.connect(self.stopWarningUser)
                    remoteAddThread.start()                                 # Start a thread for adding values to the remote database
                else:
                    self.useRemote = False

                self.sessionRunning = True                                  # Used by other functions to check if a session is running
                self.widgetList.mainMenu.sessionStarted()  # Change appearance of the mainmeny
                self.dataDisplay = DataDisplay(databaseValues=self.localDatabase,
                                               sessionId=self.localSessionId,
                                               channelList=channelDictionary,
                                               ongoing=True,
                                               timeInterval=timeInterval)
                self.dataDisplay.show()                                     # Open new window displaying data


    def warnUser(self):
        """
        Displays a warning on the main menu page
        :return: 
        """
        self.widgetList.mainMenu.displayWarning(True)

    def stopWarningUser(self):
        """
        Removes a warning from the main menu page
        :return: 
        """
        self.widgetList.mainMenu.displayWarning(False)

    def showSessionList(self):
        """
        Display the sessionlist page
        :return: 
        """
        sessionList = self.getSessions()
        self.widgetList.widget(self.widgetList.visualizeSessionSettingsIndex).updateSessionList(sessionList)
        self.widgetList.setCurrentIndex(self.widgetList.visualizeSessionSettingsIndex)


    def showVisualizeSettings(self):
        """
        Display the database settings page for the visualize option
        :return: 
        """
        self.widgetList.setCurrentIndex(self.widgetList.visualizeDatabaseSettingsIndex)

    def showDatabaseSettings(self):
        """
        Display the database settings page for the start session option 
        :return: 
        """
        self.widgetList.setCurrentIndex(self.widgetList.databaseSettingsIndex)

    def showHelpPage(self):
        """
        Display the help page
        :return: 
        """
        self.widgetList.setCurrentIndex(self.widgetList.helpPageIndex)

    def showMainMenu(self):
        """
        Display the main menu
        :return: 
        """
        self.widgetList.setCurrentIndex(self.widgetList.mainMenuIndex)

    def showChannelSettings(self):
        """
        Display the channel settings page
        :return: 
        """
        self.widgetList.setCurrentIndex(self.widgetList.channelSettingsIndex)

    def quit(self):
        """
        Checkpoint function before terminating the program 
        :return: 
        """
        if self.sessionRunning:                                             # If a session is running
            self.messageToUser(messageText="Mätning pågår, "
                                           "avsluta mätning och "
                                           "stäng programmet?"
                               , yesbuttontext="Ja",
                               closeButtonText="Nej")                       # Prompt user
        else:
            self.closeApplication()                                         # Else, terminate

    def closeApplication(self):
        """
        Terminates the program
        :return: 
        """
        if self.sessionRunning:                                             # If a session is running
            self.endCurrentSession()                                        # End the session
        self.close()                                                        # Close

    def endCurrentSession(self):
        """
        Ends a running session
        :return: 
        """
        self.programQuit.set()                                              # Signal remote add thread to stop
        self.shouldEnd.set()                                                # Signal local add thread

        endTimestamp = datetime.datetime.now()
        endTimestamp = endTimestamp.strftime("%Y-%m-%d %H:%M:%S")           # Get timestamp
        configInterface.setConfig('config.cfg',
                                   'latestsession',
                                  {'end': endTimestamp})                   # Write the timestamp to configfile

        self.widgetList.mainMenu.sessionEnded()  # Change main menu appearance
        Database.endCurrentSession(self.localDatabase, self.localSessionId)     # Give the local session an end time

        if self.useRemote:                                                # If using remote
            self.shouldEndRemote.set()
            Database.endCurrentSession(self.remoteDatabase,
                                       self.remoteSessionId)              # Give the remote session an end time

        self.dataDisplay.close()                                            # Close the datadisplay window
        self.sessionRunning = False
        self.showMainMenu()                                                 # Display main menu

    def getSessions(self):
        """
        Retrieves a list of sessions from a database specified 
        on the database settings page for the visualize option
        :return: A tuple of tuples containing information about sessions
        Example: ((1, 'session1'), (2, 'session2'))
        """
        useRemote = \
            self.widgetList.\
                widget(self.widgetList.visualizeDatabaseSettingsIndex).\
                useRemote()                                                 # Fetch database type
        if useRemote:                                                       # If remote
            remoteDatabase = configInterface.readConfig('config.cfg',
                                                   'remotevisual')
            sessionList = Database.getSessionList(remoteDatabase)               # Get session from remote database
        else:
            localDatabase = configInterface.readConfig('config.cfg', 'default')
            sessionList = Database.getSessionList(localDatabase)                # Else, get sessions from local database
        return sessionList



    def startSession(self):
        """
        Starts a new session
        :return: 
        """

        try:
            w = self.widgetList.widget
            settings = self.widgetList.channelSettingsIndex


            self.useRemote = w(self.widgetList.databaseSettingsIndex).useRemote()       # Checks if a remote database should be used
            self.localDatabase = configInterface.readConfig('config.cfg', 'default')    # Gets configuration for the local database

            sessionName = w(settings).sessionname                                       # Gets the sessionname
            channelList = w(settings).channellist                                       # Gets a list of channels to use in the session
            timeInterval = w(settings).sessionintervall                                 # Gets the time intervall for the session

            if self.useRemote:                                                          # If a remote should be used
                self.remoteDatabase = \
                    configInterface.readConfig('config.cfg', 'remote')                  # Get remote database configurations

                if configInterface.hasSection('config.cfg', 'piid'):
                    identifiers = configInterface.readConfig('config.cfg', 'piid')
                    self.uuid = identifiers['uuid']

                    if not Database.remotePiExists(self.remoteDatabase, identifiers['uuid']):
                        newIdentifiers = Database.remoteAddNewPi(self.remoteDatabase)
                        print(newIdentifiers)
                        configInterface.setConfig('config.cfg', 'piid', {'piid': str(self.piid)})
                    else:
                        self.piid = Database.remoteGetPiid(self.remoteDatabase, self.uuid)
                        configInterface.setConfig('config.cfg', 'piid', {'piid': str(self.piid)})
                else:

                    newIdentifiers = Database.remoteAddNewPi(self.remoteDatabase)
                    print(newIdentifiers)
                    self.uuid = newIdentifiers['uuid']
                    self.piid = int(newIdentifiers['piid'])
                    configInterface.setConfig('config.cfg', 'piid', {'uuid': self.uuid, 'piid': str(self.piid)})

                localChannels = copy.deepcopy(channelList)
                remoteChannels = self.convertToRemoteChannels(channelList)
                self.remoteSessionId = \
                    Database.remoteStartNewSession(databaseValues=self.remoteDatabase,
                                                   name=sessionName,
                                                   channels=remoteChannels,
                                                   piid=self.uuid)                      # Make a new session entry to the remote database


            self.localSessionId = \
                Database.startNewSession(databaseValues=self.localDatabase,
                                         name=sessionName,
                                         channels=localChannels)                          # Make a new session entry to the local database


            currentTime = datetime.datetime.now()
            startSearchValue = currentTime.strftime('%Y-%m-%d %H:%M:%S')
            startFractions = str(currentTime.microsecond)                               # Get timestamp for session start
            writeItem = {'start': startSearchValue, 'startfractions': startFractions,
                         'localdatabase': str(self.localDatabase), 'localsessionid': str(self.localSessionId),
                         'timeintervall': str(timeInterval), 'end': ''}                 # Add session information to configfile

            if self.useRemote:                                                          # If a remote is used
                writeItem['remotedatabase'] = str(self.remoteDatabase)
                writeItem['remotesessionid'] = str(self.remoteSessionId)    # Add information about the remote session

            parser = configparser.ConfigParser()
            with open('config.cfg', 'r') as r:
                parser.read_file(r)
                parser.remove_section('latestsession')                      # Remove previous information from the configfile
            with open('config.cfg', 'w') as w:
                parser.write(w)
            configInterface.setConfig('config.cfg',
                                       'latestsession',
                                      writeItem)                           # Write the new information to the configfile

            addThread = Addthread(localDatabase=self.localDatabase,
                                  sessionId=self.localSessionId,
                                  shouldEnd=self.shouldEnd,
                                  channelList=localChannels,
                                  timeInterval=timeInterval)
            addThread.start()                                               # Create a thread for adding to the local database and start it

            if self.useRemote:                                            # If a remote database is used
                remoteAddThread = AddRemoteThread(remoteDatabase=self.remoteDatabase,
                                                  localDatabase=self.localDatabase,
                                                  remoteSessionId=self.remoteSessionId,
                                                  sessionId=self.localSessionId,
                                                  shouldEnd=self.shouldEndRemote,
                                                  programQuit=self.programQuit,
                                                  timeInterval=timeInterval)
                remoteAddThread.connectionEstablished.connect(self.stopWarningUser)
                remoteAddThread.noConnection.connect(self.warnUser)
                remoteAddThread.start()                                     # Create a thread for adding to the remote database and start it

            self.dataDisplay = DataDisplay(databaseValues=self.localDatabase,
                                           sessionId=self.localSessionId,
                                           channelList=localChannels,
                                           ongoing=True,
                                           timeInterval=timeInterval)     # Create a new window for displaying data
            self.dataDisplay.show()                                         # Show the window
            self.widgetList.mainMenu.sessionStarted()  # Change appearance of mainmenu
            self.showMainMenu()                                             # Display the mainmeny
            self.sessionRunning = True

        except pymysql.err.Error as E:
            if E.args[0] == 1045:                                           # If mysql connection denied
                message = "Anslutning nekad, se över port, användare och lösenord"
                self.messageToUser(messageText=message,
                                   closeButtonText="Stäng")
            if E.args[0] == 2003:                                           # If mysql connection cant be found
                message = "Kunde inte anluta till host: '%s'" % (self.remoteDatabase['host'])
                self.messageToUser(messageText=message,
                                   closeButtonText="Stäng")
            if E.args[0] == 1049:                                           # If the database wasnt found
                message = "Hittade ingen database med namnet '%s'" % (self.remoteDatabase['name'])
                self.messageToUser(messageText=message,
                                   closeButtonText="Stäng")
            if E.args[0] == 1062:                                           # If mysql integrity error
                message = "Minst två kanaler har samma namn. Kanalnamn måste vara unika"
                self.messageToUser(messageText=message,
                                   closeButtonText="Stäng")
        except ValueError as V:                                             # If wrong value in port field
            print(V)
            wrongPortType = "Fel typ för 'Port', ett heltal förväntas"
            self.messageToUser(messageText=wrongPortType,
                               closeButtonText="Stäng")

    def messageToUser(self, messageText, yesbuttontext=None, closeButtonText=None):
        """
        Creteas a window displaying a specified message to the user
        :param messageText: A string representing the message to display 
        
        :param closeButtonText: A string representing the text to be shown on the close button
        :return: 
        """
        message = QtWidgets.QMessageBox()
        message.setMinimumSize(1000, 800)
        message.setText(messageText)
        if not yesbuttontext == None:
            yesbutton = message.addButton(yesbuttontext, QtWidgets.QMessageBox.AcceptRole)
            yesbutton.clicked.connect(self.closeApplication)
        closebutton = message.addButton(closeButtonText, QtWidgets.QMessageBox.YesRole)
        closebutton.clicked.connect(message.close)
        message.exec_()

    def convertToRemoteChannels(self, channelList):
        """
        Converts a list of local channels to a corresponding list of remote channels 
        :param channelList: the list of channels
        :return: The same tuple given as an argument, but with new keys
        """
        print(channelList)
        newList = {}
        for index in channelList:
            newValues = channelList[index]
            newValues[0] = int(newValues[0]) + 60*(self.piid-1)
            newList[index] = newValues                     # Todo: Check if this can be done without hard coding
        print(newList)
        return newList

class Addthread(threading.Thread):
    def __init__(self, localDatabase, sessionId, channelList, shouldEnd, timeInterval):
        """
        Creates a new thread for adding values to the local database
        :param localDatabase: A tuple of database configurations for the local database
        Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
        :param sessionId: An int representing the id of the running session 
        :param channelList: A tuple of channels and channel values
        Example: {1: [101, 'Celsius', 0.9, 'Temperature'], 2: [102, 'Kilograms', 1.3, 'Weigth']}
        :param shouldEnd: A threading.Event object for stopping the thread
        :param timeInterval: An int representing the amount of second between each addition to the database
        """
        self.localDatabase = localDatabase
        self.sessionId = sessionId
        self.shouldend = shouldEnd
        self.channelList = channelList
        self.timeInterval = timeInterval
        threading.Thread.__init__(self)

    def run(self):
        """
        Does all work in the thread
        :return: 
        """
        while not self.shouldend.wait(self.timeInterval):                  # While the thread has not been told to stop
                                                                            # wait for timeintervall amount of seconds
            list = {}
            #addlist = self.getData(self.channelList)
            #print(addlist)
            for item in self.channelList:
                id = int(self.channelList[item][0])

                list[id] = random.randint(1, 100)                           # Generate random integers
            print(list)
            Database.addToDatabase(self.localDatabase, list, self.sessionId)    # Add values to the local database

        self.shouldend.clear()                                              # Before exiting thread, clear Event object

    def getData(self, channelList):


        returnlist = {}
        measurementlist = {}
        lookupList = {}
        for index in channelList:
            lookupList[channelList[index][0]] = index
            print(lookupList)
            if channelList[index][4] in measurementlist:
                measurementlist[channelList[index][4]] = measurementlist[channelList[index][4]] + [channelList[index][0], ]
            else:
                measurementlist[channelList[index][4]] = [channelList[index][0], ]
            print(measurementlist)
        valuelist = {}
        for index in measurementlist:
            stringargument = str(measurementlist[index])
            stringargument = stringargument[1:-1]

            functionToCall = getattr(Communication, index)
            result = functionToCall(stringargument)

            newlistentry = dict(zip(measurementlist[index], result))

            for index3 in lookupList:
                returnlist[lookupList[index3]] = newlistentry[index3]
        return returnlist



class AddRemoteThread(QtCore.QThread):
    noConnection = QtCore.pyqtSignal()
    connectionEstablished = QtCore.pyqtSignal()                             # Custom pyqt signals used to signal the main thread

    def __init__(self, localDatabase, remoteDatabase, remoteSessionId, sessionId, shouldEnd, programQuit, timeInterval, parent=None):
        """
        Creates a new thread for adding values to a remote database
        :param localDatabase: A tuple of database configurations for the local database to fetch values from 
        Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
        :param remoteDatabase: A tuple of database configurations for the remote database to add values to
        Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
        :param remoteSessionId: An int representing the remote session id associated with the values to be added
        :param sessionId: An int representing the local session id associated with the values to be fetched
        :param shouldEnd: A threading.Event object used to stop the thread
        :param programQuit: A threading.Event object used to make the thread add values immediately
        :param timeInterval: An int representing the amount of seconds between each addition
        :param parent: 
        """
        self.remoteDatabase = remoteDatabase
        self.remoteSessionId = remoteSessionId
        self.sessionId = sessionId
        self.shouldEnd = shouldEnd
        self.localDatabase = localDatabase
        self.programQuit = programQuit
        self.timeInterval = timeInterval
        self.latestAddTime = None
        self.latestAddFractions = None
        self.addedAllData = False
        self.databaseIsDown = False
        QtCore.QThread.__init__(self, parent)

    def run(self):
        """
        Fetches values from a local database and adds them to a remote database
        :return: 
        """
        pid = configInterface.readConfig('config.cfg', 'piid')
        piid = int(pid['piid'])                                               # Gets the id of the Raspberry pi running the program
        while not self.addedAllData:
            try:
                if self.programQuit.wait(0):                                # If signaled that the program wants to terminate
                    self.timeInterval = 0                                  # Do additions immediately
                if not self.shouldEnd.wait(self.timeInterval*10):          # Wait for timeintervall seconds
                    sessionSettings = configInterface.readConfig('config.cfg', 'latestsession')
                    start = sessionSettings['start']
                    end = sessionSettings['end']                            # Get previous previous search parameters
                    if not end == '':                                       # If the session has been ended
                        checkEnd = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                        checkStart = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                        if checkEnd > checkStart:                           # Check if the last search parameter is greater than the end value fo the session
                            self.addedAllData = True


                    end = datetime.datetime.now()                           # Get new end value to use in local database search
                    valueList = Database.getMeasurements(databaseValues=self.localDatabase,
                                                         sessionId=self.sessionId,
                                                         channelId=None,
                                                         startTime=start,
                                                         endTime=end)      # Get measurements from the local database
                    templatestAddTime = None
                    templatestAddFractions = None
                    new = []
                    for row in valueList:                                   # For each row in the result
                        timestamp = row[2].strftime('%Y-%m-%d %H:%M:%S')
                        timestampFractions = row[3]
                        templatestAddTime = row[2].strftime('%Y-%m-%d %H:%M:%S')
                        templatestAddFractions = row[3]
                        data = row[4]                                       # Add measurementvalues to a new list
                        remoteChannel = row[1]+60*(piid-1)                  # Convert local id to remoteid
                        if not(timestamp == self.latestAddTime and timestampFractions == self.latestAddFractions):
                            new.append((self.remoteSessionId,
                                        remoteChannel,
                                        timestamp,
                                        timestampFractions,
                                        data))                              # If the timestamp in this result matches the last timestamp in the previous result
                                                                            # dont add it to the new list
                    if not new == []:
                        Database.remoteAddToDatabase(self.remoteDatabase, new) # If the list is not empty, add values to the remote database

                    self.latestAddTime = templatestAddTime
                    self.latestAddFractions = templatestAddFractions        # Set latest add timestamp

                    if self.databaseIsDown:                                 # If the database was down, the database is now up since the addition was succesful
                        self.connectionEstablished.emit()                   # Signals main thread that the database is connected
                        self.databaseIsDown = False

                    newStart = end.strftime('%Y-%m-%d %H:%M:%S')            # Write the end time used in the search to the configfile
                                                                            # To be used as start time in the next search
                    configInterface.setConfig('config.cfg', 'latestsession', {'start': newStart})
                else:
                    self.shouldEnd.clear()
            except pymysql.err.Error as E:                                  # If the database raises an exception
                if not self.databaseIsDown:
                    self.noConnection.emit()                                # Signal the main thread that the database is down
                    self.databaseIsDown = True
                print(E)
        self.programQuit.clear()






if __name__ == '__main__':
    remote = configInterface.readConfig('config.cfg', 'createremote')

    local = configInterface.readConfig('config.cfg', 'default')
    Database.createRemoteDatabase(remote)
    parser = configparser.ConfigParser()
    with open('config.cfg', 'r+') as file:
        parser.read_file(file)
        hasid = parser.has_section('piid')
    #if not hasid:
        #identifiers = Database.remoteAddNewPi(remote)
     #   configInterface.setConfig('config.cfg', 'piid', identifiers)
    Database.createLocalDatabase(local)
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.showFullScreen()
    sys.exit(app.exec_())