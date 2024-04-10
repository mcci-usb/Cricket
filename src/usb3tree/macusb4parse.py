class MacUsb4TreeParse():
    def __init__(self):
        self.idata = None
        self.ldata = None
    
    def parse_usb3tb_data(self, usb3data):
        print("parse_usb3tb_data")
        # self.idata = self.get_item_data(usb3data)
        # self.ldata = self.get_level_data(self.idata)
        self.idata = self.get_item_data(usb3data)
        self.ldata = self.get_level_data(self.idata)
        # if self.idata is not None:
        #     self.ldata = self.get_level_data(self.idata)
        # else:
        #     print("Error: idata is None")

    def get_item_data(self, msg):
        # print("------->......", msg)
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
            
                # print("---- vid", vid)
                # print("---- pid", pid)

                if vid is not None and pid is not None and bus is not None and speed is not None and ifc is not None:
                    key = f"{vid},{pid},{bus},{speed}"
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

# # Sample USB3 data
# usb3_data = [{'type': 'usb3', 'vid': '32903', 'pid': '2880', 'bus': '2', 'speed': 5, 'ifc': [9]}, {'type': 'usb3', 'vid': '7516', 'pid': '22529', 'bus': '1', 'speed': 3, 'ifc': [9]}, {'type': 'usb3', 'vid': '5967', 'pid': '9317', 'bus': '1', 'mport': '(7,)', 'port': '7', 'speed': 3, 'ifc': [14, 14, 254]}, {'type': 'usb3', 'vid': '1121', 'pid': '20052', 'bus': '1', 'mport': '(3,)', 'port': '3', 'speed': 1, 'ifc': [3]}, {'type': 'usb3', 'vid': '32903', 'pid': '38', 'bus': '1', 'mport': '(10,)', 'port': '10', 'speed': 2, 'ifc': [224, 224]}, {'type': 'usb3', 'vid': '7825', 'pid': '56897', 'bus': '1', 'mport': '(1, 5)', 'port': '5', 'speed': 2, 'ifc': [17, 255]}, {'type': 'usb3', 'vid': '1118', 'pid': '1606', 'bus': '1', 'mport': '(9,)', 'port': '9', 'speed': 2, 'ifc': [2, 10]}, {'type': 'usb3', 'vid': '1267', 'pid': '3147', 'bus': '1', 'mport': '(6,)', 'port': '6', 'speed': 2, 'ifc': [255]}]

# # Creating an instance of the parser
# usb_parser = WinUsb3TreeParse()

# # Parsing USB3 data
# usb_parser.parse_usb3tb_data(usb3_data)
