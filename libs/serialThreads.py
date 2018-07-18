import ConfigParser
import base64
import json
import time

from PySide.QtCore import *

"""
possible types:
msg - message
file - file
not implemented yet ... resend - request to resend chunks that were damaged
"""
settingsparser = ConfigParser.ConfigParser()
settingsparser.read('config/settings.ini')

chunk_size = int(settingsparser.get("app_settings","chunk_size"))
time_to_sleep_receive_loop = float(settingsparser.get("app_settings","time_to_sleep_receive_loop"))
time_to_sleep_after_esf = float(settingsparser.get("app_settings","time_to_sleep_after_esf"))
acp127_prefix = str(settingsparser.get("acp_127","prefix"))
acp127_postfix = str(settingsparser.get("acp_127","postfix"))

class Send(QThread):
    
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
        self.parent = parent

    def run(self):

        if type(self.text) == unicode:
            self.text = self.text.encode('utf-8')
        full_size = len(self.text)
        self.totalData.emit(full_size)
        pieces = full_size/chunk_size
        remain = full_size%chunk_size
        size = chunk_size 
        t2s = ''
        if self.parent.acp127:
            t2s = acp127_prefix 
        sending_data = {}
        sending_data['type'] = self.type 
        sending_data['filename'] = self.filename 
        sending_data['nickname'] = self.nickname
        sending_data['size'] = full_size
        sending_data['pieces'] = pieces
        sending_data['remain'] = remain
        try:
            t2s += json.dumps(sending_data)
        except Exception as e:
            print(e)
        t2s += "_E_s_F_"
        if self.parent.acp127:
            t2s += acp127_postfix 
        self.ser.write(t2s)
        self.ser.flush()
        time.sleep(time_to_sleep_after_esf)
        texttmp = '' 
        sending_data = {}
        self.counter = 0

        for i in range(0,pieces+1):
            if i== pieces and remain !=0:
                t2s = ''
                if self.parent.acp127:
                    t2s =  acp127_prefix
                sending_data = {}
                texttmp = self.text[-(remain):]
                self.counter += len(texttmp)
                sending_data['data_remain'] = base64.b64encode(texttmp)
                try:
                    t2s += json.dumps(sending_data)
                except Exception as e:
                    print(e) 
                t2s += "_E_0_F_"
                if self.parent.acp127:
                    t2s += acp127_postfix 
                self.ser.write(t2s)
                self.ser.flush()
                self.sendData.emit(self.counter)
                self.endData.emit()
                self.ser.flushInput()
                self.ser.flushOutput()
            elif i == pieces and remain == 0:
                t2s = ''
                if self.parent.acp127:
                    t2s = acp127_prefix
                sending_data['data_remain'] = base64.b64encode("_")
                try:
                    t2s += json.dumps(sending_data)
                except Exception as e:
                    print(e)
                t2s += "_E_0_F_"
                if self.parent.acp127:
                    t2s += acp127_postfix 
                self.ser.write(t2s)
                self.ser.flush()
                self.endData.emit()
                self.ser.flushInput()
                self.ser.flushOutput()
            else:
                t2s = ''
                if self.parent.acp127:
                    t2s = acp127_prefix
                sending_data = {}
                texttmp = self.text[size*i:size*(i+1)]
                self.counter += len(texttmp)
                sending_data['data_'+str(i)] =  base64.b64encode(texttmp)
                try:
                    t2s += json.dumps(sending_data)
                except Exception as e:
                    print(e)
                t2s += "_E_0_P_"
                if self.parent.acp127:
                    t2s += acp127_postfix
                self.ser.write(t2s)
                self.ser.flush()
                self.sendData.emit(self.counter)
                time.sleep(self.interval_time)


class Receive(QThread):

    start_receive_signal = Signal(int)
    end_receive_signal = Signal()
    catch_esf_signal = Signal(str)
    catch_eop_signal = Signal(int)
    interface_problem_signal = Signal(str)

    def __init__(self,parent):
        QThread.__init__(self)
        self.is_waiting_data = False
        self.data = {} 
        self.size = 0
        self.pieces = 0
        self.remain = 0
        self.filename = None 
        self.nickname = None
        self.type = None
        self.ser = parent.serial_port 
        self.parent = parent
        self.loop_run = True
        self.tdata = ''

    def clear_vars(self):
        self.data = {}
        self.tdata = ''

    def run(self):

        self.tdata = ''
        self.counter = 0
        while self.loop_run:
        
            
            try:
                iswait = self.ser.inWaiting()
            except Exception as e:
                print(e)
                self.interface_problem_signal.emit(str(e))
            
            
            if iswait > 0:
                self.start_receive_signal.emit(self.ser.inWaiting())
                if iswait > chunk_size:
                    iswait = chunk_size 
                if self.tdata == '':
                    self.tdata = self.ser.read(iswait) 
                else:
                    self.tdata += self.ser.read(iswait) 
                if "_E_s_F_" in self.tdata:
                    if self.parent.acp127 :
                        self.tdata = self.tdata.replace(acp127_prefix,"")
                        self.tdata = self.tdata.replace(acp127_postfix,"")
                        

                    self.tdata = self.tdata.replace("_E_s_F_","")
                    self.catch_esf_signal.emit(self.tdata)
                    try:
                        self.tdata = json.loads(self.tdata)
                        self.size = self.tdata['size']
                        self.filename = self.tdata['filename']
                        self.nickname = self.tdata['nickname']
                        self.pieces = self.tdata['pieces']
                        self.remain = self.tdata['remain']
                        self.type = self.tdata['type']
                        self.tdata=''
                    except Exception:
                        print(Exception)
                        self.tdata=''

                if "_E_0_P_" in self.tdata:
                    if self.parent.acp127 :
                        self.tdata = self.tdata.replace(acp127_prefix,"")
                        self.tdata = self.tdata.replace(acp127_postfix,"")
                    self.tdata  = self.tdata.replace("_E_0_P_","")
                    try:
                        self.tdata = json.loads(self.tdata) 
                        key,value = self.tdata.popitem() 
                        value = base64.b64decode(value)
                    except Exception:
                        print("Problem... b64")
                        print(value)
                    self.data[key]=str(value)
                    lenofdata = len(value)
                    self.catch_eop_signal.emit(lenofdata)
                    self.tdata = ''

                if "_E_0_F_" in self.tdata:
                    if self.parent.acp127 :
                        self.tdata = self.tdata.replace(acp127_prefix,"")
                        self.tdata = self.tdata.replace(acp127_postfix,"")
                    self.tdata  = self.tdata.replace("_E_0_F_","")
                    try:
                        self.tdata = json.loads(self.tdata) 
                        key,value = self.tdata.popitem() 
                        value = base64.b64decode(value)
                    except Exception:
                        print("Problem...b64")
                        print(value)
                    self.data[key]=str(value)
                    lenofdata = len(value)
                    self.catch_eop_signal.emit(lenofdata)
                    self.end_receive_signal.emit()
                    self.tdata = ''
                    self.counter = 0
                    self.ser.flushInput()
                    self.ser.flushOutput()
            time.sleep(time_to_sleep_receive_loop)
