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
#    V4.0.0 Wed May 25 2023 17:00:00   Seenivasan V
#       Module created
##############################################################################

# from importlib.resources import contents
import wx

from dutLogWindow import DutLogWindow

class RightPanel(wx.Panel):
    def __init__(self, parent):
        super(RightPanel, self).__init__(parent)

        self.SetBackgroundColour('White')

        self.parent =  parent

        self.slobj = []

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)

        self.main_sizer.Fit(self)
        self.Layout()

    def update_slog_panel(self, duts):

        if(len(self.slobj) > 0):
            self.main_sizer.Clear(True)

        self.slobj.clear()

        keylen = list(duts.keys())

        if(len(keylen) > 0):
            nodes = []
            for node in duts["nodes"]:
                if(duts["nodes"][node]):
                    # nodes.append(suts[node])
                    self.slobj.append(DutLogWindow(self, self.parent, {node: duts[node]}))

        self.main_sizer.Add((0,20), 0, wx.EXPAND)
        for slobj in self.slobj:
            self.main_sizer.Add(slobj, 1, wx.EXPAND, 5)
            self.main_sizer.Add((0,10), 0, wx.EXPAND)
            
        self.main_sizer.Add((0,20), 0, wx.EXPAND)
        self.Layout()

    def add_switches(self, swlist):
        self.Layout()