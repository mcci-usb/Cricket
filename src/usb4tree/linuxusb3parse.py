# -*- coding: utf-8 -*-
##############################################################################
# 
# Module: linuxusb3parse.py
#
# Description:
#     parsing the USB3 Tree view data in Linux 
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
# Revision history:
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
#
##############################################################################
##############################################################################
# Utilities
##############################################################################
class LinuxUsb3TreeParse():
    """
    Linux USB3 Tree Parser.

    Description:
        Parses USB 3.x enumeration data collected from
        Linux systems and converts it into structured
        hierarchy buffers for Tree View visualization.

        The parser generates:

            • Indexed device data (idata)
            • Level-wise hierarchy mapping (ldata)

    Attributes:
        idata (dict):
            Parsed USB3 device dictionary indexed by node ID.

        ldata (dict):
            Hierarchy level mapping dictionary.
    """
    def __init__(self):
        self.idata = None
        self.ldata = None
    
    def parse_usb3tb_data(self, usb3data):
        """
        Parse USB3 topology data.

        Description:
            Converts raw USB3 enumeration output into structured
            internal buffers suitable for Tree View rendering.

            Processing steps:

                1. Normalize USB3 attributes
                2. Build indexed device dictionary
                3. Generate hierarchy level mappings

        Args:
            usb3data (list):
                List of USB3 device dictionaries obtained from
                Linux enumeration modules.

        Returns:
            None
        """
        self.idata = self.get_item_data(usb3data)
        self.ldata = self.get_level_data(self.idata)

    def get_item_data(self, msg):
        """
        Parse USB3 device list into indexed dictionary.

        Description:
            Converts a list of USB3 device dictionaries into a
            structured mapping indexed by composite keys.

            Key format:

                vid,pid,bus,speed

        Args:
            msg (list):
                USB3 device list collected during enumeration.

        Returns:
            dict:
                Parsed USB3 dictionary.

            None:
                If input format is invalid.
        """
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
        """
        Organize USB3 data into hierarchy levels.

        Description:
            Groups USB3 devices into levels based on the
            number of comma separators in their keys.

            This enables Tree View hierarchical rendering.

        Args:
            u3tbuf (dict):
                Parsed USB3 device dictionary.

        Returns:
            dict:
                Level-wise USB3 hierarchy mapping.

            None:
                If input format is invalid.
        """
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

