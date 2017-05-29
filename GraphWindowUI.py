import Database
import datetime
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FC
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NT
from matplotlib.figure import Figure
import matplotlib.dates as matdates


class DataDisplay(QtWidgets.QDialog):
    dataContents = QtCore.pyqtSignal()

    def __init__(self, databaseValues, sessionId, channelList, ongoing, timeInterval, parent=None):
        self.databaseValues = databaseValues
        self.sessionId = sessionId
        channelPairs = {}
        for index in channelList:
            displayChannel = channelList[index][0]
            backendChannel = int(index)
            channelPairs[displayChannel] = backendChannel
        self.channelPairs = channelPairs
        self.currentChannels = {}
        self.ongoing = ongoing



        QtWidgets.QDialog.__init__(self, parent)

        self.plot = Currentsessionplot(DatabaseValues=databaseValues,
                                       sessionId=sessionId,
                                       plotChannels=self.currentChannels,
                                       timeIntervall=timeInterval)

        self.toolbar = NT(self.plot, self)

        if self.ongoing:
            self.plot.updateFigure()
        else:
            self.plot.drawFigure()


        font = QtGui.QFont()
        font.setFamily('Ubuntu')
        font.setPointSize(18)

        #self.label = QtWidgets.QLabel("Visar kanal %s" % self.currentChannel)
        #self.label.setFont(font)

        #self.dropDown = QtWidgets.QComboBox()
        #self.dropDown.currentIndexChanged.connect(self.addChannel)
        #for item in self.channelPairs:
        #    self.dropDown.addItem(item)

        exportButton = QtWidgets.QPushButton("Exportera mätvärden")
        exportButton.setMinimumSize(200, 80)
        exportButton.clicked.connect(self.exportValues)

        channelSelection = self.createLists()
        rightHandVBox = QtWidgets.QVBoxLayout()
        rightHandVBox.addLayout(channelSelection)
        rightHandVBox.addWidget(exportButton)


        vbox = QtWidgets.QVBoxLayout()
        vbox.addStretch(1)
        #vbox.addWidget(self.dropDown)
        vbox.addWidget(self.toolbar)
        vbox.addWidget(self.plot)
        vbox.addStretch(1)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addLayout(rightHandVBox)
        hbox.addStretch(1)
        self.setModal(False)
        self.setLayout(hbox)

    def exportValues(self):
        values = self.plot.getValues()

    def addChannel(self):
        channelToAdd = self.dropDown.currentText()
        #newTitle = "Kanal: %s" % self.currentChannel
        #self.plot.channelSwitch(newId=self.channelPairs[self.currentChannel],
        #                        newTitle=newTitle)
        self.plot.addChannel(channelToAdd, self.channelPairs[channelToAdd])


    def closeEvent(self, QCloseEvent):
        self.plot.stopUpdate()

    def createLists(self):

        self.displayList = QtWidgets.QListWidget()
        self.displayList.itemActivated.connect(self.setDisplayListItem)
        self.displayList.itemClicked.connect(self.setDisplayListItem)
        self.displayList.setMinimumSize(200, 300)
        self.channelList = QtWidgets.QListWidget()
        self.channelList.setMinimumSize(200, 300)

        displayScroll = QtWidgets.QScrollArea()
        displayScroll.setMaximumSize(200, 300)
        channelScroll = QtWidgets.QScrollArea()
        channelScroll.setMaximumSize(200, 300)

        displayScroll.setWidget(self.displayList)
        channelScroll.setWidget(self.channelList)

        self.channelFilled = False

        for index in self.channelPairs:
            item = QtWidgets.QListWidgetItem()
            item.setText(index)
            self.channelList.addItem(item)
            self.channelList.itemActivated.connect(self.setChannelListItem)
            self.channelList.itemClicked.connect(self.setChannelListItem)

        self.channelFilled = True

        self.displayButton = QtWidgets.QPushButton("<")
        self.removedisplayButton = QtWidgets.QPushButton(">")


        self.displayButton.clicked.connect(self.addToDisplay)
        self.removedisplayButton.clicked.connect(self.removeFromDisplay)


        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(self.displayButton)
        vlayout.addWidget(self.removedisplayButton)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(displayScroll)
        layout.addLayout(vlayout)
        layout.addWidget(channelScroll)

        return layout

    def setChannelListItem(self, item):
        if self.channelFilled:
            self.channelList.setCurrentItem(item)

    def setDisplayListItem(self, item):
        self.displayList.setCurrentItem(item)

    def addToDisplay(self):
        row = self.channelList.currentRow()
        item = self.channelList.takeItem(row)
        self.displayList.addItem(item)
        key = item.text()
        self.plot.addChannel(key, self.channelPairs[key])

        if self.ongoing == True:
            pass
            self.plot.updateFigure()
        else:
            self.plot.drawFigure()

    def removeFromDisplay(self):
        row = self.displayList.currentRow()
        item = self.displayList.takeItem(row)
        self.channelList.addItem(item)
        key = item.text()
        self.plot.removeChannel(key, self.channelPairs[key])

        if self.ongoing == True:
            pass
            self.plot.updateFigure()
        else:
            self.plot.drawFigure()


class Currentsessionplot(FC):

    def __init__(self, DatabaseValues, sessionId, plotChannels, timeIntervall):
        self.databaseValues = DatabaseValues
        self.sessionId = sessionId
        self.plotChannels = plotChannels
        self.timeInterval = timeIntervall
        #figureTitle = "Kanal: %s" % figureTitle
        self.plotChannelValues = {}

        self.figure = Figure(figsize=(10, 10), dpi=100)
        #self.figure.suptitle(figureTitle)
        self.axes = self.figure.add_subplot(111)
        self.axes.xaxis_date()
       # self.axes.hold(False)


        FC.__init__(self, self.figure)

        FC.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding,
                         QtWidgets.QSizePolicy.Expanding)

        FC.updateGeometry(self)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateFigure)

    def stopUpdate(self):
        self.timer.stop()

    def addChannel(self, key, value):
        self.plotChannels[key] = value

    def channelSwitch(self, newId, newTitle):
        self.timer.stop()
        self.plotChannel = newId
        self.figure.clear()
        self.axes = self.figure.add_subplot(111)
        self.figure.suptitle(newTitle, fontsize=20)
        self.axes.hold(False)

    def removeChannel(self, key, value):
        self.plotChannels.pop(key, None)

    def updateFigure(self):
        rawNow = datetime.datetime.now()
        rawStart = rawNow - datetime.timedelta(seconds=100)
        now = rawNow.strftime('%Y-%m-%d %H:%M:%S')
        start = rawStart.strftime('%Y-%m-%d %H:%M:%S')

        self.axes.clear()

        print(self.plotChannels)
        for index in self.plotChannels:
            values = Database.getMeasurements(databaseValues=self.databaseValues,
                                          sessionId=self.sessionId,
                                          channelId=self.plotChannels[index],
                                          startTime=start,
                                          endTime=now)
            xAxisValues = []
            yAxisValues = []
            for index2 in values:
                xAxisValues.append(index2[2])
                yAxisValues.append(index2[4])
            self.plotChannelValues[index] = [xAxisValues, yAxisValues]

        print(self.plotChannelValues)
        for index3 in self.plotChannelValues:
            self.axes.plot(self.plotChannelValues[index3][0], self.plotChannelValues[index3][1], label=index3)


        #addToX = numpy.asarray(xAxisValues)
        #addToY = numpy.asarray(yAxisValues)

        print("UPDATE FIGURE IS STILL RUNNING")

        #ticks = np.arange(rawstart, rawnow, 5)
        major = matdates.DateFormatter('%Y-%m-%d %H:%M:%S')
        minor = matdates.DateFormatter('%Y-%m-%d')
        self.axes.xaxis.set_major_formatter(major)
        self.axes.xaxis.set_minor_formatter(minor)
        #self.axes.set_xticks(ticks)

        self.axes.set_xlim([rawStart, rawNow])
        self.axes.legend()

        for tick in self.axes.get_xticklabels():
            tick.set_rotation(15)                           # change this
        self.draw()
        self.timer.start(1000 * self.timeInterval)

    def drawFigure(self):

        self.axes.clear()
        for index in self.plotChannels:
            values = Database.getMeasurements(databaseValues=self.databaseValues,
                                            sessionId=self.sessionId,
                                            channelId=self.plotChannels[index],
                                            startTime=None,
                                            endTime=None)

            xAxisValues = []
            yAxisValues = []
            for index2 in values:
                xAxisValues.append(index2[2])
                yAxisValues.append(index2[4])

            self.axes.plot(xAxisValues, yAxisValues, label=index)

        self.axes.legend()
        # ticks = np.arange(rawstart, rawnow, 5)
        xformater = matdates.DateFormatter('%Y-%m-%d %H:%M:%S')
        major = matdates.DateFormatter('%H:%M:%S')
        minor = matdates.DateFormatter('%Y-%m-%d')
        self.axes.xaxis.set_major_formatter(xformater)
        self.axes.xaxis.set_minor_formatter(minor)

        #self.axes.xaxis.set_major_formatter(xformater)
        # self.axes.set_xticks(ticks)

        #self.axes.set_xlim([rawstart, rawnow])
        for tick in self.axes.get_xticklabels():
            tick.set_rotation(15)  # change this
        self.draw()

    def getValues(self):
        print("Hej")
