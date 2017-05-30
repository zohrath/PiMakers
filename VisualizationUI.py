from PyQt5 import QtWidgets
from PyQt5 import QtCore


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
        self.listFilled = False

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
        self.sessionlist.itemClicked.connect(self._sessionactivated)        # Connects the signal emitted when a user selects an item in the list

        scrollablesessions = QtWidgets.QScrollArea()
        scrollablesessions.setWidget(self.sessionlist)                      # Creates a scroll area

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
        self.listFilled = False
        self.backPressed.emit()                                             # Emit the backPressed signal

    def _sessionactivated(self, activatedrow):
        """
        Handles what happens when an item in the session list has been chosen
        :param activatedrow: an int representing the row number of the chosen item
        :return: 
        """
        idandname = QtWidgets.QListWidgetItem(activatedrow).text()
        list = idandname.split()
        if self.listFilled:
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
        self.listFilled = True

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
