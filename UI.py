from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
import configinterface
import sys
import configparser


class Visualizationsettings(QtWidgets.QWidget):
    backPressed = QtCore.pyqtSignal()
    okPressed = QtCore.pyqtSignal(int, object)
    sessionChosen = QtCore.pyqtSignal(int)                                  # Custom pyqt signals

    def __init__(self):
        """
        Initializes a new instance of a VisualizeSession object
        :param parent: 
        """
        QtWidgets.QWidget.__init__(self)
        buttons = QtWidgets.QDialogButtonBox()
        okbutton = buttons.addButton('Nästa', buttons.AcceptRole)
        cancelbutton = buttons.addButton('Tillbaka', buttons.RejectRole)
        okbutton.setMinimumSize(300, 100)
        okbutton.clicked.connect(self._nextPage)
        cancelbutton.setMinimumSize(300, 100)
        cancelbutton.clicked.connect(self._goback)                          # Creates the two buttons of the widget

        message = QtWidgets.QLabel("Välj en mätning att visa")              # Creates the top message of the widget

        self.sessionlist = QtWidgets.QListWidget()
        self.sessionlist.setMinimumSize(600, 100)
        self.channellist = None
        self.currentsession = None                                          # Initializes variables used to hold session and channels information

        self.sessionlist.itemActivated.connect(self._sessionactivated)
        self.sessionlist.itemClicked.connect(self._sessionactivated)         # Connects the signal emitted when a user selects an item in the list

        scrollablesessions = QtWidgets.QScrollArea()
        scrollablesessions.setWidget(self.sessionlist)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(message)
        vbox.addWidget(scrollablesessions)
        vbox.addWidget(buttons)
        vbox.addStretch(2)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)                                                  # Creates the layout of the widget

        self.setLayout(hbox)                                                # Sets the layout

    def _nextPage(self):
        """ 
        Handles what happens when the next page button is pressed
        :return: 
        """
        if not self.currentsession == None:                                 # If a session has been chosen
            self.okPressed.emit(self.currentsession, self.channellist)      # Emit a signal with the chosen session and its corresponding channels as arguments
        else:
            self._messageToUser(messagetext="Du måste välja en mätning!", yesbuttontext=None, closebuttontext="Stäng")                # Else, prompt the user with a message

    def _goback(self):
        """
        Handles what happens when the back button is pressed
        :return: 
        """
        self.backPressed.emit()                                             # Emit the backPressed signal

    def _sessionactivated(self, activatedrow):
        """
        Handles what happens when an item in the session list has been chosen
        :param activatedrow: an int representing the row number of the chosen item
        :return: 
        """
        idandname = QtWidgets.QListWidgetItem(activatedrow).text()
        list = idandname.split()
        self.currentsession = int(list[0])
        self.sessionChosen.emit(int(list[0]))                               # Extracts the session id and uses it as an emit argument

    def updateSessionList(self, idandnamelist):
        """
        Updates the list of sessions displayed in the widget
        :param idandnamelist: a list or tuple containing list or tuple of channel ids and channel names
        Example: ((1, 'Session one'), (2, 'session two'))
        :return: 
        """
        self.sessionlist.clear()                                            # Removes the previous items in the list
        for item in idandnamelist:                                          # For each item in the received list
            widgetitem = QtWidgets.QListWidgetItem()
            widgetitem.setText("%d %s" % (item[0], item[1]))                # Extract id and name
            self.sessionlist.addItem(widgetitem)                            # Add it to the widget list
            self.sessionlist.itemActivated.emit(widgetitem)
            self.sessionlist.itemClicked.emit(widgetitem)                   # Emit the item when it is chosen
        self.currentsession = None                                          # Makes sure the user has to choose an item before moving to the nect page

    def updateChannelList(self, channellist):
        """
        Updates the list of channels connected to a session
        :param channellist: a tuple of tuples containing channel id and channel name
        Example: ((1, 'temperature'), (2, 'weigth'))
        :return: 
        """
        formattedchannellist = {}
        for index in channellist:
            formattedchannellist[index[0]] = [index[1]]                     # Converts the list of channels to a dictionary
        self.channellist = formattedchannellist                             # Sets the channellist of the widget to be the dictionary

    def _messageToUser(self, messagetext, yesbuttontext, closebuttontext):
        message = QtWidgets.QMessageBox()
        message.setMinimumSize(1000, 800)
        message.setText(messagetext)
        if not yesbuttontext == None:
            yesbutton = message.addButton(yesbuttontext, QtWidgets.QMessageBox.YesRole)
            yesbutton.clicked.connect(self.closeapplication)
        if not closebuttontext == None:
            closebutton = message.addButton(closebuttontext, QtWidgets.QMessageBox.YesRole)
            closebutton.clicked.connect(message.close)
        message.exec_()
                                                       # Displays it


class Channelsettings(QtWidgets.QWidget):
    backPressed = QtCore.pyqtSignal()
    okPressed = QtCore.pyqtSignal()                                         # Custom pyqt signals

    def __init__(self):
        """
        Initialises a new instance of a Channelsettingspage
        """
        QtWidgets.QWidget.__init__(self)
        self.channels = {}

        buttons = QtWidgets.QDialogButtonBox()
        okbutton = buttons.addButton('Nästa', buttons.AcceptRole)
        cancelbutton = buttons.addButton('Tillbaka', buttons.RejectRole)
        okbutton.setMinimumSize(300, 80)
        okbutton.clicked.connect(self._nextPage)
        cancelbutton.setMinimumSize(300, 80)
        cancelbutton.clicked.connect(self._goback)                           # Creates the buttons of the page

        self._setchanneltable()                                              # Cretes the table of channels displayed on the page
        channelmessage = self._setmessage("Välj vilka kanaler som ska användas i mätningen")                                         # Creates the message displayed on top of the page

        input = self.sessioninfo()


        vbox = QtWidgets.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(input)
        vbox.addWidget(channelmessage)
        vbox.addWidget(self.tableWidget)
        vbox.addWidget(buttons)
        vbox.addStretch(2)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)                                                  # Creates the layout of the page

        self.setLayout(hbox)                                                # Sets the layout

    def sessioninfo(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        self.nameinput = QtWidgets.QLineEdit()
        self.intervallinput = QtWidgets.QLineEdit()
        namemessage = self._setmessage("Namnge mätningen")
        intervallmessage = self._setmessage("Ange tidsintervall (sekunder)")
        layout.addWidget(namemessage)
        layout.addWidget(self.nameinput)
        layout.addWidget(intervallmessage)
        layout.addWidget(self.intervallinput)

        widget.setLayout(layout)
        return widget

    def _goback(self):
        """
        Handles what happens when the back button is pressed
        :return: 
        """
        self.backPressed.emit()                                             # Emits a custom signal

    def _nextPage(self):
        """
        Handles what happens when the next button is pressed
        :return: 
        """
        exceptionraised = False
        self.channellist = {}
        try:
            for i in range(60):                                             # For each row in the table
                item = self.tableWidget.item(i, 0)
                if item.checkState() == QtCore.Qt.Checked:                  # If a channel has been chosen
                    channelid = "%d" % (i+1)
                    channelidalias = "%s" % (self.tableWidget.verticalHeaderItem(i).text(),)
                    channelunit = "%s" % (self.tableWidget.item(i, 1).text(),)
                    channeltolerance = "%s" % (self.tableWidget.item(i, 2).text(),)
                    channelname = "%s" % (self.tableWidget.item(i, 3).text(),)
                    if channelname == "":
                        raise AttributeError
                    self.channellist[channelid] = \
                        str([channelidalias,
                             channelname,
                             channelunit,
                             channeltolerance])                             # Collect channel information and add it to the list of channels

                    float(channeltolerance)                                 # Raises a ValueError if channeltolerance can not be converted to float

            self.sessionname = self.nameinput.text()
            self.sessionintervall = self.intervallinput.text()

            try:
                self.sessionintervall = float(self.sessionintervall)  # Otherwise, custom pyqt signal
            except ValueError:
                exceptionraised = True
                wrongintervalltype = "Tidsintervall måste anges som ett nummer"
                self._messageToUser(wrongintervalltype, yesbuttontext=None, closebuttontext="Stäng")

            if not self.sessionname:
                noname = "Du måste namnge mätningen"
                self._messageToUser(noname, yesbuttontext=None, closebuttontext="Stäng")

            elif not self.sessionintervall:
                nointervall = "Du måste ange ett tidsintervall"
                self._messageToUser(nointervall, yesbuttontext=None, closebuttontext="Stäng")

            elif self.channellist == {}:  # If no channel has been selected
                nochannels = "Du måste välja minst en kanal!"
                self._messageToUser(nochannels, yesbuttontext=None,
                                    closebuttontext="Stäng")  # Prompt the user with a message
            elif not exceptionraised:
                self.okPressed.emit()

            parser = configparser.ConfigParser()
            with open('config.cfg', 'r+') as r:
                parser.read_file(r)
                parser.remove_section('channels')
            with open('config.cfg', 'w+') as w:
                parser.write(w)
            configinterface.set_config('config.cfg', 'channels', self.channellist)

        except AttributeError:                                              # A channel is missing some input
            textmissing = \
                "Kanal %s saknar nödvändig information!" % (channelidalias)
            self._messageToUser(textmissing, yesbuttontext=None, closebuttontext="Stäng")                                # Tell the user which channel is missing input
            self.channellist = {}
        except ValueError as V:  # Wrong type has been inputted into the tolerance field
            exceptionraised = True
            wronginputtype = \
                "Kanal %s har fel typ av tolerans, " \
                "tolerans ska vara ett flyttal t.ex. 42.0" \
                % (channelidalias)
            self._messageToUser(wronginputtype, yesbuttontext=None, closebuttontext="Stäng")                             # Tell the user which channel has wrong type of tolerance
            self.channellist = {}


    def _messageToUser(self, messagetext, yesbuttontext, closebuttontext):
        message = QtWidgets.QMessageBox()
        message.setMinimumSize(1000, 800)
        message.setText(messagetext)
        if not yesbuttontext == None:
            yesbutton = message.addButton(yesbuttontext, QtWidgets.QMessageBox.YesRole)
            yesbutton.clicked.connect(self.closeapplication)
        if not closebuttontext == None:
            closebutton = message.addButton(closebuttontext, QtWidgets.QMessageBox.YesRole)
            closebutton.clicked.connect(message.close)
        message.exec_()

    def _setmessage(self, messagetext):
        """
        Creates the message displayed at the top of the widget
        :return: A QtWidgets.QLabel object representing the message
        """
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(18)
        message = QtWidgets.QLabel(messagetext)
        message.setFont(font)
        return message

    def _setchanneltable(self):
        """
        Creates table of channels displayed on the page
        :return: A QtWidgets.QTableWidget object representing the table created
        """
        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setMinimumSize(300, 200)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setRowCount(60)
        self.tableWidget.setShowGrid(True)                                  # Creates the actual table

        for i in range(60):                                                 # For each row in the table
            checkbox = QtWidgets.QTableWidgetItem()
            checkbox.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            checkbox.setText("Använd")
            checkbox.setCheckState(QtCore.Qt.Unchecked)                     # Create a checkbox
            font = QtGui.QFont()
            font.setPointSize(12)
            checkbox.setFont(font)
            self.tableWidget.setItem(i, 0, checkbox)                        # Add the checkbox to the first column
            self.tableWidget.itemClicked.emit(checkbox)
            self.tableWidget.itemActivated.emit(checkbox)                   # Emit the checkbox when it is pressed

        self.tableWidget.itemClicked.connect(self._checkrow)
        self.tableWidget.itemActivated.connect(self._checkrow)              # Connects the emit signal to the checkrow function

        for ii in range(1, 4):                                              # Adds a label to each row in the table
            index = 100*ii
            for i in range(1, 21):
                vheadertext = "%d" % (i + index)
                vheader = QtWidgets.QTableWidgetItem(vheadertext)
                self.tableWidget.setVerticalHeaderItem((ii-1)*20 + i - 1, vheader)

        useheader = QtWidgets.QTableWidgetItem("")
        unitheader = QtWidgets.QTableWidgetItem("Enhet")
        toleranceheader = QtWidgets.QTableWidgetItem("Tolerans")
        nameheader = QtWidgets.QTableWidgetItem("Namn")
        self.tableWidget.setHorizontalHeaderItem(0, useheader)
        self.tableWidget.setHorizontalHeaderItem(1, unitheader)
        self.tableWidget.setHorizontalHeaderItem(2, toleranceheader)
        self.tableWidget.setHorizontalHeaderItem(3, nameheader)             # Adds a label to each column in the table

        self.tableWidget.verticalHeader().setCascadingSectionResizes(True)
        self.tableWidget.setColumnWidth(0, 80)
        self.tableWidget.setColumnWidth(1, 80)
        self.tableWidget.setColumnWidth(2, 80)
        self.tableWidget.setColumnWidth(3, 80)                             # Sets the sizes of the columns



    def _checkrow(self, checkbox):
        """
        Toggles a checkbox
        :param checkbox: a QtWidgets.QTableWidgetItem object representing the checkbox to be toggled
        :return: 
        """
        checked = checkbox.checkState()                                     # Checks the checkState of the checkbox
        if checked == 0:                                                    # If checked, set to unchecked
            checkbox.setCheckState(2)
        else:                                                               # Else, set to checked
            checkbox.setCheckState(0)


class Databasesettings(QtWidgets.QWidget):
    cancelPressed = QtCore.pyqtSignal()
    okPressed = QtCore.pyqtSignal()

    def __init__(self, message, firsttoggle, secondtoggle, writesection):
        """
        Initializes a new Databasesettings page
        :param message: A string representing the message to be displayed at the top of the page
        :param firsttoggle: A string representing text to be displayed at the left radiobutton
        :param secondtoggle: A string representing text to be displayed at the right radiobutton 
        :param writesection: A string representing a section of the configfile to write the databasesettings to
        """
        QtWidgets.QWidget.__init__(self)
        self.writesection = writesection
        buttons = QtWidgets.QDialogButtonBox()
        okbutton = buttons.addButton('Starta', buttons.AcceptRole)
        cancelbutton = buttons.addButton('Tillbaka', buttons.RejectRole)
        okbutton.setMinimumSize(200, 80)
        okbutton.clicked.connect(self.nextPage)
        cancelbutton.setMinimumSize(200, 80)
        cancelbutton.clicked.connect(self.backToMain)                       # Creates the main buttons of the page

        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(18)
        infostring = QtWidgets.QLabel(message)
        infostring.setFont(font)                                            # Creates the message displayed at the top of the page

        self.databaseform = Databaseform()                                  # Creates the form where settings can be configured

        yesbutton = QtWidgets.QRadioButton()
        yesbutton.setText(firsttoggle)
        yesbutton.setAutoExclusive(True)
        yesbutton.setCheckable(True)
        yesbutton.toggled.connect(self.databaseform.useRemote)
        yesbutton.toggled.connect(self._setRemoteTrue)                       # Creates the left radiobutton

        nobutton = QtWidgets.QRadioButton()
        nobutton.setText(secondtoggle)
        nobutton.setAutoExclusive(True)
        nobutton.setCheckable(True)
        nobutton.toggled.connect(self.databaseform.dontUseRemote)
        nobutton.toggled.connect(self._setRemoteFalse)
        nobutton.setChecked(True)                                           # creates the right radiobutton

        buttonlayout = QtWidgets.QHBoxLayout()
        buttonlayout.addWidget(yesbutton)
        buttonlayout.addWidget(nobutton)

        buttongroup = QtWidgets.QWidget()
        buttongroup.setLayout(buttonlayout)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(infostring)
        vbox.addWidget(buttongroup)
        vbox.addWidget(self.databaseform)
        vbox.addWidget(buttons)
        vbox.addStretch(2)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)                                                # Creates the layout of the page
        hbox.addStretch(1)

        self.setLayout(hbox)                                                # Sets the layout of the page

    def _setRemoteTrue(self):
        self.remote = True

    def _setRemoteFalse(self):
        self.remote = False

    def backToMain(self):
        self.cancelPressed.emit()

    def nextPage(self):
        """
        Handles what happens when the next button is pressed 
        :return: 
        """
        if self.remote:                                                     # If a remote database should be used
            host = self.databaseform.host.text()
            user = self.databaseform.user.text()
            port = self.databaseform.port.text()
            name = self.databaseform.database.text()
            password = self.databaseform.password.text()
            newremotevalues = {'host': host, 'user': user, 'port': port, 'name': name, 'password': password}
            configinterface.set_config('config.cfg',
                                       self.writesection,
                                       newremotevalues)                      # Write the database settings to the configfile

        self.okPressed.emit()                                               # Emit the okPressed signal

    def useRemote(self):
        use = self.remote
        return use

class Databaseform(QtWidgets.QWidget):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        font = self.createFormFont()
        previous_remote_database = configinterface.read_config('config.cfg', 'remote')

        self.host = QtWidgets.QLineEdit()
        self.host.setMinimumSize(200, 50)
        self.host.setFont(font)
        self.hosttext = previous_remote_database['host']
        self.hostlabel = QtWidgets.QLabel("Host")
        self.hostlabel.setFont(font)
        self.hostlabel.setMinimumSize(50, 50)

        self.port = QtWidgets.QLineEdit()
        self.port.setMinimumSize(200, 50)
        self.port.setFont(font)
        self.porttext = previous_remote_database['port']
        self.portlabel = QtWidgets.QLabel("Port")
        self.portlabel.setFont(font)
        self.portlabel.setMinimumSize(50, 50)

        self.database = QtWidgets.QLineEdit()
        self.database.setMinimumSize(200, 50)
        self.database.setFont(font)
        self.databasetext = previous_remote_database['name']
        self.databaselabel = QtWidgets.QLabel("Database name")
        self.databaselabel.setFont(font)
        self.databaselabel.setMinimumSize(50, 50)

        self.user = QtWidgets.QLineEdit()
        self.user.setMinimumSize(200, 50)
        self.user.setFont(font)
        self.usertext = previous_remote_database['user']
        self.userlabel = QtWidgets.QLabel("User")
        self.userlabel.setFont(font)
        self.userlabel.setMinimumSize(50, 50)

        self.password = QtWidgets.QLineEdit()
        self.password.setMinimumSize(200, 50)
        self.password.setFont(font)
        self.passwordtext = previous_remote_database['password']
        self.password.setEchoMode(self.password.Password)
        self.passwordlabel = QtWidgets.QLabel("Password")
        self.passwordlabel.setFont(font)
        self.passwordlabel.setMinimumSize(50, 50)

        form = QtWidgets.QFormLayout()
        form.addRow(self.hostlabel, self.host)
        form.addRow(self.portlabel, self.port)
        form.addRow(self.databaselabel, self.database)
        form.addRow(self.userlabel, self.user)
        form.addRow(self.passwordlabel, self.password)
        form.setVerticalSpacing(10)

        self.setLayout(form)

    def dontUseRemote(self):

        backgroundcolor = "background-color: grey;"

        self.host.setReadOnly(True)
        self.host.setStyleSheet(backgroundcolor)
        self.host.setText("")
        self.host.setPlaceholderText(self.hosttext)

        self.user.setReadOnly(True)
        self.user.setStyleSheet(backgroundcolor)
        self.user.setText("")
        self.user.setPlaceholderText(self.usertext)

        self.port.setReadOnly(True)
        self.port.setStyleSheet(backgroundcolor)
        self.port.setText("")
        self.port.setPlaceholderText(self.porttext)

        self.password.setReadOnly(True)
        self.password.setStyleSheet(backgroundcolor)
        self.password.setText("")

        self.database.setReadOnly(True)
        self.database.setStyleSheet(backgroundcolor)
        self.database.setText("")
        self.database.setPlaceholderText(self.databasetext)

    def useRemote(self):

        backgroundcolor = "background-color: white;"

        self.host.setReadOnly(False)
        self.host.setStyleSheet(backgroundcolor)
        self.host.setText(self.hosttext)

        self.user.setReadOnly(False)
        self.user.setStyleSheet(backgroundcolor)
        self.user.setText(self.usertext)

        self.port.setReadOnly(False)
        self.port.setStyleSheet(backgroundcolor)
        self.port.setText(self.porttext)

        self.password.setReadOnly(False)
        self.password.setStyleSheet(backgroundcolor)
        self.password.setText(self.passwordtext)

        self.database.setReadOnly(False)
        self.database.setStyleSheet(backgroundcolor)
        self.database.setText(self.databasetext)

    def createFormFont(self):
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(18)
        font.setStyleName("Regular")
        return font


class currentSession(QtWidgets.QWidget):

    cancelPressed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)


        buttons = QtWidgets.QDialogButtonBox()
        cancelbutton = buttons.addButton('Tillbaka', buttons.RejectRole)
        cancelbutton.setMinimumSize(300, 100)
        cancelbutton.clicked.connect(self.backToMain)

        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(18)

        self.currentlabel = QtWidgets.QLabel("There's nothing going on...but Alex Jones won't tell you that. #HillaryIsEvil")
        self.currentlabel.setFont(font)
        self.currentlabel.setMinimumSize(50, 50)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.currentlabel)
        vbox.addWidget(buttons)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def backToMain(self):
        self.cancelPressed.emit()


class helpPages(QtWidgets.QWidget):

    cancelPressed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)


        buttons = QtWidgets.QDialogButtonBox()
        cancelbutton = buttons.addButton('Tillbaka', buttons.RejectRole)
        cancelbutton.setMinimumSize(300, 100)
        cancelbutton.clicked.connect(self.backToMain)

        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(18)

        self.helplabel = QtWidgets.QLabel("To Be Implemented")
        self.helplabel.setFont(font)
        self.helplabel.setMinimumSize(50, 50)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.helplabel)
        vbox.addWidget(buttons)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def backToMain(self):
        self.cancelPressed.emit()


class UIpages(QtWidgets.QStackedWidget):
    def __init__(self):
        """
        Initilizes a new instance of a UIpages object
        """
        QtWidgets.QStackedWidget.__init__(self)

        self.mainmenu = Mainmenu()
        self.mainmenuindex = self.addWidget(self.mainmenu)                  # Creates a main menu page and stores its index

        self.databasesettings = Databasesettings(firsttoggle="Ja",
                                                       secondtoggle="Nej",
                                                       writesection="remote",
                                                       message="Mätvärden kommer att "
                                                               "sparas lokalt, vill du även "
                                                               "spara till en annan databas?")
        self.databasesettingsindex = self.addWidget(self.databasesettings)  # Creates a databasesettings page and stores its index

        self.helppage = helpPages()
        self.helppageindex = self.addWidget(self.helppage)                  # Creates a help page and stores its index

        self.channelsettings = Channelsettings()
        self.channelsettingsindex = self.addWidget(self.channelsettings)    # Creates a Channelsettings page and stores its index

        self.current = currentSession()
        self.currentsessionindex = self.addWidget(self.current)             # Creates a currentsession page and stores its index

        self.visualizedatabasesettings = Databasesettings(firsttoggle="Annan",
                                                                secondtoggle="Lokal",
                                                                writesection="remotevisual",
                                                                message="Hämta lokala mätvärden, "
                                                                        "eller hämta från en databas?")
        self.visualizedatabasesettingsindex = \
            self.addWidget(self.visualizedatabasesettings)                  # Creates a Databasesettings page and stores its index

        self.visualizesessionsettings = Visualizationsettings()
        self.visualizesessionsettingsindex = \
            self.addWidget(self.visualizesessionsettings)                   # Creates a Visualizationsettings page and stores its idnex



class Mainmenu(QtWidgets.QWidget):
    warningPressed = QtCore.pyqtSignal()
    quitSignal = QtCore.pyqtSignal()
    sessionSignal = QtCore.pyqtSignal()
    helpSignal = QtCore.pyqtSignal()
    currentSignal = QtCore.pyqtSignal()
    visualizeSignal = QtCore.pyqtSignal()

    def __init__(self):
        """
        Initialises a new instance of a Mainmenu page 
        """
        QtWidgets.QWidget.__init__(self)
        icon = QtGui.QIcon('alert-icon--free-icons-24.png')
        self.warningButton = QtWidgets.QPushButton("Varning!")
        self.warningButton.setMinimumSize(300, 80)
        self.warningButton.setIcon(icon)
        self.warningButton.setStyleSheet("background-color: red;")
        """
        self.warningButton.setToolTip("Varning: Anslutningen till "
                                        "den databas som används i den "
                                        "pågående mätningen är nere. \n "
                                        "Mätningen kommer att fortsätta "
                                        "och anslutningen till databasen "
                                        "kommer att försöka upprättas. \n"
                                        "Denna varning kommer att försvinna "
                                        "när anslutningen är återuprättad")
        
        """
        self.warningButton.hide()
        self.warningButton.clicked.connect(self.warningPressed.emit)

        self.startButton = QtWidgets.QPushButton("Starta nya mätning")
        self.startButton.setMinimumSize(300, 80)
        self.startButton.clicked.connect(self.newSession)                   # Creates the start session button and connects its signal

        self.currentButton = QtWidgets.QPushButton("Avsluta pågående mätning")
        self.currentButton.setMinimumSize(300, 80)
        self.currentButton.clicked.connect(self.currentSession)             # Creates the end current session button and connects its signal
        self.currentButton.hide()                                           # Hides the button

        self.visualizeButton = QtWidgets.QPushButton("Visa mätningar")
        self.visualizeButton.setMinimumSize(300, 80)
        self.visualizeButton.clicked.connect(self.visualize)                # Creates the visualize button and connects its signal

        self.helpButton = QtWidgets.QPushButton("Hjälp")
        self.helpButton.setMinimumSize(300, 80)
        self.helpButton.clicked.connect(self.help)                          # Creates the help button and connects its signal

        self.quitButton = QtWidgets.QPushButton("Avsluta")
        self.quitButton.setMinimumSize(300, 80)
        self.quitButton.clicked.connect(self.quit)                          # Creates the quit button and connects its signal

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.warningButton)
        vbox.addWidget(self.startButton)
        vbox.addWidget(self.currentButton)
        vbox.addWidget(self.visualizeButton)
        vbox.addWidget(self.helpButton)
        vbox.addWidget(self.quitButton)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)                                                # Creates the layout of the page
        hbox.addStretch(1)

        self.setLayout(hbox)                                                # Sets the layout of the page

    def visualize(self):
        """
        Handles what happens when the visualize button is clicked
        :return: 
        """
        self.visualizeSignal.emit()                                         # Emits the visualizeSignal signal

    def quit(self):
        """
        Handles what happens when the quit button is clicked
        :return: 
        """
        self.quitSignal.emit()                                              # Emits the quitSignal signal

    def newSession(self):
        """
        Handles what happens when the new session button is clicked
        :return: 
        """
        self.sessionSignal.emit()                                           # Emits the visualizeSignal signal

    def currentSession(self):
        """
        Handles what happens when the current end current session button is clicked
        :return: 
        """
        self.currentSignal.emit()                                           # Emits the currentSignal signal

    def help(self):
        """
        Handles what happens when the help button is clicked
        :return: 
        """
        self.helpSignal.emit()                                              # Emits the helpSignal signal

    def sessionstarted(self):
        """
        Sets the appearance of the main menu when a session is started
        :return: 
        """
        self.startButton.hide()
        self.currentButton.show()                                           # Hides the start new session button and show the end current session button

    def sessionended(self):
        """
        Sets the appearance of the main menu when no session is running
        :return: 
        """
        self.currentButton.hide()
        self.startButton.show()                                             # Hides the end current session button and shows the start new session button

    def displayWarning(self, display):
        if display:
            self.warningButton.show()
        else:
            self.warningButton.hide()

if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = Mainmenu()
    widget.show()
    sys.exit(app.exec_())
