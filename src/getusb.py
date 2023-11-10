
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
    
    # Create path and executable path
    path = sys.executable

    path = path.replace("python.exe", "")

    backend = None
    # Running Python-application on Windows
    if sys.platform == "win32":
        backend = usb.backend.libusb1.get_backend(find_library=lambda x: "" + 
              path + "Lib\\site-packages\\libusb\\_platform\\_windows\\x64\\libusb-1.0.dll")

    # Generator object
    usb_devices = usb.core.find(find_all=True, backend=backend) 

    # Here attached a list of Host controlloers, list of Hub,
    # List of periperals info with specific vid, pid.
    for d in usb_devices:  # Device object
        if(d.bDeviceClass == 9 and d.port_number == 0):
            tempDict = {}
            tempDict["type"] = "usb3"
            tempDict["vid"] = str(d.idVendor)
            tempDict["pid"] = str(d.idProduct)
            tempDict["bus"] = str(d.bus)
            tempDict["speed"]= d.speed
            tempDict["ifc"]= ""
            hc_list.append(tempDict)
        elif(d.bDeviceClass == 9 and d.port_number != 0):
            tempDict = {}
            tempDict["type"] = "usb3"
            tempDict["vid"] = str(d.idVendor)
            tempDict["pid"] = str(d.idProduct)
            tempDict["bus"] = str(d.bus)
            tempDict["speed"]= d.speed
            hub_list.append(tempDict)
        else:
            tempDict = {}
            tempDict["type"] = "usb3"
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
            print("Error")

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
            print("Error")
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