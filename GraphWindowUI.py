import Database
import datetime
import csv
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FC
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NT
from matplotlib.figure import Figure
import matplotlib.dates as matdates


class DataDisplay(QtWidgets.QDialog):
    dataContents = QtCore.pyqtSignal()

    def __init__(self, databaseValues, sessionId, channelList, ongoing, timeInterval, parent=None):
        self.databaseValues = databaseValues
        self.sessionId = sessionId
        self.channelPairs = channelList

        self.currentChannels = {}
        self.ongoing = ongoing

        QtWidgets.QDialog.__init__(self, parent)

        self.plot = Currentsessionplot(DatabaseValues=databaseValues,
                                       sessionId=sessionId,
                                       plotChannels=self.currentChannels,
                                       timeIntervall=timeInterval)

        self.toolbar = Toolbar(self.plot, self.ongoing)


        if self.ongoing:
            self.plot.updateFigure()
        else:
            self.plot.drawFigure()


        font = QtGui.QFont()
        font.setFamily('Ubuntu')
        font.setPointSize(18)

        exportButton = QtWidgets.QPushButton("Exportera mätvärden")
        exportButton.setMinimumSize(200, 80)
        exportButton.clicked.connect(self.createSaveDialog)

        channelSelection = self.createLists()
        rightHandVBox = QtWidgets.QVBoxLayout()
        rightHandVBox.addLayout(channelSelection)
        rightHandVBox.addWidget(exportButton)


        vbox = QtWidgets.QVBoxLayout()
        vbox.addStretch(1)
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
        saveFile = str(self.fileselector.selectedFiles()[0])
        channels = self.plot.getValues()
        if channels:
            listKey = next(iter(channels.keys()))
            numberOfValues = len(channels[listKey])
            headers = ['Kanal', 'Enhet', 'Tolerans', 'Mätvärde', '']
            with open(saveFile, 'w', newline='') as file:
                writer = csv.writer(file, dialect='excel')
                writer.writerow(['Tidsstämpel', ''] + headers * len(channels))
            for index in range(numberOfValues):
                timestamp = channels[listKey][index][0]
                valueList = []
                for channel in channels:
                    if index < 1:
                        valueList.append('')
                        valueList.append(channel)
                        valueList.append(self.channelPairs[channel][1])
                        valueList.append(self.channelPairs[channel][2])
                    else:
                        valueList.append('')
                        valueList.append('')
                        valueList.append('')
                        valueList.append('')
                    valueList.append(channels[channel][index][1])
                with open(saveFile, 'a', newline='') as file:
                    writer = csv.writer(file, dialect='excel')
                    writer.writerow([timestamp, ] + valueList)



    def createSaveDialog(self):
        self.fileselector = QtWidgets.QFileDialog()
        self.fileselector.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        self.fileselector.setOption(QtWidgets.QFileDialog.ShowDirsOnly)
        self.fileselector.setNameFilter("(*.csv)")
        self.fileselector.setDefaultSuffix("csv")
        self.fileselector.fileSelected.connect(self.fileselector.selectFile)
        self.fileselector.urlSelected.connect(self.fileselector.selectUrl)
        self.fileselector.accepted.connect(self.exportValues)
        self.fileselector.show()




    def addChannel(self):
        channelToAdd = self.dropDown.currentText()
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
        self.mpl_connect('button_press_event', self.onClick)

    def onClick(self, event):
        if self.toolbar._active is not None:
            self.timer.stop()

    def timerIsActive(self):
        return self.timer.isActive()

    def stopUpdate(self):
        self.timer.stop()

    def startTimer(self):
        self.timer.start()

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
        rawStart = rawNow - datetime.timedelta(seconds=self.timeInterval*100)
        now = rawNow.strftime('%Y-%m-%d %H:%M:%S')
        start = rawStart.strftime('%Y-%m-%d %H:%M:%S')

        self.axes.clear()

        print(self.plotChannels)
        for index in self.plotChannels:
            values = Database.getMeasurements(databaseValues=self.databaseValues,
                                          sessionId=self.sessionId,
                                          channelId=int(self.plotChannels[index][0]),
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
                                            channelId=self.plotChannels[index][0],
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
        channelDictionary = {}
        for index in self.axes.lines:
            xvalues = index.get_xdata()
            newvalues = []
            for values in xvalues:
                values = datetime.datetime.strftime(values, "%Y-%m-%d %H:%M:%S")
                newvalues.append(values)
            yvalues = index.get_ydata()
            values = list(zip(newvalues, yvalues))
            label = index.get_label()
            channelDictionary[label] = values
        return channelDictionary




class Toolbar(NT):
    def __init__(self, canvas, ongoing, parent=None):
        self.figurecanvas = canvas
        self.ongoing = ongoing
        NT.__init__(self, self.figurecanvas, parent)

    def home(self):
        if self.ongoing:
            if not self.figurecanvas.timerIsActive():
                self.figurecanvas.startTimer()
        else:
            NT.home(self)