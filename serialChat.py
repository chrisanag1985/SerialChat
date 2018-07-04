from PySide.QtCore import *
from PySide.QtGui import *
import libs.settingsDialog as settingsDialog
import libs.libserial as libserial
import time




icons_folder = "resources/icons/"







class MainWindow(QMainWindow):

    def __init__(self):
        super(self.__class__,self).__init__()


        
        self.menuBar = QMenuBar()
        self.Menusettings = self.menuBar.addMenu('Settings')
        self.connect(self.Menusettings,SIGNAL('aboutToShow()'),self.openSettings)
        self.MenuSendFile = self.menuBar.addMenu('Send File')
        self.MenuAbout = self.menuBar.addMenu('About')
        self.MenuExit = self.menuBar.addMenu('Exit')

        self.setMenuBar(self.menuBar)

        
        
        self.layoutCentralWidget = QVBoxLayout()

        self.listWidget = QListWidget()
        self.inputText = QTextEdit()
        self.sendButton = QPushButton("Send")
        self.clearButton = QPushButton("Clear")

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

        self.threadReceiving = libserial.ReceiveData(self)
        self.threadReceiving.start()



    def openSettings(self):
            settingsDialog.SettingsWindow(self)


    def sendFile(self):
        pass

    def openAbout(self):
        pass

    def exitApp(self):
        pass













##########################end class Main Window#############################

app = QApplication([])
window = MainWindow()
app.exec_()
