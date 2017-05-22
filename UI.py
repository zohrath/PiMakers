from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from MainMenuUI import Mainmenu
from VisualizationUI import Visualizationsettings
from MeasuringSessionUI import Channelsettings
import configInterface
import sys

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

    def nextPage(self):
        """
        Handles what happens when the next button is pressed 
        :return: 
        """
        errorocurred = False
        if self.remote:                                                     # If a remote database should be used
            host = self.databaseform.host.text()
            user = self.databaseform.user.text()
            port = self.databaseform.port.text()
            name = self.databaseform.database.text()
            password = self.databaseform.password.text()

            if not host:
                message = "Du måste ange en host"
                self._messageToUser(messagetext=message, closebuttontext="Stäng")
                errorocurred = True
            elif not user:
                message = "Du måste ange en användare"
                self._messageToUser(messagetext=message, closebuttontext="Stäng")
                errorocurred = True
            elif not port:
                message = "Du måste ange en port"
                self._messageToUser(messagetext=message, closebuttontext="Stäng")
                errorocurred = True
            elif not name:
                message = "Du måste ange en databas"
                self._messageToUser(messagetext=message, closebuttontext="Stäng")
                errorocurred = True
            elif not password:
                message = "Du måste ange ett lösenord"
                self._messageToUser(messagetext=message, closebuttontext="Stäng")
                errorocurred = True
            else:
                newremotevalues = {'host': host, 'user': user, 'port': port, 'name': name, 'password': password}
                configInterface.setConfig('config.cfg',
                                          self.writesection,
                                          newremotevalues)                     # Write the database settings to the configfile

        if not errorocurred:
            self.okPressed.emit()                                               # Emit the okPressed signal

    def useRemote(self):
        use = self.remote
        return use

class Databaseform(QtWidgets.QWidget):

    def __init__(self, parent=None):
        """
        Creates a new instance of a Databaseform page
        :param parent: 
        """
        QtWidgets.QWidget.__init__(self, parent)

        font = self.createFormFont()

        self.host = QtWidgets.QLineEdit()
        self.host.setMinimumSize(200, 50)                                   # Creates the host input field
        self.host.setFont(font)
        self.hosttext = ""
        self.hostlabel = QtWidgets.QLabel("Host")
        self.hostlabel.setFont(font)
        self.hostlabel.setMinimumSize(50, 50)

        self.port = QtWidgets.QLineEdit()
        self.port.setMinimumSize(200, 50)
        self.port.setFont(font)
        self.porttext = ""
        self.portlabel = QtWidgets.QLabel("Port")
        self.portlabel.setFont(font)
        self.portlabel.setMinimumSize(50, 50)

        self.database = QtWidgets.QLineEdit()
        self.database.setMinimumSize(200, 50)
        self.database.setFont(font)
        self.databasetext = ""
        self.databaselabel = QtWidgets.QLabel("Database name")
        self.databaselabel.setFont(font)
        self.databaselabel.setMinimumSize(50, 50)

        self.user = QtWidgets.QLineEdit()
        self.user.setMinimumSize(200, 50)
        self.user.setFont(font)
        self.usertext = ""
        self.userlabel = QtWidgets.QLabel("User")
        self.userlabel.setFont(font)
        self.userlabel.setMinimumSize(50, 50)

        self.password = QtWidgets.QLineEdit()
        self.password.setMinimumSize(200, 50)
        self.password.setFont(font)
        self.passwordtext = ""
        self.password.setEchoMode(self.password.Password)
        self.passwordlabel = QtWidgets.QLabel("Password")
        self.passwordlabel.setFont(font)
        self.passwordlabel.setMinimumSize(50, 50)

        hasprevious = configInterface.hasSection('config.cfg', 'remote')

        if hasprevious:
            previous_remote_database = \
                configInterface.readConfig('config.cfg', 'remote')         # Reads previously used database configs
            self.hosttext = previous_remote_database['host']
            self.porttext = previous_remote_database['port']
            self.usertext = previous_remote_database['user']
            self.databasetext = previous_remote_database['name']
            self.passwordtext = previous_remote_database['password']


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


class currentSession(QtWidgets.QWidget):                                    # Not currently used

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

    cancelPressed = QtCore.pyqtSignal()                                     # Custom pyqt signal

    def __init__(self, parent=None):
        """
        Initializes a new instance of a help page
        :param parent: 
        """
        QtWidgets.QWidget.__init__(self, parent)


        buttons = QtWidgets.QDialogButtonBox()
        cancelbutton = buttons.addButton('Tillbaka', buttons.RejectRole)    # Creates the back button
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
        hbox.addLayout(vbox)                                                # Creates the page layout
        hbox.addStretch(1)

        self.setLayout(hbox)                                                # Sets the page layout

    def backToMain(self):
        self.cancelPressed.emit()


class UIpages(QtWidgets.QStackedWidget):
    def __init__(self):
        """
        Initilizes a new instance of a UIpages object, i.e. 
        a stacked widget containing the UI pages of the application
        """
        QtWidgets.QStackedWidget.__init__(self)

        self.mainMenu = Mainmenu()
        self.mainMenuIndex = self.addWidget(self.mainMenu)                  # Creates a main menu page and stores its index

        self.databasesettings = Databasesettings(firsttoggle="Ja",
                                                       secondtoggle="Nej",
                                                       writesection="remote",
                                                       message="Mätvärden kommer att "
                                                               "sparas lokalt, vill du även "
                                                               "spara till en annan databas?")
        self.databaseSettingsIndex = self.addWidget(self.databasesettings)  # Creates a databasesettings page and stores its index

        self.helppage = helpPages()
        self.helpPageIndex = self.addWidget(self.helppage)                  # Creates a help page and stores its index

        self.channelsettings = Channelsettings()
        self.channelSettingsIndex = self.addWidget(self.channelsettings)    # Creates a Channelsettings page and stores its index

        self.current = currentSession()
        self.currentSessionIndex = self.addWidget(self.current)             # Creates a currentsession page and stores its index

        self.visualizedatabasesettings = Databasesettings(firsttoggle="Annan",
                                                                secondtoggle="Lokal",
                                                                writesection="remotevisual",
                                                                message="Hämta lokala mätvärden, "
                                                                        "eller hämta från en databas?")
        self.visualizeDatabaseSettingsIndex = \
            self.addWidget(self.visualizedatabasesettings)                  # Creates a Databasesettings page and stores its index

        self.visualizesessionsettings = Visualizationsettings()
        self.visualizeSessionSettingsIndex = \
            self.addWidget(self.visualizesessionsettings)                   # Creates a Visualizationsettings page and stores its idnex





if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = Mainmenu()
    widget.show()
    sys.exit(app.exec_())
