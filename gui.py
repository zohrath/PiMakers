import sys
import threading
import pymysql
import configinterface
import numpy as np
import configparser
import Database
import queue
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtChart
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FC
from matplotlib.figure import Figure
import matplotlib.dates as matdates
import datetime
import UI
import random




class Main(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        self.sessionrunning = False

        QtWidgets.QMainWindow.__init__(self, parent)
        self.widgetlist = UI.UIpages()
        self.widgetlist.setCurrentIndex(self.widgetlist.mainmenuindex)
        self.setCentralWidget(self.widgetlist)
        self.shouldend = threading.Event()
        self.set_connections()

    def set_connections(self):
        self.widgetlist.widget(self.widgetlist.mainmenuindex).quitSignal.connect(self.quit)
        self.widgetlist.widget(self.widgetlist.mainmenuindex).sessionSignal.connect(self.showchannelsettings)
        self.widgetlist.widget(self.widgetlist.mainmenuindex).helpSignal.connect(self.showhelppage)
        self.widgetlist.widget(self.widgetlist.mainmenuindex).currentSignal.connect(self.endcurrentsession)

        self.widgetlist.widget(self.widgetlist.databasesettingsindex).cancelPressed.connect(self.showchannelsettings)
        self.widgetlist.widget(self.widgetlist.databasesettingsindex).okPressed.connect(self.startsession)

        self.widgetlist.widget(self.widgetlist.helppageindex).cancelPressed.connect(self.showmainmenu)
        self.widgetlist.widget(self.widgetlist.currentsessionindex).cancelPressed.connect(self.showmainmenu)

        self.widgetlist.widget(self.widgetlist.channelsettingsindex).backPressed.connect(self.showmainmenu)
        self.widgetlist.widget(self.widgetlist.channelsettingsindex).okPressed.connect(self.showdatabasesettings)




    def showdatabasesettings(self):
        self.widgetlist.setCurrentIndex(self.widgetlist.databasesettingsindex)

    def showhelppage(self):
        self.widgetlist.setCurrentIndex(self.widgetlist.helppageindex)

    def showmainmenu(self):
        self.widgetlist.setCurrentIndex(self.widgetlist.mainmenuindex)

    def showchannelsettings(self):
        self.widgetlist.setCurrentIndex(self.widgetlist.channelsettingsindex)

    def quit(self):
        if self.sessionrunning:
            self.endcurrentsession()
        self.close()

    def endcurrentsession(self):
        self.shouldend.set()
        self.widgetlist.mainmenu.sessionended()
        Database.end_current_session(self.localdb, self.sessionid)
        self.datadisplay.close()
        self.sessionrunning = False
        self.showmainmenu()




    def startsession(self):
        try:
            self.localdb = configinterface.read_config('config.cfg', 'default')
            self.remotedb = configinterface.read_config('config.cfg', 'remote')
            self.channellist = configinterface.read_config('config.cfg', 'channels')
            self.sessionid = Database.start_new_session(dbvalues=self.localdb, name='placeholdername', channels=self.channellist)

            #self.remotesessionid = Database.start_new_session(dbvalues=self.remotedb, name='Placeholdername', channels=self.channellist)
            addthread = Addthread(localdb=self.localdb, remotedb=self.remotedb, sessionid=self.sessionid, shouldend=self.shouldend, channellist=self.channellist)


            self.datadisplay = Datadisplay(self.localdb, self.sessionid, self.channellist)
            self.datadisplay.show()

            addthread.start()
            self.widgetlist.mainmenu.sessionstarted()
            self.widgetlist.setCurrentIndex(self.widgetlist.mainmenuindex)
            self.sessionrunning = True
        except pymysql.err.Error as E:
            if E.args[0] == 1045:
                message = "Anslutning nekad, se över port, användare och lösenord"
                self.messageToUser(message)
            if E.args[0] == 2003:
                message = "Kunde inte anluta till host: '%s'" % (self.localdb['host'])
                self.messageToUser(message)
        except ValueError as V:
            wrongporttype = "Fel typ för 'Port', ett heltal förväntas"
            self.messageToUser(wrongporttype)


    def messageToUser(self, messagetext):
        message = QtWidgets.QMessageBox()
        message.setMinimumSize(1000, 800)
        message.setText(messagetext)
        message.setStandardButtons(QtWidgets.QMessageBox.Close)
        message.exec_()


class Addthread(threading.Thread):

    def __init__(self, localdb, remotedb, sessionid, channellist, shouldend):
        self.localdb = localdb
        self.remotedb = remotedb
        self.sessionid = sessionid
        self.shouldend = shouldend
        self.channellist = channellist
        threading.Thread.__init__(self)

    def run(self):

        while not self.shouldend.wait(1.0):                             #change hard coded wait
            list = {}
            for item in self.channellist:
                id = int(item)
                list[id] = random.randint(1, 100)
            print(list)
            Database.add_to_database(self.localdb, list, self.sessionid)
        self.shouldend.clear()


class Addremotethread(threading.Thread):

    def __init__(self, localdb, remotedb, channellist, shouldend):
        self.localdb = localdb
        self.remotedb = remotedb
        self.sessionid = sessionid
        self.shouldend = shouldend
        self.channellist = channellist
        threading.Thread.__init__(self)

    def run(self):

        while not self.shouldend.wait(10.0)                          #change hard coded wait




class Datadisplay(QtWidgets.QDialog):
    datafetched = QtCore.pyqtSignal()

    def __init__(self, dbvalues, sessionid, channellist, parent=None):
        self.dbvalues = dbvalues
        self.sessionid = sessionid
        self.channellist = channellist
        self.displaychannel = int(next(iter(self.channellist)))

        QtWidgets.QDialog.__init__(self, parent)
        self.plot = Currentsessionplot(dbvalues, sessionid, self.displaychannel)

        formlayout = QtWidgets.QFormLayout()

        font = QtGui.QFont()
        font.setFamily('Ubuntu')
        font.setPointSize(18)

        self.label = QtWidgets.QLabel("Visar kanal %d" % self.displaychannel)
        self.label.setFont(font)

        self.dropdown = QtWidgets.QComboBox()
        self.dropdown.currentIndexChanged.connect(self.switchchannel)
        for item in channellist:
            self.dropdown.addItem(item)

        formlayout.insertRow(0, self.label, self.dropdown)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(formlayout)
        vbox.addWidget(self.plot)
        vbox.addStretch(1)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)
        self.setModal(False)
        self.setLayout(hbox)

    def switchchannel(self):
        self.displaychannel = int(self.dropdown.currentText())
        print(self.displaychannel)
        self.label.setText("Visar kanal %d" % self.displaychannel)
        self.plot.channelswitch(self.displaychannel)


class Currentsessionplot(FC):

    def __init__(self, dbvalues, sessionid, displaychannel):
        self.dbvalues = dbvalues
        self.sessionid = sessionid
        self.displaychannel = displaychannel


        self.figure = Figure(figsize=(10, 10), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.axes.hold(False)


        FC.__init__(self, self.figure)

        FC.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding,
                         QtWidgets.QSizePolicy.Expanding)

        FC.updateGeometry(self)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_figure)
        self.update_figure()

    def channelswitch(self, newid):
        self.timer.stop()
        self.displaychannel = newid
        self.figure.clear()
        self.axes = self.figure.add_subplot(111)
        self.axes.hold(False)
        self.update_figure()


    def update_figure(self):
        rawnow = datetime.datetime.now()
        rawstart = rawnow - datetime.timedelta(seconds=100)
        now = rawnow.strftime('%Y-%m-%d %H:%M:%S')
        start = rawstart.strftime('%Y-%m-%d %H:%M:%S')
        values = Database.get_measurements(dbvalues=self.dbvalues, sessionid=self.sessionid, channelid=self.displaychannel,
                                           starttime=start,
                                           endtime=now)
        xaxisvalues = []
        yaxisvalues = []
        for index in values:
            xaxisvalues.append(index[2])
            yaxisvalues.append(index[4])


        #ticks = np.arange(rawstart, rawnow, 5)
        xformater = matdates.DateFormatter('%H:%M:%S')
        self.axes.xaxis.set_major_formatter(xformater)
        #self.axes.set_xticks(ticks)
        self.axes.plot(xaxisvalues, yaxisvalues)
        self.axes.set_xlim([rawstart, rawnow])
        for tick in self.axes.get_xticklabels():
            tick.set_rotation(20)                           # change this
        self.draw()
        self.timer.start(1000)














if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.showFullScreen()
    sys.exit(app.exec_())