EADR = 'EvtAddDeviceRouter'
ERDR = 'EvtRemoveDeviceRouter'

PNPDD = 'pnpDeviceDescription'
MODEL = 'modelName'
PID = 'productId'
VID = 'vendorId'
VNAME = 'vendorName'
TID = 'topologyId'

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

MAX_LEVEL = 7

class WinUsb4TreeParse():
    def __init__(self):
        self.idata = None
        self.ldata = None
    
    def parse_usb4tb_data(self, usb4data):
        self.idata = None
        self.ldata = None
        self.idata = self.get_item_data(usb4data)
        self.ldata = self.get_level_data(self.idata)
   

    def get_item_data(self, msg):
       
        """
        Extracts USB4 item data from the input message.

        Parameters:
            msg (dict): The input message containing USB4 events.

        Returns:
            dict: A dictionary mapping unique identifiers to USB4 item data.
        """
        usb4e = msg["events"]
        pu4dict = {}

        for i in range(0, len(usb4e)):
            if usb4e[i]["eventKind"] == EADR:
                if PNPDD in usb4e[i] and "ufp" in usb4e[i]:
                    if not "Root Router" in usb4e[i][PNPDD] and not "Host Router" in usb4e[i][PNPDD]:
                        mydict = {}
                        mydict["desc"] = usb4e[i][PNPDD]
                        mydict["mname"] = usb4e[i][MODEL]
                        mydict["vname"] = usb4e[i][VNAME]
                        mydict["vid"] = usb4e[i][VID]
                        mydict["pid"] = usb4e[i][PID]
                        mydict["ports"] = []

                        ikeys = list(usb4e[i].keys())
                        if 'dfps' in ikeys:
                            plist =  usb4e[i]['dfps']
                            if len(plist) > 1:
                                for item in plist:
                                    mydict["ports"].append(item["portNumber"])
                        
                        # u4dict["item"+str(icnt)] = mydict
                        # icnt = icnt + 1
                        
                        tarr = usb4e[i][TID]
                        tarr = tarr[:tarr.index(0)]
                        idxstr = ','.join([str(aitem) for aitem in tarr])
                        pu4dict[idxstr] = mydict
        return pu4dict
    

    def get_level_data(self, u4tbuf):
        """
        Organizes data based on levels and returns a dictionary.

        Parameters:
            u4tbuf: The input data dictionary to be processed.

        Returns:
            dict: A dictionary organizing data items based on their level.
        """
        rkarr = list(u4tbuf.keys())
        pdict = {}
        for rkitem in rkarr:
            lcnt = rkitem.count(',')
            kl = list(pdict.keys())
            if 'level'+str(lcnt) in kl:
                pdict['level'+str(lcnt)].append(rkitem)
            else:
                pdict['level'+str(lcnt)] = [rkitem]
        return pdict
    