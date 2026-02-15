# -*- coding: utf-8 -*-
##############################################################################
# 
# Module: linuxusbenum.py
#
# Description:
#     Linux USB Enumeration module.
#     Provides functionality to scan the USB bus on Linux systems
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
import re
import copy

# Lib imports
import usb.util
from usb.backend import libusb1

# Own modules
from . import usbenumall

##############################################################################
# Utilities
##############################################################################
class LinuxUSBDeviceEnumerator(usbenumall.USBDeviceEnumerator):
    """
    Summary:
        Linux USB Device Enumerator.

    Longer Description:
        Enumerates USB devices connected to Linux systems.
        Supports USB 3.x and USB4/Thunderbolt device scanning,
        classification, and topology extraction using system tools.

    Attributes:
        usb_type_dict: Dictionary storing count of USB device types.
        usb_list: List of enumerated USB3 devices.
        usb4tb_json: Parsed USB4 Thunderbolt JSON data.
        usb4tb_list: List of USB4 Thunderbolt devices.
    """
    def __init__(self):
        """
        Initialize Linux USB Device Enumerator.

        Args:
            None

        Returns:
            None
        """
        self.usb_type_dict = {}
        self.usb_list = []

        self.websocket_thread = None
        self.ws = None
        self.connected = False
        self.uname = None
        self.pwd = None
        self.usb4tb_json = None
        self.usb4tb_list = []
        
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
        
        self.usb_type_dict["host"] = len(hc_list)
        self.usb_type_dict["hub"] = len(hub_list)
        self.usb_type_dict["peri"] = len(per_list)

        self.usb_list = copy.deepcopy(master_list)
    
    def enumerate_usb4tb_devices(self):
        """
        Enumerate USB4 / Thunderbolt devices.

        Description:
            Uses `boltctl` command-line utility to gather
            Thunderbolt device topology and speed details.

        Args:
            None

        Returns:
            None
        """
        usb4tb_data = self.run_boltctl_command()

        mydata = usb4tb_data.replace('"','')
        mydata = mydata.replace('|','')

        entries = mydata.split("\\n\\n")

        dev_list = []

        for entry in entries:
            # dev_list.append(self.find_device(entry))
            res = self.find_device(entry)
            if res != None:
                dev_list.append(res)

        self.usb4tb_list = copy.deepcopy(dev_list)

        self.usb4tb_json = {}
        
        for dev in dev_list:
            if 'uuid' in dev:
                self.usb4tb_json[dev['uuid']] = dev


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
        return {"usb3type": self.usb_type_dict, "usb3list": self.usb_list, "usb4tbjson": self.usb4tb_json, "usb4tblist": self.usb4tb_list}


    def find_device(self, gistr):
        """
        Parse device entry.

        Description:
            Extracts Thunderbolt device details from
            formatted command output string.

        Args:
            gistr (str):
                Raw device information string.

        Returns:
            dict | None:
                Parsed device dictionary if found,
                otherwise None.
        """
        
        pattern = re.compile(r'\*\s(.*?)(?=\\n)')

        matches = pattern.findall(gistr)

        if matches:
            desc = matches[0].strip()
            return self.extract_json(desc, gistr)
 
        else:
            print("Pattern not found.")
            return None

   
    def extract_json(self, desc, gistr):
        """
        Extract structured device data.

        Description:
            Converts parsed string data into structured
            dictionary format containing device metadata.

        Args:
            desc (str):
                Device description.
            gistr (str):
                Raw key-value formatted string.

        Returns:
            dict:
                Structured USB4 device information.
        """
        lines = gistr.split('\\n')

        # Create a dictionary to store key-value pairs
        key_value_pairs = {}

        # Process each line
        for line in lines:
            # Split each line into key and value
            parts = line.split(':')

            # Ensure there are at least two parts (key and value)
            if len(parts) >= 2:
                # Strip leading and trailing spaces from key and value
                key = parts[0].strip()
                value = ':'.join(parts[1:]).strip()

                # Add to the dictionary
                key_value_pairs[key] = value

        uuid = key_value_pairs['uuid'].split('-', 3)[:-1]

        final_dict = {}
        final_dict['name'] = key_value_pairs['name']
        final_dict['uuid'] = '-'.join(uuid)
        final_dict['devtype'] = key_value_pairs['type']
        final_dict['type'] = 'usb4'
        final_dict['vendor'] = key_value_pairs['vendor']
        final_dict['generation'] = key_value_pairs['generation']
        final_dict['rx speed'] = key_value_pairs['rx speed']
        final_dict['tx speed'] = key_value_pairs['tx speed']

        return final_dict
    
    def run_boltctl_command(self):
        """
        Execute boltctl scan command.

        Description:
            Runs system command to retrieve formatted
            Thunderbolt device information.

        Args:
            None

        Returns:
            str:
                Formatted command output string.
        """
        # Run the boltctl command and capture the output
        with os.popen('boltctl | jq -R -s -c \'split("\\n\n")[:-1] | map(gsub("^\\\\s*[-|]+\\\\s*"; "") | gsub("\\\\|-"; "")) | join("\\n\\n")\'') as pipe:
            return pipe.read()
