import sys
from PyQt5.QtCore import *
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtCore

class Sessionwindow():
    def __init__(self):
        self.window = QtWidgets.QDialog()
        self.initUI()

    def initUI(self):

        testbutton = QtWidgets.QPushButton("Test")
        testbutton.setMinimumSize(500, 200)


        self.window.setFixedSize(200, 200)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(testbutton)
        self.window.setLayout(vbox)





class Mainmenu():
    def __init__(self, app):
        self.app = app
        self.initUI()


    def initUI(self):

        startButton = QtWidgets.QPushButton("Starta ny mätning")
        startButton.setMinimumSize(500, 200)
        startButton.clicked.connect(self.switch)

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

        self.w = QtWidgets.QWidget()
        self.w.setLayout(hbox)

    def switch(self):
        self.w.hide()
        nd = Sessionwindow()
        nd.window.show()




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = Mainmenu(app)
    main.w.showFullScreen()
    sys.exit(app.exec_())