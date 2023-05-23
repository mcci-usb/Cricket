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
#    V4.0.0 Wed May 25 2023 17:00:00   Seenivasan V
#       Module created
##############################################################################
# Built-in imports

import devClient as devnw

from cricketlib import searchswitch

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
    if not top.myrole['cc']:
        if top.ucConfig['mycc']['interface'] == 'serial':
            top.devCtrl = "serial"
            pass
        else:
            top.devCtrl = "tcp"
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
    
def get_avail_ports(top):
    dev_list = searchswitch.get_avail_ports()
    return dev_list
            
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
        dev_dict = searchswitch.get_switches()
        return dev_dict
    elif top.devCtrl == "tcp":
        resdict = devnw.get_device_list(top.ldata['sccid'],
                                    int(top.ldata['ssccpn']))
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

def connect_device(top, swdict):
    if top.devCtrl == "local":
        swname = list(swdict.keys())
        port = list(swdict.values())
        swhand = top.swobjmap[swname[0]](port[0])
        if(swhand.connect() or swname[0] == "2101"):
            top.handlers[port[0]] = swhand
            top.swuidict[port[0]] = swname[0]

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
        return devnw.close_serial_device(top.ldata['sccid'],
                                    int(top.ldata['ssccpn']))

def send_port_cmd(top, cmd):
    if top.fault_flg == True:
        return (1, "Stop Event occurred!")
    
    if top.devCtrl == "local":
        swid, opr, pno = cmd.split(',')
        if(pno == "0"):
            return top.handlers[swid].port_off()
        else:
            return top.handlers[swid].port_on(pno)

def control_port(top, cmd):
    if top.devCtrl == "local":
        swid, opr = cmd.split(',')
        if(opr == "off"):
            return top.handlers[swid].port_off()
        else:
            return top.handlers[swid].port_on(opr)

def read_port(top, swid):
    if top.devCtrl == "local":
        return top.handlers[swid].read_port()
        
def send_speed_cmd(top, cmd):
    if top.devCtrl == "local":
        swid, speed = cmd.split(',')
        return top.handlers[swid].set_speed(speed)

def send_volts_cmd(top, swid):
    if top.devCtrl == "local":
        return top.handlers[swid].get_volts()

def send_amps_cmd(top, swid):
    if top.devCtrl == "local":
        return top.handlers[swid].get_amps()

def send_status_cmd(top, swid):
    """
    sending the status coammand
    Args:
        top: top creates the object
    Returns:
        return top.devHand.send_status_cmd() return the devcie status.
        return findict: status in dict
    """
    if top.devCtrl == "local":
        return top.handlers[swid].get_status()
    elif top.devCtrl == "network":
        resdict = devnw.send_status_cmd(top.ldata['sccid'],
                                    int(top.ldata['ssccpn']))
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

def read_port_status(top, swid):
    """
    reading the port coammand
    Args:
        top: top creates the object
    Returns:
        return top.devHand.send_status_cmd() return the devcie status.
        return findict: status in dict
    """
    if top.devCtrl == "local":
        return top.handlers[swid].get_port_status()
    elif top.devCtrl == "network":
        resdict = devnw.read_port_cmd(top.ldata['sccid'],
                                int(top.ldata['ssccpn']))
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
    top.print_on_log("MCCI USB Switch "+DEVICES[top.selDevice]
                                        +" Connected!\n")
    top.device_connected()