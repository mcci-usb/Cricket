##############################################################################
# 
# Module: devControl.py
#
# Description:
#     Receive device function commands from resepective device window
#     Check if the device is available in network, then send command to server
#     If the device is available in same computer then send command to device
#
# Author:
#     Seenivasan V, MCCI Corporation June 2021
#
# Revision history:
#    V4.3.1 Mon Apr 15 2024 17:00:00   Seenivasan V 
#       Module created
##############################################################################
# Built-in imports

import devClient as devnw

from cricketlib import searchswitch

from uiGlobals import *


def SetDeviceControl(top):
    """
    set the serial device control
    Args:
        top: top creates the object
    Returns:
        None
    """
    if not top.myrole['cc']:
        if top.myrole['uc']:
            if top.ucConfig['mynodes']["mycc"]['interface'] == 'serial':
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
        nwip = top.ucConfig['mynodes']["mycc"]["tcp"]["ip"]
        nwport = top.ucConfig['mynodes']["mycc"]["tcp"]["port"]
        
        resdict = devnw.get_device_list(nwip, int(nwport))
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
        
def get_dev_baud(devname):
    devidx = None
    for i in range(len(DEVICES)):
        if devname == DEVICES[i]:
            # self.top.selDevice = i
            devidx = i
            break
    return devidx

def connect_device(top, swdict):
    if top.devCtrl == "local":
        swname = list(swdict.keys())
        port = list(swdict.values())
        swhand = top.swobjmap[swname[0]](port[0])
        if(swhand.connect() or swname[0] == "2101"):
            top.handlers[port[0]] = swhand
            top.swuidict[port[0]] = swname[0]
    elif top.devCtrl == "tcp":
        resdict = None
        nwip = top.ucConfig['mynodes']["mycc"]["tcp"]["ip"]
        nwport = top.ucConfig['mynodes']["mycc"]["tcp"]["port"]

        swname = list(swdict.keys())
        port = list(swdict.values())

        top.swuidict[port[0]] = swname[0]

        # if swname[0] == DEV_2101:
        if swname[0] == "2101":
            resdict = devnw.select_usb_device(nwip,
                                            int(nwport), 
                                            port[0])
        else:
            devid = get_dev_baud(swname[0])
            resdict = devnw.open_serial_device(nwip,
                        int(nwport), swname[0], port[0], 
                        BAUDRATE[devid])
        
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

# Need to check
def disconnect_device(top, swport):
    """
    disconnect the devices
    Args:
        top: top creates the object
    Returns:
        return devHand.close() device close
        return devnw.close() network device close()
    """
    if top.devCtrl == "local":
        if swport in top.handlers:
            top.handlers[swport].disconnect()
            top.handlers.pop(swport)
        # return top.devHand.close()
    elif top.devCtrl == "tcp":
        nwip = top.ucConfig['mynodes']["mycc"]["tcp"]["ip"]
        nwport = top.ucConfig['mynodes']["mycc"]["tcp"]["port"]
        return devnw.close_serial_device(nwip, int(nwport), swport)

def send_port_cmd(top, cmd):
    """
    Send a command to control a port.

    Args:
        top: The object that manages the devices.
        cmd (str): A command string in the format "swid,opr,pno" where:
            - swid: Switch ID
            - opr: Operation ("0" for port_off, other values for port_on)
            - pno: Port number

    Returns:
        tuple: A tuple containing the result of the command. If an error occurs,
        the tuple is (1, "Stop Event occurred!"). Otherwise, the result depends
        on the specific operations performed by the device handlers.
    """
    if top.fault_flg == True:
        return (1, "Stop Event occurred!")
    
    if top.devCtrl == "local":
        swid, opr, pno = cmd.split(',')
        if(opr == "OFF"):
            return top.handlers[swid].port_off()
        else:
            return top.handlers[swid].port_on(pno)
    elif top.devCtrl == "tcp":
        nwip = top.ucConfig['mynodes']["mycc"]["tcp"]["ip"]
        nwport = top.ucConfig['mynodes']["mycc"]["tcp"]["port"]
     
        resdict = devnw.send_port_cmd(nwip, int(nwport), cmd)
       
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
    Control the state of a port.

    Args:
        top: The object managing the devices.
        cmd (str): A command string in the format "swid,opr" where:
            - swid: Switch ID
            - opr: Operation ("off" to turn off, any other value to turn on)

    Returns:
        The result of the port control operation. The specific return value
        depends on the operations performed by the device handlers.
    """
    if top.devCtrl == "local":
        swid, opr = cmd.split(',')
        if(opr == "off"):
            return top.handlers[swid].port_off()
        else:
            return top.handlers[swid].port_on(opr)
    elif top.devCtrl == "tcp":
        nwip = top.ucConfig['mynodes']["mycc"]["tcp"]["ip"]
        nwport = top.ucConfig['mynodes']["mycc"]["tcp"]["port"]

        resdict = devnw.control_port(nwip, int(nwport), cmd)
        
        if resdict["result"][0]["status"] == "OK":
            top.ccflag = True
            findict = resdict["result"][1]["data"]
            if findict[0] == -1:
                top.device_no_response()
                return -1, "Data Error"
            return 0,findict
        else:
            top.print_on_log("Control Computer Connection Fail!\n")
            top.device_no_response()
            top.ccflag = False
            return-1, "No CC"

def read_port(top, swid):
    """
    Read the state of a port.

    Args:
        top: The object managing the devices.
        swid: Switch ID for the port to be read.

    Returns:
        The current state of the specified port. The specific return value
        depends on the read operation performed by the device handler.
    """
    if top.devCtrl == "local":
        return top.handlers[swid].read_port()
    elif top.devCtrl == "tcp":
        nwip = top.ucConfig['mynodes']["mycc"]["tcp"]["ip"]
        nwport = top.ucConfig['mynodes']["mycc"]["tcp"]["port"]

        resdict = devnw.read_port(nwip, int(nwport), swid)
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
        
# Need to check
def send_speed_cmd(top, cmd):

    """
    Set the speed for a switch.

    Args:
        top: The object managing the devices.
        cmd (str): A command string in the format "swid,speed" where:
            - swid: Switch ID
            - speed: The desired speed value

    Returns:
        The result of the speed setting operation. The specific return value
        depends on the set_speed operation performed by the device handler.
    """
    swid, speed = cmd.split(',')
   
    if top.devCtrl == "local":
        # swid, speed = cmd.split(',')
        return top.handlers[swid].set_speed(speed)
    elif top.devCtrl == "tcp":
        nwip = top.ucConfig['mynodes']["mycc"]["tcp"]["ip"]
        nwport = top.ucConfig['mynodes']["mycc"]["tcp"]["port"]
        resdict = devnw.send_speed_cmd(nwip, int(nwport), cmd)
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


def send_volts_cmd(top, swid):
    """
    Get the voltage level for a switch.

    Args:
        top: The object managing the devices.
        swid: Switch ID for which voltage is to be queried.

    Returns:
        The voltage level of the specified switch. The specific return value
        depends on the get_volts operation performed by the device handler.
    """
    if top.devCtrl == "local":
        return top.handlers[swid].get_volts()
    elif top.devCtrl == "tcp":
        nwip = top.ucConfig['mynodes']["mycc"]["tcp"]["ip"]
        nwport = top.ucConfig['mynodes']["mycc"]["tcp"]["port"]
        resdict = devnw.send_volts_cmd(nwip, int(nwport), swid)
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

def send_amps_cmd(top, swid):
    """
    Get the current (amperage) for a switch.

    Args:
        top: The object managing the devices.
        swid: Switch ID for which current is to be queried.

    Returns:
        The current (amperage) of the specified switch. The specific return value
        depends on the get_amps operation performed by the device handler.
    """
    if top.devCtrl == "local":
        return top.handlers[swid].get_amps()
    elif top.devCtrl == "tcp":
        nwip = top.ucConfig['mynodes']["mycc"]["tcp"]["ip"]
        nwport = top.ucConfig['mynodes']["mycc"]["tcp"]["port"]
        resdict = devnw.send_amps_cmd(nwip, int(nwport), swid)
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
    elif top.devCtrl == "tcp":
        nwip = top.ucConfig['mynodes']["mycc"]["tcp"]["ip"]
        nwport = top.ucConfig['mynodes']["mycc"]["tcp"]["port"]
        resdict = devnw.send_status_cmd(nwip, int(nwport), swid)
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
    elif top.devCtrl == "tcp":
        nwip = top.ucConfig['mynodes']["mycc"]["tcp"]["ip"]
        nwport = top.ucConfig['mynodes']["mycc"]["tcp"]["port"]
        resdict = devnw.read_port_cmd(nwip, int(nwport), swid)
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