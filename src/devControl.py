##############################################################################
# 
# Module: devControl.py
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

import devClient as devnw
import control2101 as d2101
import search
import socket
import json

from uiGlobals import *

PORT = 5566

def SetDeviceControl(top):
    if not top.ldata['cc']:
        if top.ldata['sccif'] == 'serial':
            # serial not implemented
            top.devCtrl = "serial"
            pass
        else:
            top.devCtrl = "network"
            #OpenNetwork(top)
    else:
        top.devCtrl = "local"

def ResetDeviceControl(top):
    if top.ccclient != None:
        top.thread.close()
        top.ccclient.close()
            
def search_device(top):
    if top.devCtrl == "local":
        dev_dict = search.search_port()
        return dev_dict
    elif top.devCtrl == "network":
        resdict = devnw.get_device_list(top.ldata['sccid'], PORT)
        if resdict["result"][0]["status"] == "OK":
            findict = resdict["result"][1]
            top.ccflag = True
            return findict
        else:
            top.print_on_log("Control Computer Connection Fail!\n")
            top.ccflag = False
            findict = {}
            findict["devices"] = []
            return findict
       

def connect_device(top):
    if top.devCtrl == "local":
        if top.devHand.open_serial_device(top.selPort, BAUDRATE[top.selDevice]):
            return True
            #top.device_connected()
    elif top.devCtrl == "network":
        resdict = devnw.open_serial_device(top.ldata['sccid'], PORT, top.selPort, BAUDRATE[top.selDevice])
        if resdict["result"][0]["status"] == "OK":
            top.ccflag = True
            if resdict["result"][1]["data"] == "success":
                return True
            else:
                return False
        else:
            top.print_on_log("Control Computer Connection Fail!\n")
            top.ccflag = False
    return False

def disconnect_device(top):
    if top.devCtrl == "local":
        return top.devHand.close()
    elif top.devCtrl == "network":
        return devnw.close_serial_device(top.ldata['sccid'], PORT)

def send_port_cmd(top,cmd):
    if top.devCtrl == "local":
        return top.devHand.send_port_cmd(cmd)
    elif top.devCtrl == "network":
        resdict = devnw.send_port_cmd(top.ldata['sccid'], PORT, cmd)
        if resdict["result"][0]["status"] == "OK":
            top.ccflag = True
            findict = resdict["result"][1]["data"]
            if findict[0] == -1:
                top.device_no_response()
            return findict
        else:
            top.print_on_log("Control Computer Connection Fail!\n")
            top.device_no_response()
            top.ccflag = False
            return-1, "No CC"
    
def send_status_cmd(top):
    if top.devCtrl == "local":
        return top.devHand.send_status_cmd()
    elif top.devCtrl == "network":
        resdict = devnw.send_status_cmd(top.ldata['sccid'], PORT)
        if resdict["result"][0]["status"] == "OK":
            top.ccflag = True
            findict = resdict["result"][1]["data"]
            if findict[0] == -1:
                top.device_no_response()
            return findict
        else:
            top.print_on_log("Control Computer Connection Fail!\n")
            top.device_no_response()
            top.ccflag = False
            return-1, "No CC"

def read_port_cmd(top):
    if top.devCtrl == "local":
        return top.devHand.read_port_cmd()
    elif top.devCtrl == "network":
        resdict = devnw.read_port_cmd(top.ldata['sccid'], PORT)
        if resdict["result"][0]["status"] == "OK":
            top.ccflag = True
            findict = resdict["result"][1]["data"]
            if findict[0] == -1:
                top.device_no_response()
            return findict
        else:
            top.print_on_log("Control Computer Connection Fail!\n")
            top.device_no_response()
            top.ccflag = False
            return-1, "No CC"

def send_volts_cmd(top):
    if top.devCtrl == "local":
        return top.devHand.send_volts_cmd()
    elif top.devCtrl == "network":
        resdict = devnw.send_volts_cmd(top.ldata['sccid'], PORT)
        if resdict["result"][0]["status"] == "OK":
            top.ccflag = True
            findict = resdict["result"][1]["data"]
            if findict[0] == -1:
                top.device_no_response()
            return findict
        else:
            top.print_on_log("Control Computer Connection Fail!\n")
            top.device_no_response()
            top.ccflag = False
            return-1, "No CC"

def send_amps_cmd(top):
    if top.devCtrl == "local":
        return top.devHand.send_amps_cmd()
    elif top.devCtrl == "network":
        resdict = devnw.send_amps_cmd(top.ldata['sccid'], PORT)
        if resdict["result"][0]["status"] == "OK":
            top.ccflag = True
            findict = resdict["result"][1]["data"]
            if findict[0] == -1:
                top.device_no_response()
            return findict
        else:
            top.print_on_log("Control Computer Connection Fail!\n")
            top.device_no_response()
            top.ccflag = False
            return-1, "No CC"

def control_port(top, cmd):
    if top.devCtrl == "local":
        d2101.control_port(top.selPort, cmd)
    elif top.devCtrl == "network":
        resdict = devnw.control_port(top.ldata['sccid'], PORT, top.selPort, cmd)
        if resdict["result"][0]["status"] == "OK":
            top.ccflag = True
            findict = resdict["result"][1]["data"]
            if findict == 'None':
                top.device_no_response()
            return findict
        else:
            top.print_on_log("Control Computer Connection Fail!\n")
            top.device_no_response()
            top.ccflag = False
            return-1, "No CC"            

def device_connected(top):
    """
    Connect the selected device

    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        None
    """
    top.con_flg = True
    top.UpdatePort()
    top.UpdateDevice()
    top.UpdateSingle("Connected", 3)
    top.print_on_log("Model "+DEVICES[top.selDevice]
                                        +" Connected!\n")
    top.device_connected()