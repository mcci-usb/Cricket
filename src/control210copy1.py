#======================================================================
# (c) 2020  MCCI Inc.
#----------------------------------------------------------------------
# Project : UI3141/3201 GUI Application
# File    : getusb.py
#----------------------------------------------------------------------
#  Scan the USB bus and get the list of devices attached
#======================================================================

#======================================================================
# IMPORTS
#======================================================================
from __future__ import print_function
from __future__ import with_statement
import sys
import os
import usb.util
from usb.backend import libusb1
import xml.dom.minidom

if sys.platform == 'darwin':
    import hid
    
import time

#======================================================================
# COMPONENTS
#======================================================================
VID_2101 = 0x040e
PID_2101 = 0xf413

def scan_2101():
    dlist = []
    if sys.platform == 'darwin':
        for d in hid.enumerate(VID_2101):
            dlist.append(d['serial_number'])
    else:
        for dev in usb.core.find(idVendor=VID_2101, idProduct=PID_2101, find_all=1): 
            #dlist.append(usb.util.get_string(dev, 3))
            dlist.append(get_serial_number(dev))
    return dlist


def get_serial_number(dev):
    ret = dev.ctrl_transfer(0x80, 0x06, 0x303, 0x409, 0x1a)
    intarr = []
    alen = int(len(ret)/2) - 1
    k = 2
        
    for i in range(alen):
        byt = [ret[k], ret[k+1]]
        intpack = int.from_bytes(byt, byteorder='little')
        intarr.append(intpack)
        k = k + 2
        
    slno = "".join(map(chr, intarr))
    return slno

    
def get_path(serialno):
    path = None
    for d in hid.enumerate(VID_2101):
        if(serialno == d['serial_number']):
            path = d['path']
            break
    return path
    
    
def get_device(serialno):
    dev2101 = None
    for dev in usb.core.find(idVendor=VID_2101, idProduct=PID_2101, find_all=1): 
        #if(serialno == usb.util.get_string(dev, 3)):
        if(serialno == get_serial_number(dev)):
            dev2101 = dev
            break
    return dev2101
    
    
def control_port(serialno, portdata):
    result = None
    if sys.platform == 'darwin':
        devpath = get_path(serialno)
        dev = hid.device()
        dev.open_path(devpath)
        result = dev.write([portdata])
        dev.close()
    else:
        dev = get_device(serialno)
        if dev is not None:
            usbd = []
            usbd.append(portdata)
            usbd.append(0x00)
            result = dev.ctrl_transfer(0x21, 0x09, 0x200, 0x00, usbd)
    return result

