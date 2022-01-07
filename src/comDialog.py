##############################################################################
# 
# Module: comDialog.py
#
# Description:
#     Dialog to show list of available MCCI USB Switch (3141, 3201, 2101 and 2301)
#     Search, view, select and connect module
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
#     Seenivasan V, MCCI Corporation June 2021
#
# Revision history:
#     V2.4.0 Wed July 14 2021 15:20:05   Seenivasan V
#       Module created
##############################################################################
# Lib imports
import wx

# Own modules
from uiGlobals import *

import devControl


##############################################################################
# Utilities
##############################################################################

class SearchSwitch(wx.PyEvent):
    """A class ServerEvent with init method"""

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

class ComWindow(wx.Window):
    """
    A  class AboutWindow with init method
    The AboutWindow navigate to MCCI Logo with naming of 
    application UI "Criket",Version and copyright info.  
    """
    def __init__ (self, parent, top):
        """
        AboutWindow that contains the about dialog elements.

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
            top: creates an object
        Returns:
            None
        """
        wx.Window.__init__(self, parent, -1,
                           size=wx.Size(100,100),
                           style=wx.CLIP_CHILDREN,
                           name="About")

        self.top = top
        self.parent = parent

        self.dlist = []

        self.btn_scan = wx.Button(self, ID_BTN_DEV_SCAN, "Search",
                                  size=(57,25))

        self.cb_device = wx.ComboBox(self,
                                     size=(135, -1),
                                     choices=self.dlist,
                                     style=wx.CB_DROPDOWN)
        
        self.btn_connect = wx.Button(self, ID_BTN_CONNECT, "Connect", 
                                     size=(80,-1))

        self.szr_top = wx.BoxSizer(wx.HORIZONTAL)
        
        wx.BoxSizer(wx.HORIZONTAL)
        
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
            (10,10,0),
            (self.szr_top, 0, wx.EXPAND | wx.ALL),
            (10,10,0)
            ])
        
        # Set size of frame
        self.SetSizer(self.vbox)
        # Set size of frame
        self.vbox.Fit(self)
        self.Layout()
        
        # Tooltips display text over an widget elements
        # Set tooltip for switching search button.
        self.btn_scan.SetToolTip(wx.ToolTip("Search for the attached USB"
                                            "MCCI USB Switch(3141, 3201, 2101,2301)"))  
        # Bind the button event to handler
        self.btn_scan.Bind(wx.EVT_BUTTON, self.ScanDevice)
        # Bind the button event to handler
        self.btn_connect.Bind(wx.EVT_BUTTON, self.ConnectDevice)
        self.btn_connect.Disable()   
        # The Timer class allows you to execute code at specified intervals.
        self.timer_lp = wx.Timer(self)

        EVT_RESULT(self, self.SearchEvent)
        wx.PostEvent(self, SearchSwitch("search"))

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
        wx.PostEvent(self, SearchSwitch("print"))
        wx.PostEvent(self, SearchSwitch("search"))
    

    def SearchEvent(self, event):
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
        if event.data is None:
            self.top.print_on_log("No Search event\n")
        elif event.data == "search":
            #self.btn_scan.Enable(False)
            self.btn_scan.Unbind(wx.EVT_BUTTON)
            self.get_devices()
            wx.GetApp().Yield()
            self.btn_scan.Bind(wx.EVT_BUTTON, self.ScanDevice)
        elif event.data == "print":
            self.top.print_on_log("Searching Devices ...\n")
        
    def get_devices(self):    
        devlist = devControl.search_device(self.top)
        dev_list = devlist["devices"]
        if(len(dev_list) == 0):
            self.top.print_on_log("No Devices found\n")
            self.cb_device.Clear()
        else:
            key_list = []
            val_list = []

            for i in range(len(dev_list)):
                key_list.append(dev_list[i]["port"])
                val_list.append(dev_list[i]["model"])
        
            self.cb_device.Clear()
            for i in range(len(key_list)):
                str1 = val_list[i]+"("+key_list[i]+")"
                self.cb_device.Append(str1)
                self.top.print_on_log(str1+"\n")

            if(len(key_list)):
                self.cb_device.SetSelection(0)
                self.btn_connect.Enable()
                # Device is found update in status bar Model(s) found
                self.top.UpdateSingle("Switch(s) found", 3)
            else:
                self.btn_connect.Disable()
                # Device is not found update in status bar No Models found
                self.top.UpdateSingle("No Switch found", 3)
   
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
        self.connect_device()
        #self.btn_connect.Enable()
        self.top.set_mode(MODE_MANUAL)
    
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
        if devControl.connect_device(self.top):
            self.device_connected()

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
        return txt[1].replace(")",""), txt[0]

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
        self.top.device_connected()
        self.parent.EndModal(True)
           
    def device_connected2(self):
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
        # Print on logwindow
        self.top.print_on_log("MCCI USB Swicth "+DEVICES[self.top.selDevice]
                                              +" Connected!\n")
        self.top.device_connected()
        self.parent.EndModal(True)

    def OnClick (self, evt):
        """
        OnClick() event handler function retrieves the label of 
        source button, which caused the click event. 
        That label is printed on the console.

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            evt: The event parameter in the OnClick() method is an 
            object specific to a particular event type.
        Returns:
            None        
        """
        self.GetParent().OnOK(evt)
   
    def OnSize (self, evt):
        """
        OnSize() event handler function retrieves the about window size. 

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            evt: The event parameter in the OnClick() method is an 
            object specific to a particular event type.
        Returns:
            None        
        """
        self.Layout()

def EVT_RESULT(win, func):
    win.Connect(-1, -1, EVT_RESULT_ID, func)    

def get_devices(top):
    devlist = devControl.search_device(top)
    dev_list = devlist["devices"]

class ComDialog(wx.Dialog):
    """
    wxWindows application must have a class derived from wx.Dialog.
    """
    def __init__ (self, parent, top):
        """
        A AboutDialog is Window an application creates to 
        retrieve Cricket UI Application input.

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
            top: create a object
        Returns:
            None
        """
        wx.Dialog.__init__(self, parent, -1, "MCCI USB Switch",
                           size=wx.Size(100, 100),
                           style=wx.STAY_ON_TOP|wx.DEFAULT_DIALOG_STYLE,
                           name="MCCI USB Switch Search Dialog")

        self.top = top
        self.win = ComWindow(self, top)

        # Sizes the window to fit its best size.
        self.Fit()
        # Centre frame using CentreOnParent() function,
        # Show window in the center of the screen.
        # Centres the window on its parent.
        self.CenterOnParent(wx.BOTH)
    
    def OnOK (self, evt):
        """
        OnOK() event handler function retrieves the label of 
        source button, which caused the click event. 

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            evt: The event parameter in the OnOK() method is an 
            object specific to a particular event type.
        Returns:
            None        
        """
    # Returns numeric code to caller
        self.EndModal(wx.ID_OK)
     
    def OnSize (self, evt):
        """
        OnSize() event handler function retrieves the about window size. 
        
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            evt: The event parameter in the OnSize() method is an 
            object specific to a particular event type.
        Returns:
            None        
        """ 
        self.Layout()