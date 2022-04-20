##############################################################################
# 
# Module: control2101.py
#
# Description:
#     Scan the USB bus and get the list of Model 2101 devices attached
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
#    V2.6.0 Wed Apr 20 2022 17:00:00   Seenivasan V
#       Module created
##############################################################################
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

VID_2101 = 0x040e
PID_2101 = 0xf413

class Dev2101:
    """
    A  class Dev2101 with init method
    """
    def __init__(self, top):
        """
        here the function init method is serial number 
        list and device list, path list
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            top: creates an object
        Returns:
            None
        """
        self.slno_list = []
        self.path_list = []
        self.dev_list = []
        self.slno = None
        self.path = None
        self.dev = None
        self.top = top
        self.ready = False

    def get_2101(self):
        """
        get the model2101 enumaration in darwin 
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns: 
            dlist: return same device model
        """
        dlist = []
        if sys.platform == 'darwin':
            dev = hid.enumerate(VID_2101, PID_2101)
            if len(dev) != 0:
                for dev in hid.enumerate(VID_2101, PID_2101):
                    dlist.append(dev['serial_number'])
        else:
            for dev in usb.core.find(idVendor=VID_2101, idProduct=PID_2101, 
                                     find_all=1):
                slno =  self.get_serial_number(dev)
                dlist.append(slno)
        return dlist

    def scan_2101(self):
        """
        scanning the device model 2101 device

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        dlist = []
        self.slno_list.clear()
        
        if sys.platform == 'darwin':
            self.path_list.clear()
        
            dev = hid.enumerate(VID_2101, PID_2101)
            if len(dev) != 0:
                for dev in hid.enumerate(VID_2101, PID_2101):
                    print("SlNo: ", dev['serial_number'])
                    try:
                        dlist.append(dev['serial_number'])
                        self.slno_list.append(dev['serial_number'])
                        self.path_list.append(dev['path'])
                    except:
                        print("Path Error")
        else:
            self.dev_list.clear()
            for dev in usb.core.find(idVendor=VID_2101, idProduct=PID_2101, 
                                     find_all=1):
                slno =  self.get_serial_number(dev)
                dlist.append(slno)
                self.slno_list.append(slno)
                self.dev_list.append(dev)

        self.ready = True
        return dlist

    def get_serial_number(self, dev):
        """
        Get Serial number of the model 2101 device

        Args:
            dev: 2101 device found in the USB bus 
        Returns:
            serial number of the device in String format
        """
        ret  = None

        try:
            ret = dev.ctrl_transfer(0x80, 0x06, 0x303, 0x409, 0x1a)
        except:
            ret = None

        # Create data buffers
        intarr = []
        # Length of array in integer
        alen = int(len(ret)/2) - 1
        k = 2
        
        for i in range(alen):
            byt = [ret[k], ret[k+1]]
            intpack = int.from_bytes(byt, byteorder='little')
            intarr.append(intpack)
            k = k + 2
        
        slno = "".join(map(chr, intarr))
        return slno

    def select_usb_device(self, serialno):
        """
        select usb device model 2101 in darwin and windows with serail number
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
            top: creates an object
        Returns:
            True: serial is True
        """
        self.slno = None
        self.path = None
        
        if sys.platform == 'darwin':
            for i in range(len(self.slno_list)):
                if(self.slno_list[i] == serialno):
                    self.slno = serialno
                    self.path = self.path_list[i]
                    break
        else:
            for i in range(len(self.slno_list)):
                if(self.slno_list[i] == serialno):
                    self.slno = serialno
                    self.dev = self.dev_list[i]
                    break
            
        if self.slno == serialno:
            return True
        else:
            return False

    def control_port(self, cmd):
        """
        contrlling the ports in windows, Linux, darwin
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            cmd:device write  command sending to port
        Returns:
            result: is succes return ro control trasfer
        """
        result = None

        # run in Darwin or Mac OS
        if sys.platform == 'darwin':
            dev = hid.device()
            dev.open_path(self.path)
            result = dev.write([cmd])
            dev.close()
        else:
            if self.dev is not None:
                # run in Linux OS
                if sys.platform == 'linux':
                    if self.dev.is_kernel_driver_active(0):
                        self.dev.detach_kernel_driver(0) 
                usbd = []
                usbd.append(cmd)
                usbd.append(0x00)
                # ctrl_transfer method. It is used both for OUTandIN transfers
                try:
                    result = self.dev.ctrl_transfer(0x21, 0x09, 0x200, 0x00, usbd)
                except:
                    result = None
        return result