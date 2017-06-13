from PyQt5 import QtWidgets, QtCore, QtGui


import configInterface
import configparser
import Communication
import inspect

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
        okbutton.setMinimumSize(200, 80)
        okbutton.clicked.connect(self._nextPage)
        cancelbutton.setMinimumSize(200, 80)
        cancelbutton.clicked.connect(self._goback)                          # Creates the buttons of the page

        self._setchanneltable()                                             # Cretes the table of channels displayed on the page
        channelmessage = \
            self._setmessage("Välj vilka kanaler "
                             "som ska användas i mätningen")                # Creates the message displayed on top of the page

        input = self.sessioninfo()                                          # Creates session information inputs




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
        channellistforwrite = {}
        try:
            for i in range(60):                                             # For each row in the table
                item = self.tableWidget.item(i, 0)
                if item.checkState() == QtCore.Qt.Checked:                  # If a channel has been chosen
                    channelid = "%d" % (i+1)
                    channelidalias = "%s" % (self.tableWidget.verticalHeaderItem(i).text(),)
                    channelunit = "%s" % (self.tableWidget.item(i, 1).text(),)
                    channeltolerance = "%s" % (self.tableWidget.item(i, 2).text(),)
                    channelname = "%s" % (self.tableWidget.item(i, 3).text(),)

                    channelstorhet = "%s" % (self.tableWidget.cellWidget(i, 4).currentText())
                    if channelname == "":
                        raise AttributeError
                    if channelname in self.channellist:
                        exceptionraised = True
                        duplicatenames = "Kanalnamn måste vara unika!"
                        self._messageToUser(duplicatenames,
                                            closebuttontext="Stäng")
                        break

                    self.channellist[channelname] = \
                        [channelid,
                        channelunit,
                        channeltolerance,
                        channelidalias,
                        channelstorhet]                                   # Collect channel information and add it to the list of channels
                    channellistforwrite[channelname] = \
                        str([channelid,
                         channelunit,
                         channeltolerance,
                         channelidalias,
                         channelstorhet])

                    float(channeltolerance)                                 # Raises a ValueError if channeltolerance can not be converted to float

            self.sessionname = self.nameinput.text()
            self.sessionintervall = self.intervallinput.text()

            try:
                self.sessionintervall = float(self.sessionintervall)        # Check if intervall is correct type
            except ValueError:
                exceptionraised = True
                wrongintervalltype = "Tidsintervall måste anges som ett nummer"
                self._messageToUser(wrongintervalltype,
                                    closebuttontext="Stäng")                # If not, prompt user with error message

            if not self.sessionname:                                        # If no text in name field
                noname = "Du måste namnge mätningen"
                self._messageToUser(noname,
                                    closebuttontext="Stäng")                # Prompt user with a message

            elif not self.sessionintervall:                                 # else if ni text in intervall field
                nointervall = "Du måste ange ett tidsintervall"
                self._messageToUser(nointervall,
                                    closebuttontext="Stäng")                # Prompt user with a message

            elif self.channellist == {}:                                    # If no channel has been selected
                nochannels = "Du måste välja minst en kanal!"
                self._messageToUser(nochannels,
                                    closebuttontext="Stäng")                # Prompt the user with a message
            elif not exceptionraised:
                self.okPressed.emit()                                       # If no error, emit signal to change page

            parser = configparser.ConfigParser()
            with open('config.cfg', 'r+') as r:                             # Reads from the configfile
                parser.read_file(r)
                parser.remove_section('channels')                           # Removes the previous channels
            with open('config.cfg', 'w+') as w:
                parser.write(w)                                             # Writes the removal to the file
            configInterface.setConfig('config.cfg',
                                       'channels',
                                      channellistforwrite)                 # Writes the new channels to the configfile

        except AttributeError:                                              # A channel is missing some input
            textmissing = \
                "Kanal %s saknar nödvändig information!" % (channelidalias)
            self._messageToUser(textmissing,
                                closebuttontext="Stäng")                    # Tell the user which channel is missing input
            self.channellist = {}

        except ValueError:                                                  # Wrong type has been inputted into the tolerance field
            wronginputtype = \
                "Kanal %s har fel typ av tolerans, " \
                "tolerans ska vara ett flyttal t.ex. 42.0" \
                % (channelidalias)
            self._messageToUser(wronginputtype,
                                closebuttontext="Stäng")                    # Tell the user which channel has wrong type of tolerance
            self.channellist = {}


    def _messageToUser(self, messagetext, closebuttontext):
        """
        Prompts the user with a messagebox containing a given message
        :param messagetext: A string representing the message to be displayed in the window
        :param closebuttontext: A string that will be displayed on the button used to close the window
        :return: 
        """
        message = QtWidgets.QMessageBox()
        message.setMinimumSize(1000, 800)
        message.setText(messagetext)                                        # Creates the message window
        closebutton = message.addButton(closebuttontext,
                                        QtWidgets.QMessageBox.YesRole)
        closebutton.clicked.connect(message.close)                          # Configures the button
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
        self.tableWidget.setMinimumSize(400, 200)
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setRowCount(60)
        self.tableWidget.setShowGrid(True)                                  # Creates the actual table

        list = self.createUnitList()

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
            dropdown = QtWidgets.QComboBox()
            for index in list:
                dropdown.addItem(index)
            self.tableWidget.setCellWidget(i, 4, dropdown)

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
        storhetheader = QtWidgets.QTableWidgetItem("Storhet")

        self.tableWidget.setHorizontalHeaderItem(0, useheader)
        self.tableWidget.setHorizontalHeaderItem(1, unitheader)
        self.tableWidget.setHorizontalHeaderItem(2, toleranceheader)
        self.tableWidget.setHorizontalHeaderItem(3, nameheader)             # Adds a label to each column in the table
        self.tableWidget.setHorizontalHeaderItem(4, storhetheader)

        self.tableWidget.verticalHeader().setCascadingSectionResizes(True)
        self.tableWidget.setColumnWidth(0, 120)
        self.tableWidget.setColumnWidth(1, 100)
        self.tableWidget.setColumnWidth(2, 100)
        self.tableWidget.setColumnWidth(3, 100)                             # Sets the sizes of the columns
        self.tableWidget.setColumnWidth(4, 100)

    def createUnitList(self):

        functionList = self.filterList()
        return functionList


    def filterList(self):
        list = []
        temp = inspect.getmembers(Communication, inspect.isfunction)

        for index in temp:
            list.append(index[0])

        return list

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

