#======================================================================
# (c) 2020  MCCI, Inc.
#----------------------------------------------------------------------
# Project : UI3141/3201 GUI Application
# File    : comWindow.py
#----------------------------------------------------------------------
# UI for device search and interface of 3141 and 3201 switches
# Interact with search script and serial device script
#======================================================================

#======================================================================
# IMPORTS
#======================================================================
import wx

import search
import serialDev

from uiGlobals import *

#======================================================================
# COMPONENTS
#======================================================================

class ComWindow(wx.Panel):
    def __init__(self, parent, top):
        wx.Panel.__init__(self, parent)
        #self.SetBackgroundColour("white")

        self.top = top

        self.dlist = []

        self.btn_scan = wx.Button(self, ID_BTN_DEV_SCAN, "Search", 
                                  size=(55,25))

        self.cb_device = wx.ComboBox(self,
                                     size=(100, -1),
                                     choices=self.dlist,
                                     style=wx.CB_DROPDOWN)
        
        self.btn_connect = wx.Button(self, ID_BTN_CONNECT, "Connect", 
                                     size=(70,-1))

        sb = wx.StaticBox(self, -1,"Manage Model")
        self.szr_top = wx.StaticBoxSizer(sb, wx.HORIZONTAL)
        self.szr_top.AddMany([
            (10,50,0),
            (self.btn_scan, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER),
            (10,50,0),
            (self.cb_device, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL),
            (10,50,0),
            (self.btn_connect, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL),
            (10,50,0)
            ])

        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.vbox.AddMany([
            #(10,20,0),
            (self.szr_top, 0, wx.EXPAND | wx.ALL),
            #(10,30,0)
            ])
        
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.Layout()

        self.btn_scan.SetToolTip(wx.ToolTip("Search for the attached USB"
                                            "Switches (3141, 3201)"))

        self.btn_scan.Bind(wx.EVT_BUTTON, self.ScanDevice)
        self.btn_connect.Bind(wx.EVT_BUTTON, self.ConnectDevice)
        self.btn_connect.Disable()

        self.timer_lp = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.ComServ, self.timer_lp)


    def ScanDevice(self, evt):
        self.top.UpdateSingle("Searching Switch", 3)
        self.cb_device.Clear()
        self.cb_device.Enable()
        
        plist = search.search_port()
        key_list = list(plist.keys())
        val_list = list(plist.values())

        nlist = []
        for i in range(len(key_list)):
            str1 = key_list[i]+"("+val_list[i]+")"
            self.cb_device.Append(str1)

        if(len(key_list)):
            self.cb_device.SetSelection(0)
            self.btn_connect.Enable()
            self.top.UpdateSingle("Switch(s) found", 3)
        else:
            self.btn_connect.Disable()
            self.top.UpdateSingle("No Switches found", 3)

    def ConnectDevice(self, evt):
        self.btn_connect.Disable()
        if(self.top.con_flg):
            self.disconnect_device()
        else:
            self.connect_switch()
        self.btn_connect.Enable()
        self.top.update_controls()

    def ComServ(self, e):
        if self.top.con_flg:
            self.timer_lp.Stop()
            plist = search.check_port()
            if self.top.selPort in plist:
                self.timer_lp.Start(700)
            else:
                self.top.con_flg = False
                wx.MessageBox("Switch Disconnected !", "Port Error", wx.OK)
                self.disconnect_device()

    def disconnect_device(self):
        self.top.selPort = None
        self.top.con_flg = False
        self.btn_connect.Disable()
        self.top.devHand.close()
        self.btn_connect.SetLabel("Connect")
        self.timer_lp.Stop()
        self.top.print_on_log("Device disconnected !\n")
        self.top.update_controls()
        srlist = []
        srlist.append("Port")
        srlist.append("")
        srlist.append("")
        srlist.append("Disconnected")
        self.top.UpdateAll(srlist)

    def switch_connected(self):
        self.btn_connect.SetLabel("Disconnect")
        self.top.con_flg = True
        self.top.UpdatePort()
        self.top.UpdateDevice()
        self.top.UpdateSingle("Connected", 3)
        self.timer_lp.Start(500)
        self.top.init_flg = True

    def get_selected_com(self):
        self.cval = self.cb_device.GetValue()
        txt = self.cval.split("(")
        return txt[0], txt[1].replace(")","")

    def connect_switch(self):
        self.cb_device.Disable()
        self.top.selPort, self.top.selDevice = self.get_selected_com()
        if(serialDev.open_serial_device(self.top)):
            self.switch_connected()
            if self.top.selDevice == '3201':
                self.top.show_3201()
            else:
                self.top.show_3141()