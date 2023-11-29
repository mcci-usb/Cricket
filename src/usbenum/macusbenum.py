# macos_usbenum.py

import copy
import json
import os

# from usbenumall import USBDeviceEnumerator
from . import usbenumall

# USB modules
import usb.util
from usb.backend import libusb1

import xml.dom.minidom


speed_tag = ['receptacle_1_tag', 'receptacle_2_tag', 'receptacle_3_tag', 'receptacle_4_tag']
swuid_tag = 'switch_uid_key'
tbdata_tag = 'SPThunderboltDataType'

class MacOSUSBDeviceEnumerator(usbenumall.USBDeviceEnumerator):
    
    def __init__(self):
        self.usb_type_dict = {}
        self.usb_list = []

        self.usb4tb_json = None
        self.usb4tb_dict = {}
        
    def enumerate_usb_devices(self):
        """
        Enumerate both USB 3.0 and USB4 and USB4TB devices.

        This method calls specific methods to enumerate USB 3.0 and USB4TB devices,
        categorizing them into different types.

        Returns:
            None
        """
        # raise NotImplementedError("Subclasses must implement enumerate_usb_devices")
        self.enumerate_usb3_devices()
        self.enumerate_usb4tb_devices()

    def get_result(self):
        """
        Get the results of USB4 speed scanning.

        Returns:
            tuple: A tuple containing the lists of added USB4 devices (`u4added`) and all USB4 devices (`u4all`).

        """

        return {"usb3type": self.usb_type_dict, "usb3list": self.usb_list, "usb4tbjson": self.usb4tb_json, "usb4tblist": self.usb4tb_dict}

        
    def enumerate_usb3_devices(self):
        """
        Enumerate USB 3.0 devices and categorize them into Host controllers, Hubs, and Peripherals.

        This method uses the `usb.core.find` function to find all connected USB devices.
        It categorizes the devices based on their class and port number into Host controllers,
        Hubs, and Peripherals. The information is stored in separate lists.

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
        Enumerate USB4TB devices using system_profiler command.

        This method uses the `system_profiler` command to gather information about Thunderbolt devices
        and then processes the information to create a list of USB4TB devices.

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
        Recursively handle the Thunderbolt bus tree and extract information about connected devices.

        This method takes a Thunderbolt bus (`gbus`) and a list (`tblist`) to store information about
        connected devices. It recursively grabs data from the bus and continues the process until there
        are no more child devices.

        Args:
            gbus: The Thunderbolt bus to handle.
            tblist (list): The list to store information about connected devices.

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
        Extract data from a Thunderbolt bus and add it to the final list.

        This method takes a Thunderbolt bus (`gbus`) and a list (`finalList`) to store information about
        connected devices. It extracts relevant data from the bus and adds it to the list.

        Args:
            gbus: The Thunderbolt bus from which to extract data.
            finalList (list): The list to store information about connected devices.

        Returns:
            list or None: If data is extracted, returns a list containing the extracted information.
                        If no data is found, returns None.
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
