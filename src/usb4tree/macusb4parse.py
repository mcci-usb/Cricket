# -*- coding: utf-8 -*-
##############################################################################
# 
# Module: macusb4parse.py
#
# Description:
#     This module provides parsing utilities for USB4 and Thunderbolt
#     topology data on macOS systems.
#
#     It processes the macOS System Profiler output and converts the
#     hierarchical USB4 / Thunderbolt device structure into an
#     indexed tree format suitable for UI Tree View rendering.
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
import copy

class MacUsb4TreeParse():
    """
    macOS USB4 / Thunderbolt Tree Parser.

    Description:
        Parses macOS USB4 / Thunderbolt topology data obtained
        from System Profiler and converts it into structured
        tree buffers.

        The parsed output includes:

            • Indexed device data (idata)
            • Level-wise hierarchy data (ldata)
            • Port relationship mapping

    Attributes:
        idata (dict):
            Indexed USB4 device data.

        ldata (dict):
            Level-wise hierarchy mapping.
    """
    def __init__(self):
        self.idata = None
        self.ldata = None

    def parse_usb4tb_data(self, usb4data):
        """
        Parse USB4 / Thunderbolt topology data.

        Description:
            Processes raw macOS System Profiler USB4 data and
            converts it into structured tree data.

            Processing steps:

                1. Extract USB tree nodes
                2. Merge multiple root buses
                3. Build hierarchy index map
                4. Compute level groupings
                5. Populate downstream port mappings

        Args:
            usb4data (dict):
                Raw USB4 / Thunderbolt data from macOS
                System Profiler.

        Returns:
            None
        """
        self.idata = None
        self.ldata = None
        mlist = self.get_item_data(usb4data)
        
        mdlist = []
        idx = 0
        for busd in mlist:
            mdlist.append(self.merge_parent_node(busd, idx))
            idx = idx + 1
        
        mdict = {}
        for busd in mdlist:
            mdict.update(busd)

        ldict = self.get_level_data(mdict)

        portdict = {}

        for level in ldict:
            for dev in ldict[level]:
                self.add_ports(level, dev, ldict, portdict)

        for dev in mdict:
            mdict[dev]["ports"] = portdict[dev]


        self.idata = copy.deepcopy(mdict)
        self.ldata = copy.deepcopy(ldict)

    def add_ports(self, glevel, gdev, gldict, gpdict):
        """
        Populate downstream port mappings.

        Description:
            Identifies child routing nodes connected to a
            given parent device and records their port
            relationships.

        Args:
            glevel (str):
                Current hierarchy level.

            gdev (str):
                Device index key.

            gldict (dict):
                Level mapping dictionary.

            gpdict (dict):
                Output port mapping dictionary.

        Returns:
            None
        """
            
        nidx = int(glevel.split('level')[1])+1
        nlkey = 'level'+str(nidx)
        if nlkey in gldict:
            nldlist = gldict[nlkey]
            gpdict[gdev] = [int(s.split(gdev+',')[1]) for s in nldlist if s.startswith(gdev+',')]
        else:
            gpdict[gdev] = []

    # Parse the USB4 JSON to Tree buffer (customized)
    def get_item_data(self, msg):
        """
        Extract USB4 tree data from System Profiler output.

        Description:
            Parses the 'SPThunderboltDataType' section and
            builds intermediate USB tree dictionaries for
            each Thunderbolt bus.

        Args:
            msg (dict):
                macOS System Profiler JSON output.

        Returns:
            list:
                List of parsed USB4 bus dictionaries.
        """
        usb_data = msg["SPThunderboltDataType"]
        usbt_list = []

        for bus in usb_data:
            usbt_list.append(self.parse_usb_tree(bus, {}))
        return usbt_list
    
    # # Recursive function extract VID, PID and other properties
    def parse_usb_tree(self, node, accdict):
        """
        Recursively parse USB tree nodes.

        Description:
            Traverses Thunderbolt topology nodes and extracts:

                • Device name
                • Description
                • Vendor name
                • VID / PID
                • Routing index

        Args:
            node (dict):
                Current USB tree node.

            accdict (dict):
                Accumulator dictionary.

        Returns:
            dict:
                Updated accumulator dictionary.
        """
        if "_name" in node and "device_name_key" in node:
            mydict = {}
            mydict["mname"] = node['_name']
            mydict["desc"] = node['device_name_key']
            mydict['vname'] = node['vendor_name_key']
            if 'device_id_key' in node and 'vendor_id_key' in node:
                mydict['vid'] = int(node['vendor_id_key'], 16)
                mydict['pid'] = int(node['device_id_key'], 16)
            ordstr = self.convert_order(node["route_string_key"])
            # if ordstr != '0':
            accdict[ordstr] = mydict

        if "_items" in node:
            for item in node["_items"]:
                self.parse_usb_tree(item, accdict)
        return accdict
    
    def convert_order(self, instr):
        """
        Convert macOS route string to hierarchy index.

        Description:
            macOS represents routing paths as digit strings
            (example: "30701").

            This method converts them into comma-separated
            hierarchy indexes.

            Example:

                Input  → "30701"
                Output → "1,7,3"

        Args:
            instr (str):
                Route string from System Profiler.

        Returns:
            str:
                Hierarchy index string.
        """
        conv_nums = []
        for i in range(len(instr)-2, -1, -2):
            two_digits = instr[i:i+2]
            conv_numb = int(two_digits.lstrip('0'))
            conv_nums.append(conv_numb)
        if len(instr) % 2 == 1:
            conv_nums.append(int(instr[0]))
        ordstr = ','.join(map(str, conv_nums))
        return ordstr
 
    def merge_parent_node(self, u4dict, idx):
        """
        Merge Thunderbolt root buses.

        Description:
            macOS may expose multiple root Thunderbolt buses.

            This method prefixes child routing indexes with
            a root index to ensure unique topology keys.

        Args:
            u4dict (dict):
                Parsed USB4 dictionary.

            idx (int):
                Root bus index.

        Returns:
            dict:
                Updated dictionary with merged hierarchy keys.
        """
        nu4dict = {}
        for key, value in u4dict.items():
            if key != '0':
                nkey = str(idx) + ',' + key
                nu4dict[nkey] = value
            else:
                nu4dict[str(idx)] = value
        return nu4dict
    
    # Both Win and Mac
    def get_level_data(self, u4tbuf):
        """
        Generate hierarchy level mapping.

        Description:
            Groups USB4 routing indexes into levels
            based on comma depth.

            Example:

                level0 → Root routers
                level1 → First downstream routers
                level2 → Second downstream routers

        Args:
            u4tbuf (dict):
                Indexed USB4 topology data.

        Returns:
            dict:
                Level-wise hierarchy dictionary.
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