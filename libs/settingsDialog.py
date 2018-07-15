from PySide.QtCore import *
from PySide.QtGui import *
import libserial 
import ConfigParser


serial_speeds = ["1200","2400","4800","9600","14400","19200"]
parity_values = ["None","Odd","Even"]
bytesize_values = [5,6,7,8]
stop_values = ["1","1,5","2"]
flow_control_values = ["None","XON/XOFF","RTS/CTS"]

icons_folder = "resources/icons/"

lang = "GR"

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
FORMLAYOUT_NICKNAME_TITLE= language.get(lang,"FORMLAYOUT_NICKNAME_TITLE" ).decode('utf-8')
FORMLAYOUT_SAVE_FOLDER_FILE_TITLE= language.get(lang,"FORMLAYOUT_SAVE_FOLDER_FILE_TITLE" ).decode('utf-8')
MSG_SERIAL_INT_STARTED= language.get(lang,"MSG_SERIAL_INT_STARTED").decode('utf-8')


class SettingsWindow(QDialog):


    def __init__(self,parent):
        super(self.__class__,self).__init__(parent)
        self.parent = parent 
        self.lib = libserial.initApp(self)
        if self.parent.receive is not None:
            self.boolConfigIsOK = True 
        else:
            self.boolConfigIsOK = False

        self.configparser = ConfigParser.ConfigParser()
        self.configparser.read("config/profiles/profiles.ini")

        self.settingsparser = ConfigParser.ConfigParser()
        self.settingsparser.read('config/settings.ini')

        self.setWindowTitle(SERIAL_CHAT_SETTINGS_TITLE)

        self.buttonbox = QDialogButtonBox( QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonbox.button(QDialogButtonBox.Ok).setText(CONNECT)
        self.buttonbox.button(QDialogButtonBox.Cancel).setText(CANCEL)
        self.buttonbox.accepted.connect(self.accept)
        self.accepted.connect(self.applyChanges)
        self.buttonbox.rejected.connect(self.reject)
        self.serialDropDown = QComboBox()

        self.lib.init__serial()
        self.serialvalues =self.lib.get_serials()
        for serials in self.serialvalues: 
            self.serialDropDown.addItem(serials)
        
        if self.parent.serial_port != None:
            self.serialDropDown.setCurrentIndex(self.serialvalues.index(self.parent.serial_port.name))

        self.profiles = QComboBox()
        self.profiles.addItem("None")
        if self.parent.choosen_profile == "Custom":
            self.profiles.addItem("Custom")
        for profile in self.configparser.sections():
            self.profiles.addItem(profile)
        if self.parent.custom_settings:
            self.profiles.setCurrentIndex(self.profiles.findText('Custom'))
        elif self.parent.choosen_profile != 'None':
            self.profiles.setCurrentIndex(self.profiles.findText(self.parent.choosen_profile))
        else:
            self.profiles.setCurrentIndex(self.profiles.findText('None'))

        self.profiles.currentIndexChanged.connect(self.changeCustomSettingsOnProfile)
        


        self.customsettings = QCheckBox()
        self.customsettings.stateChanged.connect(self.customSettings)

        self.intervaltime = QLineEdit(str(self.parent.intervaltime))
        self.intervaltime.setDisabled(True)
         
        self.serialspeed = QComboBox()
        for sp in serial_speeds:
            self.serialspeed.addItem(str(sp))
        if self.boolConfigIsOK:
            self.serialspeed.setCurrentIndex(serial_speeds.index(str(self.parent.serial_port.baudrate)))
        else:
            self.serialspeed.setCurrentIndex(serial_speeds.index('9600'))
        self.serialspeed.setDisabled(True)

        self.databits = QComboBox()
        for db in bytesize_values:
            self.databits.addItem(str(db))
        if self.boolConfigIsOK :
            self.databits.setCurrentIndex(bytesize_values.index(self.parent.serial_port.bytesize))
        else:
            self.databits.setCurrentIndex(bytesize_values.index(8))
        self.databits.setDisabled(True)

        self.stopbits = QComboBox()
        for sb in stop_values:
            self.stopbits.addItem(str(sb))
        if self.boolConfigIsOK :
            sb =  str(self.parent.serial_port.stopbits).replace('.',',')
            self.stopbits.setCurrentIndex(stop_values.index(str(sb)))
        else:
            self.stopbits.setCurrentIndex(stop_values.index('1'))
        self.stopbits.setDisabled(True)

        self.parity = QComboBox()
        for par in parity_values:
            self.parity.addItem(str(par))
        if self.boolConfigIsOK :
            table = { 'O':'Odd','E':'Even','N':'None'}
            xxx = [ item for key , item in table.items() if self.parent.serial_port.parity == key]
            self.parity.setCurrentIndex(parity_values.index(xxx[0]))
        else:
            self.parity.setCurrentIndex(parity_values.index("None"))
        self.parity.setDisabled(True)

        self.flowcontrol = QComboBox()
        for fc in flow_control_values:
            self.flowcontrol.addItem(str(fc))
        if self.boolConfigIsOK :
            if self.parent.serial_port.xonxoff :
                self.flowcontrol.setCurrentIndex(flow_control_values.index("XON/XOFF"))
            elif self.parent.serial_port.rtscts:
                self.flowcontrol.setCurrentIndex(flow_control_values.index("RTS/CTS"))
            else:
                self.flowcontrol.setCurrentIndex(flow_control_values.index("None"))
        else:
            self.flowcontrol.setCurrentIndex(parity_values.index("None"))
        self.flowcontrol.setDisabled(True)
        
        self.nickname = QLineEdit(self.parent.nickname)
        if self.settingsparser.has_option('default','nickname'):
            self.nickname.setText(self.settingsparser.get('default','nickname'))
        
        self.savefolder = QLineEdit(self.parent.default_save_folder)
        if self.settingsparser.has_option('default','default_save_folder'):
            self.savefolder.setText(self.settingsparser.get('default','default_save_folder'))

        self.buttondir = QPushButton()
        self.buttondir.setIcon(QIcon(icons_folder+'folder.png'))
        self.buttondir.clicked.connect(self.choose_save_dir)
        
        self.hBoxLayout = QHBoxLayout()
        self.hBoxLayout.addWidget(self.savefolder)
        self.hBoxLayout.addWidget(self.buttondir)
        self.hBoxContainer = QWidget()
        self.hBoxContainer.setLayout(self.hBoxLayout)

        self.enableACP127 = QCheckBox()
        self.enableACP127.stateChanged.connect(self.enableFuncACP127)
        if self.parent.acp127:
            self.enableACP127.setChecked(True)
        
        

        
        self.grid = QFormLayout()
        self.grid.addRow(FORMLAYOUT_SERIAL_TITLE+":",self.serialDropDown)
        self.grid.addRow(FORMLAYOUT_PROFILE_TITLE+":",self.profiles)
        self.grid.addRow(FORMLAYOUT_CUSTOM_SERIAL_SETTINGS_TITLE,self.customsettings)
        self.grid.addRow(FORMLAYOUT_INTERVAL_TIME_TITLE+":",self.intervaltime)
        self.grid.addRow(FORMLAYOUT_SERIAL_SPEED_TITLE+"(baud):",self.serialspeed)
        self.grid.addRow(FORMLAYOUT_DATA_BITS_TITLE+":",self.databits)
        self.grid.addRow(FORMLAYOUT_STOP_BITS_TITLE+":",self.stopbits)
        self.grid.addRow(FORMLAYOUT_PARITY_TITLE+":",self.parity)
        self.grid.addRow(FORMLAYOUT_FLOWCONTROL_TITLE+":",self.flowcontrol)
        self.grid.addRow(FORMLAYOUT_ENABLE_ACP127_TITLE+" ACP-127",self.enableACP127)
        self.grid.addRow(FORMLAYOUT_NICKNAME_TITLE+":",self.nickname)
        self.grid.addRow(FORMLAYOUT_SAVE_FOLDER_FILE_TITLE+":",self.hBoxContainer)
        self.grid.addRow("",self.buttonbox)
        self.setLayout(self.grid)
        self.show()



    def choose_save_dir(self):
        fname = QFileDialog(self)
        fname.setFileMode(QFileDialog.Directory)
        fname.setOption(QFileDialog.ShowDirsOnly)

        if fname.exec_():
            filename = fname.selectedFiles()[0]
            self.savefolder.setText(filename)


    def enableFuncACP127(self):
        if self.enableACP127.isChecked():
            self.parent.acp127 = True
        else:
            self.parent.acp127 = False
            
    




    def applyChanges(self):
        
        res = None
        self.parent.custom_settings = self.customsettings.isChecked()
        self.parent.choosen_profile = self.profiles.currentText()
        if self.parent.custom_settings :
            self.parent.choosen_profile = "Custom"
            
        
        if self.nickname.text() != "":
            self.parent.nickname = self.nickname.text()
        if self.savefolder.text() != "" :
            self.parent.default_save_folder = self.savefolder.text()
        self.parent.intervaltime = int(self.intervaltime.text())
        if  self.flowcontrol.currentText() ==  "XON/XOFF":
            x_control = True
        else:
            x_control = False

        if self.flowcontrol.currentText() == "RTS/CTS":
            r_control = True
        else:
            r_control = False
        if self.parent.receive == None:
            res = self.lib.set_serial(port=self.serialDropDown.currentText(),baudrate=self.serialspeed.currentText(),bytesize=self.databits.currentText(),stopbits=self.stopbits.currentText(),parity=self.parity.currentText(), xonxoff = x_control , rtscts = r_control)
        else:
            self.parent.receive.loopRun = False
            self.parent.receive.wait()
            self.parent.receive = None
            res = self.lib.set_serial(port=self.serialDropDown.currentText(),baudrate=self.serialspeed.currentText(),bytesize=self.databits.currentText(),stopbits=self.stopbits.currentText(),parity=self.parity.currentText(), xonxoff = x_control , rtscts = r_control)
        if type(res) == OSError:
            self.parent.statusBar.showMessage(str(res),5000)
        if type(res) != None and type(res) != OSError:
            self.parent.serial_port = res 
            self.parent.startThreads()
            self.parent.statusBar.showMessage(MSG_SERIAL_INT_STARTED%self.parent.serial_port.port)
        else:
            print("Sth wrong just happend...")


    def changeCustomSettingsOnProfile(self):
        if self.profiles.currentText() != 'None':

            section = self.profiles.currentText()
            self.intervaltime.setText(self.configparser.get(section,"interval"))
            self.serialspeed.setCurrentIndex( serial_speeds.index( self.configparser.get(section,"serialspeed") ))
            self.databits.setCurrentIndex( bytesize_values.index(int(self.configparser.get(section,"bytesize"))))
            self.stopbits.setCurrentIndex(stop_values.index( self.configparser.get(section,"stopbits")))
            self.parity.setCurrentIndex (parity_values.index(self.configparser.get(section,"parity") ))
            if self.configparser.get(section,"xonxoff") == 'True' :
                self.flowcontrol.setCurrentIndex(flow_control_values.index("XON/XOFF"))
            elif self.configparser.get(section,"rtscts") == 'True':
                self.flowcontrol.setCurrentIndex(flow_control_values.index("RTS/CTS"))
            else:
                self.flowcontrol.setCurrentIndex(flow_control_values.index("None"))
            if self.configparser.get(section,"acp127") == "True" :
                self.enableACP127.setChecked(True)
        elif self.profiles.currentText() == "None":
            self.serialspeed.setCurrentIndex(serial_speeds.index('9600'))
            self.intervaltime.setText(str(self.parent.intervaltime))
            self.databits.setCurrentIndex(bytesize_values.index(8))
            self.stopbits.setCurrentIndex(stop_values.index('1'))
            self.parity.setCurrentIndex(parity_values.index('None'))
            self.flowcontrol.setCurrentIndex(flow_control_values.index('None'))
            self.enableACP127.setChecked(False)
            
            

        
        


    def customSettings(self):
        if self.customsettings.isChecked():
            self.intervaltime.setDisabled(False)
            self.serialspeed.setDisabled(False)
            self.databits.setDisabled(False)
            self.stopbits.setDisabled(False)
            self.parity.setDisabled(False)
            self.flowcontrol.setDisabled(False)
        else:
            self.intervaltime.setDisabled(True)
            self.serialspeed.setDisabled(True)
            self.databits.setDisabled(True)
            self.stopbits.setDisabled(True)
            self.parity.setDisabled(True)
            self.flowcontrol.setDisabled(True)
