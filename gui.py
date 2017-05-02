import sys
from PyQt5.QtCore import *
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtCore

class Sessionwindow():
    def __init__(self):
        self.window = QtWidgets.QMainWindow()
        self.initUI()

    def initUI(self):
        self.window.setFixedSize(200, 200)
        self.window.central_widget = QtWidgets.QWidget()
        self.window.setCentralWidget(self.window.central_widget)
        self.window.show()





class Mainmenu():
    def __init__(self, app):
        self.app = app
        self.initUI()

    def initUI(self):

        startButton = QtWidgets.QPushButton("Starta ny mätning")
        startButton.setMinimumSize(500, 200)
        startButton.clicked.connect(Sessionwindow)

        visualizeButton = QtWidgets.QPushButton("Visa mätningar")
        visualizeButton.setMinimumSize(500, 200)

        quitButton = QtWidgets.QPushButton("Avsluta")
        quitButton.setMinimumSize(500,200)
        quitButton.clicked.connect(self.app.quit)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(startButton)
        vbox.addWidget(visualizeButton)
        vbox.addWidget(quitButton)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)
        hbox.addStretch(1)

        w = QtWidgets.QWidget()
        w.setLayout(hbox)
        w.showFullScreen()
        sys.exit(self.app.exec_())




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    Mainmenu(app)
