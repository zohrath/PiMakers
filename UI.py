
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtChart
import configinterface
import sys
import threading
import Database
import configparser
import queue
import pymysql


class VisualiseSession(QtWidgets.QTableWidget):

    backPressed = QtCore.pyqtSignal()
    okPressed = QtCore.pyqtSignal(int, object)
    sessionChosen = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)


        buttons = QtWidgets.QDialogButtonBox()
        okbutton = buttons.addButton('Nästa', buttons.AcceptRole)
        cancelbutton = buttons.addButton('Tillbaka', buttons.RejectRole)
        okbutton.setMinimumSize(300, 100)
        okbutton.clicked.connect(self.nextPage)
        cancelbutton.setMinimumSize(300, 100)
        cancelbutton.clicked.connect(self.goback)
        message = QtWidgets.QLabel("Välj en mätning att visa")

        self.sessionlist = QtWidgets.QListWidget()
        self.channellist = None

        #self.currentchannel = None
        self.currentsession = None

        self.sessionlist.itemActivated.connect(self.sessionactivated)
        self.sessionlist.itemClicked.connect(self.sessionactivated)

        #self.channellist.itemClicked.connect(self.channelactivated)


        self.sessionlist.setMinimumSize(600, 100)
        #self.channellist.setMinimumSize(300, 100)

        scrollablesessions = QtWidgets.QScrollArea()
        #scrollablechannels = QtWidgets.QScrollArea()

        #scrollablechannels.setWidget(self.channellist)
        scrollablesessions.setWidget(self.sessionlist)

        #form = QtWidgets.QFormLayout()
        #form.addRow(scrollablesessions, scrollablechannels)


        vbox = QtWidgets.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(message)
        vbox.addWidget(scrollablesessions)
        vbox.addWidget(buttons)
        vbox.addStretch(2)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def nextPage(self):
        if not self.currentsession == None:
            print(self.currentsession)
            print(self.channellist)
            self.okPressed.emit(self.currentsession, self.channellist)
        else:
            self.messageToUser("Du måste välja en mätning!")




    def goback(self):
        self.backPressed.emit()

    def channelactivated(self, activatedrow):
        idandname = QtWidgets.QListWidgetItem(activatedrow).text()
        list = idandname.split()
        self.currentchannel = int(list[0])

    def sessionactivated(self, activatedrow):
        idandname = QtWidgets.QListWidgetItem(activatedrow).text()
        list = idandname.split()
        self.currentsession = int(list[0])
        self.sessionChosen.emit(int(list[0]))


    def updateSessionList(self, idandnamelist):
        self.sessionlist.clear()
        for item in idandnamelist:
            widgetitem = QtWidgets.QListWidgetItem()
            widgetitem.setText("%d %s" % (item[0], item[1]))
            self.sessionlist.addItem(widgetitem)
            self.sessionlist.itemActivated.emit(widgetitem)
            self.sessionlist.itemClicked.emit(widgetitem)
        self.currentsession = None

    def updateChannelList(self, channellist):
        formattedchannellist = {}
        for index in channellist:
            formattedchannellist[index[0]] = [index[1]]
        self.channellist = formattedchannellist

    def messageToUser(self, messagetext):
        message = QtWidgets.QMessageBox()
        message.setMinimumSize(1000, 800)
        message.setText(messagetext)
        message.setStandardButtons(QtWidgets.QMessageBox.Close)
        message.exec_()





class Channelsettings(QtWidgets.QWidget):
    backPressed = QtCore.pyqtSignal()
    okPressed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.channels = {}

        buttons = QtWidgets.QDialogButtonBox()
        okbutton = buttons.addButton('Nästa', buttons.AcceptRole)
        cancelbutton = buttons.addButton('Tillbaka', buttons.RejectRole)
        okbutton.setMinimumSize(300, 100)
        okbutton.clicked.connect(self.nextPage)
        cancelbutton.setMinimumSize(300, 100)
        cancelbutton.clicked.connect(self.goback)

        tableWidget = self.setchanneltable()
        message = self.setmessage()

        vbox = QtWidgets.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(message)
        vbox.addWidget(tableWidget)
        vbox.addWidget(buttons)
        vbox.addStretch(2)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def goback(self):
        self.backPressed.emit()

    def nextPage(self):
        channellist = {}
        try:
            for i in range(60):
                item = self.tableWidget.item(i, 0)
                if item.checkState() == QtCore.Qt.Checked:
                    channelid = "%d" % (i+1)
                    channelidalias = "%s" % (self.tableWidget.verticalHeaderItem(i).text(),)
                    channelunit = "%s" % (self.tableWidget.item(i, 1).text(),)
                    channeltolerance = "%s" % (self.tableWidget.item(i, 2).text(),)
                    channelname = "%s" % (self.tableWidget.item(i, 3).text(),)
                    channellist[channelid] = str([channelidalias, channelname, channelunit, channeltolerance])

                    float(channeltolerance)

            parser = configparser.ConfigParser()
            with open('config.cfg', 'r+') as r:
                parser.read_file(r)
            parser.remove_section('channels')
            with open('config.cfg', 'w+') as w:
                parser.write(w)
            configinterface.set_config('config.cfg', 'channels', channellist)
            if channellist == {}:
                nochannels = "Du måste välja minst en kanal!"
                self.messageToUser(nochannels)
            else:
                self.okPressed.emit()
        except AttributeError:
            textmissing = "Kanal %s saknar nödvändig information!" % (channelidalias)
            self.messageToUser(textmissing)
        except ValueError:
            wronginputtype = "Kanal %s har fel typ av tolerans, tolerans ska vara ett flyttal t.ex. 42.0" % (channelidalias)
            self.messageToUser(wronginputtype)


    def messageToUser(self, messagetext):
        message = QtWidgets.QMessageBox()
        message.setMinimumSize(1000, 800)
        message.setText(messagetext)
        message.setStandardButtons(QtWidgets.QMessageBox.Close)
        message.exec_()

    def setmessage(self):
        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(18)
        message = QtWidgets.QLabel("Välj vilka kanaler som ska användas i mätningen")
        message.setFont(font)
        return message

    def setchanneltable(self):

        self.tableWidget = QtWidgets.QTableWidget()
        #self.tableWidget.setGeometry(QtCore.QRect(170, 30, 260, 411))
        self.tableWidget.setMinimumSize(600, 400)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setRowCount(60)
        self.tableWidget.setShowGrid(True)



        for i in range(60):
            checkbox = QtWidgets.QTableWidgetItem()
            checkbox.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            checkbox.setText("Använd")
            checkbox.setCheckState(QtCore.Qt.Unchecked)
            font = QtGui.QFont()
            font.setPointSize(12)
            checkbox.setFont(font)
            self.tableWidget.setItem(i, 0, checkbox)
            self.tableWidget.itemClicked.emit(checkbox)
            self.tableWidget.itemActivated.emit(checkbox)

        self.tableWidget.itemClicked.connect(self.checkrow)
        self.tableWidget.itemActivated.connect(self.checkrow)

        index = 100
        for i in range(1, 21):
            vheadertext = "%d" % (i + index)
            vheader = QtWidgets.QTableWidgetItem(vheadertext)
            self.tableWidget.setVerticalHeaderItem(i - 1, vheader)

        index = 200
        for i in range(1, 21):
            vheadertext = "%d" % (i + index)
            vheader = QtWidgets.QTableWidgetItem(vheadertext)
            self.tableWidget.setVerticalHeaderItem(20+i - 1, vheader)

        index = 300
        for i in range(1, 21):
            vheadertext = "%d" % (i + index)
            vheader = QtWidgets.QTableWidgetItem(vheadertext)
            self.tableWidget.setVerticalHeaderItem(40+i - 1, vheader)

        useheader = QtWidgets.QTableWidgetItem("")
        unitheader = QtWidgets.QTableWidgetItem("Enhet")
        toleranceheader = QtWidgets.QTableWidgetItem("Tolerans")
        nameheader = QtWidgets.QTableWidgetItem("Namn")
        self.tableWidget.setHorizontalHeaderItem(0, useheader)
        self.tableWidget.setHorizontalHeaderItem(1, unitheader)
        self.tableWidget.setHorizontalHeaderItem(2, toleranceheader)
        self.tableWidget.setHorizontalHeaderItem(3, nameheader)

        self.tableWidget.verticalHeader().setCascadingSectionResizes(False)
        self.tableWidget.setColumnWidth(0, 110)
        self.tableWidget.setColumnWidth(1, 150)
        self.tableWidget.setColumnWidth(2, 150)
        self.tableWidget.setColumnWidth(3, 150)

        return self.tableWidget

    def checkrow(self, checkbox):
            checked = checkbox.checkState()
            if checked == 0:
                checkbox.setCheckState(2)
            else:
                checkbox.setCheckState(0)



class Databasesettingslayout(QtWidgets.QWidget):

    cancelPressed = QtCore.pyqtSignal()
    okPressed = QtCore.pyqtSignal()

    def __init__(self, message, firsttoggle, secondtoggle, writesection, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.writesection = writesection

        buttons = QtWidgets.QDialogButtonBox()
        okbutton = buttons.addButton('Starta', buttons.AcceptRole)
        cancelbutton = buttons.addButton('Tillbaka', buttons.RejectRole)
        okbutton.setMinimumSize(300, 100)
        okbutton.clicked.connect(self.nextPage)
        cancelbutton.setMinimumSize(300, 100)
        cancelbutton.clicked.connect(self.backToMain)

        font = QtGui.QFont()
        font.setFamily("Ubuntu")
        font.setPointSize(18)
        infostring = QtWidgets.QLabel(message)
        infostring.setFont(font)

        self.databaseform = Databaseform()

        yesbutton = QtWidgets.QRadioButton()
        yesbutton.setText(firsttoggle)
        yesbutton.setAutoExclusive(True)
        yesbutton.setCheckable(True)
        yesbutton.toggled.connect(self.databaseform.useRemote)
        yesbutton.toggled.connect(self.setRemoteTrue)

        nobutton = QtWidgets.QRadioButton()
        nobutton.setText(secondtoggle)
        nobutton.setAutoExclusive(True)
        nobutton.setCheckable(True)
        nobutton.toggled.connect(self.databaseform.dontUseRemote)
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
        vbox.addWidget(self.databaseform)
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
            host = self.databaseform.host.text()
            user = self.databaseform.user.text()
            port = self.databaseform.port.text()
            name = self.databaseform.database.text()
            password = self.databaseform.password.text()
            newremotevalues = {'host': host, 'user': user, 'port': port, 'name': name, 'password': password}
            configinterface.set_config('config.cfg', self.writesection, newremotevalues)

        self.okPressed.emit()

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

        self.helplabel = QtWidgets.QLabel("There's no help. Alex Jones be with ye.")
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
    def __init__(self, parent=None):
        QtWidgets.QStackedWidget.__init__(self, parent)

        self.mainmenu = Mainmenu()
        self.mainmenuindex = self.addWidget(self.mainmenu)
        self.databasesettings = Databasesettingslayout(firsttoggle="Ja",
                                                       secondtoggle="Nej",
                                                       writesection="remote",
                                                       message="Mätvärden kommer att "
                                                               "sparas lokalt, vill du även "
                                                               "spara till en annan databas?")
        self.databasesettingsindex = self.addWidget(self.databasesettings)

        self.helppage = helpPages()
        self.helppageindex = self.addWidget(self.helppage)

        self.channelsettings = Channelsettings()
        self.channelsettingsindex = self.addWidget(self.channelsettings)

        self.current = currentSession()
        self.currentsessionindex = self.addWidget(self.current)

        self.visualizedatabasesettings = Databasesettingslayout(firsttoggle="Annan",
                                                                secondtoggle="Lokal",
                                                                writesection="remotevisual",
                                                                message="Hämta lokala mätvärden, "
                                                                        "eller hämta från en databas?")
        self.visualizedatabasesettingsindex = self.addWidget(self.visualizedatabasesettings)

        self.visualizesessionsettings = VisualiseSession()
        self.visualizesessionsettingsindex = self.addWidget(self.visualizesessionsettings)



class Mainmenu(QtWidgets.QWidget):

    quitSignal = QtCore.pyqtSignal()
    sessionSignal = QtCore.pyqtSignal()
    helpSignal = QtCore.pyqtSignal()
    currentSignal = QtCore.pyqtSignal()
    visualizeSignal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.startButton = QtWidgets.QPushButton("Starta nya mätning")
        self.startButton.setMinimumSize(500, 100)
        self.startButton.clicked.connect(self.newSession)

        self.currentButton = QtWidgets.QPushButton("Avsluta pågående mätning")
        self.currentButton.setMinimumSize(500, 100)
        self.currentButton.clicked.connect(self.currentSession)
        self.currentButton.hide()

        self.visualizeButton = QtWidgets.QPushButton("Visa mätningar")
        self.visualizeButton.setMinimumSize(500, 100)
        self.visualizeButton.clicked.connect(self.visualize)

        self.helpButton = QtWidgets.QPushButton("Hjälp / Inte FAQ")
        self.helpButton.setMinimumSize(500, 100)
        self.helpButton.clicked.connect(self.help)

        self.quitButton = QtWidgets.QPushButton("Avsluta")
        self.quitButton.setMinimumSize(500, 100)
        self.quitButton.clicked.connect(self.quit)


        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.startButton)
        vbox.addWidget(self.currentButton)
        vbox.addWidget(self.visualizeButton)
        vbox.addWidget(self.helpButton)
        vbox.addWidget(self.quitButton)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def visualize(self):
        self.visualizeSignal.emit()

    def quit(self):
        self.quitSignal.emit()

    def newSession(self):
        self.sessionSignal.emit()

    def currentSession(self):
        self.currentSignal.emit()

    def help(self):
        self.helpSignal.emit()

    def sessionstarted(self):
        self.startButton.hide()
        self.currentButton.show()

    def sessionended(self):
        self.currentButton.hide()
        self.startButton.show()



if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = Mainmenu()
    widget.show()
    sys.exit(app.exec_())
