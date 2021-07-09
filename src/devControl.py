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
#     V2.3.14 Wed July 12 2021 15:20:05   Seenivasan V
#       Module created
##############################################################################
# Built-in imports

import devClient as devnw
import search
import socket
import json

from uiGlobals import *

PORT = 5566

def SetDeviceControl(top):
    """
    set the serial device control
    Args:
        top: top creates the object
    Returns:
        None
    """
    if not top.ldata['cc']:
        if top.ldata['sccif'] == 'serial':
            top.devCtrl = "serial"
            pass
        else:
            top.devCtrl = "network"
    else:
        top.devCtrl = "local"

def ResetDeviceControl(top):
    """
    reset the serial device control
    Args:
        top: top creates the object
    Returns:
        None
    """
    if top.ccclient != None:
        top.thread.close()
        top.ccclient.close()
            
def search_device(top):
    """
    searching the devices
    Args:
        top: top creates the object
    Returns:
        findict: network device list
        dev_dict: devices in dictionary
    """
    if top.devCtrl == "local":
        dev_dict = search.search_port(top.usbHand)
        return dev_dict
    elif top.devCtrl == "network":
        resdict = devnw.get_device_list(top.ldata['sccid'], int(top.ldata['ssccpn']))
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
    """
    connect the device
    Args:
        top: top creates the object
    Returns:
        usbHand.select_usb_device(top.selPort): select the device
        devHand.open_serial_device(top.selPort, BAUDRATE[top.selDevice]): selport with baudrate
        True: result of dictionay success
        False: result of dictionary Fail
    """
    if top.devCtrl == "local":
        if top.selDevice == DEV_2101:
            return top.usbHand.select_usb_device(top.selPort)
        else:
            return top.devHand.open_serial_device(top.selPort, BAUDRATE[top.selDevice])
        top.device_connected()
    elif top.devCtrl == "network":
        resdict = None
        
        if top.selDevice == DEV_2101:
            resdict = devnw.select_usb_device(top.ldata['sccid'], int(top.ldata['ssccpn']), top.selPort)
        else:
            resdict = devnw.open_serial_device(top.ldata['sccid'], int(top.ldata['ssccpn']), top.selPort, BAUDRATE[top.selDevice])
        
        if resdict["result"][0]["status"] == "OK":
            top.ccflag = True
            if resdict["result"][1]["data"] == "success":
                return True
            else:
                return False
        else:
            top.print_on_log("Control Computer Connection Fail!\n")
            top.device_no_response()
            top.ccflag = False
            return-1, "No CC"

def disconnect_device(top):
    """
    disconnect the devices
    Args:
        top: top creates the object
    Returns:
        return devHand.close() device close
        return devnw.close() network device close()
    """
    if top.devCtrl == "local":
        return top.devHand.close()
    elif top.devCtrl == "network":
        return devnw.close_serial_device(top.ldata['sccid'], int(top.ldata['ssccpn']))

def send_port_cmd(top,cmd):
    """
    sending the port 
    Args:
        top: top creates the object
        cmd: send the command.
    Returns:
        return top.devHand.send_port_cmd(cmd): return the sending port command.
        return findict: status of port
    """
    if top.devCtrl == "local":
        return top.devHand.send_port_cmd(cmd)
    elif top.devCtrl == "network":
        resdict = devnw.send_port_cmd(top.ldata['sccid'], int(top.ldata['ssccpn']), cmd)
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
    """
    sending the status coammand
    Args:
        top: top creates the object
    Returns:
        return top.devHand.send_status_cmd() return the devcie status.
        return findict: status in dict
    """
    if top.devCtrl == "local":
        return top.devHand.send_status_cmd()
    elif top.devCtrl == "network":
        resdict = devnw.send_status_cmd(top.ldata['sccid'], int(top.ldata['ssccpn']))
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
    """
    reading the port coammand
    Args:
        top: top creates the object
    Returns:
        return top.devHand.send_status_cmd() return the devcie status.
        return findict: status in dict
    """
    if top.devCtrl == "local":
        return top.devHand.read_port_cmd()
    elif top.devCtrl == "network":
        resdict = devnw.read_port_cmd(top.ldata['sccid'], int(top.ldata['ssccpn']))
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
    """
    sending the volts coammand
    Args:
        top: top creates the object
    Returns:
        return top.devHand.send_status_cmd() return the devcie status.
        return findict: status in dict
    """
    if top.devCtrl == "local":
        return top.devHand.send_volts_cmd()
    elif top.devCtrl == "network":
        resdict = devnw.send_volts_cmd(top.ldata['sccid'], int(top.ldata['ssccpn']))
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
    """
    sending the amps coammand
    Args:
        top: top creates the object
    Returns:
        return top.devHand.send_status_cmd() return the devcie status.
        return findict: status in dict
    """
    if top.devCtrl == "local":
        return top.devHand.send_amps_cmd()
    elif top.devCtrl == "network":
        resdict = devnw.send_amps_cmd(top.ldata['sccid'], int(top.ldata['ssccpn']))
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
    """
    controls the ports
    Args:
        top: top creates the object
        cmd: throgh command
    Returns:
        return findict: status in dict
    """
    if top.devCtrl == "local":
        top.usbHand.control_port(cmd)
    elif top.devCtrl == "network":
        resdict = devnw.control_port(top.ldata['sccid'], int(top.ldata['ssccpn']), cmd)
        print(resdict)
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
        top: The self parameter is a reference to the current 
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