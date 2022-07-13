from tkinter import *
import socket, threading
import time
import datetime
import sys
import os
import random
from pymodbus.client.sync import ModbusTcpClient
import struct

def data_to_float32(data) :
    #return struct.unpack('<f',struct.pack('=I',concatData(data)))[0]
    return concatData(data)
def concatData (data):
    msb=struct.pack('=I',data[0])
    lsb=struct.pack('=I',data[1]<<16)
    return struct.unpack('<f',msb[0:2] + lsb[2:4])
#int(bytearray((msb[0:2]+lsb[2:4]).encode()))

class arc_it(Frame) :
    def on_closing(self) :
        self.run = False
        os._exit(0)
    def tare(self):
        if self.coil_state == 0x00 :
          self.coil_state = 0xff
        else :
          self.coil_state = 0x00
        #msg = chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x06) + chr(0x00)#trans protocol length unit
        #msg = msg + chr(0x05) + chr(0x00) + chr(0x0a) + chr(0x00) + chr(self.coil_state)
        #self.ser.send( msg.encode('iso-8859-1') )
        #response = self.ser.recv(12).decode('iso-8859-1')
        self.mbc.write_coil(0x0a,self.coil_state, unit=1)
        self.read_mass()
    def set_zero(self) :
        zero = float(self.z_entry.get())
        z_bytes = struct.pack('<f',zero)
        self.mbc.write_register(4,z_bytes,unit=1)
        #msg = chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x0a) + chr(0x00)#trans protocol length unit
        #msg = msg + chr(0x10) + chr(0x00) + chr(0x04) + chr(0x00) + chr(0x02) + chr(z_bytes[0]) + chr(z_bytes[1]) + chr(z_bytes[2]) + chr(z_bytes[3])
        #self.ser.send( msg.encode('iso-8859-1') )
        #response = self.ser.recv(10).decode('iso-8859-1')#comment out these lines later
        self.read_mass()
    def set_cal(self) :
        cal_factor = float(self.cal_entry.get())
        cal_bytes = struct.pack('>f',cal_factor)
        #self.mbc.write_register(4,int(bytearray(cal_bytes[0:2].encode())),unit=1)
        #self.mbc.write_register(5,int(bytearray(cal_bytes[2:4].encode())),unit=1)
        lsInt = int.from_bytes(cal_bytes[2:4], 'big')
        msInt = int.from_bytes(cal_bytes[0:2], 'big')
        self.mbc.write_register(2,lsInt,unit=1)
        self.mbc.write_register(3,msInt,unit=1)
                        #int(bytearray((msb[0:2]+lsb[2:4]).encode()))
       # msg = chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x0a) + chr(0x00)#trans protocol length unit
       # msg = msg + chr(0x10) + chr(0x00) + chr(0x02) + chr(0x00) + chr(0x02) + chr(cal_bytes[0]) + chr(cal_bytes[1]) + chr(cal_bytes[2]) + chr(cal_bytes[3])
        #self.ser.send( msg.encode('iso-8859-1') )
        #response = self.ser.recv(10).decode('iso-8859-1')#comment out these lines later 
        self.read_mass()

    def read_mass(self) :
        #msg = chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x06) + chr(0x00)#trans protocol length unit
        #msg = msg + chr(0x03) + chr(0x00) + chr(0x00) + chr(0x00) + chr(0x02)
        #self.ser.send( msg.encode('iso-8859-1') )
        #resp = self.ser.recv(13).decode('iso-8859-1')
        #print(resp)
        #mass_val = struct.unpack('>f',bytes((resp[9]+resp[10]+resp[11]+resp[12]).encode('iso-8859-1')))[0]
        #self.mass_disp.delete('1.0','end')
        #self.mass_disp.insert('1.0',str(mass_vafol))
        regval = self.mbc.read_holding_registers(0,2,unit=1) #maybe write a while loop here to repeatedly call read_holding_registers
        mass_val = data_to_float32(regval.registers)
        self.mass_disp.delete('1.0','end')
        #frts='{:.5f}'.format(mass_val)
        self.mass_disp.insert('1.0',str(mass_val[0]))


    def keepAlive(self):   #runs a while loop "forever" and it calls read_holding_register() (read the coil state) and read it every 
        while True:
            self.mbc.read_holding_registers(0,2,unit=1)
            time.sleep(1.0)
  

        
    def __init__(self):
        self.window = Tk()
        self.window.geometry('360x128')
        self.window.title( 'scale calibrator' )
        #self.ser = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        #self.ser.connect(('localhost',502))
        self.mbc = ModbusTcpClient('10.0.0.4')
        Label(self.window, text='calibration factor').grid(row=0)
        #Label(self.window, text='zero offset').grid(row=1)
        Label(self.window, text='kg').grid(row=2)
        
        self.cal_entry = Entry(self.window)
        self.z_entry = Entry(self.window)
        self.mass_disp = Text(self.window,height=1,width=20)

        self.cal_entry.grid(row=0,column=1)
        #self.z_entry.grid(row=1,column=1)
        self.mass_disp.grid(row=2,column=1)

        self.coil_state = 0x00

        Button(self.window,text='Send',command=self.set_cal).grid(row=0,column=2)
        #Button(self.window,text='Send',command=self.set_zero).grid(row=1,column=2)
        Button(self.window,text='TARE',command=self.tare).grid(row=3,column=1)
 
        self.window.protocol( 'WM_DELETE_WINDOW', self.on_closing )
        self.keepalivethread=threading.Thread(target=self.keepAlive)
        #self.keepalivethread.start()
        self.window.mainloop()
        
appl = arc_it()



   
