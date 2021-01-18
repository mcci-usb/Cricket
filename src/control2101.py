##############################################################################
# 
# Module: control2101.py
#
# Description:
#     Scan the USB bus and get the list of Model2101 devices attached
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
#     V2.0.0 Fri Jan 15 2021 18:50:59 seenivasan
#       Module created
##############################################################################
# Future imports
from __future__ import print_function
from __future__ import with_statement

# Built-in imports
import sys
import os
import usb.util

# Lib imports
from usb.backend import libusb1
import xml.dom.minidom

if sys.platform == 'darwin':
    import hid
    
import time

##############################################################################
# Utilities
##############################################################################
# Arguments:
VID_2101 = 0x040e
PID_2101 = 0xf413

"""
Called by check_port() in search.py, to monitor the 
device unplug from the bus
Scan list of 2101 in the USB bus, returns a list with 
Serial number of 2101
Args:
    No arguments
Returns:
    No return
"""
def scan_2101():
    dlist = []
    if sys.platform == 'darwin':
        for d in hid.enumerate(VID_2101):
            dlist.append(d['serial_number'])
    else:
        # find our devic
        for dev in usb.core.find(idVendor=VID_2101, idProduct=PID_2101, find_all=1): 
            dlist.append(get_serial_number(dev))
    return dlist
"""
Get Serial number for the 2101
Args:
    dev: serial number of device 2101
Returns:
    return serial number
"""
def get_serial_number(dev):
    ret = dev.ctrl_transfer(0x80, 0x06, 0x303, 0x409, 0x1a)

    # Create data buffers
    intarr = []
    # length of array in integer
    alen = int(len(ret)/2) - 1
    k = 2
        
    for i in range(alen):
        byt = [ret[k], ret[k+1]]
        intpack = int.from_bytes(byt, byteorder='little')
        intarr.append(intpack)
        k = k + 2
        
    slno = "".join(map(chr, intarr))
    return slno
"""
Get Device path for the selected serial number of 2101
Only for hid in Mac
Args:
    serialno: serial number of device 2101
Returns:
    return serial number
"""
def get_path(serialno):
    path = None
    # Real device
    for d in hid.enumerate(VID_2101):
        if(serialno == d['serial_number']):
            path = d['path']
            break
    return path

"""
Get Device object for the selected serial number of 2101
for Windows and Linux   
Args:
    serialno: serial number of device 2101
Returns:
    return serial number
"""     
def get_device(serialno):
    dev2101 = None
    # will return Device object with device VendorID, ProductID
    for dev in usb.core.find(idVendor=VID_2101, idProduct=PID_2101, find_all=1): 
        #if(serialno == usb.util.get_string(dev, 3)):
        if(serialno == get_serial_number(dev)):
            dev2101 = dev
            break
    return dev2101
"""
Controlling 2101 port for 2101 operations 
Args:
    serialno: serial number of device 2101
    portdata: portdata return device highspeed and superspeed
"""      
def control_port(serialno, portdata):
    result = None
    # run in Darwin or Mac OS
    if sys.platform == 'darwin':
        devpath = get_path(serialno)
        dev = hid.device()
        dev.open_path(devpath)
        result = dev.write([portdata])
        dev.close()
    else:
        dev = get_device(serialno)
        if dev is not None:
            # run in Linux OS
            if sys.platform == 'linux':
                if dev.is_kernel_driver_active(0):
                    dev.detach_kernel_driver(0) 
            usbd = []
            usbd.append(portdata)
            usbd.append(0x00)
            # ctrl_transfer method. It is used both for OUT and IN transfers
            result = dev.ctrl_transfer(0x21, 0x09, 0x200, 0x00, usbd)
    return result