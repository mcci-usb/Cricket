# -*- coding: utf-8 -*-
##############################################################################
# 
# Module: Winusb4parse.py
#
# Description:
#     USB4 Tree View Parsing module for Windows systems.
#     Parses USB4 / Thunderbolt topology data received from
#     Windows USB4 services and organizes it into hierarchical levels.
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
# Revision history:
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
#
##############################################################################
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


##############################################################################
# Utilities
##############################################################################
class WinUsb4TreeParse():
    """
    Summary:
        Windows USB4 Tree Parser.

    Longer Description:
        Parses USB4 / Thunderbolt topology data received from
        Windows event streams and converts it into structured
        dictionaries for UI tree rendering.

    Attributes:
        idata (dict):
            Parsed item-level USB4 data.

        ldata (dict):
            Hierarchical level-wise USB4 topology data.
    """
    def __init__(self):
        """
        Initialize Windows USB4 Tree Parser.

        Args:
            None

        Returns:
            None
        """
        self.idata = None
        self.ldata = None
    
    def parse_usb4tb_data(self, usb4data):
        """
        Parse USB4 Thunderbolt data.

        Description:
            Entry method to parse incoming USB4 event data.
            Generates item-level data and hierarchical level data.

        Args:
            usb4data (dict):
                Raw USB4 event JSON data.

        Returns:
            None
        """
        self.idata = None
        self.ldata = None
        self.idata = self.get_item_data(usb4data)
        self.ldata = self.get_level_data(self.idata)
   
    def get_item_data(self, msg):
        """
        Extract USB4 item data from event message.

        Description:
            Processes USB4 router add events and extracts
            device-level information such as:

            - Description
            - Model name
            - Vendor name
            - VID / PID
            - Port mapping

        Args:
            msg (dict):
                Input USB4 event message.

        Returns:
            dict:
                Dictionary mapping topology index strings
                to parsed USB4 device information.
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
        Organize USB4 data into hierarchical levels.

        Description:
            Groups parsed USB4 devices based on their
            topology depth level for tree visualization.

        Args:
            u4tbuf (dict):
                Parsed USB4 item dictionary.

        Returns:
            dict:
                Dictionary with level keys such as:

                    level0
                    level1
                    level2

                Each containing topology index references.
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
    