##############################################################################
# 
# Module: logWindow.py
#
# Description:
#     Log Window UI
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
#     V2.4.0 Wed July 14 2021 15:20:05   Seenivasan V
#       Module created
##############################################################################
# Lib imports
import wx

# Own modules
from uiGlobals import *
from datetime import datetime

##############################################################################
# Utilities
##############################################################################
class LogWindow(wx.Window):
    """
    A class logWindow with init method

    To show the all actions while handling ports of devices 
    """ 
    def __init__(self, parent, top):
        """
        logWindow values displayed for all Models 3201, 3141,2101 
        Args:
            self: The self parameter is a reference to the current 
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

        self.top = top
        # Create static box with naming of Log Window
        sb = wx.StaticBox(self, -1,"Log Window")

        # Create StaticBoxSizer as vertical
        self.vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)

        self.chk_box = wx.CheckBox(self, -1, label='Show Timestamp')  
        self.chk_usb = wx.CheckBox(self, -1,
                                  label='Show USB Tree View Changes')  
        self.btn_save = wx.Button(self, ID_BTN_AUTO, "Save",
                                        size=(60, -1))  
        self.btn_clear = wx.Button(self, ID_BTN_CLEAR, "Clear",
                                         size=(60, -1))     

        self.scb = wx.TextCtrl(self, -1, style= wx.TE_MULTILINE, 
                                         size=(-1,-1))
        self.scb.SetEditable(False)
        self.scb.SetBackgroundColour((255,255,255))
        
        # Tooltips display text over an widget elements
        # set tooltip for switching interval and auto buttons.
        self.btn_save.SetToolTip(wx.
                      ToolTip("Save Log content into a text file"))

        # Create BoxSizer as horizontal
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        self.hbox.Add(self.chk_box, 0, wx.ALIGN_LEFT | 
                                       wx.ALIGN_CENTER_VERTICAL)
        self.hbox.Add(30,0,0)
        self.hbox.Add(self.chk_usb, 0, wx.ALIGN_LEFT | 
                                       wx.ALIGN_CENTER_VERTICAL)
        self.hbox.Add(120,0,0)
        self.hbox.Add(self.btn_clear, 0, wx.ALIGN_RIGHT | 
                                         wx.ALIGN_CENTER_VERTICAL)
        self.hbox.Add(30,0,0)
        self.hbox.Add(self.btn_save, 1, flag=wx.RIGHT , 
                                         border = 10)
        
        # Bind the button event to handler
        self.btn_clear.Bind(wx.EVT_BUTTON, self.ClearLogWindow)
        self.btn_save.Bind(wx.EVT_BUTTON, self.SaveLogWindow)

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
        # Set size of frame
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.Layout()

    def ClearLogWindow(self, e):
        """
        Clear the Log Window.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            e: event handler for clear log window.
            set the new text control value  
        Returns:
            None
        """
        self.scb.SetValue("")
    
    def SaveLogWindow(self, e):
        """
        Save the Logwindow data
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            e: event handler for save the content of logwindow.  
        Returns:
            None
        """
        # Get the content of the control
        content = self.scb.GetValue()
        self.top.save_file(content, "*.txt")
    
    def get_time_stamp(self):
        """
        Get system time stamp.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class. 
        Returns:
            cstr - Time stamp
        """
        ct = datetime.now()
        # Format using strftime 
        dtstr = ct.strftime("%Y-%m-%d  %H:%M:%S.%f")
        cstr = "[" + dtstr[:-3] + "]  "
        return cstr
     
    def print_on_log(self, strin):
        """
        Update the data in Log Window
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class. 
            strin: print with string
        Returns:
            None
        """
        ctstr = ""
        # Print values of checkbox buttons True
        if(self.chk_box.GetValue() == True):
            ctstr = ctstr + self.get_time_stamp()
        ctstr = ctstr + strin
        self.scb.AppendText(ctstr)
     
    def is_usb_enabled(self):
        """
        Get the status of USB Device Tree View Enable option
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class. 
        Returns:
            Boolean: True - Enabled, False - Disabled
        """
        return self.chk_usb.GetValue()