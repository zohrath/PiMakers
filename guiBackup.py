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
#import pyqtgraph as pg
#import numpy

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FC
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NT
from matplotlib.figure import Figure
import matplotlib.dates as matdates



class Main(QtWidgets.QMainWindow):
    def __init__(self):
        """
        Creates the main window of the application
        """
        self.sessionrunning = False
        piid = configInterface.read_config('config.cfg', 'piid')
        self.piid = int(piid['id'])

        QtWidgets.QMainWindow.__init__(self)
        self.widgetlist = UI.UIpages()                                      # Creates a stacked widget containing the UI pages of the application
        self.widgetlist.setCurrentIndex(self.widgetlist.mainMenuIndex)
        self.setCentralWidget(self.widgetlist)                              # Displays the mainmenu

        self.shouldend = threading.Event()
        self.shouldendremote = threading.Event()                            # Initialize events for communication with other threads
        self.programquit = threading.Event()

        self.set_connections()                                              # Connects the main window to respond to user interactions

        self.checkforabortedsession()                                       # Checks if the last program session was aborted before a measuring session was ended

    def set_connections(self):
        """
        Connects the signals of the UI pages to various slots. 
        This controls how the application responds to user interaction
        :return: 
        """
        self.widgetlist.widget(self.widgetlist.mainMenuIndex)\
            .quitSignal.connect(self.quit)
        self.widgetlist.widget(self.widgetlist.mainMenuIndex)\
            .sessionSignal.connect(self.showchannelsettings)
        self.widgetlist.widget(self.widgetlist.mainMenuIndex)\
            .helpSignal.connect(self.showhelppage)
        self.widgetlist.widget(self.widgetlist.mainMenuIndex)\
            .currentSignal.connect(self.endcurrentsession)
        self.widgetlist.widget(self.widgetlist.mainMenuIndex)\
            .visualizeSignal.connect(self.showvisualizesettings)            # Connects the signals emitted by the main menu buttons
        self.widgetlist.widget(self.widgetlist.mainMenuIndex)\
            .warningPressed.connect(self.explainWarning)


        self.widgetlist.widget(self.widgetlist.currentSessionIndex)\
            .cancelPressed.connect(self.showmainmenu)                       # Connects the signal emitted by the 'Avsluta mätning' in the main menu

        self.widgetlist.widget(self.widgetlist.databaseSettingsIndex)\
            .cancelPressed.connect(self.showchannelsettings)
        self.widgetlist.widget(self.widgetlist.databaseSettingsIndex)\
            .okPressed.connect(self.startsession)                           # Connects the signals emitted by the databasesettings page

        self.widgetlist.widget(self.widgetlist.helpPageIndex)\
            .cancelPressed.connect(self.showmainmenu)                       # Connects the signals emitted by the helppage

        self.widgetlist.widget(self.widgetlist.channelSettingsIndex)\
            .backPressed.connect(self.showmainmenu)
        self.widgetlist.widget(self.widgetlist.channelSettingsIndex)\
            .okPressed.connect(self.showdatabasesettings)                   # Connects the signals emitted by channelsettings page

        self.widgetlist.widget(self.widgetlist.visualizeDatabaseSettingsIndex)\
            .cancelPressed.connect(self.showmainmenu)
        self.widgetlist.widget(self.widgetlist.visualizeDatabaseSettingsIndex)\
            .okPressed.connect(self.showsessionlist)                        # Connects the signals emitted by the databasesettings page for visualizing a measuring session

        self.widgetlist.widget(self.widgetlist.visualizeSessionSettingsIndex)\
            .backPressed.connect(self.showvisualizesettings)
        self.widgetlist.widget(self.widgetlist.visualizeSessionSettingsIndex)\
            .sessionChosen.connect(self.fetchChannels)
        self.widgetlist.widget(self.widgetlist.visualizeSessionSettingsIndex)\
            .okPressed.connect(self.visualize)                              # Connects the signals emitted by the visualize session page

    def explainWarning(self):
        message = "Varning: Anslutningen till den databas som används i mätningen är nere. \n" \
                  "Mätningen kommer att fortsätta lokalt samtidigt som anslutningen försöker återuprättas. \n" \
                  "Varningssymbolen i startmenyn kommer att försvinna när anslutningen är återupprättad."
        self.messageToUser(messagetext=message, yesbuttontext=None, closebuttontext="Stäng")


    def fetchChannels(self, sessionid):
        """
        Uses a session id to fetch all channels connected to the id from a database
        :param sessionid: An int representing the session id to be used in the database search
        :return: 
        """
        useremote = \
            self.widgetlist.\
                widget(self.widgetlist.visualizeDatabaseSettingsIndex)\
                .useRemote()                                                # Checks if the local or a remote database should be searched
        if useremote:                                                       # If remote, get remote channels
            remotedb = \
                configInterface.read_config('config.cfg', 'remotevisual')
            channellist = \
                Database.getSessionChannelList(remotedb, sessionid)
        else:                                                               # Else, get local channels
            localdb = \
                configInterface.read_config('config.cfg', 'default')
            channellist = \
                Database.getSessionChannelList(localdb, sessionid)

        self.widgetlist.widget(self.widgetlist.visualizeSessionSettingsIndex)\
            .updateChannelList(channellist)                                 # Use the channels to update the channel list on the session settings for the visualize page



    def visualize(self, sessionid, channellist):
        """
        Uses a session id and a list of channels to display related data in a new window
        :param sessionid: An int representing the session id to fetch data from
        :param channellist: a dictionary where the keys are channel ids and the values 
        are lists where the first item should be the display name of the channel
        Example: {1: ['Temperature Room 1', 20.0, 'Celsius'], 2: ['Weight Room 2', 2.34, 'Kilograms']}
        :return: 
        """
        useremote = \
            self.widgetlist.\
                widget(self.widgetlist.visualizeDatabaseSettingsIndex)\
                .useRemote()                                                # Checks the settings from the visualize page to see if local or remote database should be used in the visualization

        if useremote:                                                       # If remote get remote database settings
            database = configInterface.read_config('config.cfg', 'remotevisual')
        else:                                                               # Else, get local database settings
            database = configInterface.read_config('config.cfg', 'default')

        self.datadisplay = Datadisplay(dbvalues=database,
                                       sessionid=sessionid,
                                       channellist=channellist,
                                       ongoing=False,
                                       timeintervall=1)                     # Displays data from the database in a new window, change hard coded timeintervall
        self.datadisplay.show()
        #print("showed datadisplay")




    def checkforabortedsession(self):
        """
        Continues a started session if the program was terminated without ending the session 
        :return: 
        """
        with open('config.cfg', 'r') as configfile:                        # Check if the configfile has a latestsession section
            parser = configparser.ConfigParser()
            parser.read_file(configfile)
            hassection = parser.has_section('latestsession')

        if hassection:                                                      # If the configfile has the section
            hasremote = parser.has_option('latestsession', 'remotedatabase')# Check for remote option
            channels = configInterface.read_config('config.cfg', 'channels')# Fetch channels

            channellist = {}
            for index in channels:
                channellist[index] = ast.literal_eval(channels[index])      # Formats the channellist

            sessionsettings = configInterface.read_config('config.cfg', 'latestsession')
            start = sessionsettings['start']
            end = sessionsettings['end']
            self.localdb = ast.literal_eval(sessionsettings['localdatabase'])
            self.localsessionid = int(sessionsettings['localsessionid'])
            timeintervall = float(sessionsettings['timeintervall'])

            if not end:                                                     # If the session was not ended
                addthread = Addthread(localdb=self.localdb,
                                      sessionid=self.localsessionid,
                                      channellist=channellist,
                                      shouldend=self.shouldend,
                                      timeintervall=timeintervall)
                addthread.start()                                           # Start a thread for adding values to local database

                if hasremote:                                               # If a remote database is used in the session
                    self.usingremote = True
                    self.remotedb = ast.literal_eval(sessionsettings['remotedatabase'])
                    self.remotesessionid = int(sessionsettings['remotesessionid'])
                    remoteaddhtread = Addremotethread(remotedb=self.remotedb,
                                                      remotesessionid=self.remotesessionid,
                                                      localdb=self.localdb,
                                                      sessionid=self.localsessionid,
                                                      shouldend=self.shouldendremote,
                                                      programquit=self.programquit,
                                                      timeintervall=timeintervall)
                    remoteaddhtread.noConnection.connect(self.warnuser)
                    remoteaddhtread.connectionEstablished.connect(self.stopwarninguser)
                    remoteaddhtread.start()                                 # Start a thread for adding values to the remote database
                else:
                    self.usingremote = False

                self.sessionrunning = True                                  # Used by other functions to check if a session is running
                self.widgetlist.mainMenu.sessionStarted()  # Change appearance of the mainmeny
                self.datadisplay = Datadisplay(dbvalues=self.localdb,
                                               sessionid=self.localsessionid,
                                               channellist=channellist,
                                               ongoing=True,
                                               timeintervall=timeintervall)
                self.datadisplay.show()                                     # Open new window displaying data


    def warnuser(self):
        """
        Displays a warning on the main menu page
        :return: 
        """
        self.widgetlist.mainMenu.displayWarning(True)

    def stopwarninguser(self):
        """
        Removes a warning from the main menu page
        :return: 
        """
        self.widgetlist.mainMenu.displayWarning(False)

    def showsessionlist(self):
        """
        Display the sessionlist page
        :return: 
        """
        useremote = \
            self.widgetlist. \
                widget(self.widgetlist.visualizeDatabaseSettingsIndex). \
                useRemote()  # Fetch database type
        if useremote:  # If remote
            remotedb = configInterface.read_config('config.cfg',
                                                   'remotevisual')
            self.widgetlist.widget(self.widgetlist.visualizeSessionSettingsIndex).updateSessionList(remotedb)
        else:
            localdb = configInterface.read_config('config.cfg', 'default')
            self.widgetlist.widget(self.widgetlist.visualizeSessionSettingsIndex).updateSessionList(localdb)
        self.widgetlist.setCurrentIndex(self.widgetlist.visualizeSessionSettingsIndex)
        """
        sessionlist = self.getsessions()
        self.widgetlist.widget(self.widgetlist.visualizesessionsettingsindex).updateSessionList(sessionlist)
        self.widgetlist.setCurrentIndex(self.widgetlist.visualizesessionsettingsindex)
        """


    def showvisualizesettings(self):
        """
        Display the database settings page for the visualize option
        :return: 
        """
        self.widgetlist.setCurrentIndex(self.widgetlist.visualizeDatabaseSettingsIndex)

    def showdatabasesettings(self):
        """
        Display the database settings page for the start session option 
        :return: 
        """
        self.widgetlist.setCurrentIndex(self.widgetlist.databaseSettingsIndex)

    def showhelppage(self):
        """
        Display the help page
        :return: 
        """
        self.widgetlist.setCurrentIndex(self.widgetlist.helpPageIndex)

    def showmainmenu(self):
        """
        Display the main menu
        :return: 
        """
        self.widgetlist.setCurrentIndex(self.widgetlist.mainMenuIndex)

    def showchannelsettings(self):
        """
        Display the channel settings page
        :return: 
        """
        self.widgetlist.setCurrentIndex(self.widgetlist.channelSettingsIndex)

    def quit(self):
        """
        Checkpoint function before terminating the program 
        :return: 
        """
        if self.sessionrunning:                                             # If a session is running
            self.messageToUser(messagetext="Mätning pågår, "
                                           "avsluta mätning och "
                                           "stäng programmet?"
                               , yesbuttontext="Ja",
                               closebuttontext="Nej")                       # Prompt user
        else:
            self.closeapplication()                                         # Else, terminate

    def closeapplication(self):
        """
        Terminates the program
        :return: 
        """
        if self.sessionrunning:                                             # If a session is running
            self.endcurrentsession()                                        # End the session
        self.close()                                                        # Close

    def endcurrentsession(self):
        """
        Ends a running session
        :return: 
        """
        self.programquit.set()                                              # Signal remote add thread to stop
        self.shouldend.set()                                                # Signal local add thread

        endtimestamp = datetime.datetime.now()
        endtimestamp = endtimestamp.strftime("%Y-%m-%d %H:%M:%S")           # Get timestamp
        configInterface.set_config('config.cfg',
                                   'latestsession',
                                   {'end': endtimestamp})                   # Write the timestamp to configfile

        self.widgetlist.mainMenu.sessionEnded()  # Change main menu appearance
        Database.endCurrentSession(self.localdb, self.localsessionid)     # Give the local session an end time
        if self.usingremote:                                                # If using remote
            self.shouldendremote.set()
            Database.endCurrentSession(self.remotedb,
                                       self.remotesessionid)              # Give the remote session an end time

        self.datadisplay.close()                                            # Close the datadisplay window
        self.sessionrunning = False
        self.showmainmenu()                                                 # Display main menu

    def getsessions(self):
        """
        Retrieves a list of sessions from a database specified 
        on the database settings page for the visualize option
        :return: A tuple of tuples containing information about sessions
        Example: ((1, 'session1'), (2, 'session2'))
        """
        useremote = \
            self.widgetlist.\
                widget(self.widgetlist.visualizeDatabaseSettingsIndex).\
                useRemote()                                                 # Fetch database type
        if useremote:                                                       # If remote
            remotedb = configInterface.read_config('config.cfg',
                                                   'remotevisual')
            sessionlist = Database.getSessionList(remotedb)               # Get session from remote database
        else:
            localdb = configInterface.read_config('config.cfg', 'default')
            sessionlist = Database.getSessionList(localdb)                # Else, get sessions from local database
        return sessionlist



    def startsession(self):
        """
        Starts a new session
        :return: 
        """
        try:
            self.usingremote = \
                self.widgetlist.\
                    widget(self.widgetlist.databaseSettingsIndex).\
                    useRemote()                                             # Checks if a remote database should be used
            self.localdb = \
                configInterface.read_config('config.cfg', 'default')        # Gets configuration for the local database
            sessionname = \
                self.widgetlist.\
                    widget(self.widgetlist.channelSettingsIndex).\
                    sessionname                                             # Gets the sessionname
            channellist = \
                self.widgetlist.\
                    widget(self.widgetlist.channelSettingsIndex).\
                    channellist                                             # Gets a list of channels to use in the session
            timeintervall = \
                self.widgetlist.\
                    widget(self.widgetlist.channelSettingsIndex).\
                    sessionintervall                                        # Gets the time intervall for the session


            if self.usingremote:                                            # If a remote should be used
                self.remotedb = \
                    configInterface.read_config('config.cfg', 'remote')     # Get remote database configurations
                remotechannels = self.convertToRemoteChannels(channellist)
                self.remotesessionid = \
                    Database.remote_start_new_session(dbvalues=self.remotedb,
                                                      name=sessionname,
                                                      channels=remotechannels,
                                                      piid=self.piid)       # Make a new session entry to the remote database

            self.localsessionid = \
                Database.start_new_session(dbvalues=self.localdb,
                                           name=sessionname,
                                           channels=channellist)            # Make a new session entry to the local database


            now = datetime.datetime.now()
            startsearchvalue = now.strftime('%Y-%m-%d %H:%M:%S')
            startfractions = str(now.microsecond)                           # Get timestamp for session start
            writeitem = {'start': startsearchvalue, 'startfractions': startfractions,
                         'localdatabase': str(self.localdb), 'localsessionid': str(self.localsessionid),
                         'timeintervall': str(timeintervall), 'end': ''}    # Add session information to configfile

            if self.usingremote:                                            # If a remote is used
                writeitem['remotedatabase'] = str(self.remotedb)
                writeitem['remotesessionid'] = str(self.remotesessionid)    # Add information about the remote session

            parser = configparser.ConfigParser()
            with open('config.cfg', 'r') as r:
                parser.read_file(r)
                parser.remove_section('latestsession')                      # Remove previous information from the configfile
            with open('config.cfg', 'w') as w:
                parser.write(w)
            configInterface.set_config('config.cfg',
                                       'latestsession',
                                       writeitem)                           # Write the new information to the configfile

            addthread = Addthread(localdb=self.localdb,
                                  sessionid=self.localsessionid,
                                  shouldend=self.shouldend,
                                  channellist=channellist,
                                  timeintervall=timeintervall)
            addthread.start()                                               # Create a thread for adding to the local database and start it

            if self.usingremote:                                            # If a remote database is used
                remoteaddthread = Addremotethread(remotedb=self.remotedb,
                                                  localdb=self.localdb,
                                                  remotesessionid=self.remotesessionid,
                                                  sessionid=self.localsessionid,
                                                  shouldend=self.shouldendremote,
                                                  programquit=self.programquit,
                                                  timeintervall=timeintervall)
                remoteaddthread.connectionEstablished.connect(self.stopwarninguser)
                remoteaddthread.noConnection.connect(self.warnuser)
                remoteaddthread.start()                                     # Create a thread for adding to the remote database and start it

            self.datadisplay = Datadisplay(dbvalues=self.localdb,
                                           sessionid=self.localsessionid,
                                           channellist=channellist,
                                           ongoing=True,
                                           timeintervall=timeintervall)     # Create a new window for displaying data
            self.datadisplay.show()                                         # Show the window
            self.widgetlist.mainMenu.sessionStarted()  # Change appearance of mainmenu
            self.showmainmenu()                                             # Display the mainmeny
            self.sessionrunning = True

        except pymysql.err.Error as E:
            if E.args[0] == 1045:                                           # If mysql connection denied
                message = "Anslutning nekad, se över port, användare och lösenord"
                self.messageToUser(messagetext=message,
                                   closebuttontext="Stäng")
            if E.args[0] == 2003:                                           # If mysql connection cant be found
                message = "Kunde inte anluta till host: '%s'" % (self.remotedb['host'])
                self.messageToUser(messagetext=message,
                                   closebuttontext="Stäng")
            if E.args[0] == 1049:                                           # If the database wasnt found
                message = "Hittade ingen database med namnet '%s'" % (self.remotedb['name'])
                self.messageToUser(messagetext=message,
                                   closebuttontext="Stäng")
            if E.args[0] == 1062:                                           # If mysql integrity error
                message = "Minst två kanaler har samma namn. Kanalnamn måste vara unika"
                self.messageToUser(messagetext=message,
                                   closebuttontext="Stäng")
        except ValueError as V:                                             # If wrong value in port field
            print(V)
            wrongporttype = "Fel typ för 'Port', ett heltal förväntas"
            self.messageToUser(messagetext=wrongporttype,
                               closebuttontext="Stäng")

    def messageToUser(self, messagetext, yesbuttontext, closebuttontext):
        """
        Creteas a window displaying a specified message to the user
        :param messagetext: A string representing the message to display 
        :param closebuttontext: A string representing the text to be shown on the close button
        :return: 
        """
        message = QtWidgets.QMessageBox()
        message.setMinimumSize(1000, 800)
        message.setText(messagetext)
        closebutton = message.addButton(closebuttontext, QtWidgets.QMessageBox.YesRole)
        closebutton.clicked.connect(message.close)
        message.exec_()

    def convertToRemoteChannels(self, channellist):
        """
        Converts a list of local channels to a corresponding list of remote channels 
        :param channellist: the list of channels
        :return: The same tuple given as an argument, but with new keys
        """
        newlist = {}
        for index in channellist:
            newindex = int(index)
            newindex = newindex + 60*(self.piid-1)
            newlist[str(newindex)] = channellist[index]                     # Todo: Check if this can be done without hard coding
        return newlist

class Addthread(threading.Thread):
    def __init__(self, localdb, sessionid, channellist, shouldend, timeintervall):
        """
        Creates a new thread for adding values to the local database
        :param localdb: A tuple of database configurations for the local database
        Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
        :param sessionid: An int representing the id of the running session 
        :param channellist: A tuple of channels and channel values
        Example: {1: [101, 'Celsius', 0.9, 'Temperature'], 2: [102, 'Kilograms', 1.3, 'Weigth']}
        :param shouldend: A threading.Event object for stopping the thread
        :param timeintervall: An int representing the amount of second between each addition to the database
        """
        self.localdb = localdb
        self.sessionid = sessionid
        self.shouldend = shouldend
        self.channellist = channellist
        self.timeintervall = timeintervall
        threading.Thread.__init__(self)

    def run(self):
        """
        Does all work in the thread
        :return: 
        """
        while not self.shouldend.wait(self.timeintervall):                  # While the thread has not been told to stop
                                                                            # wait for timeintervall amount of seconds
            list = {}
            for item in self.channellist:
                id = int(item)
                #list[id] = id+0.23
                list[id] = random.randint(1, 100)                           # Generate random integers
            print(list)
            Database.addToDatabase(self.localdb, list, self.sessionid)    # Add values to the local database

        self.shouldend.clear()                                              # Before exiting thread, clear Event object


class Addremotethread(QtCore.QThread):
    noConnection = QtCore.pyqtSignal()
    connectionEstablished = QtCore.pyqtSignal()                             # Custom pyqt signals used to signal the main thread

    def __init__(self, localdb, remotedb, remotesessionid, sessionid, shouldend, programquit, timeintervall, parent=None):
        """
        Creates a new thread for adding values to a remote database
        :param localdb: A tuple of database configurations for the local database to fetch values from 
        Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
        :param remotedb: A tuple of database configurations for the remote database to add values to
        Example: {'user': 'root', 'host': '127.0.0.1', 'password': '1234', 'name': 'databasename', 'port': '3306'}
        :param remotesessionid: An int representing the remote session id associated with the values to be added
        :param sessionid: An int representing the local session id associated with the values to be fetched
        :param shouldend: A threading.Event object used to stop the thread
        :param programquit: A threading.Event object used to make the thread add values immediately
        :param timeintervall: An int representing the amount of seconds between each addition
        :param parent: 
        """
        self.remotedb = remotedb
        self.remotesessionid = remotesessionid
        self.sessionid = sessionid
        self.shouldend = shouldend
        self.localdb = localdb
        self.programquit = programquit
        self.timeintervall = timeintervall
        self.latestaddtime = None
        self.latestaddfractions = None
        self.addedalldata = False
        self.databaseisdown = False
        QtCore.QThread.__init__(self, parent)

    def run(self):
        """
        Fetches values from a local database and adds them to a remote database
        :return: 
        """
        pid = configInterface.read_config('config.cfg', 'piid')
        piid = int(pid['id'])                                               # Gets the id of the Raspberry pi running the program
        while not self.addedalldata:
            try:
                if self.programquit.wait(0):                                # If signaled that the program wants to terminate
                    self.timeintervall = 0                                  # Do additions immediately
                if not self.shouldend.wait(self.timeintervall*10):          # Wait for timeintervall seconds
                    sessionsettings = configInterface.read_config('config.cfg', 'latestsession')
                    start = sessionsettings['start']
                    end = sessionsettings['end']                            # Get previous previous search parameters
                    if not end == '':                                       # If the session has been ended
                        checkend = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                        checkstart = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                        if checkend > checkstart:                           # Check if the last search parameter is greater than the end value fo the session
                            self.addedalldata = True


                    end = datetime.datetime.now()                           # Get new end value to use in local database search
                    valuelist = Database.getMeasurements(dbvalues=self.localdb,
                                                         sessionid=self.sessionid,
                                                         channelid=None,
                                                         starttime=start,
                                                         endtime=end)      # Get measurements from the local database
                    templatestaddtime = None
                    templatestaddfractions = None
                    new = []
                    for row in valuelist:                                   # For each row in the result
                        timestamp = row[2].strftime('%Y-%m-%d %H:%M:%S')
                        timestampfractions = row[3]
                        templatestaddtime = row[2].strftime('%Y-%m-%d %H:%M:%S')
                        templatestaddfractions = row[3]
                        data = row[4]                                       # Add measurementvalues to a new list
                        remotechannel = row[1]+60*(piid-1)                  # Convert local id to remoteid
                        if not(timestamp == self.latestaddtime and timestampfractions == self.latestaddfractions):
                            new.append((self.remotesessionid,
                                        remotechannel,
                                        timestamp,
                                        timestampfractions,
                                        data))                              # If the timestamp in this result matches the last timestamp in the previous result
                                                                            # dont add it to the new list
                    if not new == []:
                        Database.remoteAddToDatabase(self.remotedb, new) # If the list is not empty, add values to the remote database

                    self.latestaddtime = templatestaddtime
                    self.latestaddfractions = templatestaddfractions        # Set latest add timestamp

                    if self.databaseisdown:                                 # If the database was down, the database is now up since the addition was succesful
                        self.connectionEstablished.emit()                   # Signals main thread that the database is connected
                        self.databaseisdown = False

                    newstart = end.strftime('%Y-%m-%d %H:%M:%S')            # Write the end time used in the search to the configfile
                                                                            # To be used as start time in the next search
                    configInterface.set_config('config.cfg', 'latestsession', {'start': newstart})
                else:
                    self.shouldend.clear()
            except pymysql.err.Error as E:                                  # If the database raises an exception
                if not self.databaseisdown:
                    self.noConnection.emit()                                # Signal the main thread that the database is down
                    self.databaseisdown = True
                print(E)
        self.programquit.clear()




class Datadisplay(QtWidgets.QDialog):
    datafetched = QtCore.pyqtSignal()

    def __init__(self, dbvalues, sessionid, channellist, ongoing, timeintervall, parent=None):
        self.dbvalues = dbvalues
        self.sessionid = sessionid
        channelpairs = {}
        for index in channellist:
            displaychannel = channellist[index][0]
            backendchannel = int(index)
            channelpairs[displaychannel] = backendchannel
        self.channelpairs = channelpairs
        self.currentchannel = next(iter(self.channelpairs))
        self.ongoing = ongoing

        QtWidgets.QDialog.__init__(self, parent)

        self.plot = Currentsessionplot(dbvalues=dbvalues,
                                       sessionid=sessionid,
                                       plotchannel=self.channelpairs[self.currentchannel],
                                       timeintervall=timeintervall,
                                       figuretitle=self.currentchannel)
        self.toolbar = NT(self.plot, self)

        if self.ongoing:
            self.plot.updatefigure()
        else:
            self.plot.drawfigure()


        font = QtGui.QFont()
        font.setFamily('Ubuntu')
        font.setPointSize(18)

        self.label = QtWidgets.QLabel("Visar kanal %s" % self.currentchannel)
        self.label.setFont(font)

        self.dropdown = QtWidgets.QComboBox()
        self.dropdown.currentIndexChanged.connect(self.switchchannel)
        for item in self.channelpairs:
            self.dropdown.addItem(item)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(self.dropdown)
        vbox.addWidget(self.toolbar)
        vbox.addWidget(self.plot)
        vbox.addStretch(1)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)
        self.setModal(False)
        self.setLayout(hbox)

    def switchchannel(self):
        self.currentchannel = self.dropdown.currentText()
        newtitle = "Kanal: %s" % self.currentchannel
        self.plot.channelswitch(newid=self.channelpairs[self.currentchannel],
                                newtitle=newtitle)
        if self.ongoing == True:
            pass
            self.plot.updatefigure()
        else:
            self.plot.drawfigure()




class Currentsessionplot(FC):

    def __init__(self, dbvalues, sessionid, plotchannel, timeintervall, figuretitle):
        self.dbvalues = dbvalues
        self.sessionid = sessionid
        self.plotchannel = plotchannel
        self.timeintervall = timeintervall
        figuretitle = "Kanal: %s" % figuretitle

        self.figure = Figure(figsize=(10, 10), dpi=100)
        self.figure.suptitle(figuretitle)
        self.axes = self.figure.add_subplot(111)
        self.axes.hold(False)


        FC.__init__(self, self.figure)

        FC.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding,
                         QtWidgets.QSizePolicy.Expanding)

        FC.updateGeometry(self)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updatefigure)


    def channelswitch(self, newid, newtitle):
        self.timer.stop()
        self.plotchannel = newid
        self.figure.clear()
        self.axes = self.figure.add_subplot(111)
        self.figure.suptitle(newtitle, fontsize=20)
        self.axes.hold(False)


    def updatefigure(self):
        rawnow = datetime.datetime.now()
        rawstart = rawnow - datetime.timedelta(seconds=100)
        now = rawnow.strftime('%Y-%m-%d %H:%M:%S')
        start = rawstart.strftime('%Y-%m-%d %H:%M:%S')
        values = Database.getMeasurements(dbvalues=self.dbvalues,
                                          sessionid=self.sessionid,
                                          channelid=self.plotchannel,
                                          starttime=start,
                                          endtime=now)
        xaxisvalues = []
        yaxisvalues = []
        for index in values:
            xaxisvalues.append(index[2])
            yaxisvalues.append(index[4])

        print("UPDATE FIGURE IS STILL RUNNING")

        #ticks = np.arange(rawstart, rawnow, 5)
        xformater = matdates.DateFormatter('%H:%M:%S')
        self.axes.xaxis.set_major_formatter(xformater)
        #self.axes.set_xticks(ticks)
        self.axes.plot(xaxisvalues, yaxisvalues)
        self.axes.set_xlim([rawstart, rawnow])
        for tick in self.axes.get_xticklabels():
            tick.set_rotation(10)                           # change this
        self.draw()
        self.timer.start(1000*self.timeintervall)

    def drawfigure(self):
        values = Database.getMeasurements(dbvalues=self.dbvalues,
                                          sessionid=self.sessionid,
                                          channelid=self.plotchannel,
                                          starttime=None,
                                          endtime=None)

        xaxisvalues = []
        yaxisvalues = []
        for index in values:
            xaxisvalues.append(index[2])
            yaxisvalues.append(index[4])

        # ticks = np.arange(rawstart, rawnow, 5)
        #xformater = matdates.DateFormatter('%Y-%m-%d %H:%M:%S')
        #self.axes.xaxis.set_major_formatter(xformater)
        # self.axes.set_xticks(ticks)
        self.axes.plot(xaxisvalues, yaxisvalues)
        #self.axes.set_xlim([rawstart, rawnow])
        for tick in self.axes.get_xticklabels():
            tick.set_rotation(10)  # change this
        self.draw()



if __name__ == '__main__':
    #remote = configinterface.read_config('config.cfg', 'createremote')

    local = configInterface.read_config('config.cfg', 'default')
    #Database.create_remote_database(remote)
    parser = configparser.ConfigParser()
    with open('config.cfg', 'r') as file:
        parser.read_file(file)
        hasid = parser.has_section('piid')
    if not hasid:
        id = str(Database.remoteAddNewPi(remote, 'placeholdername'))
        configInterface.set_config('config.cfg', 'piid', {'id': id})
    Database.create_local_database(local)
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.showFullScreen()
    sys.exit(app.exec_())