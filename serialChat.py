#-*- coding: utf-8 -*-
from PySide.QtCore import *
from PySide.QtGui import *
import libs.settingsDialog as settingsDialog
import libs.serialThreads as libthread 
import libs.libserial as libserial
import time
import os
import re
import datetime
import ntpath
import base64
import json




icons_folder = "resources/icons/"
nickname = "Guest"
default_save_folder = os.path.expanduser('~')
serial_port = None
intervaltime = 6
choosen_profile = None





class MainWindow(QMainWindow):

    def __init__(self):
        super(self.__class__,self).__init__()
        self.nickname = nickname
        self.default_save_folder = default_save_folder
        self.serial_port = serial_port
        self.intervaltime = intervaltime
        self.counter = 0
        self.iswaitingData = False
        self.receive = None
        self.send = None
        self.acp127 = False
        self.choosen_profile = choosen_profile


        
        self.menuBar = QMenuBar()
        self.Menusettings = self.menuBar.addMenu('Settings')
        self.actionOpenSettings = QAction("Open Settings",self)
        self.actionOpenSettings.triggered.connect(self.openSettings)
        self.Menusettings.addAction(self.actionOpenSettings)
        self.MenuSendFile = self.menuBar.addMenu('Send File')
        self.actionSendFile = QAction("Choose File to Send",self)
        self.actionSendFile.triggered.connect(self.sendFile)
        self.MenuSendFile.addAction(self.actionSendFile)
        self.MenuHelp = self.menuBar.addMenu('Help')
        self.actionOpenHelp = QAction("Manual",self)
        self.actionOpenAbout = QAction("About",self)
        self.MenuHelp.addAction(self.actionOpenHelp)
        self.actionOpenHelp.triggered.connect(self.openHelp)
        self.MenuHelp.addAction(self.actionOpenAbout)
        self.actionOpenAbout.triggered.connect(self.openAbout)

        self.MenuExit = self.menuBar.addMenu('Exit')
        self.actionExit = QAction('Exit App',self)
        self.actionExit.triggered.connect(self.exitApp)
        self.MenuExit.addAction(self.actionExit)

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
        self.statusBar.showMessage("Started!!!",5000)
        self.setStatusBar(self.statusBar)

        win = QWidget()
        win.setLayout(self.layoutCentralWidget)
        self.setCentralWidget(win)

        self.setGeometry(200,200,500,500)
        self.setWindowTitle("SerialChat Application")
        self.setWindowIcon(QIcon(icons_folder+'chat.ico'))
        self.show()



    def exitApp(self):
        if self.send != None:
            if self.send.isRunning():
                self.send.wait()
        if self.receive !=None:
            if self.receive.isRunning():
                self.receive.loopRun = False
                self.receive.wait()
        self.close()

    def startThreads(self):
        if self.receive == None:
            self.statusBar.showMessage("Starting Threads...",5000)
            self.send = libthread.Send(self)
            self.receive = libthread.Receive(self)

            self.send.totalData.connect(self.totalData)
            self.send.sendData.connect(self.sendData)
            self.send.endData.connect(self.endData)

            self.receive.startRCV.connect(self.startRCV)
            self.receive.endRCV.connect(self.endRCV)
            self.receive.catchESF.connect(self.catchESF)
            self.receive.catchEOP.connect(self.catchEOP)

            self.receive.start()




    def openSettings(self):
        settingsDialog.SettingsWindow(self)

    def sendFile(self):
        if self.checkIfsettingsROK():
            if not self.iswaitingData and not self.send.isRunning() :
                self.statusBar.showMessage("Start Sending...",5000)
                fname = QFileDialog(self)
                fname.setFileMode(QFileDialog.ExistingFile)

                if fname.exec_():
                     filename = fname.selectedFiles()[0]
                     self.send.type = 'file'
                     with open(filename,'r') as f:
                         fileText = ''
                         for line in f.xreadlines():
                             fileText +=line
                     self.send.text = fileText
                     tt = "[ Sent File : "+filename+"  @ "+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" ] "
                     tmp  = QListWidgetItem(tt)
                     tmp.setForeground(QColor('red'))
                     self.listWidget.addItem(tmp)
                     self.listWidget.scrollToBottom()
                     self.send.filename  = ntpath.basename(filename)
                     self.send.start()

    def openAbout(self):
        t = """
        A Multi-Threading Chat Application for communication over serial cable.

                     
                     Created by Christos Anagnostopoulos.
                         chrisanag1985@gmail.com

        """
        msgBox = QMessageBox.about(self,"SerialChat Application",t)

    def openHelp(self):
        t = """
        
        This is a help text for demo only :P
        !!!



        """
        helpBox = QMessageBox.question(self,"SerialChat Application Help",t)


    def checkIfsettingsROK(self):
        
        if self.receive == None:
            msgBox = QMessageBox(icon=QMessageBox.Warning,text="Check your Settings...")
            msgBox.setWindowTitle('Warning')
            msgBox.exec_()
            self.inputText.clear()
            return False
        return True

    def sendMsg(self):
        if self.checkIfsettingsROK():
            if not self.iswaitingData and not self.send.isRunning():

                self.send.text = self.inputText.toPlainText()
                self.send.filename = None
                self.send.type = 'msg'
                find = re.search("^\s*$",self.send.text)
                if not find:
                    self.statusBar.showMessage("Start Sending...",5000)
                    tt = "[ "+self.nickname+" (me) @ "+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" ]: "+self.send.text
                    tmp = QListWidgetItem(tt)
                    tmp.setForeground(QColor('blue'))
                    self.listWidget.addItem(tmp)
                    self.listWidget.scrollToBottom()
                    self.send.start()
                    self.inputText.clear()
                else:
                    self.statusBar.showMessage("Cannot Send an Empty String...",5000)
            elif self.iswaitingData:
               self.statusBar.showMessage("Cannot send yet... Receiving data...",5000)

    def clearSendingArea(self):
        self.inputText.clear()

    @Slot()
    def sendData(self,xx):
        self.progressBar.setValue(xx)

    @Slot()
    def totalData(self,total):
        self.progressBar.setMaximum(total)
        self.progressBar.setMinimum(0)
        self.progressBar.setValue(0)

    @Slot()
    def endData(self):
        self.statusBar.showMessage("Data has been Sent...",5000)

    @Slot()
    def startRCV(self,x):
        self.iswaitingData = True
        
    #TODO must be in the Receice Class file !!! NOT HERE
    def reassembleData(self,rdata):

        end_text = ''
        count = 0
        if self.receive.pieces > 0 :
            for chunk in range(0,self.receive.pieces):
                end_text += rdata['data_'+str(chunk)]
        if self.receive.remain > 0:
            end_text += rdata['data_remain']
        if type(end_text) == unicode:
            return end_text.decode('utf-8')
        else:
            return end_text

                

    @Slot()
    def endRCV(self):
        self.statusBar.showMessage("Receiving Data has ended...",5000)
        self.iswaitingData = False
        self.counter = 0
        if self.receive.type == 'msg':
            tt = "[ "+self.receive.nickname+" @ "+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" ]: "
            xxxx= self.reassembleData(self.receive.data)
            if type(xxxx) == str:
                xxxx = xxxx.decode('utf-8')
            tt += xxxx
         
        elif self.receive.type == 'file':
           with open(self.default_save_folder+str('/')+self.receive.filename,'w') as f:
               f.write(self.reassembleData(self.receive.data))
           f.close()
           tt = "[ Received File from "+self.receive.nickname+"  @ "+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" ]: "
           tt += self.default_save_folder+str('/')+self.receive.filename
           

        self.receive.clear_vars()
        tmp = QListWidgetItem(tt)
        if self.receive.type=='msg':
            tmp.setForeground(QColor('green'))
        elif self.receive.type=='file':
            tmp.setForeground(QColor('red'))
        self.listWidget.addItem(tmp)
        self.listWidget.scrollToBottom()

    @Slot()
    def catchESF(self,specs):
        self.statusBar.showMessage("Receiving Data...",10000)
        specs = json.loads(specs)
        self.progressBar.setMaximum( int(specs['size']))
        self.progressBar.setMinimum(  0)
        self.progressBar.setValue( 0)


    @Slot()
    def catchEOP(self,len_of_data):
        self.statusBar.showMessage("Receiving Data...",10000)
        self.counter += int(len_of_data)
        self.progressBar.setValue(self.counter)



    













##########################end class Main Window#############################

app = QApplication([])
window = MainWindow()
app.exec_()
