from PySide.QtGui import *
from PySide.QtCore import *






class ReceiveData(QThread):

    def __init__(self,parent):
        QThread.__init__(self)
        self.parent = parent

    def run(self):
        print("Start Receiving Data")
        




class SendData(QThread):
    pass
