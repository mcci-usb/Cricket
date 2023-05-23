##############################################################################
# 
# Module: leftPanel.py
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
#    V4.0.0 Wed May 25 2023 17:00:00   Seenivasan V
#       Module created
##############################################################################
from matplotlib.pyplot import switch_backend
import wx

from wx.lib.scrolledpanel import ScrolledPanel

from dev2101Window import Dev2101Window
from dev3141Window import Dev3141Window
from dev3142Window import Dev3142Window
from dev3201Window import Dev3201Window
from dev2301Window import Dev2301Window
from noSwWindow import NoSwWindow

class LeftPanel(ScrolledPanel):
    def __init__(self, parent, top):
        super(LeftPanel, self).__init__(parent)

        self.SetBackgroundColour('White')

        self.SetupScrolling()

        self.parent = top

        # self.SetSize((300, 720))

        self.SetMinSize((320, 720))

        self.sb = wx.StaticBox(self, -1, "MCCI USB Switches")

        self.main_sizer = wx.StaticBoxSizer(self.sb,wx.VERTICAL)

        # self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.swobj = []

        self.swobjmap = {"3141": Dev3141Window,"3142":Dev3142Window,"3201": Dev3201Window, "2301": Dev2301Window, "2101": Dev2101Window}

        self.multiswobj = {}

        self.SetSizer(self.main_sizer)

        # Setting Layouts
        self.SetAutoLayout(True)
        self.main_sizer.Fit(self)
        self.Layout()

    def no_switches(self):
        if(len(self.multiswobj) > 0):
            self.main_sizer.Clear(True)
        self.main_sizer.Add(NoSwWindow(self, self.parent), 0, wx.ALL, 5)
        self.main_sizer.Add((0,20), 0, wx.EXPAND)
        self.Layout()

    def add_switches(self, swlist):
        if len(swlist) > 0:
            if(len(self.multiswobj) > 0):
                self.main_sizer.Clear(True)
                
            self.multiswobj.clear()

            for key, value in swlist.items():
                self.multiswobj[key] = self.swobjmap[value](self, self.parent, key)
        else:
            self.multiswobj["noswitch"] = NoSwWindow(self, self.parent)

        # self.main_sizer.Add((0,20), 0, wx.EXPAND)
        for key, value in self.multiswobj.items():
            self.main_sizer.Add(value, 0, wx.ALL, 5)
            self.main_sizer.Add((0,10), 0, wx.EXPAND)
            
        self.main_sizer.Add((0,20), 0, wx.EXPAND)
        self.Layout()

    def port_on(self, swkey, port, stat):
        self.multiswobj[swkey].port_on(port, stat)

    def set_speed(self, swkey, speed):
        self.multiswobj[swkey].set_speed(speed)

    def read_param(self, swkey, param):
        self.multiswobj[swkey].read_param(param)