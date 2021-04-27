##############################################################################
# 
# Module: comWindow.py
#
# Description:
#     UI for device search and interface of 3141 and 3201, 2101, 2301 switches
#     Interact with search script and serial device script
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
class ComWindow(wx.Panel):
    """
    A  class comWindow with init method

    the comWindow navigate to search and connect buttons in manage model.
    click on search button the connecting device is listed in drop down box.
    """
    def __init__(self, parent, top):
        """
        comWindow that contains the about scan device and 
        connect device(s).

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
            top: creates an object
        Returns:
            None
        """
        wx.Panel.__init__(self, parent)
        # Self.SetBackgroundColour("white")

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
        # Creates a boxsizer as vertical
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.vbox.AddMany([
            (self.szr_top, 0, wx.EXPAND | wx.ALL),
            ])
        
        # Set size of frame
        self.SetSizer(self.vbox)
        # Set size of frame
        self.vbox.Fit(self)
        self.Layout()
        
        # Tooltips display text over an widget elements
        # Set tooltip for switching search button.
        self.btn_scan.SetToolTip(wx.ToolTip("Search for the attached USB"
                                            "Models (3141, 3201, 2101,2301)"))  
        # Bind the button event to handler
        self.btn_scan.Bind(wx.EVT_BUTTON, self.ScanDevice)
        # Bind the button event to handler
        self.btn_connect.Bind(wx.EVT_BUTTON, self.ConnectDevice)
        self.btn_connect.Disable()
        
        # The Timer class allows you to execute code at specified intervals.
        self.timer_lp = wx.Timer(self)
        # Bind the timer event to handler
        self.Bind(wx.EVT_TIMER, self.ComServ, self.timer_lp)

    def ScanDevice(self, evt):
        """
        Scan the list of connected devices over the USB bus

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            evt: The event parameter in the AutoButton() method is an 
            object specific to a particular event type.
        Returns:
            None
        """
        self.search_device()

    def search_device(self):
        """
        Event Handler for Device Search Button.
        search the device(s) its displays in the statusbar and dropdown box 

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
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
            # Device is found update in status bar Model(s) found
            self.top.UpdateSingle("Model(s) found", 3)
        else:
            self.btn_connect.Disable()
            # Device is not found update in status bar No Models found
            self.top.UpdateSingle("No Models found", 3)
   
    def ConnectDevice(self, evt):
        """
        Event Handler for Connect Button, to connect device
        Connect status will be displayed in the statusbar 

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            evt: handling the event for connect the device
        Returns:
            None
        """
        self.btn_connect.Disable()
        if(self.top.con_flg):
            self.disconnect_device()
        else:
            self.connect_device()
        self.btn_connect.Enable()
        self.top.set_mode(MODE_MANUAL)
    
    def ComServ(self, e):
        """
        Scan the USB/COM port to check the status of the connected device

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            e:message updated in Popup window with model disconnected 
        Returns:
            None
        """
        if self.top.con_flg:
            self.timer_lp.Stop()
            plist = search.check_port()
            if self.top.selPort in plist:
                self.timer_lp.Start(700)
            else:
                self.top.con_flg = False
                # Print the message
                wx.MessageBox("Model Disconnected !", "Port Error", wx.OK)
                self.disconnect_device()
    
    def disconnect_device(self):
        """
        Disconnect the connected device

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.top.device_disconnected()
        self.top.selPort = None
        self.top.con_flg = False
        self.btn_connect.Disable()
        self.top.devHand.close()
        # Set label button name as Connect
        self.btn_connect.SetLabel("Connect")
        self.timer_lp.Stop()
        srlist = []
        srlist.append("Port")
        srlist.append("")
        srlist.append("")
        srlist.append("Disconnected")
        self.top.UpdateAll(srlist)
        # Print on logwindow
        self.top.print_on_log("Model "+DEVICES[self.top.selDevice]
                              +" Disconnected!\n")
        
    def device_connected(self):
        """
        Connect the selected device

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        # Set label button name as Disconnect
        self.btn_connect.SetLabel("Disconnect")
        self.top.con_flg = True
        self.top.UpdatePort()
        # Device update info
        self.top.UpdateDevice()
        self.top.UpdateSingle("Connected", 3)
        self.timer_lp.Start(500)
        # Print on logwindow
        self.top.print_on_log("Model "+DEVICES[self.top.selDevice]
                                              +" Connected!\n")
        self.top.device_connected()
    
    def get_selected_com(self):
        """
        Get the selected Com port and Switch Model

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            it returns the Com Port and Model in String
        """
        self.cval = self.cb_device.GetValue()
        txt = self.cval.split("(")
        return txt[0], txt[1].replace(")","")
    
    def connect_device(self):    
        """
        Establish the connection with selected Model

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        # Combo box, device list is disable
        self.cb_device.Disable()
        self.top.selPort, devname = self.get_selected_com()
        if devname == DEVICES[DEV_2301]:
            self.top.selBaud = 9600
        else:
            self.top.selBaud = 115200
        for i in range(len(DEVICES)):
            if devname == DEVICES[i]:
                self.top.selDevice = i
                break
        if self.top.selDevice == DEV_2101:
            self.device_connected()
        elif(serialDev.open_serial_device(self.top)):
            self.device_connected() 
    def auto_connect(self):
        """
        Do connect device automatically if the last connected device is 
        available

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        if(self.top.ldata['port'] != '' and self.top.ldata['device'] != ''):
            instr = ""+self.top.ldata['port']+"("+DEVICES[
                                self.top.ldata['device']]+")"
            self.search_device()
            if self.cb_device.FindString(instr) >= 0:
                self.cb_device.SetValue(instr)
                self.connect_device()
                # Connect button is enable automatically 
                # If last connected device is avalaible
                self.btn_connect.Enable()
                self.top.set_mode(MODE_MANUAL)
