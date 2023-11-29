import os
import usb.util

import copy
from usb.backend import libusb1
# from usbenumall import USBDeviceEnumerator
from . import usbenumall

import re

class LinuxUSBDeviceEnumerator(usbenumall.USBDeviceEnumerator):
    def __init__(self):
        self.usb_type_dict = {}
        self.usb_list = []

        self.websocket_thread = None
        self.ws = None
        self.connected = False
        self.uname = "mcci"
        self.pwd = "mcci"
        self.usb4tb_json = None
        self.usb4tb_list = []

    def enumerate_usb_devices(self):
        """
        Enumerate both USB 3.0 and USB4TB devices.

        This method calls specific methods to enumerate USB 3.0 and USB4TB devices,
        categorizing them into different types.

        Returns:
            None
        """
        # raise NotImplementedError("Subclasses must implement enumerate_usb_devices")
        self.enumerate_usb3_devices()
        self.enumerate_usb4tb_devices()

    def enumerate_usb3_devices(self):
        """
        Enumerate USB 3.0 devices and categorize them into Host controllers, Hubs, and Peripherals.

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
        Enumerate USB4TB devices using boltctl command.

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
        Get the results of USB4 speed scanning.

        Returns:
            tuple: A tuple containing the lists of added USB4 devices (`u4added`) and all USB4 devices (`u4all`).

        """
        return {"usb3type": self.usb_type_dict, "usb3list": self.usb_list, "usb4tbjson": self.usb4tb_json, "usb4tblist": self.usb4tb_list}


    def find_device(self, gistr):
        """
        Find and extract information about a device from a given string.

        Args:
            gistr (str): The string containing information about devices.

        Returns:
            dict or None: If a device is found, returns a dictionary containing extracted information.
                            If no device is found, returns None.
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
        Extract relevant information from a given JSON-like string.

        Args:
            desc (str): A description of the information being extracted.
            gistr (str): The JSON-like string containing key-value pairs.

        Returns:
            dict: A dictionary containing extracted information with keys such as 'name', 'uuid', 'devtype',
                'type', 'vendor', 'generation', 'rx speed', and 'tx speed'.
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
        Run the boltctl command and capture the formatted output.

        Returns:
            str: The formatted output of the boltctl command.
        """
        # Run the boltctl command and capture the output
        with os.popen('boltctl | jq -R -s -c \'split("\\n\n")[:-1] | map(gsub("^\\\\s*[-|]+\\\\s*"; "") | gsub("\\\\|-"; "")) | join("\\n\\n")\'') as pipe:
            return pipe.read()
