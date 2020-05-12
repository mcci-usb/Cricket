#======================================================================
# (c) 2020  MCCI Inc.
#----------------------------------------------------------------------
# Project : UI3141/3201 GUI application
# File    : search.py
#----------------------------------------------------------------------
# Script for scanning the switches connected to the Com Port.
#======================================================================

#======================================================================
# IMPORTS
#======================================================================

import serial.tools.list_ports
import serial
import time


#======================================================================
# COMPONENTS
#======================================================================

def check_port():
    comlist = serial.tools.list_ports.comports()
    port_name = []
    
    for port, desc, hwid in sorted(comlist):
        if(hwid.find('USB VID:PID=045E:0646')!= -1):
            port_name.append(port)
    return port_name

def search_port():
    comlist = serial.tools.list_ports.comports()
    port_name = []
    rev_list = []
    dev_list = []

    for port, desc, hwid in sorted(comlist):
        if(hwid.find('USB VID:PID=045E:0646')!= -1):
            port_name.append(port)
    
    for i in range(len(port_name)):
        try:
            ser = serial.Serial(port=port_name[i], baudrate=115200, 
                                bytesize=serial.EIGHTBITS,
                                parity=serial.PARITY_NONE, timeout=1, 
                                stopbits=serial.STOPBITS_ONE)

            time.sleep(1)
    
            cmd = 'version\r\n'
    
            ser.write(cmd.encode())
            strout = ser.readline().decode('utf-8')
            nstr = strout[2:]
            if(nstr.find('01') != -1):
                rev_list.append(port_name[i])
                dev_list.append('3141')
            elif(nstr.find('12') != -1):
                rev_list.append(port_name[i])
                dev_list.append('3201')
            ser.close()
        except serial.SerialException as e:
            pass
    rdict = dict(zip(rev_list, dev_list))
    return rdict