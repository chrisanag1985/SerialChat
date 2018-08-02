import ConfigParser
import os
from PySide.QtGui import QDialog, QDialogButtonBox, QComboBox, QCheckBox, QLineEdit, QPushButton, QIcon, QHBoxLayout, \
    QWidget, QFormLayout, QFileDialog, QMessageBox
from Crypto.Hash import MD5

import libserial
import datetime

serial_speeds = ["300","600","1200","2400","4800","9600","14400","19200","38400","56000","57600","115200"]
parity_values = ["None","Odd","Even"]
bytesize_values = [5,6,7,8]
stop_values = ["1","1,5","2"]
flow_control_values = ["None","XON/XOFF","RTS/CTS"]

icons_folder = "resources/icons/"

settings_parser_1 = ConfigParser.ConfigParser()
settings_parser_1.read('config/settings.ini')
lang = settings_parser_1.get("default", "lang")

language = ConfigParser.ConfigParser()
language.read("resources/languages/"+lang+".ini")

SERIAL_CHAT_SETTINGS_TITLE= language.get(lang,"SERIAL_CHAT_SETTINGS_TITLE").decode('utf-8')
CONNECT = language.get(lang,"CONNECT" ).decode('utf-8')
CANCEL = language.get(lang,"CANCEL" ).decode('utf-8')
FORMLAYOUT_SERIAL_TITLE= language.get(lang,"FORMLAYOUT_SERIAL_TITLE" ).decode('utf-8')
FORMLAYOUT_PROFILE_TITLE= language.get(lang,"FORMLAYOUT_PROFILE_TITLE" ).decode('utf-8')   
FORMLAYOUT_CUSTOM_SERIAL_SETTINGS_TITLE= language.get(lang,"FORMLAYOUT_CUSTOM_SERIAL_SETTINGS_TITLE" ).decode('utf-8')
FORMLAYOUT_INTERVAL_TIME_TITLE= language.get(lang,"FORMLAYOUT_INTERVAL_TIME_TITLE" ).decode('utf-8')
FORMLAYOUT_SERIAL_SPEED_TITLE= language.get(lang,"FORMLAYOUT_SERIAL_SPEED_TITLE" ).decode('utf-8')
FORMLAYOUT_DATA_BITS_TITLE= language.get(lang,"FORMLAYOUT_DATA_BITS_TITLE" ).decode('utf-8')
FORMLAYOUT_STOP_BITS_TITLE= language.get(lang,"FORMLAYOUT_STOP_BITS_TITLE" ).decode('utf-8')
FORMLAYOUT_PARITY_TITLE= language.get(lang,"FORMLAYOUT_PARITY_TITLE" ).decode('utf-8')
FORMLAYOUT_FLOWCONTROL_TITLE= language.get(lang,"FORMLAYOUT_FLOWCONTROL_TITLE" ).decode('utf-8')
FORMLAYOUT_ENABLE_ACP127_TITLE= language.get(lang,"FORMLAYOUT_ENABLE_ACP127_TITLE").decode('utf-8')
FORMLAYOUT_ENABLE_ENCRYPTION_TITLE = language.get(lang,"FORMLAYOUT_ENABLE_ENCRYPTION_TITLE").decode('utf-8')
FORMLAYOUT_ENCRYPTION_KEY_TITLE = language.get(lang,"FORMLAYOUT_ENCRYPTION_KEY_TITLE").decode('utf-8')
FORMLAYOUT_NICKNAME_TITLE= language.get(lang,"FORMLAYOUT_NICKNAME_TITLE" ).decode('utf-8')
FORMLAYOUT_SAVE_FOLDER_FILE_TITLE= language.get(lang,"FORMLAYOUT_SAVE_FOLDER_FILE_TITLE" ).decode('utf-8')
ERROR_NO_DIR_MESSAGE = language.get(lang,"ERROR_NO_DIR_MESSAGE").decode('utf-8')
ERROR_NO_DIR_TITLE =  language.get(lang,"ERROR_NO_DIR_TITLE").decode('utf-8')
ERROR_NO_INT_MESSAGE = language.get(lang,"ERROR_NO_INT_MESSAGE").decode('utf-8')
ERROR_NO_INT_TITLE = language.get(lang,"ERROR_NO_INT_TITLE").decode('utf-8')
MSG_SERIAL_INT_STARTED= language.get(lang,"MSG_SERIAL_INT_STARTED").decode('utf-8')


class SettingsWindow(QDialog):


    def __init__(self,parent):
        super(self.__class__,self).__init__(parent)
        self.parent = parent
        self.lib = libserial.InitApp(self)
        if self.parent.receive is not None:
            self.boolean_config_is_ok = True
        else:
            self.boolean_config_is_ok = False

        self.config_parser = ConfigParser.ConfigParser()
        self.config_parser.read("config/profiles/profiles.ini")

        self.settings_parser = ConfigParser.ConfigParser()
        self.settings_parser.read('config/settings.ini')

        self.setWindowTitle(SERIAL_CHAT_SETTINGS_TITLE)

        self.button_box_dialog = QDialogButtonBox( QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.button_box_dialog.button(QDialogButtonBox.Ok).setText(CONNECT)
        self.button_box_dialog.button(QDialogButtonBox.Cancel).setText(CANCEL)
        self.button_box_dialog.accepted.connect(self.accept)
        self.accepted.connect(self.apply_setting_changes)
        self.button_box_dialog.rejected.connect(self.reject)
        self.serial_dropdown = QComboBox()

        self.lib.init__serial()
        self.serial_values =self.lib.get_serials()
        for serials in self.serial_values:
            self.serial_dropdown.addItem(serials)
        
        if self.parent.serial_port is not None:
            self.serial_dropdown.setCurrentIndex(self.serial_dropdown.findText(self.parent.serial_port.name))

        self.profiles_combobox = QComboBox()
        self.profiles_combobox.addItem("None")
        if self.parent.choosen_profile == "Custom":
            self.profiles_combobox.addItem("Custom")
        for profile in self.config_parser.sections():
            self.profiles_combobox.addItem(profile)
        if self.parent.custom_settings:
            self.profiles_combobox.setCurrentIndex(self.profiles_combobox.findText('Custom'))
        elif self.parent.choosen_profile != 'None':
            self.profiles_combobox.setCurrentIndex(self.profiles_combobox.findText(self.parent.choosen_profile))
        else:
            self.profiles_combobox.setCurrentIndex(self.profiles_combobox.findText('None'))

        self.profiles_combobox.currentIndexChanged.connect(self.change_custom_settings_on_profile)
        


        self.custom_settings_checkbox = QCheckBox()
        self.custom_settings_checkbox.stateChanged.connect(self.custom_settings_enable_disable)

        self.interval_time_lineedit = QLineEdit(str(self.parent.interval_time))
        self.interval_time_lineedit.editingFinished.connect(self.check_if_digit)
        self.interval_time_lineedit.setDisabled(True)
         
        self.serial_speed_combobox = QComboBox()
        for sp in serial_speeds:
            self.serial_speed_combobox.addItem(str(sp))
        if self.boolean_config_is_ok:
            self.serial_speed_combobox.setCurrentIndex(self.serial_speed_combobox.findText(str(self.parent.serial_port.baudrate)))
        else:
            self.serial_speed_combobox.setCurrentIndex(self.serial_speed_combobox.findText('9600'))
        self.serial_speed_combobox.setDisabled(True)

        self.databits_combobox = QComboBox()
        for db in bytesize_values:
            self.databits_combobox.addItem(str(db))
        if self.boolean_config_is_ok :
            self.databits_combobox.setCurrentIndex(self.databits_combobox.findText(str(self.parent.serial_port.bytesize)))
        else:
            self.databits_combobox.setCurrentIndex(self.databits_combobox.findText('8'))
        self.databits_combobox.setDisabled(True)

        self.stopbits_combobox = QComboBox()
        for sb in stop_values:
            self.stopbits_combobox.addItem(str(sb))
        if self.boolean_config_is_ok :
            sb =  str(self.parent.serial_port.stopbits).replace('.',',')
            self.stopbits_combobox.setCurrentIndex(self.stopbits_combobox.findText(str(sb)))
        else:
            self.stopbits_combobox.setCurrentIndex(self.stopbits_combobox.findText('1'))
        self.stopbits_combobox.setDisabled(True)

        self.parity_combobox = QComboBox()
        for par in parity_values:
            self.parity_combobox.addItem(str(par))
        if self.boolean_config_is_ok :
            table = { 'O':'Odd','E':'Even','N':'None'}
            xxx = [ item for key , item in table.items() if self.parent.serial_port.parity == key]
            self.parity_combobox.setCurrentIndex(parity_values.index(xxx[0]))
        else:
            self.parity_combobox.setCurrentIndex(self.parity_combobox.findText("None"))
        self.parity_combobox.setDisabled(True)

        self.flowcontrol_combobox = QComboBox()
        for fc in flow_control_values:
            self.flowcontrol_combobox.addItem(str(fc))
        if self.boolean_config_is_ok :
            if self.parent.serial_port.xonxoff :
                self.flowcontrol_combobox.setCurrentIndex(self.flowcontrol_combobox.findText("XON/XOFF"))
            elif self.parent.serial_port.rtscts:
                self.flowcontrol_combobox.setCurrentIndex(self.flowcontrol_combobox.findText("RTS/CTS"))
            else:
                self.flowcontrol_combobox.setCurrentIndex(self.flowcontrol_combobox.findText("None"))
        else:
            self.flowcontrol_combobox.setCurrentIndex(self.flowcontrol_combobox.findText("None"))
        self.flowcontrol_combobox.setDisabled(True)
        
        self.nickname_lineedit = QLineEdit()
        if self.settings_parser.has_option('default', 'nickname'):
            nickname = self.settings_parser.get('default', 'nickname')
            if type(nickname) == str:
                nickname = nickname.decode('utf-8')
            self.nickname_lineedit.setText(self.settings_parser.get('default', 'nickname'))
        else:
            if self.parent.nickname is None:
                self.nickname_lineedit.setText("Guest_"+ MD5.new(str(datetime.datetime.now())).digest().encode('hex')[:5])
            else:
                self.nickname_lineedit.setText(self.parent.nickname)

        
        self.save_folder_editline = QLineEdit(self.parent.default_save_folder)
        self.save_folder_editline.editingFinished.connect(self.check_if_folder_exists)
        if self.settings_parser.has_option('default', 'default_save_folder'):
            folder = self.settings_parser.get('default', 'default_save_folder')
            if type(folder) == str :
                folder = folder.decode('utf-8')
            self.save_folder_editline.setText(folder)
            self.check_if_folder_exists()

        self.dir_browser_button = QPushButton()
        self.dir_browser_button.setIcon(QIcon(icons_folder + 'folder.png'))
        self.dir_browser_button.clicked.connect(self.choose_save_dir)
        
        self.horizontal_box_hboxlayout = QHBoxLayout()
        self.horizontal_box_hboxlayout.addWidget(self.save_folder_editline)
        self.horizontal_box_hboxlayout.addWidget(self.dir_browser_button)
        self.horizontal_box_container_widget = QWidget()
        self.horizontal_box_container_widget.setLayout(self.horizontal_box_hboxlayout)

        self.enable_ACP127 = QCheckBox()
        self.enable_ACP127.stateChanged.connect(self.enable_functionality_ACP127)
        if self.parent.acp127:
            self.enable_ACP127.setChecked(True)

        self.encryption_password_lineedit = QLineEdit()
        self.enable_encryption_checkbox = QCheckBox()
        self.enable_encryption_checkbox.stateChanged.connect(self.enable_functionality_encryption)
        if self.parent.isEncryptionEnabled:
            self.enable_encryption_checkbox.setChecked(True)

        self.encryption_password_lineedit.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        if self.parent.encryption_key is not None:
            self.encryption_password_lineedit.setText(self.parent.encryption_key)
        if self.enable_encryption_checkbox.isChecked():
            self.encryption_password_lineedit.setDisabled(False)
        else:
            self.encryption_password_lineedit.setDisabled(True)
        

        
        self.grid_form_layout = QFormLayout()
        self.grid_form_layout.addRow(FORMLAYOUT_SERIAL_TITLE + ":", self.serial_dropdown)
        self.grid_form_layout.addRow(FORMLAYOUT_PROFILE_TITLE + ":", self.profiles_combobox)
        self.grid_form_layout.addRow(FORMLAYOUT_CUSTOM_SERIAL_SETTINGS_TITLE, self.custom_settings_checkbox)
        self.grid_form_layout.addRow(FORMLAYOUT_INTERVAL_TIME_TITLE + ":", self.interval_time_lineedit)
        self.grid_form_layout.addRow(FORMLAYOUT_SERIAL_SPEED_TITLE + "(baud):", self.serial_speed_combobox)
        self.grid_form_layout.addRow(FORMLAYOUT_DATA_BITS_TITLE + ":", self.databits_combobox)
        self.grid_form_layout.addRow(FORMLAYOUT_STOP_BITS_TITLE + ":", self.stopbits_combobox)
        self.grid_form_layout.addRow(FORMLAYOUT_PARITY_TITLE + ":", self.parity_combobox)
        self.grid_form_layout.addRow(FORMLAYOUT_FLOWCONTROL_TITLE + ":", self.flowcontrol_combobox)
        self.grid_form_layout.addRow(FORMLAYOUT_ENABLE_ACP127_TITLE + " ACP-127", self.enable_ACP127)
        self.grid_form_layout.addRow(FORMLAYOUT_ENABLE_ENCRYPTION_TITLE ,self.enable_encryption_checkbox)
        self.grid_form_layout.addRow(FORMLAYOUT_ENCRYPTION_KEY_TITLE, self.encryption_password_lineedit)
        self.grid_form_layout.addRow(FORMLAYOUT_NICKNAME_TITLE + ":", self.nickname_lineedit)
        self.grid_form_layout.addRow(FORMLAYOUT_SAVE_FOLDER_FILE_TITLE + ":", self.horizontal_box_container_widget)
        self.grid_form_layout.addRow("", self.button_box_dialog)
        self.setLayout(self.grid_form_layout)
        self.show()

    def enable_functionality_encryption(self):
        if self.enable_encryption_checkbox.isChecked():
            self.encryption_password_lineedit.setDisabled(False)
        else:
            self.encryption_password_lineedit.setDisabled(True)

    def check_if_folder_exists(self):

        if not os.path.isdir(self.save_folder_editline.text()):
            msgBox = QMessageBox(icon=QMessageBox.Warning,text=ERROR_NO_DIR_MESSAGE)
            msgBox.setWindowTitle(ERROR_NO_DIR_TITLE)
            msgBox.exec_()
            self.save_folder_editline.setText(self.parent.default_save_folder)

    def check_if_digit(self):

        try:
            int(self.interval_time_lineedit.text())
        except:
            msgBox = QMessageBox(icon=QMessageBox.Warning, text=ERROR_NO_INT_MESSAGE)
            msgBox.setWindowTitle(ERROR_NO_INT_TITLE)
            msgBox.exec_()
            self.interval_time_lineedit.setText(str(self.parent.interval_time))



    def choose_save_dir(self):
        fname = QFileDialog(self)
        fname.setFileMode(QFileDialog.Directory)
        fname.setOption(QFileDialog.ShowDirsOnly)

        if fname.exec_():
            filename = fname.selectedFiles()[0]
            self.save_folder_editline.setText(filename)


    def enable_functionality_ACP127(self):
        if self.enable_ACP127.isChecked():
            self.parent.acp127 = True
        else:
            self.parent.acp127 = False
            
    




    def apply_setting_changes(self):
        
        res = None
        self.parent.custom_settings_enable_disable = self.custom_settings_checkbox.isChecked()
        self.parent.choosen_profile = self.profiles_combobox.currentText()
        if self.parent.custom_settings_enable_disable :
            self.parent.choosen_profile = "Custom"

        if self.enable_encryption_checkbox.isChecked():
            self.parent.isEncryptionEnabled = True
            self.parent.encryption_key = self.encryption_password_lineedit.text()
        else:
            self.parent.isEncryptionEnabled = False
            self.parent.encryption_key = None
        
        if self.nickname_lineedit.text() != "":
            nick = self.nickname_lineedit.text().rstrip()
            nick = nick.replace(" ","_")
            self.parent.nickname = nick
        if self.save_folder_editline.text() != "" :
            if os.path.isdir(self.save_folder_editline.text()):
                self.parent.default_save_folder = self.save_folder_editline.text()
        self.parent.interval_time = int(self.interval_time_lineedit.text())
        if  self.flowcontrol_combobox.currentText() == "XON/XOFF":
            x_control = True
        else:
            x_control = False

        if self.flowcontrol_combobox.currentText() == "RTS/CTS":
            r_control = True
        else:
            r_control = False
        if self.parent.receive is  None:
            res = self.lib.set_serial(port=self.serial_dropdown.currentText(), baudrate=self.serial_speed_combobox.currentText(), bytesize=self.databits_combobox.currentText(), stopbits=self.stopbits_combobox.currentText(), parity=self.parity_combobox.currentText(), xonxoff = x_control, rtscts = r_control)
        else:
            self.parent.receive.loop_run = False
            self.parent.receive.wait()
            self.parent.receive = None
            res = self.lib.set_serial(port=self.serial_dropdown.currentText(), baudrate=self.serial_speed_combobox.currentText(), bytesize=self.databits_combobox.currentText(), stopbits=self.stopbits_combobox.currentText(), parity=self.parity_combobox.currentText(), xonxoff = x_control, rtscts = r_control)
        if type(res) == OSError:
            self.parent.statusBar.showMessage(str(res),5000)
        if type(res) is not None and type(res) != OSError:
            self.parent.serial_port = res 
            self.parent.start_threads()
            self.parent.status_bar_widget.showMessage(MSG_SERIAL_INT_STARTED%self.parent.serial_port.port)

        else:
            print("Sth wrong just happend...")


    def change_custom_settings_on_profile(self):
        if self.profiles_combobox.currentText() != 'None':

            section = self.profiles_combobox.currentText()
            self.interval_time_lineedit.setText(self.config_parser.get(section, "interval"))
            self.serial_speed_combobox.setCurrentIndex(self.serial_speed_combobox.findText(self.config_parser.get(section, "serialspeed")))
            self.databits_combobox.setCurrentIndex(self.databits_combobox.findText(self.config_parser.get(section, "bytesize")))
            self.stopbits_combobox.setCurrentIndex(self.stopbits_combobox.findText(self.config_parser.get(section, "stopbits")))
            self.parity_combobox.setCurrentIndex (self.parity_combobox.findText(self.config_parser.get(section, "parity")))
            if self.config_parser.get(section, "xonxoff") == 'True' :
                self.flowcontrol_combobox.setCurrentIndex(self.flowcontrol_combobox.findText("XON/XOFF"))
            elif self.config_parser.get(section, "rtscts") == 'True':
                self.flowcontrol_combobox.setCurrentIndex(self.flowcontrol_combobox.findText("RTS/CTS"))
            else:
                self.flowcontrol_combobox.setCurrentIndex(self.flowcontrol_combobox.findText("None"))
            if self.config_parser.get(section, "acp127") == "True" :
                self.enable_ACP127.setChecked(True)
            else:
                self.enable_ACP127.setChecked(False)
        elif self.profiles_combobox.currentText() == "None":
            self.serial_speed_combobox.setCurrentIndex(self.serial_speed_combobox.findText('9600'))
            self.interval_time_lineedit.setText(str(self.parent.intervaltime))
            self.databits_combobox.setCurrentIndex(self.databits_combobox.findText('8'))
            self.stopbits_combobox.setCurrentIndex(self.stopbits_combobox.findText('1'))
            self.parity_combobox.setCurrentIndex(self.parity_combobox.findText('None'))
            self.flowcontrol_combobox.setCurrentIndex(self.flowcontrol_combobox.findText('None'))
            self.enable_ACP127.setChecked(False)
            
            

        
        


    def custom_settings_enable_disable(self):
        if self.custom_settings_checkbox.isChecked():
            self.interval_time_lineedit.setDisabled(False)
            self.serial_speed_combobox.setDisabled(False)
            self.databits_combobox.setDisabled(False)
            self.stopbits_combobox.setDisabled(False)
            self.parity_combobox.setDisabled(False)
            self.flowcontrol_combobox.setDisabled(False)
        else:
            self.interval_time_lineedit.setDisabled(True)
            self.serial_speed_combobox.setDisabled(True)
            self.databits_combobox.setDisabled(True)
            self.stopbits_combobox.setDisabled(True)
            self.parity_combobox.setDisabled(True)
            self.flowcontrol_combobox.setDisabled(True)
