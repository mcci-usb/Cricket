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
        print("Init USB4 Speed Bus ---->****")
        self.websocket_thread = None
        self.ws = None
        self.connected = False
        self.completed = False
        self.uname = None
        self.pwd = None
        self.connected = False
        self.mystr = "Result Not Found"
        self.u4added = []

        msudpdict = configdata.read_msudp_config()
        self.uname = msudpdict["uname"]
        self.pwd = msudpdict["pwd"]
        # print(msudpdict)

    def connect(self):
        print("\nScanning Clicked\n")
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
        self.ws.close()
        print("\nDisconnect - Scanning Closed\n")
        self.ws = None

    def append_to_scb(self, text):
        pass

    def get_result(self):
        while(not self.completed):
            
            mydata = None
        return self.u4added     
        


    def run_websocket(self):
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

        print("\nScanning USB4 Hubs/Devices\n")
        self.connected = True
        self.ws.run_forever()

    def on_message(self, ws, message):
        self.update_text_ctrl(message)
        self.ws.close()
        print("\nScanning Closed\n")
        # print(message)
        self.ws = None
        self.connected = False
        self.completed = True

    def update_text_ctrl(self, message):
        self.mystr = self.parseresponse(message)

    # def parseresponse(self, msgusb4):
    #     # Implement the response parsing functionality here
        # pass
    
    def parseresponse(self, msgusb4):
       
        mystr = ""
        msg = json.loads(msgusb4)
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
        if len(self.u4added) > 0:
            for i in range(0, len(self.u4added)):
                if u4remobj[DID] == self.u4added[i][DID]:
                    return self.u4added.pop(i)
        return None


