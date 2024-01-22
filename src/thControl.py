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
#    V4.3.0 Mon Jan 22 2024 17:00:00   Seenivasan V
#       Module created
##############################################################################
# Built-in imports

import thClient as thnw
import usbChange as thlocal
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
    if not top.myrole['thc']:
        if top.myrole['uc']:
            try:
                if top.ucConfig['mynodes']["mythc"]['interface'] == 'serial':
                    top.thCtrl = "serial"
                    pass
                else:
                    top.thCtrl = "tcp"
            except:
                top.thCtrl = "tcp"
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
    if top.thCtrl == "local":
        thlocal.get_usb_change(top)
    elif top.thCtrl == "tcp":
        nwip = top.ucConfig['mynodes']["mythc"]["tcp"]["ip"]
        nwport = top.ucConfig['mynodes']["mythc"]["tcp"]["port"]
      
        resdict = thnw.get_usb_tree(nwip, int(nwport))
        
        if len(resdict) > 0:
            
            if resdict["result"][0]["status"] == "OK":
                findict = resdict["result"][1]["data"]
                thlocal.prepare_tree_change(top, findict["usb3d"], findict["usb4d"])
                if findict["tbjson"] != None and len(findict["tbjson"]) > 0:
                    top.store_usb4_win_info(findict["tbjson"])
            else:
                top.print_on_log("TH Computer Connection Fail!\n")
                top.device_no_response()
        else:
            top.print_on_log("TH Computer Connection Fail!\n")
            top.device_no_response()
            