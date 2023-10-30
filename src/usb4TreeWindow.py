##############################################################################
# 
# Module: serialLogWindow.py
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

# Lib imports
import wx

# Own modules
from uiGlobals import *
from datetime import datetime

import wx

from wdpLogin import LoginFrame

##############################################################################
# Utilities
##############################################################################
class Usb4TreeWindow(wx.Window):
    """
    A class logWindow with init method

    To show the all actions while handling ports of devices 
    """
    def __init__(self, parent, top):
        """
        logWindow values displayed for all Models 3201, 3141,2101 
        Args:
            self: The self parameter is a reference to the current .
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
            top: creates an object
        Returns:
            None
        """
        wx.Window.__init__(self, parent)
        # SET BACKGROUND COLOUR TO White
        self.SetBackgroundColour("White")
        self.SetMinSize((480,330))

        self.top = top
        self.parent = parent

        self.totline = 0

        sb = wx.StaticBox(self, -1, "USB4 Tree View")

        self.vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)

        self.btn_config = wx.Button(self, ID_BTN_SL_CONFIG, "Config",
                                        size=(60, -1))
 

        self.scb = wx.TextCtrl(self, -1, style= wx.TE_MULTILINE, 
                                         size=(-1,-1))
        self.scb.SetEditable(False)
        self.scb.SetBackgroundColour((255,255,255))
        
        # Tooltips display text over an widget elements
        # set tooltip for switching interval and auto buttons.
        # Create BoxSizer as horizontal
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.wait_flg = False

        self.btn_config.Bind(wx.EVT_BUTTON, self.OnDutConfig)

        self.hbox.Add(30,0,0)
        self.hbox.Add(self.btn_config, 0, wx.ALIGN_LEFT | 
                                         wx.ALIGN_CENTER_VERTICAL)

        self.szr_top = wx.BoxSizer(wx.VERTICAL)
        self.szr_top.AddMany([
            (5,0,0),
            (self.scb, 1, wx.EXPAND),
            (5,0,0)
            ])

        self.vbox.AddMany([
            (self.hbox, 0, wx.ALIGN_LEFT),
            (10,5,0),
            (self.szr_top, 1, wx.EXPAND),
            (0,0,0)
            ])

        print("USB4 Tree View Layout Added")

        

        # Set size of frame
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.Layout()



    def OnDutConfig(self, e):

        dlg = LoginFrame(self, self)
        dlg.Show()