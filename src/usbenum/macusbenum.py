# -*- coding: utf-8 -*-
##############################################################################
# 
# Module: macusbenum.py
#
# Description:
#     macOS USB Enumeration module.
#     Provides functionality to scan the USB bus on macOS systems
#     and retrieve the list of connected USB 3.x and USB4/Thunderbolt
#     devices with topology and speed details.
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
# Revision history:
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
#
##############################################################################

# Built-in imports
import os
import json
import copy
import xml.dom.minidom

# Lib imports
import usb.util
from usb.backend import libusb1

# Own modules
from . import usbenumall


speed_tag = ['receptacle_1_tag', 'receptacle_2_tag', 'receptacle_3_tag', 'receptacle_4_tag']
swuid_tag = 'switch_uid_key'
tbdata_tag = 'SPThunderboltDataType'

##############################################################################
# Utilities
##############################################################################
class MacOSUSBDeviceEnumerator(usbenumall.USBDeviceEnumerator):
    """
    Summary:
        macOS USB Device Enumerator.

    Longer Description:
        Enumerates USB devices connected to macOS systems.
        Supports USB 3.x and USB4/Thunderbolt device scanning,
        classification, and topology extraction.

    Attributes:
        usb_type_dict: Dictionary storing count of USB device types.
        usb_list: List of enumerated USB3 devices.
        usb4tb_json: Raw Thunderbolt JSON data.
        usb4tb_dict: Parsed Thunderbolt device list.
    """
    def __init__(self):
        """
        Initialize macOS USB Device Enumerator.

        Args:
            None

        Returns:
            None
        """
        self.usb_type_dict = {}
        self.usb_list = []

        self.usb4tb_json = None
        self.usb4tb_dict = {}
        
    def set_login_credentials(self, uname, pwd):
        """
        Set login credentials.

        Description:
            Placeholder method for compatibility with other
            OS enumerators that require authentication.

        Args:
            uname: Username.
            pwd: Password.

        Returns:
            None
        """
        pass
        
    def enumerate_usb_devices(self):
        """
        Enumerate USB devices.

        Description:
            Initiates enumeration of both USB3 and
            USB4/Thunderbolt devices.

        Args:
            None

        Returns:
            None
        """
        # raise NotImplementedError("Subclasses must implement enumerate_usb_devices")
        self.enumerate_usb3_devices()
        self.enumerate_usb4tb_devices()

    def get_result(self):
        """
        Get enumeration results.

        Description:
            Returns collected USB enumeration data.

        Args:
            None

        Returns:
            dict:
                Dictionary containing USB3 and USB4
                enumeration results.
        """

        return {"usb3type": self.usb_type_dict, 
                "usb3list": self.usb_list, 
                "usb4tbjson": self.usb4tb_json, 
                "usb4tblist": self.usb4tb_dict
            }

    def enumerate_usb3_devices(self):
        """
        Enumerate USB3 devices.

        Description:
            Scans and categorizes USB3 devices into:
            - Host Controllers
            - Hubs
            - Peripherals

        Args:
            None

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
        masterDict = {}
        backend = None
        
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
        
        self.usb_type_dict["host"] = len(hc)
        self.usb_type_dict["hub"] = len(hub_list)
        self.usb_type_dict["peri"] = len(per_list)

        self.usb_list = copy.deepcopy(master_list)

    # Enumerate USB4 TB devices
    def enumerate_usb4tb_devices(self):
        """
        Enumerate USB4 / Thunderbolt devices.

        Description:
            Uses macOS `system_profiler` command to gather
            Thunderbolt topology and device information.

        Args:
            None

        Returns:
            None
        """
        tbbus = []
        tblist = []

        xmldoc = os.popen("system_profiler -json SPThunderboltDataType")
        mytb = json.load(xmldoc)
        self.usb4tb_json = copy.deepcopy(mytb)

        # Use the parse() function to load and parse an XML file
        # xmlobj = xml.dom.minidom.parseString(xmldoc.read())

        if tbdata_tag in mytb.keys():
            tbbuses = mytb[tbdata_tag]

            for tbus in tbbuses:
                tbbus.append(tbus)

            for i in range(len(tbbus)):
                self.handleBusTree(tbbus[i], tblist)
        
        self.usb4tb_dict = copy.deepcopy(tblist)
        

    def handleBusTree(self, gbus, tblist):
        """
        Process Thunderbolt bus tree.

        Description:
            Recursively traverses Thunderbolt bus hierarchy
            and extracts connected device information.

        Args:
            gbus:
                Thunderbolt bus data.
            tblist (list):
                List storing parsed device details.

        Returns:
            None
        """
        doflg = True
        while doflg:
            gchild = self.grabData(gbus, tblist)
            if gchild == None:
                doflg = False
            else:
                # print(len(gchild))
                if len(gchild) > 0:
                    gbus = gchild[0]
                else:
                    doflg = False

    def grabData(self, gbus, finalList):
        """
        Extract Thunderbolt device data.

        Description:
            Parses bus node information and appends
            formatted device details into final list.

        Args:
            gbus:
                Thunderbolt bus node.
            finalList (list):
                Destination list for parsed data.

        Returns:
            list | None:
                Child device list if available.
        """
        childs = None
        if swuid_tag in gbus:
            bdict = {}
            bdict['name'] = gbus['_name']
            bdict['type'] = 'usb4'
            bdict['deviceName'] = gbus['device_name_key']
            bdict['vendorName'] = gbus['vendor_name_key']
            bdict['tid'] = gbus['route_string_key']

            for stag in speed_tag:
                if stag in gbus:
                    bdict['speed'] = gbus[stag]['current_speed_key']
                    # print(stag)
                    break
            
            if '_items' in gbus.keys():
                childs = gbus['_items']
                nchild = []
                for ielem in childs:
                    nchild.append(ielem[swuid_tag])
                bdict['child'] = nchild
            else:
                bdict['child'] = []
                childs = []
            bdict['hwid'] = gbus[swuid_tag]
            finalList.append(bdict)
        
        kilist = list(gbus.keys())
        for ikey in kilist:
            if ikey != "_items":
                del gbus[ikey]
        
        return childs   
