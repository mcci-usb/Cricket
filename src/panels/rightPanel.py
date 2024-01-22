##############################################################################
# 
# Module: rightPanel.py
#
# Description:
#     Scan the USB bus and get the list of devices attached
#
# Copyright notice:
#     This file copyright (c) 2020 by
#
#         MCCI Corporation
#         3520 Krums Corners Road
#         Ithaca, NY  14850
#
#     Released under the MCCI Corporation.
#
# Author:
#     Seenivasan V, MCCI Corporation Mar 2020
#
# Revision history:
#    V4.3.0 Mon Jan 22 2024 17:00:00   Seenivasan V
#       Module created
##############################################################################

# from importlib.resources import contents
import wx

from features.dut import dutLogWindow
# from usb4TreeWindow import Usb4TreeWindow
from usb4tree import usb4TreeWindow

class RightPanel(wx.Panel):
    def __init__(self, parent):
        super(RightPanel, self).__init__(parent)

        self.SetBackgroundColour('White')

        self.parent =  parent

        self.usb4t = None

        self.slobj = []

        self.objtype = []

        self.objdict = {"dut1": False, "dut2": False, "u4tree": False}

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)

        self.main_sizer.Fit(self)
        self.Layout()

    
    def init_my_panel(self, pdict):
        rpdict = pdict["rpanel"]
        dutdict = pdict["dut"]
        pkeys = list(rpdict.keys())

        for pobj in pkeys:
            if rpdict[pobj] == True:
                if(pobj == "u4tree"):
                    self.slobj.append(usb4TreeWindow.Usb4TreeWindow(self, self.parent))
                    # self.objdict[pbj] = True
                else:
                    self.slobj.append(dutLogWindow.DutLogWindow(self, self.parent, {pobj: dutdict[pobj]}))
                    # self.objdict[pbj] = True
        self.display_my_objects()

        
    def display_my_objects(self):
        self.main_sizer.Clear(True)
        self.main_sizer.Add((0,20), 0, wx.EXPAND)
        for slobj in self.slobj:
            self.main_sizer.Add(slobj, 1, wx.EXPAND, 5)
            self.main_sizer.Add((0,10), 0, wx.EXPAND)
            
        self.main_sizer.Add((0,20), 0, wx.EXPAND)
        self.Layout()

    def update_my_panel(self, pdict):
        rpdict = pdict["rpanel"]
        dutdict = pdict["dut"]
        pkeys = list(pdict["rpanel"].keys())

        self.slobj.clear()

        for pobj in pkeys:
            if rpdict[pobj] == True:
                if(pobj == "u4tree"):
                    self.slobj.append(usb4TreeWindow.Usb4TreeWindow(self, self.parent))
                else:
                    self.slobj.append(dutLogWindow.DutLogWindow(self, self.parent, {pobj: dutdict[pobj]}))
        self.display_my_objects()

    def add_switches(self, swlist):
        self.Layout()
    
    def update_usb4_tree(self, msusb4):
        for rpobj in self.slobj:
            if rpobj.name == "usb4tree":
                rpobj.update_usb4_tree(msusb4)
                break
    
    def print_on_log(self, data):
        pass
