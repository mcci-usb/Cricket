# -*- coding: utf-8 -*-
##############################################################################
# 
# Module: winusbenum.py
#
# Description:
#     This module provides a class for scanning the USB bus on windows systems
#     and retrieving the list of attached devices.
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
# Revision history:
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
##############################################################################

# Built-in imports
import sys
import threading
import base64
import json
import copy

# Lib imports
import usb.util
from usb.backend import libusb1
import websocket

# Own modules
from .usbenumall import USBDeviceEnumerator

EADR = 'EvtAddDeviceRouter'
ERDR = 'EvtRemoveDeviceRouter'

PNPDD = 'pnpDeviceDescription'
MODEL = 'modelName'
PID = 'productId'
VID = 'vendorId'
VNAME = 'vendorName'
DID = 'domainId'
CLS = 'currentLinkSpeed'
TLS = 'targetLinkSpeed'
TID = 'topologyId'

TLW = 'targetLinkWidth'
NLW = 'negotiatedLinkWidth'

USB4RR = 'USB4 Root Router'
USB4R = 'USB4 Router'
USB4HR = 'USB4(TM) Host Router (Microsoft)'
TB3R = 'Thunderbolt 3(TM) Router'

SPEED_DICT = {"Unknown 0": "0 Gbp/s", "Gen 2": "10 Gbp/s", "Gen 3": "20 Gbp/s"}
WIDTH_DICT = {"Unknown 0": "0", "Single Lane": "1", "Dual Lane": "2", "Two Single Lanes": "2"}

USB4_SCAN_DELAY = 6000

##############################################################################
# Utilities
##############################################################################
class WindowsUSBDeviceEnumerator(USBDeviceEnumerator):
    """
    Windows USB Device Enumerator.

    This class implements USB enumeration functionality specific to
    Windows platforms. It supports:

        • USB 3.x device enumeration using libusb backend
        • USB4 / Thunderbolt device detection via WebSocket service
        • Link speed and width extraction
        • Device topology parsing

    Attributes:
        usb_type_dict: Summary count of host, hub, and peripheral devices.
        usb_list: List of enumerated USB 3.x devices.
        usb4tb_json: Raw USB4 / Thunderbolt JSON response.
        usb4tb_list: Parsed USB4 / Thunderbolt device list.
        connected: WebSocket connection state.
        completed: Enumeration completion flag.
        fail_cnt: WebSocket retry failure counter.
    """
    def __init__(self):
        """
        Initialize Windows USB enumerator instance.

        Sets up internal data structures, WebSocket state flags,
        authentication placeholders, and enumeration result storage.

        Args:
            self: Reference to the class instance.

        Returns:
            None
        """
        self.usb_type_dict = {}
        self.usb_list = []
        self.start_time = None
        self.end_time = None
        
        self.websocket_thread = None
        self.ws = None
        self.connected = False
        self.completed = False
        self.uname = None
        self.pwd = None
        self.usb4tb_json = None
        self.usb4tb_list = []

        self.fail_cnt = 0
        
    def set_login_credentials(self, uname, pwd):
        """
        Set authentication credentials for USB4 scanning service.

        Args:
            self: Reference to the class instance.
            uname: Username for authentication.
            pwd: Password for authentication.

        Returns:
            None
        """
        self.uname = uname
        self.pwd = pwd

    def enumerate_usb_devices(self):
        """
        Perform complete USB enumeration.

        This includes:

            • USB 3.x device scanning
            • USB4 / Thunderbolt device scanning

        Args:
            self: Reference to the class instance.

        Returns:
            None
        """
        # raise NotImplementedError("Subclasses must implement enumerate_usb_devices")
        self.completed = False
        self.enumerate_usb3_devices()
        self.enumerate_usb4tb_devices()
    
    def enumerate_usb4tb_devices(self):
        """
        Initiate USB4 / Thunderbolt enumeration.

        Description:
            • Validates login credentials.
            • Starts WebSocket scan if allowed.
            • Handles retry failure limits.

        Args:
            self: Reference to the class instance.

        Returns:
            None
        """
        if self.uname != None and self.pwd != None:
            if self.fail_cnt > 2:
                self.fail_cnt = 3
                self.completed = True
            else:
                self.open_usb4tb_ws()
        else:
            self.completed = True
        
    def open_usb4tb_ws(self):
        """
        Open WebSocket connection for USB4 scanning.

        Description:
            • Verifies thread state.
            • Starts WebSocket listener thread.

        Args:
            self: Reference to the class instance.

        Returns:
            None
        """
        if self.websocket_thread is None or not self.websocket_thread.is_alive():
            if self.connected == False:
                self.websocket_thread = threading.Thread(target=self.run_usb4tb_websocket)
                self.websocket_thread.start()


    def close_usb4t_ws(self):
        """
        Close USB4 WebSocket connection.

        Args:
            self: Reference to the class instance.

        Returns:
            None
        """
        self.ws.close()
        self.ws = None
        self.completed = True

    def get_result(self):
        """
        Retrieve enumeration results.

        Waits until enumeration completes and returns collected data.

        Args:
            self: Reference to the class instance.

        Returns:
            dict: USB enumeration result containing:
                • usb3type
                • usb3list
                • usb4tbjson
                • usb4tblist
        """
        while(not self.completed):
            mydata = None
        return {"usb3type": self.usb_type_dict, "usb3list": self.usb_list, "usb4tbjson": self.usb4tb_json, "usb4tblist": self.usb4tb_list}

    def run_usb4tb_websocket(self):
        """
        Execute USB4 scanning WebSocket client.

        Description:
            • Encodes credentials using Base64.
            • Creates authenticated WebSocket session.
            • Listens for USB4 device events.

        Args:
            self: Reference to the class instance.

        Returns:
            None
        """
        # Encode the credentials in base64
        credentials = base64.b64encode(f"{self.uname}:{self.pwd}".encode("utf-8")).decode("utf-8")

        # Define custom headers for basic authentication
        headers = {
            "Authorization": f"Basic {credentials}",
            # Add any other headers required for authentication
        }

        # Create a WebSocket connection with custom headers
        self.ws = websocket.WebSocketApp(
            "ws://localhost:50080/ext/devices/usb4viewplugin",
            header=headers,
            on_message=self.on_usb4tb_message,
            on_error=self.on_usb4tb_error,
            on_close=self.on_usb4tb_close
        )

        self.connected = True
        self.ws.run_forever()

    def on_usb4tb_message(self, ws, message):
        """
        Handle incoming USB4 WebSocket message.

        Args:
            self: Reference to the class instance.
            ws: WebSocket client instance.
            message: Received JSON message.

        Returns:
            None
        """
        # self.update_text_ctrl(message)
        self.parseresponse(message)
        self.ws.close()
        self.ws = None
        self.connected = False
        self.completed = True
        self.fail_cnt = 0

    def on_usb4tb_error(self, ws, error):
        """
        Handle WebSocket error during USB4 scanning.

        Args:
            self: Reference to the class instance.
            ws: WebSocket client instance.
            error: Error information.

        Returns:
            None
        """
        self.completed = True
        self.ws.close()
        self.ws = None
        self.connected = False
        self.fail_cnt = self.fail_cnt + 1

    def on_usb4tb_close(self, ws, scode, msg):
        """
        Handle WebSocket closure event.

        Args:
            self: Reference to the class instance.
            ws: WebSocket client instance.
            scode: Status code.
            msg: Closure message.

        Returns:
            None
        """
        self.completed = True

    def parseresponse(self, msgusb4):
        """
        Parse USB4 / Thunderbolt JSON response.

        Extracts device attributes such as:

            • VID / PID
            • Model name
            • Link speed
            • Link width
            • Topology ID

        Args:
            self: Reference to the class instance.
            msgusb4: Raw JSON message string.

        Returns:
            None
        """
        self.usb4tb_json = json.loads(msgusb4)
        usb4e = self.usb4tb_json["events"]
        self.usb4tb_list = []

        for i in range(0, len(usb4e)):
            if usb4e[i]["eventKind"] == EADR:
                if PNPDD in usb4e[i] and "ufp" in usb4e[i]:
                    if not "Root Router" in usb4e[i][PNPDD] and not "Host Router" in usb4e[i][PNPDD]:
                        mydict = {}
                        mydict["type"] = "usb4"
                        mydict["desc"] = usb4e[i][PNPDD]
                        mydict["vid"] = str(usb4e[i][VID])
                        mydict["pid"] = str(usb4e[i][PID])
                        mydict["mname"] = usb4e[i][MODEL]
                        mydict["tid"] = usb4e[i][TID]
                        # mydict["ufp"] = usb4e[i]["ufp"]
                        ufpdict = usb4e[i]['ufp']
                        
                        # current_link_speed = ufpdict['currentLinkSpeed']
                        # target_link_speed = ufpdict['targetLinkSpeed']
                        if ufpdict["isLaneAdaptersBonded"] == True:

                            current_link_speed = SPEED_DICT[ufpdict[CLS]]
                            target_link_speed = SPEED_DICT[ufpdict[TLS]]

                            Negotiated_link_width = str(ufpdict[NLW])
                            target_link_width = str(ufpdict[TLW])

                            mydict["ufpCLS"] = current_link_speed
                            mydict["ufpTLS"] = target_link_speed

                            mydict["ufpNLW"] = Negotiated_link_width
                            mydict["ufpTLW"] = target_link_width

                        self.usb4tb_list.append(mydict)
    
    def enumerate_usb3_devices(self):
        """
        Enumerate USB 3.x devices using libusb backend.

        Description:
            • Detects host controllers, hubs, and peripherals.
            • Extracts VID, PID, bus, port, and speed.
            • Retrieves interface class details.

        Args:
            self: Reference to the class instance.

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
            backend = usb.backend.libusb1.get_backend()

        # Generator object
        usb_devices = usb.core.find(find_all=True, backend=backend)

        # Generator object
        # usb_devices = usb.core.find(find_all=True, backend=backend)

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
        
        for i in range(len(hub_list)):
            master_list.append(hub_list[i])
        for i in range(len(per_list)):
            master_list.append(per_list[i])

        self.usb_type_dict["host"] = len(hc_list)
        self.usb_type_dict["hub"] = len(hub_list)
        self.usb_type_dict["peri"] = len(per_list)

        self.usb_list = copy.deepcopy(master_list)