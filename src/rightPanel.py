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
#    V2.6.0 Wed Apr 20 2022 17:00:00   Seenivasan V
#       Module created
##############################################################################

# from importlib.resources import contents
import wx

from sutLogWindow import SutLogWindow

class RightPanel(wx.Panel):
    def __init__(self, parent):
        super(RightPanel, self).__init__(parent)

        self.SetBackgroundColour('White')

        # self.SetMaxSize((400, -1))
        # self.SetSize((300, 700))

        # self.slogPan = SerialLogWindow(self, parent)
        # self.slogPan2 = SerialLogWindow(self, parent)
        self.parent =  parent

        self.slobj = []

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        # for number in range(5):
        #     btn = wx.Button(self, label='Button {}'.format(number))
        #     main_sizer.Add(btn, 0, wx.ALL, 5)


        # self.main_sizer.Add(0, 10, 0)
        # self.main_sizer.Add(self.slogPan, 1, wx.EXPAND)
        # self.main_sizer.Add(0, 10, 0)
        # self.main_sizer.Add(self.slogPan2, 1, wx.EXPAND)
        # self.main_sizer.Add(0, 10, 0)

        self.SetSizer(self.main_sizer)

        # self.SetSizer(self.vb_outer)
        
        # Setting Layouts
        # self.SetAutoLayout(True)
        self.main_sizer.Fit(self)
        self.Layout()

    def update_slog_panel_old(self, cnt):
        if(len(self.slobj) > 0):
            self.main_sizer.Clear(True)

        self.slobj.clear()

        for idx in range(0, cnt):
            self.slobj.append(SutLogWindow(self, self.parent))

        self.main_sizer.Add((0,20), 0, wx.EXPAND)
        for slobj in self.slobj:
            self.main_sizer.Add(slobj, 1, wx.EXPAND, 5)
            self.main_sizer.Add((0,10), 0, wx.EXPAND)
            
        self.main_sizer.Add((0,20), 0, wx.EXPAND)
        self.Layout()

    def update_slog_panel(self, suts):

        if(len(self.slobj) > 0):
            self.main_sizer.Clear(True)

        self.slobj.clear()

        keylen = list(suts.keys())

        if(len(keylen) > 0):
            nodes = []
            for node in suts["nodes"]:
                if(suts["nodes"][node]):
                    # nodes.append(suts[node])
                    self.slobj.append(SutLogWindow(self, self.parent, {node: suts[node]}))

        self.main_sizer.Add((0,20), 0, wx.EXPAND)
        for slobj in self.slobj:
            self.main_sizer.Add(slobj, 1, wx.EXPAND, 5)
            self.main_sizer.Add((0,10), 0, wx.EXPAND)
            
        self.main_sizer.Add((0,20), 0, wx.EXPAND)
        self.Layout()


    def Hide_SL1(self):
        self.slogPan.Hide()
        self.Layout()

    def Hide_SL2(self):
        self.slogPan2.Hide()
        self.Layout()

    def Show_SL1(self):
        self.slogPan.Show()
        self.Layout()

    def Show_SL2(self):
        self.slogPan2.Show()
        self.Layout()

    def add_switches(self, swlist):
        self.Layout()
        pass