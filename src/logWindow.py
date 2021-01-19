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
#     V2.0.0 Fri Jan 15 2021 18:50:59 seenivasan
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
"""
A class logWindow with init method

the logWindow navigate to displayed the scrollable list of strings 
"""
class LogWindow(wx.Window):
    """
    logWindow values displayed for all Models 3201, 3141,2101 
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        parent: Pointer to a parent window.
        top: create a object
    Returns:
        return None
    """
    def __init__(self, parent, top):
        wx.Window.__init__(self, parent)
        # SET BACKGROUND COLOUR TO White
        self.SetBackgroundColour("White")

        self.top = top
        # create static box with naming of Auto Mode
        sb = wx.StaticBox(self, -1,"Log Window")

        # create StaticBoxSizer as vertical
        self.vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)

        self.chk_box = wx.CheckBox(self, -1, label='Show Timestamp')  
        self.chk_usb = wx.CheckBox(self, -1, label='Show USB Tree View Changes')  
        self.btn_save = wx.Button(self, ID_BTN_AUTO, "Save", size=(60, -1))  
        self.btn_clear = wx.Button(self, ID_BTN_CLEAR, "Clear", size=(60, -1))     

        self.scb = wx.TextCtrl(self, -1, style= wx.TE_MULTILINE, size=(-1,-1))
        self.scb.SetEditable(False)
        self.scb.SetBackgroundColour((255,255,255))
        #self.SetMinSize((600,360))

        #Tooltips display text over an widget elements
        #set tooltip for switching interval and auto buttons.
        self.btn_save.SetToolTip(wx.ToolTip("Save Log content into a text file"))

        # create BoxSizer as horizontal
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        self.hbox.Add(self.chk_box, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.hbox.Add(30,0,0)
        self.hbox.Add(self.chk_usb, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.hbox.Add(120,0,0)
        self.hbox.Add(self.btn_clear, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        self.hbox.Add(30,0,0)
        self.hbox.Add(self.btn_save, 1, flag=wx.RIGHT , border = 10)
        
        # bind the button event to handler
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
        # set size of frame
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.Layout()

    """
    Clear a Log Window
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        e: event handler for clear log window.
        set the new text control value  
    Returns:
        return None
    """
    def ClearLogWindow(self, e):
        self.scb.SetValue("")
    """
    Export LogWindow content to a file
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        e: event handler for save the content of logwindow.  
    Returns:
        return None
    """
    def SaveLogWindow(self, e):
        # get the content of the control
        content = self.scb.GetValue()
        self.top.save_file(content, "*.txt")
    """
    Get System Time stamp
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class. 
    Returns:
        return None
    """
    def get_time_stamp(self):
        ct = datetime.now()
        # format using strftime 
        dtstr = ct.strftime("%Y-%m-%d  %H:%M:%S.%f")
        cstr = "[" + dtstr[:-3] + "]  "
        return cstr
    """
    Show the Content in LogWindow
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class. 
        strin: print with string
    Returns:
        return None
    """ 
    def print_on_log(self, strin):
        ctstr = ""
        # print values of checkbox buttons True
        if(self.chk_box.GetValue() == True):
            ctstr = ctstr + self.get_time_stamp()
        ctstr = ctstr + strin
        self.scb.AppendText(ctstr)
    """
    Get the status of USB Scan selection option
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class. 
    Returns:
        return None
    """ 
    def is_usb_enabled(self):
        return self.chk_usb.GetValue()
