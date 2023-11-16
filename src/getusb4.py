##############################################################################
# 
# Module: getusb4.py
#
# Description:
#     get the usb4 device data.
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


import threading
import websocket
import base64
import json

import configdata

ID_BTN_AUTO = 1001

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

TLW = 'targetLinkWidth'
NLW = 'negotiatedLinkWidth'

USB4RR = 'USB4 Root Router'
USB4R = 'USB4 Router'
USB4HR = 'USB4(TM) Host Router (Microsoft)'
TB3R = 'Thunderbolt 3(TM) Router'

IMG_LOGO = "mcci_logo.png"

SPEED_DICT = {"Unknown 0": "0 Gbp/s", "Gen 2": "10 Gbp/s", "Gen 3": "20 Gbp/s"}
WIDTH_DICT = {"Unknown 0": "0", "Single Lane": "1", "Dual Lane": "2", "Two Single Lanes": "2"}


class Usb4speedScan:
    def __init__(self):
        self.websocket_thread = None
        self.ws = None
        self.connected = False
        self.completed = False
        self.uname = None
        self.pwd = None
        self.connected = False
        self.mystr = "Result Not Found"
        self.u4added = []
        self.u4all = None

        msudpdict = configdata.read_msudp_config()
        self.uname = msudpdict["uname"]
        self.pwd = msudpdict["pwd"]
        # print(msudpdict)

    def connect(self):
        """
        Connect to the USB4 speed scanning service.

        Description:
            - Check if valid credentials are provided.
            - If the WebSocket thread is not running, start it.
        
        """
        if self.uname == None or self.pwd == None:
            print("Please provide valid credentials")
        else:
            
            if self.websocket_thread is None or not self.websocket_thread.is_alive():
                
                if self.connected == False:
                    
                    self.websocket_thread = threading.Thread(target=self.run_websocket)
                    self.websocket_thread.start()

    # def set_msudp_credentials(self, mydict):
    #     self.uname = mydict["uname"]
    #     self.pwd = mydict["pwd"]

    def disconnect(self):
        """
        Disconnect from the USB4 speed scanning service.

        Description:
            - Close the WebSocket connection.
        
        """
        self.ws.close()
        print("\nDisconnect - Scanning Closed\n")
        self.ws = None

    def append_to_scb(self, text):
        """
        Append the provided text to the scanning control box.

        Parameters:
            text (str): The text to be appended to the scanning control box.

        """
        pass

    def get_result(self):
        """
        Get the results of USB4 speed scanning.

        Returns:
            tuple: A tuple containing the lists of added USB4 devices (`u4added`) and all USB4 devices (`u4all`).

        """
        while(not self.completed):
            
            mydata = None
        return self.u4added, self.u4all        
        
    def run_websocket(self):
        """
        Run the WebSocket connection for USB4 speed scanning.

        Description:
            - Encode the credentials in base64.
            - Define custom headers for basic authentication.
            - Create a WebSocket connection with custom headers.
            - Set the `connected` flag to True.

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
            on_message=self.on_message
        )

        self.connected = True
        self.ws.run_forever()

    def on_message(self, ws, message):
        """
        Handle the incoming message from the WebSocket.

        Description:
            - Update the text control with the received message.
            - Close the WebSocket connection.
            - Set flags to indicate that scanning is closed.

        Parameters:
            ws (websocket.WebSocketApp): The WebSocket instance.
            message (str): The received message.

        """
        self.update_text_ctrl(message)
        self.ws.close()
        print("\nScanning Closed\n")
        # print(message)
        self.ws = None
        self.connected = False
        self.completed = True

    def update_text_ctrl(self, message):
        """
        Update the text control with the parsed response.

        Parameters:
            message (str): The received message.

        """
        self.mystr = self.parseresponse(message)

    # def parseresponse(self, msgusb4):
    #     # Implement the response parsing functionality here
        # pass
    
    def parseresponse(self, msgusb4):
        """
        parsing the usb4 list json its getting from msgusb4.
        """
   
        mystr = ""
        msg = json.loads(msgusb4)
        self.u4all = msg
        usb4e = msg["events"]
        # print("USB4E:",usb4e)
        self.u4added = []
        u4removed = []
        for i in range(0, len(usb4e)):
            if usb4e[i]["eventKind"] == EADR:
                if PNPDD in usb4e[i] and "ufp" in usb4e[i]:
                    if not "Root Router" in usb4e[i][PNPDD] and not "Host Router" in usb4e[i][PNPDD]:
                        mydict = {}
                        mydict["type"] = "usb4"
                        mydict["disc"] = usb4e[i][PNPDD]
                        mydict["vid"] = str(usb4e[i][VID])
                        mydict["pid"] = str(usb4e[i][PID])
                        mydict["mname"] = usb4e[i][MODEL]
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

                        self.u4added.append(mydict)
        return mystr
                       
    def getremovedDD(self, u4remobj):
        """
        remove the Data.

        """
        if len(self.u4added) > 0:
            for i in range(0, len(self.u4added)):
                if u4remobj[DID] == self.u4added[i][DID]:
                    return self.u4added.pop(i)
        return None


