# -*- coding: utf-8 -*-
##############################################################################
# 
# Module: winusb3parse.py
#
# Description:
#     USB 3.0 Tree View Parsing module for Windows systems.
#     Parses USB3 enumeration data and organizes it into
#     hierarchical tree levels for UI representation.
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
class WinUsb3TreeParse():
    """
    Summary:
        Windows USB3 Tree Parser.

    Longer Description:
        Parses enumerated USB3 device data and converts it into
        structured dictionaries suitable for tree view rendering
        in UI applications.

    Attributes:
        idata (dict):
            Parsed USB3 device item data.

        ldata (dict):
            Hierarchical level-wise USB3 topology data.
    """
    def __init__(self):
        """
        Initialize USB3 Tree Parser.

        Args:
            None

        Returns:
            None
        """
        self.idata = None
        self.ldata = None
    
    def parse_usb3tb_data(self, usb3data):
        """
        Parse USB3 topology data.

        Description:
            Entry method to parse raw USB3 enumeration data.
            Generates structured item data and hierarchical level data.

        Args:
            usb3data (list):
                List of USB3 device dictionaries obtained
                from enumeration modules.

        Returns:
            None
        """
        self.idata = self.get_item_data(usb3data)
        self.ldata = self.get_level_data(self.idata)
        
    def get_item_data(self, msg):
        """
        Extract USB3 item data.

        Description:
            Processes USB3 device list and extracts key device
            attributes required for tree rendering such as:

            - Vendor ID
            - Product ID
            - Bus number
            - Speed
            - Interface classes
            - Port mapping

        Args:
            msg (list):
                Raw USB3 enumeration data list.

        Returns:
            dict:
                Dictionary mapping unique keys to parsed USB3 items.
                Returns None if input format is invalid.
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
        """
        Organize USB3 data into hierarchical levels.

        Description:
            Groups parsed USB3 devices based on topology depth
            by counting key delimiters. Used for UI tree generation.

        Args:
            u3tbuf (dict):
                Parsed USB3 item dictionary.

        Returns:
            dict:
                Dictionary with level keys such as:

                    level0
                    level1
                    level2

                Each containing lists of topology keys.
                Returns None if input is invalid.
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
