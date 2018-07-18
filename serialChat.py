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
import ConfigParser




icons_folder = "resources/icons/"
nickname = "Guest"
default_save_folder = os.path.expanduser('~')
serial_port = None
intervaltime = 6
choosen_profile = "None"
custom_settings = False


settingsparser = ConfigParser.ConfigParser()
settingsparser.read('config/settings.ini')

time_before_flush_junk_data = int(settingsparser.get("app_settings","time_before_flush_junk_data"))
time_show_msg_on_statusbar = int(settingsparser.get("app_settings","time_show_msg_on_statusbar"))
date_format = str(settingsparser.get("app_settings","date_format"))

lang = str(settingsparser.get("default","lang"))
language = ConfigParser.ConfigParser()
language.read("resources/languages/"+lang+".ini")

MENU_SETTINGS = language.get(lang,"MENU_SETTINGS").decode('utf-8')
MENU_OPEN_SETTINGS = language.get(lang,"MENU_OPEN_SETTINGS").decode('utf-8')
MENU_SEND_FILE = language.get(lang,"MENU_SEND_FILE").decode('utf-8')
MENU_CHOOSE_FILE_TO_SEND = language.get(lang,"MENU_CHOOSE_FILE_TO_SEND").decode('utf-8')
MENU_HELP = language.get(lang,"MENU_HELP").decode('utf-8')
MENU_MANUAL = language.get(lang,"MENU_MANUAL").decode('utf-8')
MENU_ABOUT = language.get(lang,"MENU_ABOUT").decode('utf-8')
MENU_EXIT = language.get(lang,"MENU_EXIT").decode('utf-8')
MENU_EXIT_APP = language.get(lang,"MENU_EXIT_APP").decode('utf-8')
BUTTON_SEND = language.get(lang,"BUTTON_SEND").decode('utf-8')
BUTTON_CLEAR = language.get(lang,"BUTTON_CLEAR").decode('utf-8')
MSG_STARTED = language.get(lang,"MSG_STARTED").decode('utf-8')
MSG_STARTING_THREADS = language.get(lang,"MSG_STARTING_THREADS").decode('utf-8')
MSG_JUNK_DATA_CLEARED = language.get(lang,"MSG_JUNK_DATA_CLEARED").decode('utf-8')
MSG_START_SENDING = language.get(lang,"MSG_START_SENDING").decode('utf-8')
MSG_SENT_FILE = language.get(lang,"MSG_SENT_FILE").decode('utf-8')
MSG_CHECK_YOUR_SETTINGS = language.get(lang,"MSG_CHECK_YOUR_SETTINGS").decode('utf-8')
MSG_ME = language.get(lang,"MSG_ME").decode('utf-8')
MSG_CANNOT_SEND_AN_EMPTY_STRING = language.get(lang,"MSG_CANNOT_SEND_AN_EMPTY_STRING").decode('utf-8')
MSG_CANNOT_SEND_YET_RECEIVING_DATA = language.get(lang,"MSG_CANNOT_SEND_YET_RECEIVING_DATA").decode('utf-8')
MSG_DATA_HAS_BEEN_SENT = language.get(lang,"MSG_DATA_HAS_BEEN_SENT").decode('utf-8')
MSG_RECEIVING_DATA_HAS_END = language.get(lang,"MSG_RECEIVING_DATA_HAS_END").decode('utf-8')
MSG_RECEIVED_FILE_FROM = language.get(lang,"MSG_RECEIVED_FILE_FROM").decode('utf-8')
MSG_RECEIVING_DATA = language.get(lang,"MSG_RECEIVING_DATA").decode('utf-8')
APP_TITLE = language.get(lang,"APP_TITLE").decode('utf-8')
MSGBOX_HELP_TITLE = language.get(lang,"MSGBOX_HELP_TITLE").decode('utf-8')
MSGBOX_WARNING_TITLE = language.get(lang,"MSGBOX_WARNING_TITLE").decode('utf-8')


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
        self.custom_settings = custom_settings

        self.timer = QTimer()
        self.timer.setInterval(time_before_flush_junk_data) 
        self.timer.timeout.connect(self.clearJunkData)

        
        self.menuBar = QMenuBar()
        self.Menusettings = self.menuBar.addMenu(MENU_SETTINGS)
        self.actionOpenSettings = QAction(MENU_OPEN_SETTINGS,self)
        self.actionOpenSettings.triggered.connect(self.openSettings)
        self.Menusettings.addAction(self.actionOpenSettings)
        self.MenuSendFile = self.menuBar.addMenu(MENU_SEND_FILE)
        self.actionSendFile = QAction(MENU_CHOOSE_FILE_TO_SEND,self)
        self.actionSendFile.triggered.connect(self.sendFile)
        self.MenuSendFile.addAction(self.actionSendFile)
        self.MenuHelp = self.menuBar.addMenu(MENU_HELP)
        self.actionOpenHelp = QAction(MENU_MANUAL,self)
        self.actionOpenAbout = QAction(MENU_ABOUT,self)
        self.MenuHelp.addAction(self.actionOpenHelp)
        self.actionOpenHelp.triggered.connect(self.openHelp)
        self.MenuHelp.addAction(self.actionOpenAbout)
        self.actionOpenAbout.triggered.connect(self.openAbout)

        self.MenuExit = self.menuBar.addMenu(MENU_EXIT)
        self.actionExit = QAction(MENU_EXIT_APP,self)
        self.actionExit.triggered.connect(self.exitApp)
        self.MenuExit.addAction(self.actionExit)

        self.setMenuBar(self.menuBar)

        
        
        self.layoutCentralWidget = QVBoxLayout()

        self.listWidget = QListWidget()
        self.inputText = QTextEdit()
        self.sendButton = QPushButton(BUTTON_SEND)
        self.sendButton.clicked.connect(self.sendMsg)

        self.clearButton = QPushButton(BUTTON_CLEAR)
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
        self.statusBar.showMessage(MSG_STARTED,time_show_msg_on_statusbar)
        self.setStatusBar(self.statusBar)

        win = QWidget()
        win.setLayout(self.layoutCentralWidget)
        self.setCentralWidget(win)

        self.setGeometry(200,200,500,500)
        self.setWindowTitle(APP_TITLE)
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
            self.statusBar.showMessage(MSG_STARTING_THREADS,time_show_msg_on_statusbar)
            self.send = libthread.Send(self)
            self.receive = libthread.Receive(self)

            self.send.totalData.connect(self.totalData)
            self.send.sendData.connect(self.sendData)
            self.send.endData.connect(self.endData)

            self.receive.startRCV.connect(self.startRCV)
            self.receive.endRCV.connect(self.endRCV)
            self.receive.catchESF.connect(self.catchESF)
            self.receive.catchEOP.connect(self.catchEOP)
            self.receive.interfaceProblem.connect(self.interfaceproblem)

            self.receive.start()

    def interfaceproblem(self,exception):
        self.statusBar.showMessage(exception,time_show_msg_on_statusbar)
        self.receive.loopRun = False
        self.receive.wait()
        self.receive = None


    def clearJunkData(self):
        self.statusBar.showMessage(MSG_JUNK_DATA_CLEARED,time_show_msg_on_statusbar)
        self.iswaitingData = False 
        self.timer.stop()
        self.receive.clear_vars()




    def openSettings(self):
        settingsDialog.SettingsWindow(self)

    def sendFile(self):
        if self.checkIfsettingsROK():
            if not self.iswaitingData and not self.send.isRunning() :
                self.statusBar.showMessage(MSG_START_SENDING,time_show_msg_on_statusbar)
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
                     tt = "[ "+MSG_SENT_FILE+" : "+filename+"  @ "+datetime.datetime.now().strftime(date_format)+" ] "
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

        t_GR = """
        Πολυνηματική εφαρμογή ανταλλαγης μηνυμάτων μέσω σειριακού καλωδίου

                    Δημιουργήθηκε από τον Χρίστο Αναγνωστόπουλο
                        chrisanag1985@gmail.com

        """
        if lang ==  "EN":
            msgBox = QMessageBox.about(self,APP_TITLE,t)
        elif lang == "GR" :
            msgBox = QMessageBox.about(self,APP_TITLE,t_GR.decode('utf-8'))


    def openHelp(self):

        t = ''
        filename = "help_"+lang+".txt"
        with open("resources/docs/"+filename) as help_doc:
            for line in help_doc.xreadlines():
                t += line
        t = t.decode('utf-8')
        helpBox = QMessageBox.question(self,MSGBOX_HELP_TITLE,t)


    def checkIfsettingsROK(self):
        
        if self.receive == None:
            msgBox = QMessageBox(icon=QMessageBox.Warning,text=MSG_CHECK_YOUR_SETTINGS)
            msgBox.setWindowTitle(MSGBOX_WARNING_TITLE)
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
                    self.statusBar.showMessage(MSG_START_SENDING,time_show_msg_on_statusbar)
                    tt = "[ "+self.nickname+" ("+MSG_ME+") @ "+datetime.datetime.now().strftime(date_format)+" ]: "+self.send.text
                    tmp = QListWidgetItem(tt)
                    tmp.setForeground(QColor('blue'))
                    self.listWidget.addItem(tmp)
                    self.listWidget.scrollToBottom()
                    self.send.start()
                    self.inputText.clear()
                else:
                    self.statusBar.showMessage(MSG_CANNOT_SEND_AN_EMPTY_STRING,time_show_msg_on_statusbar)
            elif self.iswaitingData:
               self.statusBar.showMessage(MSG_CANNOT_SEND_YET_RECEIVING_DATA,time_show_msg_on_statusbar)

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
        self.statusBar.showMessage(MSG_DATA_HAS_BEEN_SENT,time_show_msg_on_statusbar)

    @Slot()
    def startRCV(self,x):
        self.timer.start()
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
        self.timer.stop()
        self.statusBar.showMessage(MSG_RECEIVING_DATA_HAS_END,time_show_msg_on_statusbar)
        self.iswaitingData = False
        self.counter = 0
        try:
            if self.receive.type == 'msg':
                tt = "[ "+self.receive.nickname+" @ "+datetime.datetime.now().strftime(date_format)+" ]: "
                xxxx= self.reassembleData(self.receive.data)
                if type(xxxx) == str:
                    xxxx = xxxx.decode('utf-8')
                tt += xxxx
             
            elif self.receive.type == 'file':
               with open(self.default_save_folder+str('/')+self.receive.filename,'w') as f:
                   f.write(self.reassembleData(self.receive.data))
               f.close()
               tt = "[ "+MSG_RECEIVED_FILE_FROM+" "+self.receive.nickname+"  @ "+datetime.datetime.now().strftime(date_format)+" ]: "
               tt += self.default_save_folder+str('/')+self.receive.filename
               

            self.receive.clear_vars()
            tmp = QListWidgetItem(tt)
            if self.receive.type=='msg':
                tmp.setForeground(QColor('green'))
            elif self.receive.type=='file':
                tmp.setForeground(QColor('red'))
            self.listWidget.addItem(tmp)
            self.listWidget.scrollToBottom()
        except Exception as e:
            print(e)

    @Slot()
    def catchESF(self,specs):
        self.statusBar.showMessage(MSG_RECEIVING_DATA,time_show_msg_on_statusbar)
        try:
            specs = json.loads(specs)
        except Exception as e:
            print(e)
        self.progressBar.setMaximum( int(specs['size']))
        self.progressBar.setMinimum(  0)
        self.progressBar.setValue( 0)


    @Slot()
    def catchEOP(self,len_of_data):
        self.statusBar.showMessage(MSG_RECEIVING_DATA,time_show_msg_on_statusbar)
        self.counter += int(len_of_data)
        self.progressBar.setValue(self.counter)


##########################end class Main Window#############################

app = QApplication([])
window = MainWindow()
app.exec_()
