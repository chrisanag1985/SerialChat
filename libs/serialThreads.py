from PySide.QtCore import *
from PySide.QtGui import *
import time
import serial
import sys
import json
import base64
import re

#sport = sys.argv[1] 
#ser = serial.Serial(port=sport)
#print(ser)

#text2 = "a"*2330
#
#interval_time = 4
"""
possible types:
msg - message
file - file
resend - request to resend chunks that were damaged
"""




class Send(QThread):
    
    """
    before you start() you must enter the self.text 
    """

    sendData = Signal(int)
    totalData = Signal(int)
    endData = Signal()

    def __init__(self,parent):
        QThread.__init__(self)
        self.counter = 0
        self.text = None
        self.nickname = parent.nickname 
        self.filename = None
        self.type = 'msg'
        self.ser = parent.serial_port 
        self.interval_time = parent.intervaltime
        self.progressbar = parent.progressBar


    def run(self):
        if type(self.text) == unicode:
            self.text = self.text.encode('utf-8')
        full_size = len(self.text)
        self.totalData.emit(full_size)
        pieces = full_size/1024
        remain = full_size%1024
        size = 1024
        t2s = ''
        sending_data = {}
        sending_data['type'] = self.type 
        sending_data['filename'] = self.filename 
        sending_data['nickname'] = self.nickname
        sending_data['size'] = full_size
        sending_data['pieces'] = pieces
        sending_data['remain'] = remain
        t2s = json.dumps(sending_data)
        t2s += "_E_s_F_"
        self.ser.write(t2s)
        self.ser.flush()
        time.sleep(3) 
        texttmp = '' 
        sending_data = {}
        self.counter = 0

        for i in range(0,pieces+1):
            if i== pieces and remain !=0:

                t2s = ''
                sending_data = {}
                texttmp = self.text[-(remain):]
                self.counter += len(texttmp)
                sending_data['data_remain'] = base64.b64encode(texttmp)
                t2s = json.dumps(sending_data)
                t2s += "_E_0_F_"
                self.ser.write(t2s)
                self.ser.flush()
                self.sendData.emit(self.counter)
                self.endData.emit()
                self.ser.flushInput()
                self.ser.flushOutput()
            elif i == pieces and remain == 0:
                t2s = ''
                sending_data['data_remain'] = base64.b64encode("_")
                t2s = json.dumps(sending_data)
                t2s += "_E_0_F_"
                self.ser.write(t2s)
                self.ser.flush()
                self.endData.emit()
                self.ser.flushInput()
                self.ser.flushOutput()
            else:
                t2s = ''
                sending_data = {}
                texttmp = self.text[size*i:size*(i+1)]
                self.counter += len(texttmp)
                sending_data['data_'+str(i)] =  base64.b64encode(texttmp)
                t2s = json.dumps(sending_data)
                t2s += "_E_0_P_"
                
                self.ser.write(t2s)
                self.ser.flush()
                self.sendData.emit(self.counter)
                time.sleep(self.interval_time)




class Receive(QThread):

    startRCV = Signal(int)
    endRCV = Signal()
    catchESF = Signal(str)
    catchEOP = Signal(int)

    def __init__(self,parent):
        QThread.__init__(self)
        self.iswaitingData = False
        self.data = {} 
        self.size = 0
        self.pieces = 0
        self.remain = 0
        self.filename = None 
        self.nickname = None
        self.type = None
        self.ser = parent.serial_port 
        self.parent = parent
        self.loopRun = True

    def clear_vars(self):
        self.data = {}

    def run(self):
        tdata = ''
        self.counter = 0
        while self.loopRun:
        
            
            iswait = self.ser.inWaiting()
            
            if iswait > 0:
                #self.emit(SIGNAL('startRCV(int)'),self.ser.inWaiting())
                self.startRCV.emit(self.ser.inWaiting())
                if iswait >1024:
                    iswait = 1024
                if tdata == '':
                    tdata = self.ser.read(iswait) 
                else:
                    tdata += self.ser.read(iswait) 
                if "_E_s_F_" in tdata:
                    #self.emit(SIGNAL('catchESF(str)'),tdata)
                    self.catchESF.emit(tdata)

                    tdata = tdata.replace("_E_s_F_","")
                    try:
                        tdata = json.loads(tdata)
                        self.size = tdata['size']
                        self.filename = tdata['filename']
                        self.nickname = tdata['nickname']
                        self.pieces = tdata['pieces']
                        self.remain = tdata['remain']
                        self.type = tdata['type']
                        tdata=''
                    except Exception:
                        print(Exception)
                        tdata=''

                if "_E_0_P_" in tdata:
                    tdata  = tdata.replace("_E_0_P_","")
                    #lenofdata = len(tdata)
                    tdata = json.loads(tdata) 
                    key,value = tdata.popitem() 
                    try:
                        value = base64.b64decode(value)
                    except Exception:
                        print("Problem... b64")
                        print(value)
                    self.data[key]=str(value)
                    lenofdata = len(value)
                    #self.emit(SIGNAL('catchEOP(int)'),lenofdata)
                    self.catchEOP.emit(lenofdata)
                    tdata = ''

                if "_E_0_F_" in tdata:
                    tdata  = tdata.replace("_E_0_F_","")
                    tdata = json.loads(tdata) 
                    key,value = tdata.popitem() 
                    try:
                        value = base64.b64decode(value)
                    except Exception:
                        print("Problem...b64")
                        print(value)
                    self.data[key]=str(value)
                    lenofdata = len(value)
                    #self.emit(SIGNAL('catchEOP(int)'),lenofdata)
                    self.catchEOP.emit(lenofdata)
                    #self.emit(SIGNAL('endRCV()'))
                    self.endRCV.emit()
                    tdata = ''
                    self.counter = 0
                    self.ser.flushInput()
                    self.ser.flushOutput()
            time.sleep(0.5)




#class mainWindow(QMainWindow):
#
#
#
#    def __init__(self):
#        super(MainWindow,self).__init__()
#
#        self.iswaitingData = False
#        self.counter = 0
#
#
#        self.layout = QVBoxLayout()
#
#        self.button2 = QPushButton("Send")
#        self.thread2 = Send()
#        self.receiveThread = Receive()
#        self.connect(self.receiveThread,SIGNAL("startRCV(int)"),self.printMsg)
#        self.connect(self.receiveThread,SIGNAL("finished()"),self.done1)
#        self.connect(self.receiveThread,SIGNAL("endRCV()"),self.done2)
#        self.connect(self.receiveThread,SIGNAL("catchESF()"),self.catchESF)
#        self.connect(self.receiveThread,SIGNAL("catchEOP(int)"),self.catchEOP)
#        self.button2.pressed.connect(self.startT2)
#
#
#        self.buttonrunning = QPushButton("Running?")
#        self.buttonrunning.pressed.connect(self.checkrun)
#
#
#        self.layout.addWidget(self.button2)
#        self.layout.addWidget(self.buttonrunning)
#
#
#
#        w = QWidget()
#        w.setLayout(self.layout)
#        self.setCentralWidget(w)
#        self.show()
#
#        self.receiveThread.start()
#
#
#
#    def startT2(self):
#
#        if not self.iswaitingData:
#            self.thread2.text = text2
#            self.thread2.start()
#            
#        else:
#            print("Cannot Send yet ... receiving...")
#
#    def catchEOP(self,len_of_data):
#        print("catch %i"%len_of_data)
#        self.counter +=  int(len_of_data)
#        print(self.counter)
#
#
#
#    def catchESF(self):
#        print("Found ESF(end of spec file)")
#
#    def done1(self):
#        print("receive terminated")
#
#       
#    def done2(self):
#        self.iswaitingData = False
#        self.counter = 0
#        print("Ended receiving msg")
#        print(self.receiveThread.data)
#
#        
#
#    def printMsg(self,a):
#        self.iswaitingData = True
#        print("strt rcv "+str(a))
#
#    def checkrun(self):
#        print("send is running -> %s"%self.thread2.isRunning())
#        print("receive is  running -> %s"%self.receiveThread.isRunning())
#        print("is waiting data %s"%self.iswaitingData)
#
#app = QApplication([])
#window = MainWindow()
#app.exec_()
