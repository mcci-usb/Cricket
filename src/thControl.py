##############################################################################
# 
# Module: thControl.py
#
# Description:
#     Receive device function commands from resepective device window
#     Check if the device is available in network, then send command to server
#     If the device is available in same computer then send command to device
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
#     Seenivasan V, MCCI Corporation June 2021
#
# Revision history:
#     V2.4.0-2 Wed June 14 2021 18:50:10 seenivasan
#       Module created
##############################################################################
# Built-in imports

import thClient as thnw
import usbDev as thlocal
import socket
import json

from uiGlobals import *

def SetDeviceControl(top):
    """
    set a device control through serial or Netwotk
    Args:
        top:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Return:
       None
    """  
    if not top.ldata['hc']:
        if top.ldata['thcif'] == 'serial':
            # serial not implemented
            top.thCtrl = "serial"
            pass
        else:
            top.thCtrl = "network"
            #OpenNetwork(top)
    else:
        top.thCtrl = "local"

def ResetDeviceControl(top):
    """
    Reset the device
    Args:
        top:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Return:
        None 
    """
    if top.hcclient != None:
        top.clienthc.close()
        top.hcclient.close()

def get_tree_change(top):
    """
    get the device tree change info throgh network
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Return:
        None

    """
    if top.thCtrl == "local":
        dl, newlist = thlocal.get_usb_tree()
        thlocal.get_tree_change(top, dl, newlist)
    elif top.thCtrl == "network":
        resdict = thnw.get_usb_tree(top.ldata['thcid'], int(top.ldata['sthcpn']))
        if resdict["result"][0]["status"] == "OK":
            findict = resdict["result"][1]["data"]
            if findict[0] == -1:
                top.device_no_response()
                return
            thlocal.get_tree_change(top, findict[0], findict[1])    
        else:
            top.print_on_log("TH Computer Connection Fail!\n")
            top.device_no_response()           