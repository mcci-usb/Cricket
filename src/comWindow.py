##############################################################################
# 
# Module: comWindow.py
#
# Description:
#     Dialog to display copyright information
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
import search
import serialDev
import control2101 as d2101
from uiGlobals import *

##############################################################################
# Utilities
##############################################################################
"""
A  class comWindow with init method

the comWindow navigate to search and connect buttons in manage model.
click on search button the connecting device is listed in drop down box.
"""
class ComWindow(wx.Panel):
    """
    comWindow that contains the about scan device and connect device elements.
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
        
        # set size of frame
        self.SetSizer(self.vbox)
        # set size of frame
        self.vbox.Fit(self)
        self.Layout()
        
        #Tooltips display text over an widget elements
        #set tooltip for switching search button.
        self.btn_scan.SetToolTip(wx.ToolTip("Search for the attached USB"
                                            "Models (3141, 3201, 2101)"))  
        # bind the button event to handler
        self.btn_scan.Bind(wx.EVT_BUTTON, self.ScanDevice)
        # bind the button event to handler
        self.btn_connect.Bind(wx.EVT_BUTTON, self.ConnectDevice)
        self.btn_connect.Disable()
        
        # The Timer class allows you to execute code at specified intervals.
        self.timer_lp = wx.Timer(self)
        # bind the timer event to handler
        self.Bind(wx.EVT_TIMER, self.ComServ, self.timer_lp)
    """
    Event Handler for Device Search Button.
    Scan the list Switches(3141, 3201 & 2101) over the USB bus
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        evt: The event parameter in the AutoButton() method is an 
        object specific to a particular event type.
    Returns:
        return None
    """
    def ScanDevice(self, evt):
         self.search_device()

    """
    Event Handler for Device Search Button.
    search the device(s) its displays the statusbar 
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
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
            # device is found update in status bar Model(s) found
            self.top.UpdateSingle("Model(s) found", 3)
        else:
            self.btn_connect.Disable()
            # device is not found update in status bar No Models found
            self.top.UpdateSingle("No Models found", 3)
    """
    Event Handler for Device Connect/Disconnect
    connect and disconnect the device(s) its displays the statusbar 
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def ConnectDevice(self, evt):
        self.btn_connect.Disable()
        if(self.top.con_flg):
            self.disconnect_device()
        else:
            self.connect_device()
        self.btn_connect.Enable()
        self.top.set_mode(MODE_MANUAL)
    """
    Scanning the USB/COM port for device unplugging
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def ComServ(self, e):
        if self.top.con_flg:
            self.timer_lp.Stop()
            plist = search.check_port()
            if self.top.selPort in plist:
                self.timer_lp.Start(700)
            else:
                self.top.con_flg = False
                # print the message
                wx.MessageBox("Model Disconnected !", "Port Error", wx.OK)
                self.disconnect_device()
    """
    Called when device discoonect required
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def disconnect_device(self):
        self.top.device_disconnected()
        self.top.selPort = None
        self.top.con_flg = False
        self.btn_connect.Disable()
        self.top.devHand.close()
        # set label button name as Connect
        self.btn_connect.SetLabel("Connect")
        self.timer_lp.Stop()
        srlist = []
        srlist.append("Port")
        srlist.append("")
        srlist.append("")
        srlist.append("Disconnected")
        self.top.UpdateAll(srlist)
        # print on logwindow
        self.top.print_on_log("Model "+DEVICES[self.top.selDevice]+" Disconnected!\n")
    """
    Called when device connect required
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def device_connected(self):
        # set label button name as Disconnect
        self.btn_connect.SetLabel("Disconnect")
        self.top.con_flg = True
        self.top.UpdatePort()
        #device update info
        self.top.UpdateDevice()
        self.top.UpdateSingle("Connected", 3)
        self.timer_lp.Start(500)
        # print on logwindow
        self.top.print_on_log("Model "+DEVICES[self.top.selDevice]
                                              +" Connected!\n")
        self.top.device_connected()
    """
    Get the selected switch through the index of Combobox
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def get_selected_com(self):
        self.cval = self.cb_device.GetValue()
        txt = self.cval.split("(")
        return txt[0], txt[1].replace(")","")
    
    """
    Called as when connect device initiated
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def connect_device(self):    
        # combo box, device list is disable
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
    """
    Do connect device automatically if last connected device is available
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """ 
    def auto_connect(self):
        if(self.top.ldata['port'] != '' and self.top.ldata['device'] != ''):
            instr = ""+self.top.ldata['port']+"("+DEVICES[
                                self.top.ldata['device']]+")"
            self.search_device()
            if self.cb_device.FindString(instr) >= 0:
                self.cb_device.SetValue(instr)
                self.connect_device()
                # connect button is enable automatically 
                # if last connected device is avalaible
                self.btn_connect.Enable()
                self.top.set_mode(MODE_MANUAL)
