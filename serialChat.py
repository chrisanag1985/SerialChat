#-*- coding: utf-8 -*-
import ConfigParser
import datetime
import json
import ntpath
import os
import re
import playsound

from PySide.QtCore import *
from PySide.QtGui import *


import libs.serialThreads as lib_thread
import libs.settingsDialog as settings_Dialog

icons_folder = "resources/icons/"
nickname = None
default_save_folder = os.path.expanduser('~')
serial_port = None
intervaltime = 6
choosen_profile = "None"
custom_settings = False


def make_RGB(str_rgb):
    r,g,b = str_rgb.split(",")
    return int(r),int(g),int(b)


settings_parser = ConfigParser.ConfigParser()
settings_parser.read('config/settings.ini')

time_before_flush_junk_data = int(settings_parser.get("app_settings", "time_before_flush_junk_data"))
time_show_msg_on_statusbar = int(settings_parser.get("app_settings", "time_show_msg_on_statusbar"))
date_format = str(settings_parser.get("app_settings", "date_format"))
date_format_underscored = str(settings_parser.get("app_settings", "date_format_underscored"))

incoming_message_sound_file = str(settings_parser.get("app_settings","incoming_message_sound_file"))

r,g,b = make_RGB(settings_parser.get("app_settings","color_me"))
color_me = QColor(r,g,b)
r,g,b = make_RGB(settings_parser.get("app_settings","color_input_text"))
color_input_text = QColor(r,g,b)
r,g,b = make_RGB(settings_parser.get("app_settings","color_receive_msg"))
color_receive_msg = QColor(r,g,b)
r,g,b = make_RGB(settings_parser.get("app_settings","color_receive_file"))
color_receive_file = QColor(r,g,b)
r,g,b = make_RGB(settings_parser.get("app_settings","color_online"))
color_online = QColor(r,g,b)
color_background = settings_parser.get("app_settings","color_background")
color_background_nightmode = settings_parser.get("app_settings","color_background_nightmode")


lang = str(settings_parser.get("default", "lang"))
language = ConfigParser.ConfigParser()
language.read("resources/languages/"+lang+".ini")

MENU_FILE = language.get(lang, "MENU_FILE").decode('utf-8')
MENU_OPEN_SETTINGS = language.get(lang,"MENU_OPEN_SETTINGS").decode('utf-8')
MENU_SAVE_DIALOG = language.get(lang,"MENU_SAVE_DIALOG").decode('utf-8')
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
USERS_TITLE = language.get(lang,"USERS_TITLE").decode('utf-8')
USERS_LAST_SEEN = language.get(lang,"USERS_LAST_SEEN").decode('utf-8')
USERS_COORDINATES = language.get(lang,"USERS_COORDINATES").decode('utf-8')
CHECKBOX_NIGHTMODE_TITLE = language.get(lang,"CHECKBOX_NIGHTMODE_TITLE").decode('utf-8')
CHECKBOX_BEEP_TITLE = language.get(lang,"CHECKBOX_BEEP_TITLE").decode('utf-8')
APP_TITLE = language.get(lang,"APP_TITLE").decode('utf-8')
MSGBOX_HELP_TITLE = language.get(lang,"MSGBOX_HELP_TITLE").decode('utf-8')
MSGBOX_WARNING_TITLE = language.get(lang,"MSGBOX_WARNING_TITLE").decode('utf-8')
ERROR_INTERFACE_DOWN_MESSAGE = language.get(lang,"ERROR_INTERFACE_DOWN_MESSAGE").decode('utf-8')
ERROR_INTERFACE_DOWN_TITLE = language.get(lang,"ERROR_INTERFACE_DOWN_TITLE").decode('utf-8')


class MainWindow(QMainWindow):

    def __init__(self):
        super(self.__class__,self).__init__()
        self.nickname = nickname
        self.other_nicknames = {}
        self.default_save_folder = default_save_folder
        self.serial_port = serial_port
        self.interval_time = intervaltime
        self.counter = 0
        self.is_waiting_data = False
        self.receive = None
        self.send = None
        self.acp127 = False
        self.isEncryptionEnabled = False
        self.encryption_key = None
        self.choosen_profile = choosen_profile
        self.custom_settings = custom_settings

        self.timer = QTimer()
        self.timer.setInterval(time_before_flush_junk_data) 
        self.timer.timeout.connect(self.clear_junk_data)



        self.menu_menubar = QMenuBar()
        self.menu_file = self.menu_menubar.addMenu(MENU_FILE)
        self.qaction_open_settings = QAction(MENU_OPEN_SETTINGS, self)
        self.qaction_open_settings.triggered.connect(self.open_settings)
        self.menu_file.addAction(self.qaction_open_settings)
        self.qaction_save_dialog = QAction(MENU_SAVE_DIALOG,self)
        self.menu_file.addAction(self.qaction_save_dialog)
        self.qaction_save_dialog.triggered.connect(self.save_dialog)
        self.menu_send_file = self.menu_menubar.addMenu(MENU_SEND_FILE)
        self.action_send_file = QAction(MENU_CHOOSE_FILE_TO_SEND, self)
        self.action_send_file.triggered.connect(self.send_file)
        self.menu_send_file.addAction(self.action_send_file)
        self.menu_help = self.menu_menubar.addMenu(MENU_HELP)
        self.action_open_help = QAction(MENU_MANUAL, self)
        self.action_open_about = QAction(MENU_ABOUT, self)
        self.menu_help.addAction(self.action_open_help)
        self.action_open_help.triggered.connect(self.open_help)
        self.menu_help.addAction(self.action_open_about)
        self.action_open_about.triggered.connect(self.open_about)
        self.menu_exit = self.menu_menubar.addMenu(MENU_EXIT)
        self.action_exit = QAction(MENU_EXIT_APP, self)
        self.action_exit.triggered.connect(self.exit_app)
        self.menu_exit.addAction(self.action_exit)
        self.setMenuBar(self.menu_menubar)
        self.layout_central_widget = QVBoxLayout()
        self.list_widget = QTextEdit()
        self.list_widget.setReadOnly(True)
        self.list_widget.setLineWrapMode(QTextEdit.NoWrap)
        self.input_text_textedit = QTextEdit()
        self.input_text_textedit.setLineWrapMode(QTextEdit.NoWrap)
        self.input_text_textedit.setTextColor(color_input_text)
        self.send_button = QPushButton(BUTTON_SEND)
        self.send_button.clicked.connect(self.send_message)
        self.clear_button = QPushButton(BUTTON_CLEAR)
        self.clear_button.clicked.connect(self.clear_inputtext_text)
        self.horizontal_button_layout = QHBoxLayout()
        self.horizontal_button_layout.addWidget(self.send_button)
        self.horizontal_button_layout.addWidget(self.clear_button)
        self.layout_central_widget.addWidget(self.list_widget)
        self.layout_central_widget.addWidget(self.input_text_textedit)
        self.layout_central_widget.addLayout(self.horizontal_button_layout)
        self.right_dockwidget = QDockWidget()
        self.right_dockwidget.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.online_vertical_layout = QVBoxLayout()
        self.online_night_mode = QCheckBox(CHECKBOX_NIGHTMODE_TITLE)
        self.online_night_mode.setChecked(False)
        self.online_night_mode.stateChanged.connect(self.night_mode)
        self.online_beep_checkbox = QCheckBox(CHECKBOX_BEEP_TITLE)
        self.online_label = QLabel(USERS_TITLE)
        self.online_list_widget = QListWidget()
        self.online_multi_widget = QWidget()
        self.online_vertical_layout.addWidget(self.online_beep_checkbox)
        self.online_vertical_layout.addWidget(self.online_night_mode)
        self.online_vertical_layout.addWidget(self.online_label)
        self.online_vertical_layout.addWidget(self.online_list_widget)
        self.online_multi_widget.setLayout(self.online_vertical_layout)
        self.right_dockwidget.setWidget(self.online_multi_widget)
        self.addDockWidget(Qt.RightDockWidgetArea , self.right_dockwidget)



        self.down_dockwidget = QDockWidget()
        self.progress_bar_widget = QProgressBar()
        self.down_dockwidget.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.down_dockwidget.setWidget(self.progress_bar_widget)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.down_dockwidget)
        self.status_bar_widget = QStatusBar()
        self.status_bar_widget.showMessage(MSG_STARTED, time_show_msg_on_statusbar)
        self.setStatusBar(self.status_bar_widget)
        window_widget = QWidget()
        window_widget.setLayout(self.layout_central_widget)
        self.setCentralWidget(window_widget)
        self.setGeometry(200,200,900,600)
        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(QIcon(icons_folder+'chat.ico'))
        self.show()

    def exit_app(self):
        if self.send is not None:
            if self.send.isRunning():
                self.send.wait()
        if self.receive is not None:
            if self.receive.isRunning():
                self.receive.loop_run = False
                self.receive.wait()
        self.close()

    def start_threads(self):
        if self.receive is None:
            self.status_bar_widget.showMessage(MSG_STARTING_THREADS, time_show_msg_on_statusbar)
            self.send = lib_thread.Send(self)
            self.receive = lib_thread.Receive(self)

            self.send.total_data_signal.connect(self.total_data_slot)
            self.send.send_data_signal.connect(self.send_data_slot)
            self.send.end_data_signal.connect(self.end_data_slot)

            self.receive.start_receive_signal.connect(self.start_receive_slot)
            self.receive.end_receive_signal.connect(self.end_receive_slot)
            self.receive.catch_esf_signal.connect(self.catch_esf_slot)
            self.receive.catch_eop_signal.connect(self.catch_eop_slot)
            self.receive.interface_problem_signal.connect(self.interface_problem)

            self.receive.start()

    def night_mode(self):
        if self.online_night_mode.isChecked():
            self.list_widget.setStyleSheet("QTextEdit { background-color: rgb("+color_background_nightmode+")} ")
            self.input_text_textedit.setStyleSheet("QTextEdit { background-color: rgb("+color_background_nightmode+") } ")
            self.online_list_widget.setStyleSheet("QListWidget { background-color: rgb("+color_background_nightmode+") } ")
        else:
            self.list_widget.setStyleSheet("QTextEdit { background-color: rgb("+color_background+" )} ")
            self.input_text_textedit.setStyleSheet("QTextEdit { background-color: rgb("+color_background+" )} ")
            self.online_list_widget.setStyleSheet(("QListWidget {background-color: rgb("+color_background+")}"))

    def interface_problem(self, exception):
        self.status_bar_widget.showMessage(exception, time_show_msg_on_statusbar)
        self.receive.loop_run = False
        self.receive.wait()
        if "Input/output" in exception:
            msgBox = QMessageBox(icon=QMessageBox.Critical, text=ERROR_INTERFACE_DOWN_MESSAGE)
            msgBox.setWindowTitle(ERROR_INTERFACE_DOWN_TITLE)
            msgBox.exec_()
        self.receive = None

    def clear_junk_data(self):
        self.status_bar_widget.showMessage(MSG_JUNK_DATA_CLEARED, time_show_msg_on_statusbar)
        self.is_waiting_data = False
        self.timer.stop()
        self.receive.clear_vars()

    def open_settings(self):
        settings_Dialog.SettingsWindow(self)

    def save_dialog(self):
        text = self.list_widget.toPlainText()
        with open(self.default_save_folder + str('/') + "saved_dialog@"+datetime.datetime.now().strftime(date_format_underscored), 'w') as f:
            f.write(text)
            f.close()

    def send_file(self):
        if self.check_if_settings_r_ok():
            if not self.is_waiting_data and not self.send.isRunning() :
                self.status_bar_widget.showMessage(MSG_START_SENDING, time_show_msg_on_statusbar)
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
                     self.list_widget.setTextColor(color_receive_file)
                     self.list_widget.append(tt)
                     self.send.filename  = ntpath.basename(filename)
                     self.send.start()

    def send_message(self):
        if self.check_if_settings_r_ok():
            if not self.is_waiting_data and not self.send.isRunning():

                self.send.text = self.input_text_textedit.toPlainText()
                self.send.filename = None
                self.send.type = 'msg'
                find = re.search("^\s*$",self.send.text)
                if not find:
                    self.status_bar_widget.showMessage(MSG_START_SENDING, time_show_msg_on_statusbar)
                    tt = "[ "+self.nickname+" ("+MSG_ME+") @ "+datetime.datetime.now().strftime(date_format)+" ]: "+self.send.text
                    self.list_widget.setTextColor(color_me)
                    self.list_widget.append(tt)

                    self.send.start()
                    self.input_text_textedit.clear()
                else:
                    self.status_bar_widget.showMessage(MSG_CANNOT_SEND_AN_EMPTY_STRING, time_show_msg_on_statusbar)
            elif self.is_waiting_data:
               self.status_bar_widget.showMessage(MSG_CANNOT_SEND_YET_RECEIVING_DATA, time_show_msg_on_statusbar)



    def open_about(self):
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

    def open_help(self):

        t = ''
        filename = "help_"+lang+".txt"
        with open("resources/docs/"+filename) as help_doc:
            for line in help_doc.xreadlines():
                t += line
        t = t.decode('utf-8')
        helpBox = QMessageBox.question(self,MSGBOX_HELP_TITLE,t)

    def check_if_settings_r_ok(self):

        if self.receive is None:
            msgBox = QMessageBox(icon=QMessageBox.Warning,text=MSG_CHECK_YOUR_SETTINGS)
            msgBox.setWindowTitle(MSGBOX_WARNING_TITLE)
            msgBox.exec_()
            self.input_text_textedit.clear()
            return False
        return True


    def clear_inputtext_text(self):
        self.input_text_textedit.clear()

    @Slot()
    def send_data_slot(self, xx):
        self.progress_bar_widget.setValue(xx)

    @Slot()
    def total_data_slot(self, total):
        self.progress_bar_widget.setMaximum(total)
        self.progress_bar_widget.setMinimum(0)
        self.progress_bar_widget.setValue(0)

    @Slot()
    def end_data_slot(self):
        self.status_bar_widget.showMessage(MSG_DATA_HAS_BEEN_SENT, time_show_msg_on_statusbar)

    @Slot()
    def start_receive_slot(self, x):
        self.timer.start()
        self.is_waiting_data = True
        
    #TODO must be in the Receice Class file !!! NOT HERE
    def reassemble_data(self, rdata):

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
    def end_receive_slot(self):
        self.timer.stop()
        self.status_bar_widget.showMessage(MSG_RECEIVING_DATA_HAS_END, time_show_msg_on_statusbar)
        self.is_waiting_data = False
        self.counter = 0
        try:
            if self.receive.type == 'msg':
                tt = "[ "+self.receive.nickname+" @ "+datetime.datetime.now().strftime(date_format)+" ]: "
                xxxx= self.reassemble_data(self.receive.data)
                if type(xxxx) == str:
                    xxxx = xxxx.decode('utf-8')
                tt += xxxx
             
            elif self.receive.type == 'file':
               with open(self.default_save_folder+str('/')+self.receive.filename,'w') as f:
                   f.write(self.reassemble_data(self.receive.data))
               f.close()
               tt = "[ "+MSG_RECEIVED_FILE_FROM+" "+self.receive.nickname+"  @ "+datetime.datetime.now().strftime(date_format)+" ]: "
               tt += self.default_save_folder+str('/')+self.receive.filename
               

            self.receive.clear_vars()
            if self.receive.type=='msg':
                self.list_widget.setTextColor(color_receive_msg)
            elif self.receive.type=='file':
                self.list_widget.setTextColor(color_receive_file)

            if not self.receive.nickname in self.other_nicknames.keys():
                dtime = datetime.datetime.now().strftime(date_format)
                self.other_nicknames[self.receive.nickname] = dtime
                tmp_item = QListWidgetItem(self.receive.nickname)
                tmp_text = self.receive.nickname+"\n"+USERS_LAST_SEEN+":"+dtime+"\n"+USERS_COORDINATES+":"
                tmp_item.setText(tmp_text)
                tmp_item.setForeground(color_online)
                if self.online_list_widget.count()%2 == 0:
                    tmp_item.setBackground(Qt.lightGray)
                self.online_list_widget.addItem(tmp_item)
            else:
                dtime = datetime.datetime.now().strftime(date_format)
                self.other_nicknames[self.receive.nickname] = dtime
                aaaa= self.online_list_widget.findItems("^"+self.receive.nickname+"\n.*\n.*$", Qt.MatchRegExp)
                aaaa[0].setText(self.receive.nickname+"\n"+USERS_LAST_SEEN+":"+dtime+"\n"+USERS_COORDINATES+":")
            self.list_widget.append(tt)
            if self.online_beep_checkbox.isChecked():
                playsound.playsound(incoming_message_sound_file)


        except Exception as e:
            print(e)

    @Slot()
    def catch_esf_slot(self, specs):
        self.status_bar_widget.showMessage(MSG_RECEIVING_DATA, time_show_msg_on_statusbar)
        try:
            specs = json.loads(specs)
        except Exception as e:
            print(e)
        self.progress_bar_widget.setMaximum(int(specs['size']))
        self.progress_bar_widget.setMinimum(0)
        self.progress_bar_widget.setValue(0)

    @Slot()
    def catch_eop_slot(self, len_of_data):
        self.status_bar_widget.showMessage(MSG_RECEIVING_DATA, time_show_msg_on_statusbar)
        self.counter += int(len_of_data)
        self.progress_bar_widget.setValue(self.counter )


##########################end class Main Window#############################

app = QApplication([])
window = MainWindow()
app.exec_()
