from PySide.QtCore import *
from PySide.QtGui import *
import time
import serial
import os
import base64
import json
import datetime


__mod_comports = None
__mod_glob = None
__serial_ports = {}



class initApp(QThread):

    def __init__(self,parent):
        QThread.__init__(self)
        #self.nickname = parent.__nickname
        #self.default_save_folder = parent.__default_save_folder
        #self.serial_port = parent.__serial_port
        self.__serial_ports = {}


    def init__serial(self):

        global __mod_glob
        global __mod_comports
        global __isNT
        os_name = os.name

        try:
            if os_name == 'posix':
                __isNT = False
                from serial.tools.list_ports_posix import comports
                __mod_comports = comports
                from serial.tools.list_ports_posix import glob
                __mod_glob = glob
            elif os_name == 'nt':
                __isNT = True
                from serial.tools.list_ports_windows import comports
                __mod_comports = comports
        
        except ImportError as iError:
            print("[!!]Import Error: %s"%iError)
            
    def get_serials(self):

        global __mod_glob
        global __mod_comports
        counter = 0
        __total_ports = []



        for ports in __mod_comports():
            self.__serial_ports[counter] = ports[0]
            counter +=1
        if not __isNT:
            for ports in __mod_glob.glob('/dev/pts/*'):
                self.__serial_ports[counter] = ports
                counter +=1
        for ports in self.__serial_ports:
            __total_ports.append(self.__serial_ports[ports])
        return __total_ports

    def set_serial(self,**kwargs):

            
        try:
            if len(kwargs) == 1:

                serialInterface = serial.Serial(port=kwargs['port'])

            if len(kwargs) > 1:
                
                bytesize_table={ 5:serial.FIVEBITS,6:serial.SIXBITS,7:serial.SEVENBITS,8:serial.EIGHTBITS}
                par_table = {  'None':serial.PARITY_NONE , 'Odd':serial.PARITY_ODD , 'Even':serial.PARITY_EVEN}
                stop_table = { '1':serial.STOPBITS_ONE,'1,5':serial.STOPBITS_ONE_POINT_FIVE,'2':serial.STOPBITS_TWO}
                serialInterface  = serial.Serial(port=kwargs['port'],baudrate=kwargs['baudrate'],bytesize=bytesize_table[int(kwargs['bytesize'])],parity=par_table[kwargs['parity']],stopbits=stop_table[kwargs['stopbits']],xonxoff=kwargs['xonxoff'],rtscts=kwargs['rtscts'])
            
            #do i need this????
            serialInterface.timeout = 1
            serialInterface.flushInput()
            serialInterface.flushOutput()

            return serialInterface 

        except Exception as e:

            return e






