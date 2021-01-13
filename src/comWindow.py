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

import control2101 as d2101

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
                                     size=(128, -1),
                                     choices=self.dlist,
                                     style=wx.CB_DROPDOWN)
        
        self.btn_connect = wx.Button(self, ID_BTN_CONNECT, "Connect", 
                                     size=(80,-1))

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
            (self.szr_top, 0, wx.EXPAND | wx.ALL),
            ])
        
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.Layout()

        self.btn_scan.SetToolTip(wx.ToolTip("Search for the attached USB"
                                            "Models (3141, 3201, 2101)"))

        self.btn_scan.Bind(wx.EVT_BUTTON, self.ScanDevice)
        self.btn_connect.Bind(wx.EVT_BUTTON, self.ConnectDevice)
        self.btn_connect.Disable()

        self.timer_lp = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.ComServ, self.timer_lp)


    # Event Handler for Device Search Button
    # Scan the list Switches(3141, 3201 & 2101) over the USB bus
    def ScanDevice(self, evt):
         self.search_device()
    
    def search_device(self):
        self.top.UpdateSingle("Searching Model", 3)
        self.cb_device.Clear()
        self.cb_device.Enable()
        
        plist = search.search_port()
        key_list = list(plist.keys())
        val_list = list(plist.values())
        dlist = d2101.scan_2101()
        for dl in dlist:
            key_list.append(dl)
            val_list.append(DEVICES[DEV_2101])

        for i in range(len(key_list)):
            str1 = key_list[i]+"("+val_list[i]+")"
            self.cb_device.Append(str1)

        if(len(key_list)):
            self.cb_device.SetSelection(0)
            self.btn_connect.Enable()
            self.top.UpdateSingle("Model(s) found", 3)
        else:
            self.btn_connect.Disable()
            self.top.UpdateSingle("No Models found", 3)

    # Event Handler for Device Connect/Disconnect
    def ConnectDevice(self, evt):
        self.btn_connect.Disable()
        if(self.top.con_flg):
            self.disconnect_device()
        else:
            self.connect_device()
        self.btn_connect.Enable()
        self.top.set_mode(MODE_MANUAL)

    # Scanning the USB/COM port for device unplugging
    def ComServ(self, e):
        if self.top.con_flg:
            self.timer_lp.Stop()
            plist = search.check_port()
            if self.top.selPort in plist:
                self.timer_lp.Start(700)
            else:
                self.top.con_flg = False
                wx.MessageBox("Model Disconnected !", "Port Error", wx.OK)
                self.disconnect_device()
    
    # Called when device discoonect required
    def disconnect_device(self):
        self.top.device_disconnected()
        self.top.selPort = None
        self.top.con_flg = False
        self.btn_connect.Disable()
        self.top.devHand.close()
        self.btn_connect.SetLabel("Connect")
        self.timer_lp.Stop()
        srlist = []
        srlist.append("Port")
        srlist.append("")
        srlist.append("")
        srlist.append("Disconnected")
        self.top.UpdateAll(srlist)
        self.top.print_on_log("Model "+DEVICES[self.top.selDevice]+" Disconnected!\n")
    
    # Called when device connect required
    def device_connected(self):
        self.btn_connect.SetLabel("Disconnect")
        self.top.con_flg = True
        self.top.UpdatePort()
        self.top.UpdateDevice()
        self.top.UpdateSingle("Connected", 3)
        self.timer_lp.Start(500)
        self.top.print_on_log("Model "+DEVICES[self.top.selDevice]+" Connected!\n")
        self.top.device_connected()

    # Get the selected switch through the index of Combobox
    def get_selected_com(self):
        self.cval = self.cb_device.GetValue()
        txt = self.cval.split("(")
        return txt[0], txt[1].replace(")","")

    # Called when connect device initiated
    def connect_device(self):    
        self.cb_device.Disable()
        self.top.selPort, devname = self.get_selected_com()
        for i in range(len(DEVICES)):
            if devname == DEVICES[i]:
                self.top.selDevice = i
                break
        if self.top.selDevice == DEV_2101:
            self.device_connected()
        elif(serialDev.open_serial_device(self.top)):
            self.device_connected()
        
    # Do connect device automatically if last connected device is available
    def auto_connect(self):
        if(self.top.ldata['port'] != '' and self.top.ldata['device'] != ''):
            instr = ""+self.top.ldata['port']+"("+DEVICES[self.top.ldata['device']]+")"
            self.search_device()
            if self.cb_device.FindString(instr) >= 0:
                self.cb_device.SetValue(instr)
                self.connect_device()
                self.btn_connect.Enable()
                self.top.set_mode(MODE_MANUAL)
