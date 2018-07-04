from PySide.QtCore import *
from PySide.QtGui import *


serial_speed = ["2400","4800","9600","19200"]
parity_values = ["None","Odd","Even"]
bytesize_values = [5,6,7,8]
stop_values = ["1","1,5","2"]
flow_control_values = ["None","XON/XOFF","RTS/CTS"]

icons_folder = "resources/icons/"



class SettingsWindow(QDialog):


    def __init__(self,parent):
        super(self.__class__,self).__init__(parent)

        self.setWindowTitle('Settings')

        self.buttonbox = QDialogButtonBox( QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonbox.button(QDialogButtonBox.Ok).setText("Connect")
        self.buttonbox.accepted.connect(self.accept)
        self.buttonbox.rejected.connect(self.reject)
        self.serialDropDown = QComboBox()
        self.customSettings = QCheckBox()
        self.serialSpeed = QComboBox()
        self.databits = QComboBox()
        self.stopbits = QComboBox()
        self.parity = QComboBox()
        self.flowControl = QComboBox()
        self.nickname = QLineEdit()
        self.saveFolder = QLineEdit()
        self.buttonDir = QPushButton()
        self.buttonDir.setIcon(QIcon(icons_folder+'folder.png'))
        
        self.hBoxLayout = QHBoxLayout()
        self.hBoxLayout.addWidget(self.saveFolder)
        self.hBoxLayout.addWidget(self.buttonDir)
        self.hBoxContainer = QWidget()
        self.hBoxContainer.setLayout(self.hBoxLayout)
        
        

        
        self.grid = QFormLayout()
        self.grid.addRow("Serial:",self.serialDropDown)
        self.grid.addRow("Custom Serial Settings",self.customSettings)
        self.grid.addRow("Serial Speed(baud):",self.serialSpeed)
        self.grid.addRow("Data Bits:",self.databits)
        self.grid.addRow("Stop Bits:",self.stopbits)
        self.grid.addRow("Parity:",self.parity)
        self.grid.addRow("Flow Control:",self.flowControl)
        self.grid.addRow("Nickname:",self.nickname)
        self.grid.addRow("Save File Folder:",self.hBoxContainer)
        self.grid.addRow("",self.buttonbox)
        self.setLayout(self.grid)
        self.show()
