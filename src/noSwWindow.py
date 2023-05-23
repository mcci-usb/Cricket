##############################################################################
# 
# Module: dev2101Window.py
#
# Description:
#     Device specific functions and UI for interfacing Model 2101 with GUI
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
#Lib imports
import wx

# Built-in imports
import os

from uiGlobals import *


##############################################################################
# Utilities
##############################################################################
class NoSwWindow(wx.Panel):
    """
    A class Dev2101Window with init method

    the Dev2101Window navigate to Super speed and High speed enable 
    or disable options.
    """
    def __init__(self, parent, top):
        """
        Device specific functions and UI for interfacing Model 2101 with GUI
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
            top: create a object
        Returns:
            None
        """
        wx.Panel.__init__(self, parent)
        
        self.parent = parent
        self.top = top
 
        self.swtitle = "No Switches Selected"
       

        # Call this to give the sizer a minimal size.
        self.SetMinSize((280, 220))
        # Create a staticbox naming as  Model2101 
        self.sb = wx.StaticBox(self, -1, self.swtitle)
        # BoxSizer fixed with Vertical
        self.vbox = wx.StaticBoxSizer(self.sb,wx.VERTICAL)
        
        self.hboxs1 = wx.BoxSizer(wx.HORIZONTAL)
        
        base = os.path.abspath(os.path.dirname(__file__))
        self.picnosw = wx.Bitmap (base+"/icons/"+IMG_NOSWITCH, wx.BITMAP_TYPE_ANY)
        
        self.btn_nosw = wx.BitmapButton(self, ID_BTN_3141, self.picnosw,size= (-1,-1))
        
        self.hboxs1.Add(self.btn_nosw, flag=wx.ALIGN_CENTER | 
                       wx.LEFT, border = 0)
        
        self.vbox.AddMany([
            (self.hboxs1, 1, wx.EXPAND | wx.ALL),
            ])

        # Set size of frame
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.Layout()