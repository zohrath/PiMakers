from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui


class Mainmenu(QtWidgets.QWidget):
    warningPressed = QtCore.pyqtSignal()
    quitSignal = QtCore.pyqtSignal()
    sessionSignal = QtCore.pyqtSignal()                                     # The pyqt signals emitted from the main menu page
    helpSignal = QtCore.pyqtSignal()
    currentSignal = QtCore.pyqtSignal()
    visualizeSignal = QtCore.pyqtSignal()

    def __init__(self):
        """
        Initialises a new instance of a Mainmenu page 
        """
        QtWidgets.QWidget.__init__(self)
        icon = QtGui.QIcon('alert-icon--free-icons-24.png')
        self.warningButton = QtWidgets.QPushButton("Varning!")
        self.warningButton.setMinimumSize(300, 80)
        self.warningButton.setIcon(icon)
        self.warningButton.setStyleSheet("background-color: red;")          # Creates the warning button and connects its signal
        self.warningButton.hide()                                           # Hides the button
        self.warningButton.clicked.connect(self.warningPressed.emit)

        self.startButton = QtWidgets.QPushButton("Starta nya mätning")
        self.startButton.setMinimumSize(300, 80)
        self.startButton.clicked.connect(self.newSession)                   # Creates the start session button and connects its signal

        self.currentButton = QtWidgets.QPushButton("Avsluta pågående mätning")
        self.currentButton.setMinimumSize(300, 80)
        self.currentButton.clicked.connect(self.currentSession)             # Creates the end current session button and connects its signal
        self.currentButton.hide()                                           # Hides the button

        self.visualizeButton = QtWidgets.QPushButton("Visa mätningar")
        self.visualizeButton.setMinimumSize(300, 80)
        self.visualizeButton.clicked.connect(self.visualize)                # Creates the visualize button and connects its signal

        self.helpButton = QtWidgets.QPushButton("Hjälp")
        self.helpButton.setMinimumSize(300, 80)
        self.helpButton.clicked.connect(self.help)                          # Creates the help button and connects its signal

        self.quitButton = QtWidgets.QPushButton("Avsluta")
        self.quitButton.setMinimumSize(300, 80)
        self.quitButton.clicked.connect(self.quit)                          # Creates the quit button and connects its signal

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.warningButton)
        vbox.addWidget(self.startButton)
        vbox.addWidget(self.currentButton)
        vbox.addWidget(self.visualizeButton)
        vbox.addWidget(self.helpButton)
        vbox.addWidget(self.quitButton)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)                                                # Creates the layout of the page
        hbox.addStretch(1)

        self.setLayout(hbox)                                                # Sets the layout of the page

    def visualize(self):
        """
        Handles what happens when the visualize button is clicked
        :return: 
        """
        self.visualizeSignal.emit()                                         # Emits the visualizeSignal signal

    def quit(self):
        """
        Handles what happens when the quit button is clicked
        :return: 
        """
        self.quitSignal.emit()                                              # Emits the quitSignal signal

    def newSession(self):
        """
        Handles what happens when the new session button is clicked
        :return: 
        """
        self.sessionSignal.emit()                                           # Emits the visualizeSignal signal

    def currentSession(self):
        """
        Handles what happens when the current end current session button is clicked
        :return: 
        """
        self.currentSignal.emit()                                           # Emits the currentSignal signal

    def help(self):
        """
        Handles what happens when the help button is clicked
        :return: 
        """
        self.helpSignal.emit()                                              # Emits the helpSignal signal

    def sessionStarted(self):
        """
        Sets the appearance of the main menu when a session is started
        :return: 
        """
        self.startButton.hide()
        self.currentButton.show()                                           # Hides the start new session button and show the end current session button

    def sessionEnded(self):
        """
        Sets the appearance of the main menu when no session is running
        :return: 
        """
        self.currentButton.hide()
        self.startButton.show()                                             # Hides the end current session button and shows the start new session button

    def displayWarning(self, display):
        """
        Hides or shows the warning button
        :param display: True, to display the button, false to hide it 
        :return: 
        """
        if display:
            self.warningButton.show()
        else:
            self.warningButton.hide()