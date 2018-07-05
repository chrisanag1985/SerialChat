from PySide.QtCore import *
from PySide.QtGui import *
import libs.settingsDialog as settingsDialog
import libs.serialThreads as sThreads
import libs.libserial as libserial
import time
import os




icons_folder = "resources/icons/"
nickname = "Guest"
default_save_folder = os.path.expanduser('~')
serial_port = None
intervaltime = 6





class MainWindow(QMainWindow):

    def __init__(self):
        super(self.__class__,self).__init__()
        self.nickname = nickname
        self.default_save_folder = default_save_folder
        self.serial_port = serial_port
        self.intervaltime = intervaltime


        
        self.menuBar = QMenuBar()
        self.Menusettings = self.menuBar.addMenu('Settings')
        self.actionOpenSettings = QAction("Open Settings",self)
        self.actionOpenSettings.triggered.connect(self.openSettings)
        self.Menusettings.addAction(self.actionOpenSettings)
        self.MenuSendFile = self.menuBar.addMenu('Send File')
        self.actionSendFile = QAction("Choose File to Send",self)
        #add trigger 
        self.MenuSendFile.addAction(self.actionSendFile)
        self.MenuHelp = self.menuBar.addMenu('Help')
        self.actionOpenHelp = QAction("Manual",self)
        self.actionOpenAbout = QAction("About",self)
        self.MenuHelp.addAction(self.actionOpenHelp)
        self.MenuHelp.addAction(self.actionOpenAbout)

        self.setMenuBar(self.menuBar)

        
        
        self.layoutCentralWidget = QVBoxLayout()

        self.listWidget = QListWidget()
        self.inputText = QTextEdit()
        self.sendButton = QPushButton("Send")
        self.sendButton.clicked.connect(self.sendMsg)

        self.clearButton = QPushButton("Clear")
        self.clearButton.clicked.connect(self.clearSendingArea)

        self.horizontalButtonLayout = QHBoxLayout()
        self.horizontalButtonLayout.addWidget(self.sendButton)
        self.horizontalButtonLayout.addWidget(self.clearButton)

        self.layoutCentralWidget.addWidget(self.listWidget)
        self.layoutCentralWidget.addWidget(self.inputText)
        self.layoutCentralWidget.addLayout(self.horizontalButtonLayout)

        self.progressBar = QProgressBar()

        self.downDockWidget = QDockWidget()
        self.downDockWidget.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.downDockWidget.setWidget(self.progressBar)
        self.addDockWidget(Qt.BottomDockWidgetArea,self.downDockWidget)

        self.statusBar = QStatusBar()
        self.statusBar.showMessage("Started!!!")
        self.setStatusBar(self.statusBar)

        win = QWidget()
        win.setLayout(self.layoutCentralWidget)
        self.setCentralWidget(win)

        self.setGeometry(200,200,500,500)
        self.setWindowTitle("SerialChat Application")
        self.setWindowIcon(QIcon(icons_folder+'chat.ico'))
        self.show()

        #self.threadReceiving = sThreads.ReceiveData(self)
        #self.threadReceiving.start()



    def openSettings(self):
            settingsDialog.SettingsWindow(self)

    def sendFile(self):
        pass

    def openAbout(self):
        pass

    def sendMsg(self):
        print("sending")

    def clearSendingArea(self):
        self.inputText.clear()













##########################end class Main Window#############################

app = QApplication([])
window = MainWindow()
app.exec_()
