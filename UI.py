
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
import configinterface
import sys



class Databasesettingslayout(QtWidgets.QWidget):

    cancelPressed = QtCore.pyqtSignal()
    okPressed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)


        buttons = QtWidgets.QDialogButtonBox()
        okbutton = buttons.addButton('Nästa', buttons.AcceptRole)
        cancelbutton = buttons.addButton('Tillbaka', buttons.RejectRole)
        okbutton.setMinimumSize(300, 100)
        okbutton.clicked.connect(self.nextPage)
        cancelbutton.setMinimumSize(300, 100)
        cancelbutton.clicked.connect(self.backToMain)

        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(18)
        infostring = QtWidgets.QLabel("Mätvärden kommer att sparas lokalt, vill du även spara till en annan databas?")
        infostring.setFont(font)

        databaseform = Databaseform()

        yesbutton = QtWidgets.QRadioButton()
        yesbutton.setText("Ja")
        yesbutton.setAutoExclusive(True)
        yesbutton.setCheckable(True)
        yesbutton.toggled.connect(databaseform.useRemote)
        yesbutton.toggled.connect(self.setRemoteTrue)

        nobutton = QtWidgets.QRadioButton()
        nobutton.setText("Nej")
        nobutton.setAutoExclusive(True)
        nobutton.setCheckable(True)
        nobutton.toggled.connect(databaseform.dontUseRemote)
        nobutton.toggled.connect(self.setRemoteFalse)
        nobutton.setChecked(True)

        buttonlayout = QtWidgets.QHBoxLayout()
        buttonlayout.addWidget(yesbutton)
        buttonlayout.addWidget(nobutton)

        buttongroup = QtWidgets.QWidget()
        buttongroup.setLayout(buttonlayout)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(infostring)
        vbox.addWidget(buttongroup)
        vbox.addWidget(databaseform)
        vbox.addWidget(buttons)
        vbox.addStretch(2)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def setRemoteTrue(self):
        self.remote = True

    def setRemoteFalse(self):
        self.remote = False

    def backToMain(self):
        self.cancelPressed.emit()

    def nextPage(self):
        if self.remote:
            configinterface.set_config('config.cfg', )
        self.okPressed.emit()



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


class UIpages(QtWidgets.QStackedWidget):
    def __init__(self, parent=None):
        QtWidgets.QStackedWidget.__init__(self, parent)

        mainmenu = Mainmenu()
        self.mainmenuindex = self.addWidget(mainmenu)

        databasesettings = Databasesettingslayout()
        self.databasesettingsindex = self.addWidget(databasesettings)

        channelsettings = Channelsettings()
        self.channelsettingsindex = self.addWidget(channelsettings)




class Channelsettings(QtWidgets.QWidget):

    backPressed = QtCore.pyqtSignal()
    okPressed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.channels = {}

        buttons = QtWidgets.QDialogButtonBox()
        okbutton = buttons.addButton('Starta', buttons.AcceptRole)
        cancelbutton = buttons.addButton('Tillbaka', buttons.RejectRole)
        okbutton.setMinimumSize(300, 100)
        #okbutton.clicked.connect(self.nextPage)
        cancelbutton.setMinimumSize(300, 100)
        cancelbutton.clicked.connect(self.goback)


        message = self.setmessage()
        channellist = self.setchannellist()

        vbox = QtWidgets.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(message)
        vbox.addWidget(channellist)
        vbox.addWidget(buttons)
        vbox.addStretch(2)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def goback(self):
        self.backPressed.emit()

    def setmessage(self):
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(18)
        message = QtWidgets.QLabel("Välj vilka kanaler som ska användas i mätningen")
        message.setFont(font)
        return message

    def setchannellist(self):

        table = QtWidgets.QTableWidget()
        table.setRowCount(20)
        table.setColumnCount(4)


        useheader = QtWidgets.QTableWidgetItem("Använd:")
        unitheader = QtWidgets.QTableWidgetItem("Enhet")
        toleranceheader = QtWidgets.QTableWidgetItem("Tolerans")
        nameheader = QtWidgets.QTableWidgetItem("Namn")
        table.setHorizontalHeaderItem(0, useheader)
        table.setHorizontalHeaderItem(1, unitheader)
        table.setHorizontalHeaderItem(2, toleranceheader)
        table.setHorizontalHeaderItem(3, nameheader)

        for i in range(0, 21):
            vheadertext = "%d" % (i+101,)
            vheader = QtWidgets.QTableWidgetItem(vheadertext)
            table.setVerticalHeaderItem(i, vheader)
            button = QtWidgets.QCheckBox()

            table.setCellWidget(i, 0, button)

        return table


class Mainmenu(QtWidgets.QWidget):

    quitSignal = QtCore.pyqtSignal()
    sessionSignal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        startButton = QtWidgets.QPushButton("Starta ny mätning")
        startButton.setMinimumSize(500, 200)
        startButton.clicked.connect(self.newSession)

        visualizeButton = QtWidgets.QPushButton("Visa mätningar")
        visualizeButton.setMinimumSize(500, 200)

        quitButton = QtWidgets.QPushButton("Avsluta")
        quitButton.setMinimumSize(500, 200)
        quitButton.clicked.connect(self.quit)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(startButton)
        vbox.addWidget(visualizeButton)
        vbox.addWidget(quitButton)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def quit(self):
        self.quitSignal.emit()

    def newSession(self):
        self.sessionSignal.emit()


if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = Mainmenu()
    widget.show()
    sys.exit(app.exec_())
