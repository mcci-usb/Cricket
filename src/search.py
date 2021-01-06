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
import os

import control2101 as d2101
from uiGlobals import *


#======================================================================
# COMPONENTS
#======================================================================

# Check the connected device is unplugged
def check_port():
    comlist = serial.tools.list_ports.comports()
    port_name = []
    
    for port, desc, hwid in sorted(comlist):
        if(hwid.find('USB VID:PID=045E:0646')!= -1):
            port_name.append(port)
    dlist = d2101.scan_2101()
    for dev in dlist:
        port_name.append(dev)
    return port_name

# Search USB port for list of Plugged devices
# Filtered the devices using VID and PID
# Required by comWindow.py for device search
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
                dev_list.append(DEVICES[DEV_3141])
            elif(nstr.find('12') != -1):
                rev_list.append(port_name[i])
                dev_list.append(DEVICES[DEV_3201])
            ser.close()
        except serial.SerialException as e:
            pass
    rdict = dict(zip(rev_list, dev_list))
    return rdict