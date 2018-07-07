from PySide.QtCore import *
from PySide.QtGui import *
import libserial 


serial_speeds = ["2400","4800","9600","19200"]
parity_values = ["None","Odd","Even"]
bytesize_values = [5,6,7,8]
stop_values = ["1","1,5","2"]
flow_control_values = ["None","XON/XOFF","RTS/CTS"]

icons_folder = "resources/icons/"





class SettingsWindow(QDialog):


    def __init__(self,parent):
        super(self.__class__,self).__init__(parent)
        self.parent = parent 
        self.lib = libserial.initApp(self)

        self.setWindowTitle('SerialChat Settings')

        self.buttonbox = QDialogButtonBox( QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonbox.button(QDialogButtonBox.Ok).setText("Connect")
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

        self.intervaltime = QLineEdit(str(self.parent.intervaltime))

        self.customsettings = QCheckBox()
        self.customsettings.stateChanged.connect(self.customSettings)
         
        self.serialspeed = QComboBox()
        for sp in serial_speeds:
            self.serialspeed.addItem(str(sp))
        self.serialspeed.setCurrentIndex(serial_speeds.index('9600'))
        self.serialspeed.setDisabled(True)

        self.databits = QComboBox()
        for db in bytesize_values:
            self.databits.addItem(str(db))
        self.databits.setCurrentIndex(bytesize_values.index(8))
        self.databits.setDisabled(True)

        self.stopbits = QComboBox()
        for sb in stop_values:
            self.stopbits.addItem(str(sb))
        self.stopbits.setCurrentIndex(stop_values.index('1'))
        self.stopbits.setDisabled(True)

        self.parity = QComboBox()
        for par in parity_values:
            self.parity.addItem(str(par))
        self.parity.setCurrentIndex(parity_values.index("None"))
        self.parity.setDisabled(True)

        self.flowcontrol = QComboBox()
        for fc in flow_control_values:
            self.flowcontrol.addItem(str(fc))
        self.flowcontrol.setCurrentIndex(parity_values.index("None"))
        self.flowcontrol.setDisabled(True)
        
        self.nickname = QLineEdit(self.parent.nickname)
        
        self.savefolder = QLineEdit(self.parent.default_save_folder)
        self.buttondir = QPushButton()
        self.buttondir.setIcon(QIcon(icons_folder+'folder.png'))
        self.buttondir.clicked.connect(self.choose_save_dir)
        
        self.hBoxLayout = QHBoxLayout()
        self.hBoxLayout.addWidget(self.savefolder)
        self.hBoxLayout.addWidget(self.buttondir)
        self.hBoxContainer = QWidget()
        self.hBoxContainer.setLayout(self.hBoxLayout)
        
        

        
        self.grid = QFormLayout()
        self.grid.addRow("Serial:",self.serialDropDown)
        self.grid.addRow("Interval Time:",self.intervaltime)
        self.grid.addRow("Custom Serial Settings",self.customsettings)
        self.grid.addRow("Serial Speed(baud):",self.serialspeed)
        self.grid.addRow("Data Bits:",self.databits)
        self.grid.addRow("Stop Bits:",self.stopbits)
        self.grid.addRow("Parity:",self.parity)
        self.grid.addRow("Flow Control:",self.flowcontrol)
        self.grid.addRow("Nickname:",self.nickname)
        self.grid.addRow("Save File Folder:",self.hBoxContainer)
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
            
        


    def applyChanges(self):
        
        res = None
        if self.nickname.text() != "":
            self.parent.nickname = self.nickname.text()
        if self.savefolder.text() != "" :
            self.parent.default_save_folder = self.savefolder.text()
        self.parent.intervaltime = int(self.intervaltime.text())
        if self.customsettings.isChecked():

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
                self.parent.receive.exit()
                self.parent.receive = None
                res = self.lib.set_serial(port=self.serialDropDown.currentText(),baudrate=self.serialspeed.currentText(),bytesize=self.databits.currentText(),stopbits=self.stopbits.currentText(),parity=self.parity.currentText(), xonxoff = x_control , rtscts = r_control)
        else:
            if self.parent.receive == None:
                res = self.lib.set_serial(port=self.serialDropDown.currentText())
            else:
                self.parent.receive.exit()
                self.parent.receive = None
                res = self.lib.set_serial(port=self.serialDropDown.currentText())
        if type(res) == OSError:
            self.parent.statusBar.showMessage(str(res))
        if type(res) != None:
            self.parent.serial_port = res 
            self.parent.startThreads()
            self.parent.statusBar.showMessage("Serial Interface %s has started..."%self.parent.serial_port.port)
        else:
            print("Sth else just happend...")
        
        


    def customSettings(self):
        if self.customsettings.isChecked():
            self.serialspeed.setDisabled(False)
            self.databits.setDisabled(False)
            self.stopbits.setDisabled(False)
            self.parity.setDisabled(False)
            self.flowcontrol.setDisabled(False)
        else:
            self.serialspeed.setDisabled(True)
            self.databits.setDisabled(True)
            self.stopbits.setDisabled(True)
            self.parity.setDisabled(True)
            self.flowcontrol.setDisabled(True)
