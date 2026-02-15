# -*- coding: utf-8 -*-
##############################################################################
# 
# Module: Macusb3parse.py
#
# Description:
#     This module provides parsing utilities for USB 3.0 topology
#     data on macOS systems.
#
#     It converts enumerated USB3 device information into structured
#     hierarchy buffers that can be rendered in Tree View UI
#     components.
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
class MacUsb3TreeParse():
    """
    macOS USB 3.0 Tree Parser.

    Description:
        Parses USB 3.0 enumeration data and converts it into
        structured tree buffers for UI visualization.

        The parser generates:

            • Indexed device data (idata)
            • Level-wise hierarchy mapping (ldata)

    Attributes:
        idata (dict):
            Parsed USB3 device dictionary.

        ldata (dict):
            Hierarchy level mapping dictionary.
    """
    def __init__(self):
        self.idata = None
        self.ldata = None
    
    def parse_usb3tb_data(self, usb3data):
        """
        Parse USB 3.0 topology data.

        Description:
            Converts raw USB3 enumeration output into structured
            internal buffers for Tree View rendering.

            Processing steps:

                1. Parse device list
                2. Build indexed dictionary
                3. Generate hierarchy levels

        Args:
            usb3data (list):
                List of USB3 device dictionaries.

        Returns:
            None
        """
        
        self.idata = self.get_item_data(usb3data)
        self.ldata = self.get_level_data(self.idata)
        

    def get_item_data(self, msg):
        """
        Extract USB 3.0 device information.

        Description:
            Parses a list of USB3 device dictionaries and
            converts them into indexed device records.

            Each device key is generated using:

                vid,pid,bus,speed

        Args:
            msg (list):
                USB3 enumeration list.

        Returns:
            dict:
                Parsed USB3 device dictionary.

            None:
                If input is invalid.
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
        Generate hierarchy level mapping.

        Description:
            Organizes USB3 device keys into hierarchy levels
            based on comma depth in index keys.

            Example key:

                "32903,2880,2,5"

            Comma count determines level grouping.

        Args:
            u3tbuf (dict):
                Indexed USB3 device dictionary.

        Returns:
            dict:
                Level-wise hierarchy mapping.

            None:
                If input is invalid.
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