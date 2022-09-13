##############################################################################
# 
# Module: getusb.py
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
#    V2.6.0 Wed Apr 20 2022 17:00:00   Seenivasan V
#       Module created
##############################################################################
from matplotlib.pyplot import switch_backend
import wx

from wx.lib.scrolledpanel import ScrolledPanel

from dev2101Window import Dev2101Window
from dev3141Window import Dev3141Window
from dev3201Window import Dev3201Window
from dev2301Window import Dev2301Window

class LeftPanel(ScrolledPanel):
    def __init__(self, parent, top):
        super(LeftPanel, self).__init__(parent)

        self.SetBackgroundColour('White')

        self.SetupScrolling()

        self.parent = top

        # self.SetSize((300, 720))

        self.SetMinSize((320, 720))

        self.sb = wx.StaticBox(self, -1, "Multiple Switches")

        self.main_sizer = wx.StaticBoxSizer(self.sb,wx.VERTICAL)

        # self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.swobj = []

        self.swobjmap = {"3141": Dev3141Window, "3201": Dev3201Window, "2301": Dev2301Window, "2101": Dev2101Window}

        self.multiswobj = {}


        self.SetSizer(self.main_sizer)

        # self.SetSizer(self.vb_outer)
        
        # Setting Layouts
        self.SetAutoLayout(True)
        self.main_sizer.Fit(self)
        self.Layout()

    # def add_switches_notreq(self, swobj):
    #     print("I am Lpanel, showning Sw objects: ", swobj)
    #     if(len(self.swobj) > 0):
    #         self.main_sizer.Clear(True)
            
    #     self.swobj.clear()

    #     self.swobj = list(swobj.values())

    #     self.main_sizer.Add((0,20), 0, wx.EXPAND)
    #     for swobj in self.swobj:
    #         self.main_sizer.Add(swobj, 0, wx.ALL, 5)
    #         self.main_sizer.Add((0,10), 0, wx.EXPAND)
            
    #     self.main_sizer.Add((0,20), 0, wx.EXPAND)
    #     self.Layout()


    def add_switches(self, swlist):
        # swkey = list(swlist.keys())
        # swvalue = list(swlist.values())
        print("Left Panel: ", swlist)

        if(len(self.multiswobj) > 0):
            self.main_sizer.Clear(True)
            
        self.multiswobj.clear()

        for key, value in swlist.items():
            self.multiswobj[key] = self.swobjmap[value](self, self.parent, key)

        # self.main_sizer.Add((0,20), 0, wx.EXPAND)
        for key, value in self.multiswobj.items():
            self.main_sizer.Add(value, 0, wx.ALL, 5)
            self.main_sizer.Add((0,10), 0, wx.EXPAND)
            
        self.main_sizer.Add((0,20), 0, wx.EXPAND)
        self.Layout()


    def add_switches_old(self, swlist):
        print("I am Left Panel, now adding switches one by one")
        nswlist = list(swlist.values())
        swidlist = list(swlist.keys())        
        
        # for swobj in self.swobj:
        #     self.main_sizer.
        if(len(self.swobj) > 0):
            self.main_sizer.Clear(True)
            
        self.swobj.clear()

        for idx in range(len(nswlist)):
            if(nswlist[idx] == '3141'):
                self.swobj.append(Dev3141Window(self, self.parent, swidlist[idx]))
            elif(nswlist[idx] == '3201'):
                self.swobj.append(Dev3201Window(self, self.parent, swidlist[idx]))
            elif(nswlist[idx] == '2101'):
                self.swobj.append(Dev2101Window(self, self.parent, swidlist[idx]))
            elif(nswlist[idx] == '2301'):
                self.swobj.append(Dev2301Window(self, self.parent, swidlist[idx]))

        self.main_sizer.Add((0,20), 0, wx.EXPAND)
        for swobj in self.swobj:
            self.main_sizer.Add(swobj, 0, wx.ALL, 5)
            self.main_sizer.Add((0,10), 0, wx.EXPAND)
            
        self.main_sizer.Add((0,20), 0, wx.EXPAND)
        self.Layout()
        
    def port_on(self, swkey, port, stat):
        self.multiswobj[swkey].port_on(port, stat)
