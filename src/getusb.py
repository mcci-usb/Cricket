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
import sys

import usb.util
from usb.backend import libusb1

#======================================================================
# COMPONENTS
#======================================================================

def scan_usb():
    hc_list = []
    hub_list = []
    per_list = []
    master_list = []

    tot_list = []

    masterDict = {} 

    path = sys.executable

    path = path.replace("python.exe", "")

    backend1 = usb.backend.libusb1.get_backend(find_library=lambda x: ""+ 
               path + "Lib/site-packages/libusb/_platform/_windows/x86"+
               "/libusb-1.0.dll")

    #generator object
    usb_devices = usb.core.find(find_all=True, backend=backend1)   

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
            dl = usb.core.find(idVendor=int(items.get("vid")), 
                               idProduct=int(items.get("pid")), 
                               backend=backend1)
            for cfg in dl:
                sclist = list(range(cfg.bNumInterfaces))
                for i in cfg:
                    sclist[i.bInterfaceNumber] = i.bInterfaceClass
                items["ifc"] = sclist
        except:
            print("Error")

    pdata = masterDict.get("peri")
    
    for items in pdata:
        try:
            dl = usb.core.find(idVendor=int(items.get("vid")), 
                               idProduct=int(items.get("pid")), 
                               backend=backend1)
            for cfg in dl:
                sclist = list(range(cfg.bNumInterfaces))
                for i in cfg:
                    sclist[i.bInterfaceNumber] = i.bInterfaceClass
                items["ifc"] = sclist
        except:
            print("Error")

    for i in range(len(hc_list)):
        master_list.append(hc_list[i])
    for i in range(len(hub_list)):
        master_list.append(hub_list[i])
    for i in range(len(per_list)):
        master_list.append(per_list[i])

    tot_list.append(len(hc_list))
    tot_list.append(len(hub_list))
    tot_list.append(len(per_list))

    return tot_list, master_list