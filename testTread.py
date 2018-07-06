from PySide.QtCore import *
from PySide.QtGui import *
import time
import serial
import sys
import json
import base64
import re

sport = sys.argv[1] 
ser = serial.Serial(port=sport)
print(ser)

text = "a"*10000

interval_time = 4




class send(QThread):


    def __init__(self):
        QThread.__init__(self)
        self.counter = 0


    def run(self):
        print("Start Sending...")
        full_size = len(text)
        print(full_size)
        pieces = full_size/1024
        remain = full_size%1024
        size = 1024
        print((pieces,remain))
        t2s = ''
        sending_data = {}
        sending_data['type'] = 'msg'
        sending_data['filename'] = None
        sending_data['size'] = full_size
        sending_data['pieces'] = pieces
        sending_data['remain'] = remain
        t2s = json.dumps(sending_data)
        t2s += "_E_s_F_"
        print(t2s)
        ser.write(t2s)
        ser.flush()
        time.sleep(4)
        print("now send the msg")
        texttmp = ''
        sending_data = {}
        self.counter = 0

        for i in range(0,pieces+1):
            if i== pieces and remain !=0:

                t2s = ''
                sending_data = {}
                texttmp = text[-(remain):].encode('utf-8')
                self.counter += len(texttmp)
                sending_data['data_remain'] = base64.b64encode(texttmp)
                t2s = json.dumps(sending_data)
                t2s += "_E_0_F_"
                ser.write(t2s)
                ser.flush()
                print(self.counter)
            else:
                t2s = ''
                sending_data = {}
                texttmp = text[size*i:size*(i+1)].encode('utf-8')
                self.counter += len(texttmp)
                sending_data['data_'+str(i)] = base64.b64encode(texttmp)
                t2s = json.dumps(sending_data)
                t2s += "_E_0_P_"
                
                ser.write(t2s)
                ser.flush()
                print(self.counter)
                print("Sleeping...")
                time.sleep(interval_time)




class Receive(QThread):

    def __init__(self):
        QThread.__init__(self)
        self.iswaitingData = False
        self.data = {} 
        self.size = 0
        self.pieces = 0
        self.remain = 0
        self.filename = None 
        self.type = None

    def run(self):
        print("Receiving Started...")
        tdata = ''
        while True:
        
            
            iswait = ser.inWaiting()
            
            if iswait > 0:
                self.emit(SIGNAL('startRCV(int)'),ser.inWaiting())
                if iswait >1024:
                    iswait = 1024
                if tdata == '':
                    tdata = ser.read(iswait) 
                else:
                    tdata += ser.read(iswait) 
                if "_E_s_F_" in tdata:
                    self.emit(SIGNAL('catchESF()'))
                    print(tdata)
                    tdata = tdata.replace("_E_s_F_","")
                    tdata = json.loads(tdata)
                    self.size = tdata['size']
                    self.filename = tdata['filename']
                    self.pieces = tdata['pieces']
                    self.remain = tdata['remain']
                    self.type = tdata['type']
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
                    self.data[key]=value
                    lenofdata = len(value)
                    self.emit(SIGNAL('catchEOP(int)'),lenofdata)
                    tdata = ''

                if "_E_0_F_" in tdata:
                    tdata  = tdata.replace("_E_0_F_","")
                    tdata = json.loads(tdata) 
                    key,value = tdata.popitem() 
                    try:
                        value = base64.b64decode(value)
                    except Exception:
                        print("Problem...b64")
                    self.data[key]=value
                    lenofdata = len(value)
                    self.emit(SIGNAL('catchEOP(int)'),lenofdata)
                    self.emit(SIGNAL('endRCV()'))
                    #send to function to decode base64 and check which pieces are damaged
                    tdata = ''
                    self.counter = 0
            time.sleep(0.5)




class MainWindow(QMainWindow):



    def __init__(self):
        super(MainWindow,self).__init__()

        self.iswaitingData = False
        self.counter = 0


        self.layout = QVBoxLayout()

        self.button2 = QPushButton("Send")
        self.thread2 = send()
        self.receiveThread = Receive()
        self.connect(self.receiveThread,SIGNAL("startRCV(int)"),self.printMsg)
        self.connect(self.receiveThread,SIGNAL("finished()"),self.done1)
        self.connect(self.receiveThread,SIGNAL("endRCV()"),self.done2)
        self.connect(self.receiveThread,SIGNAL("catchESF()"),self.catchESF)
        self.connect(self.receiveThread,SIGNAL("catchEOP(int)"),self.catchEOP)
        self.button2.pressed.connect(self.startT2)


        self.buttonrunning = QPushButton("Running?")
        self.buttonrunning.pressed.connect(self.checkrun)


        self.layout.addWidget(self.button2)
        self.layout.addWidget(self.buttonrunning)



        w = QWidget()
        w.setLayout(self.layout)
        self.setCentralWidget(w)
        self.show()

        self.receiveThread.start()



    def startT2(self):

        if not self.iswaitingData:
            self.thread2.start()
        else:
            print("Cannot Send yet ... receiving...")

    def catchEOP(self,len_of_data):
        print("catch %i"%len_of_data)
        self.counter +=  int(len_of_data)
        print(self.counter)



    def catchESF(self):
        print("Found ESF")

    def done1(self):
        print("receive terminated")

       
    def done2(self):
        self.iswaitingData = False
        print("Ended receiving msg")

    def printMsg(self,a):
        self.iswaitingData = True
        print("strt rcv "+str(a))

    def checkrun(self):
        print("send is running -> %s"%self.thread2.isRunning())
        print("receive is  running -> %s"%self.receiveThread.isRunning())
        print("is waiting data %s"%self.iswaitingData)

app = QApplication([])
window = MainWindow()
app.exec_()
