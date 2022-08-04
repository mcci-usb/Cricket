# Lib imports
import wx

# Own modules
from uiGlobals import *
from datetime import datetime

import wx
import threading


##############################################################################
# Utilities
##############################################################################
class SerialLogWindow(wx.Window):
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
        self.SetMinSize((480,330))

        self.top = top
        # Create static box with naming of Log Window
        sb = wx.StaticBox(self, -1,"Serial Log Window")

        self.vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)

        self.btn_save = wx.Button(self, ID_BTN_AUTO, "Save",
                                        size=(60, -1))  
        self.btn_clear = wx.Button(self, ID_BTN_CLEAR, "Clear",
                                         size=(60, 25))     

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
        self.wait_flg = False
        
        self.hbox.Add(30,0,0)
        self.hbox.Add(self.btn_clear, 0, wx.ALIGN_RIGHT | 
                                         wx.ALIGN_CENTER_VERTICAL)
        self.hbox.Add(45,0,0)
        self.hbox.Add(self.btn_save, 1, flag=wx.LEFT , 
                                         border = 240)
        
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
