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
#    V4.0.0 Wed May 25 2023 17:00:00   Seenivasan V
#       Module created
##############################################################################
# Built-in imports

import thClient as thnw
import usbDev as thlocal
import socket
import json
import sys

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
    if top.myrole['uc'] == True:
        if top.myrole['thc'] == True:
            top.thCtrl = "local"
        else:
            top.thCtrl = "network"


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
        if sys.platform.startswith("win"):
            updtu4list = thlocal.get_usbandusb4_tree()
            if len(top.masterList) == 0:
                for dev in updtu4list:
                    top.masterList.append(dev)
            thlocal.get_u4_tree_change(top, updtu4list)
            top.save_usb_list(updtu4list)

        else:
            dl, newlist = thlocal.get_usb_tree()
            thlocal.get_tree_change(top, dl, newlist)
            
            if sys.platform == "darwin":
                newdict = thlocal.get_tb_tree()
                thlocal.get_tb_tree_change(top, newdict)

    elif top.thCtrl == "network":
        resdict = thnw.get_usb_tree(top.ldata['thcid'],
                                int(top.ldata['sthcpn']))
        if resdict["result"][0]["status"] == "OK":
            findict = resdict["result"][1]["data"]
            if findict[0] == -1:
                top.device_no_response()
                return
            thlocal.get_tree_change(top, findict[0], findict[1])    
        else:
            top.print_on_log("TH Computer Connection Fail!\n")
            top.device_no_response()           