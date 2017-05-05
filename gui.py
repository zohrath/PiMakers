import sys
from PyQt5.QtCore import *
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtCore
import UI


class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.widgetlist = UI.UIpages()
        self.widgetlist.setCurrentIndex(self.widgetlist.mainmenuindex)
        self.setCentralWidget(self.widgetlist)
        self.set_connections()

    def set_connections(self):
        self.widgetlist.widget(self.widgetlist.mainmenuindex).quitSignal.connect(self.close)
        self.widgetlist.widget(self.widgetlist.mainmenuindex).sessionSignal.connect(self.showdatabasesettings)
        self.widgetlist.widget(self.widgetlist.mainmenuindex).helpSignal.connect(self.showhelppage)

        self.widgetlist.widget(self.widgetlist.databasesettingsindex).cancelPressed.connect(self.showmainmenu)
        self.widgetlist.widget(self.widgetlist.helppageindex).cancelPressed.connect(self.showmainmenu)
        self.widgetlist.widget(self.widgetlist.databasesettingsindex).okPressed.connect(self.showchannelsettings)

        self.widgetlist.widget(self.widgetlist.channelsettingsindex).backPressed.connect(self.showdatabasesettings)


    def showdatabasesettings(self):
        self.widgetlist.setCurrentIndex(self.widgetlist.databasesettingsindex)

    def showhelppage(self):
        self.widgetlist.setCurrentIndex(self.widgetlist.helppageindex)

    def showmainmenu(self):
        self.widgetlist.setCurrentIndex(self.widgetlist.mainmenuindex)

    def showchannelsettings(self):
       self.widgetlist.setCurrentIndex(self.widgetlist.channelsettingsindex)







if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.showFullScreen()
    sys.exit(app.exec_())