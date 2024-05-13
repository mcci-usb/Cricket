##############################################################################
# 
# Module: MacUsb3TreeParse.py
#
# Description:
#     parsing the USB4 Tree view data in Windows
#
# Author:
#     Vinay N, MCCI Corporation Mar 2024
#
# Revision history:
#      V4.3.1 Mon Apr 15 2024 17:00:00   Seenivasan V 
#       Module created
##############################################################################
class MacUsb3TreeParse():
    def __init__(self):
        self.idata = None
        self.ldata = None
    
    def parse_usb3tb_data(self, usb3data):
        self.idata = self.get_item_data(usb3data)
        self.ldata = self.get_level_data(self.idata)

    def get_item_data(self, msg):

        if not isinstance(msg, list):
            print("Error: usb3data is not a list")
            return None
        
        parsed_usb3 = {}
        for item in msg:
            if isinstance(item, dict):
                vid = item.get('vid')
                pid = item.get('pid')
                bus = item.get('bus')
                speed = item.get('speed')
                ifc = item.get('ifc')
                mport = item.get('mport')
                port = item.get('port')
            
                # if vid is not None and pid is not None and bus is not None and speed is not None and ifc is not None:
                if bus is not None and speed is not None and ifc is not None:
                    # key = f"{vid},{pid},{bus},{speed}"
                    # key = f"{vid},{pid}"
                    key = f"{mport}"
                    
                    parsed_item = {
                        'type': 'usb3',
                        'vid': vid,
                        'pid': pid,
                        'bus': bus,
                        'speed': speed,
                        'ifc': ifc
                    }
                    if mport is not None:
                        parsed_item['mport'] = mport
                        parsed_item['port'] = port
                    parsed_usb3[key] = parsed_item
                else:
                    print("Error: Missing required fields in item")
            else:
                print("Error: Item is not a dictionary")
                        
        # parsed_usb3 = {
        # '7': {'type': 'usb3', 'vid': '5967', 'pid': '9317', 'bus': '1', 'speed': 3, 'ifc': [14, 14, 254], 'mport': '(7,)', 'port': '7'},
        # '(10,)': {'type': 'usb3', 'vid': '32903', 'pid': '38', 'bus': '1', 'speed': 2, 'ifc': [224, 224], 'mport': '(10,)', 'port': '10'},
        # '(9, 4)': {'type': 'usb3', 'vid': '1118', 'pid': '1606', 'bus': '1', 'speed': 2, 'ifc': [2, 10], 'mport': '(9, 4)', 'port': '4'},
        # '(9, 1)': {'type': 'usb3', 'vid': '1121', 'pid': '20052', 'bus': '1', 'speed': 1, 'ifc': [3], 'mport': '(9, 1)', 'port': '1'},
        # '(6,)': {'type': 'usb3', 'vid': '1267', 'pid': '3147', 'bus': '1', 'speed': 2, 'ifc': [255], 'mport': '(6,)', 'port': '6'}}
        return parsed_usb3

    def get_level_data(self, u3tbuf):
        if not isinstance(u3tbuf, dict):
            print("Error: u3tbuf is not a dictionary")
            return None

        pdict = {}
        for rkitem in u3tbuf.keys():
            lcnt = rkitem.count(',')
            kl = list(pdict.keys())
            if 'level'+str(lcnt) in kl:
                pdict['level'+str(lcnt)].append(rkitem)
            else:
                pdict['level'+str(lcnt)] = [rkitem]
        return pdict

