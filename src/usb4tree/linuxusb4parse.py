
##############################################################################
# 
# Module: linuxusb4parse.py
#
# Description:
#     parsing the USB4 Tree view data in Linux 
#
# Author:
#     Seenivasan V, MCCI Corporation Jan 2024
#
# Revision history:
#      V4.3.1 Mon Apr 15 2024 17:00:00   Seenivasan V 
#       Module created
##############################################################################
class LinuxUsb4TreeParse():
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
