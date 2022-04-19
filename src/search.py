##############################################################################
# 
# Module: search.py
#
# Description:
#     Script for scanning the switches connected to the Com Port.
#
# Copyright notice:
#     This file copyright (c) 2020 by
#
#         MCCI Corporation
#         3520 Krums Corners Road
#         Ithaca, NY  14850
#
#     Released under the MCCI Corporation.
#
# Author:
#     Seenivasan V, MCCI Corporation Mar 2020
#
# Revision history:
#    V2.5.0 Fri Jan 07 2022 17:40:05   Seenivasan V
#       Module created
##############################################################################
# Lib imports
import serial.tools.list_ports
import serial
import time

# Built-in imports
import os

# Own modules
import control2101 as d2101
from uiGlobals import *

##############################################################################
# Utilities
##############################################################################
def filter_port():
    """
    filter the Comports list from list UI supported Switch with same VID and PID.
    Args:
        No argument
    Return:
        port_name -  list of availablable port numbers and serial number of 
        the 2101     
    """
    usb_hwid_str = ["USB VID:PID=045E:0646", "USB VID:PID=2341:0042"]
    comlist = serial.tools.list_ports.comports()
    port_name = []

    for port, desc, hwid in sorted(comlist):
        res = [True for gnhwid in usb_hwid_str if(gnhwid in hwid)]
        if(res):
            port_name.append(port)
    return port_name

def check_port(usbHand):
    """
    Scan the USB port and collect all the device under a list
    Args:
        No argument
    Return:
        port_name -  list of availablable port numbers and serial number of 
        the 2101     
    """
    comlist = serial.tools.list_ports.comports()
    port_name = []
    
    for port, desc, hwid in sorted(comlist):
        port_name.append(port)
    
    dlist = usbHand.get_2101()
    for dev in dlist:
        port_name.append(dev)
    return port_name

def search_port(usbHand):
    """
    Search USB port for list of Plugged devices
    Filter 3141, 3201,  2101 and 2301 from the list
    Args:
        No argument
    Return:
        rdict - A dictionary of two lists, one for port number and another for
        Model number
    """
    # It will print a list of available ports

    port_name = []

    # comlist = serial.tools.list_ports.comports()
    # for port, desc, hwid in sorted(comlist):
    #     port_name.append(port)
    port_name = filter_port()

    #port_name = []
    rev_list = []
    dev_list = []

    #for port, desc, hwid in sorted(comlist):
    #    port_name.append(port)
    
    for i in range(len(port_name)):
        try:
            # Open serial port
            # Here the baudrate 115200 as support Model 3141 and Model 3201
            ser = serial.Serial(port=port_name[i], baudrate=115200, 
                                bytesize=serial.EIGHTBITS,
                                parity=serial.PARITY_NONE, timeout=1, 
                                stopbits=serial.STOPBITS_ONE)
            # Delay execution for a given number of seconds
            # Let's wait one second before reading output
            # give the serial port sometime to receive the data

            time.sleep(1)
    
            cmd = 'version\r\n'
    
            ser.write(cmd.encode())

            # Printing the decoded string
            strout = ser.readline().decode('utf-8')
            nstr = strout[2:]
            if(nstr.find('01') != -1):
                rev_list.append(port_name[i])
                dev_list.append(DEVICES[DEV_3141])
            elif(nstr.find('12') != -1):
                rev_list.append(port_name[i])
                dev_list.append(DEVICES[DEV_3201])
            # close the serial
            ser.close()
            # Here the baudrate as fixed the 9600 
            # baudrate supports Model 2301 device
            ser = serial.Serial(port=port_name[i], baudrate=9600, 
                                bytesize=serial.EIGHTBITS,
                                parity=serial.PARITY_NONE, timeout=1, 
                                stopbits=serial.STOPBITS_ONE)
            time.sleep(1)
    
            cmd = 'version\r\n'
    
            ser.write(cmd.encode())
            strout = ser.readline().decode('utf-8')
            nstr = strout[2:]
            if(nstr.find('08') != -1):
                rev_list.append(port_name[i])
                dev_list.append(DEVICES[DEV_2301])
            ser.close()
        # There is no new data from serial port
        except serial.SerialException as e:
            pass
    dlist = usbHand.scan_2101()

    for dl in dlist:
        rev_list.append(dl)
        dev_list.append(DEVICES[DEV_2101])

    rdict = {}
    devlist = []
    
    for i in range(len(rev_list)):
        tempdict = {}
        tempdict["port"] = rev_list[i]
        tempdict["model"] = dev_list[i]
        devlist.append(tempdict)

    rdict["devices"] = devlist
    return rdict