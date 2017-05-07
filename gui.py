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
from PyQt5 import QtChart
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FC
from matplotlib.figure import Figure
import matplotlib.dates as matdates
import datetime
import UI
import random



class Main(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.widgetlist = UI.UIpages()
        self.widgetlist.setCurrentIndex(self.widgetlist.mainmenuindex)
        self.setCentralWidget(self.widgetlist)

        self.set_connections()

    def set_connections(self):
        self.widgetlist.widget(self.widgetlist.mainmenuindex).quitSignal.connect(self.close)
        self.widgetlist.widget(self.widgetlist.mainmenuindex).sessionSignal.connect(self.showchannelsettings)
        self.widgetlist.widget(self.widgetlist.mainmenuindex).helpSignal.connect(self.showhelppage)
        self.widgetlist.widget(self.widgetlist.mainmenuindex).currentSignal.connect(self.showcurrentsession)

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

    def showcurrentsession(self):
        self.widgetlist.setCurrentIndex(self.widgetlist.currentsessionindex)


    def startsession(self):
        try:
            self.localdb = configinterface.read_config('config.cfg', 'default')
            self.remotedb = configinterface.read_config('config.cfg', 'remote')
            self.channellist = configinterface.read_config('config.cfg', 'channels')
            self.sessionid = Database.start_new_session(dbvalues=self.localdb, name='placeholdername', channels=self.channellist)
            shouldend = queue.Queue()
            addthread = threading.Thread(group=None, target=self.addloop,
                                         kwargs={'localdb': self.localdb, 'remotedb': self.remotedb, 'sessionid': self.sessionid,
                                                 'shouldend': shouldend})


            self.datadisplay = Datadisplay(self.localdb, self.sessionid)
            self.datadisplay.show()

            addthread.start()
            self.widgetlist.mainmenu.sessionstarted()
            self.widgetlist.setCurrentIndex(self.widgetlist.mainmenuindex)
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

    def addloop(self, localdb, remotedb, sessionid, shouldend):
        try:
            if shouldend.empty() == True:
                list = {}
                for ii in range(1, 4):
                    index = 100 * ii
                    for i in range(1, 21):
                        list[index + 1] = random.randint(1, 100)
            Database.add_to_database(localdb, list, sessionid)
            repeat = threading.Timer(interval=1, function=self.addloop,
                                     kwargs={'localdb': localdb, 'remotedb': remotedb, 'sessionid': sessionid,
                                             'shouldend': shouldend})
            repeat.start()
        except:
            print("oops")

    def messageToUser(self, messagetext):
        message = QtWidgets.QMessageBox()
        message.setMinimumSize(1000, 800)
        message.setText(messagetext)
        message.setStandardButtons(QtWidgets.QMessageBox.Close)
        message.exec_()

class Datadisplay(QtWidgets.QDialog):
    datafetched = QtCore.pyqtSignal()

    def __init__(self, dbvalues, sessionid, parent=None):
        self.dbvalues = dbvalues
        self.sessionid = sessionid
        QtWidgets.QDialog.__init__(self, parent)
        self.plot = Currentsessionplot(dbvalues, sessionid)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(self.plot)
        vbox.addStretch(1)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)
        self.setModal(False)
        self.setLayout(hbox)


class Currentsessionplot(FC):

    def __init__(self, dbvalues, sessionid, parent=None):
        self.dbvalues = dbvalues
        self.sessionid = sessionid


        figure = Figure(figsize=(10, 10), dpi=100)
        self.axes = figure.add_subplot(111)
        self.axes.hold(False)
        #self.compute_initial_figure()

        FC.__init__(self, figure)

        FC.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding,
                         QtWidgets.QSizePolicy.Expanding)

        FC.updateGeometry(self)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_figure)
        self.timer.start(1000)

    def compute_initial_figure(self):
        self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')

    def update_figure(self):
        rawnow = datetime.datetime.now()
        rawstart = rawnow - datetime.timedelta(seconds=100)
        now = rawnow.strftime('%Y-%m-%d %H:%M:%S')
        start = rawstart.strftime('%Y-%m-%d %H:%M:%S')
        values = Database.get_measurements(dbvalues=self.dbvalues, sessionid=self.sessionid, channelid=101,
                                           starttime=start,
                                           endtime=now)
        xaxisvalues = []
        yaxisvalues = []
        for index in values:
            xaxisvalues.append(index[2])
            yaxisvalues.append(index[4])


        #ticks = np.arange(rawstart, rawnow, 5)
        xformater = matdates.DateFormatter('%Y-%m-%d %H:%M:%S')
        self.axes.xaxis.set_major_formatter(xformater)
        #self.axes.set_xticks(ticks)
        self.axes.plot(xaxisvalues, yaxisvalues)
        self.axes.set_xlim([rawstart, rawnow])
        self.draw()
        self.timer.start(1000)














if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.showFullScreen()
    sys.exit(app.exec_())