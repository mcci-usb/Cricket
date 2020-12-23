#==========================================================================
# (c) 2020  MCCI, Inc.
#--------------------------------------------------------------------------
# Project : UI3141/3201 GUI Application
# File    : logWindow.py
#--------------------------------------------------------------------------
# Log Window UI 
#==========================================================================

#==========================================================================
# IMPORTS
#==========================================================================
import wx

from uiGlobals import *

from datetime import datetime

#==========================================================================
# COMPONENTS
#==========================================================================

class LogWindow(wx.Window):
    def __init__(self, parent, top):
        wx.Window.__init__(self, parent)
        self.SetBackgroundColour("White")

        self.top = top

        sb = wx.StaticBox(self, -1,"Log Window")
        self.vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)

        self.chk_box = wx.CheckBox(self, -1, label='Show Timestamp')  
        self.chk_usb = wx.CheckBox(self, -1, label='Show USB Tree View Changes')  
        self.btn_save = wx.Button(self, ID_BTN_AUTO, "Save", size=(60, -1))  
        self.btn_clear = wx.Button(self, ID_BTN_CLEAR, "Clear", size=(60, -1))     

        self.scb = wx.TextCtrl(self, -1, style= wx.TE_MULTILINE, size=(-1,-1))
        self.scb.SetEditable(False)
        self.scb.SetBackgroundColour((255,255,255))
        #self.SetMinSize((600,360))

        self.btn_save.SetToolTip(wx.ToolTip("Save Log content into a text file"))

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        self.hbox.Add(self.chk_box, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.hbox.Add(30,0,0)
        self.hbox.Add(self.chk_usb, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.hbox.Add(120,0,0)
        self.hbox.Add(self.btn_clear, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        self.hbox.Add(30,0,0)
        self.hbox.Add(self.btn_save, 1, flag=wx.ALIGN_RIGHT | wx.ALIGN_LEFT , border = 60)

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

        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.Layout()

    
    # Clear Log Window
    def ClearLogWindow(self, e):
        self.scb.SetValue("")

    # Export LogWindow content to a file
    def SaveLogWindow(self, e):
        content = self.scb.GetValue()
        self.top.save_file(content, "*.txt")

    # Get System Time stamp
    def get_time_stamp(self):
        ct = datetime.now()
        dtstr = ct.strftime("%Y-%m-%d  %H:%M:%S.%f")
        cstr = "[" + dtstr[:-3] + "]  "
        return cstr

    # Show the Content in LogWindow    
    def print_on_log(self, strin):
        ctstr = ""
        if(self.chk_box.GetValue() == True):
            ctstr = ctstr + self.get_time_stamp()
        ctstr = ctstr + strin
        self.scb.AppendText(ctstr)
    
    # Get the status of USB Scan selection option
    def is_usb_enabled(self):
        return self.chk_usb.GetValue()