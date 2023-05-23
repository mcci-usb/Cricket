##############################################################################
# 
# Module: getusb.py
#
# Description:
#     Scan the USB bus and get the list of devices attached
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
#    V4.0.0 Wed May 25 2023 17:00:00   Seenivasan V
#       Module created
##############################################################################
# Built-in imports

import sys
import os

# Own modules
import usb.util
from usb.backend import libusb1

import xml.dom.minidom

##############################################################################
# Utilities
##############################################################################
def scan_usb():
    """
    Scan the USB bus for the list of plugged devices
    Required for device tree view changes
    
    Note: Runs for Linux and Mac. 

    Args:
        No arguments
        
    Returns:
        None
    """

    # List of Host controllers
    hc_list = []

    # List connected hub
    hub_list = []

    #List connected peripheral
    per_list = []
    master_list = []
    
    tot_list = []

    masterDict = {} 
    
    usb_devices = []

    backend = None

    try:
        usb_devices = usb.core.find(find_all=True, backend=backend)
    except:
        print("No Back End Avail Error!")

    # Here attached a list of Host controlloers, list of Hub,
    # List of periperals info with specific vid, pid.
    for d in usb_devices:  # Device object
        if(d.bDeviceClass == 9 and d.port_number == 0):
            tempDict = {}
            tempDict["vid"] = str(d.idVendor)
            tempDict["pid"] = str(d.idProduct)
            tempDict["bus"] = str(d.bus)
            tempDict["speed"]= d.speed
            tempDict["ifc"]= ""
            hc_list.append(tempDict)
        elif(d.bDeviceClass == 9 and d.port_number != 0):
            tempDict = {}
            tempDict["vid"] = str(d.idVendor)
            tempDict["pid"] = str(d.idProduct)
            tempDict["bus"] = str(d.bus)
            tempDict["speed"]= d.speed
            hub_list.append(tempDict)
        else:
            tempDict = {}
            tempDict["vid"] = str(d.idVendor)
            tempDict["pid"] = str(d.idProduct)
            tempDict["bus"] = str(d.bus)
            tempDict["mport"] = str(d.port_numbers)
            tempDict["port"] = str(d.port_number)
            tempDict["speed"]= d.speed
            per_list.append(tempDict)
                
    masterDict["host"] = hc_list
    masterDict["hub"] = hub_list
    masterDict["peri"] = per_list

    hdata = masterDict.get("hub")

    for items in hdata:
        try:
            # Find our device 
            dl = usb.core.find(idVendor=int(items.get("vid")), 
                               idProduct=int(items.get("pid")), 
                               backend=backend)
            for cfg in dl:
                sclist = list(range(cfg.bNumInterfaces))
                for i in cfg:
                    sclist[i.bInterfaceNumber] = i.bInterfaceClass
                items["ifc"] = sclist
        except:
            # Print message
            print("USB Read Error")

    pdata = masterDict.get("peri")
    
    for items in pdata:
        try:
            # Find our device 
            dl = usb.core.find(idVendor=int(items.get("vid")), 
                               idProduct=int(items.get("pid")), 
                               backend=backend)
            for cfg in dl:
                sclist = list(range(cfg.bNumInterfaces))
                for i in cfg:
                    sclist[i.bInterfaceNumber] = i.bInterfaceClass
                items["ifc"] = sclist
        except:
            # Print message
            print("USB Read Error")

    for i in range(len(hc_list)):
        master_list.append(hc_list[i])
    for i in range(len(hub_list)):
        master_list.append(hub_list[i])
    for i in range(len(per_list)):
        master_list.append(per_list[i])

    # Running Python-application on darwin (MacOS)
    if sys.platform == 'darwin':
        xmldoc = os.popen("system_profiler -xml SPUSBDataType")
        # Use the parse() function to load and parse an XML file
        domobj = xml.dom.minidom.parseString(xmldoc.read())
        keynode = domobj.getElementsByTagName("key")
        cn = []
        hc = []
        for node in keynode:
            cn.append(node.childNodes)
        for cnode in cn:
            nk = cnode.item(0).data
            if nk == 'host_controller':
                hc.append(nk)
        tot_list.append(len(hc))
    else:
        tot_list.append(len(hc_list))

    tot_list.append(len(hub_list))
    tot_list.append(len(per_list))

    return tot_list, master_list