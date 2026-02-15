# -*- coding: utf-8 -*-
##############################################################################
# 
# Module: linuxusb4parse.py
#
# Description:
#     This module provides parsing utilities for USB4 and
#     Thunderbolt topology data on Linux systems.
#
#     It converts enumerated USB4 device information into
#     structured hierarchy buffers that can be rendered in
#     Tree View UI components.
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
class LinuxUsb4TreeParse():
    """
    Linux USB4 / Thunderbolt Tree Parser.

    Description:
        Parses USB4 and Thunderbolt enumeration data collected
        from Linux systems and converts it into structured
        hierarchy buffers for Tree View visualization.

        The parser generates:

            • Indexed device data (idata)
            • Level-wise hierarchy mapping (ldata)

    Attributes:
        idata (dict):
            Parsed USB4 device dictionary indexed by node ID.

        ldata (dict):
            Hierarchy level mapping dictionary.
    """
    def __init__(self):
        self.idata = None
        self.ldata = None

    def parse_usb4tb_data(self, usb4data):
        """
        Parse USB4TB data and organize it into internal data structures.

        This method takes USB4TB data and organizes it into internal data structures
        for easier access and manipulation.

        Args:
            usb4data (dict): USB4TB data to be parsed.

        Returns:
            None
        """
        self.idata = {}
        self.ldata = {}

        cnt = 0
        level0 = []
        for dev in usb4data:
            usb4data[dev]["mname"] = usb4data[dev]["name"]
            usb4data[dev]["vname"] = usb4data[dev]["vendor"]
            usb4data[dev]["ports"] = []
            self.idata[str(cnt)] = usb4data[dev]
            level0.append(str(cnt))
            cnt = cnt + 1

        self.ldata["level0"] = level0
