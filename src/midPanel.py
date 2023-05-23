##############################################################################
# 
# Module: midPanel.py
#
# Description:
#     Scan the USB bus and get the list of devices attached
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
from enum import auto
import wx

import sys
from sys import platform

# Own modules
from uiGlobals import *

import loopWindow
import logWindow
import autoWindow
import batchWindow


class MidPanel(wx.Panel):
    """
    A class UiPanel with init method
    the UiPanel navigate to UIApp name
    """ 
    def __init__(self, parent, top, portno):
        """
        Uipanel created
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
        Returns:
            None
        """
        super(MidPanel, self).__init__(parent)

        self.SetMaxSize((540, -1))

        wx.GetApp().SetAppName("Cricket")

        self.parent = top
        # set back ground colour White
        self.SetBackgroundColour('White')

        self.font_size = DEFAULT_FONT_SIZE

        # MAC OS X
        if platform == "darwin":
            self.font_size = MAC_FONT_SIZE
        # Sets the font for this window
        self.SetFont(wx.Font(self.font_size, wx.SWISS, wx.NORMAL, wx.NORMAL,
                             False,'MS Shell Dlg 2'))

        self.portno = portno

        self.logPan = logWindow.LogWindow(self, self.parent)
        self.hboxdl = wx.BoxSizer(wx.HORIZONTAL)
        
        # p = wx.Panel(self)
        nb = wx.Notebook(self)

        # Create the tab windows
        self.autoPan = autoWindow.AutoWindow(nb, top)
        self.loopPan = loopWindow.LoopWindow(nb, top)
        self.batchPan = batchWindow.BatchWindow(nb, top)


        # Add the windows to tabs and name them.
        nb.AddPage(self.autoPan, "Auto Mode")
        nb.AddPage(self.loopPan, "Loop Mode")
        nb.AddPage(self.batchPan, "Batch Mode")
        
        self.hboxdl.Add(nb, 1, wx.EXPAND)
        
        
        self.vboxl = wx.BoxSizer(wx.VERTICAL)
        self.vboxl.Add((0,20), 0, wx.EXPAND)
        self.vboxl.Add(self.hboxdl, 0 ,wx.ALIGN_LEFT | wx.EXPAND)
        self.vboxl.Add((0,10), 0, 0)
        self.vboxl.Add(self.logPan, 1, wx.EXPAND)
        self.vboxl.Add((0,20), 0, wx.EXPAND)


        self.hboxm = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxm.Add((20,0), 0, wx.EXPAND)
        self.hboxm.Add(self.vboxl, 1, wx.EXPAND)
        self.hboxm.Add((20,0), 0, wx.EXPAND)
        
        # Set size of frame
        self.SetSizer(self.hboxm)
        
        # Setting Layouts
        self.SetAutoLayout(True)
        self.hboxm.Fit(self)
        self.Layout()


    def update_cc_panels(self):
        """
        when selecting Switching Control Computer server menu,
        its starts the Siwting control computer server.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.parent.startCcServer()
        
    def update_hc_panels(self):
        """
        when selecting Test Host Computer server menu,
        its starts the Test Host computer server.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.parent.startHcServer()
    
    def remove_all_panels(self):
        """
        Remove or Hide the the logwinodow and USB Tree view window.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.hboxm.Hide(self.vboxl)
        self.Layout()

    def remove_dev_panels(self):
        """
        Remove or Hide the the all Model 3141, 3201, 2101, 2301 windows panels.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.vboxdl.Hide(self.dev2301Pan)
        self.vboxdl.Hide(self.dev3201Pan)
        self.vboxdl.Hide(self.dev3141Pan)
        self.vboxdl.Hide(self.dev3142Pan)
        self.vboxdl.Hide(self.dev2101Pan)

    def PrintLog(self, strin):
        """
        print data/status on logwindow 

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            strin: data in String format
        Returns:
            None
        """
        self.logPan.print_on_log(strin)
    
    def get_enum_delay(self):
        """
        Get the USB Enumaration delay 

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            String - USB Enumeration delay 
        """
        return self.logPan.get_enum_delay()
      
    def get_delay_status(self):
        """
        Get the status of USB device Enumeration delay check box

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            Boolean - Status of the delay check box
        """
        return self.logPan.get_delay_status()
    
    def get_interval(self):
        """
        Get the interval parameter of Auto Mode

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            String - Auto Mode interval
        """
        return self.autoPan.get_interval()
    
    def set_interval(self, strval):
        """
        Update/Set the Auto Mode interval

        Args: 
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            strval: interval value in Sting format
        Returns:
            None
        """
        self.autoPan.set_interval(strval)
    
    def disable_usb_scan(self):
        """
        Disable the USB device scan by uncheck the check box

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns: 
            None
        """
        self.logPan.disable_usb_scan()
    
    def get_loop_param(self):
        """
        Get the Loop Window prameters

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            return None
        """
        return self.loopPan.get_loop_param()
    
    def get_auto_param(self):
        """
        Get the Auto Window prameters

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns: 
            return None
        """
        return self.autoPan.get_auto_param()
    
    def set_loop_param(self, onTime, offTime):
        """
        Set the period for Loop Window

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            strval: Period value in String format
        Returns:
            return None
        """
        self.loopPan.set_loop_param(onTime, offTime)

    def set_port_list(self, ports):
        """
        Set the ports list for Loop Window and Auto Window

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            ports: upated the ports list
        Returns:
            return None
        """
        self.loopPan.set_port_list(ports)
        self.autoPan.set_port_count(ports)
    
    def port_on(self,swkey, port, stat):
        """
        Port On/Off command from Loop and Auto Window

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            port: device port number
            stat: port on status will updated 
        Returns:
            None
        """
        self.swobj[swkey].port_on(port, stat)
    
    def device_connected(self):
        """
        Once device connected, Model Window get updated with selected Model

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        for dev in range(len(DEVICES)):
            if dev == self.parent.selDevice:
                self.vboxdl.Show(self.devObj[self.parent.selDevice])
            else:
                self.vboxdl.Hide(self.devObj[dev])
        self.Layout()
        self.devObj[self.parent.selDevice].device_connected()
    
    def device_disconnected(self):
        """
        Once device disconnected, disable all controls in Model, Loop 
        and Auto Window

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.devObj[self.parent.selDevice].device_disconnected()
        self.loopPan.device_disconnected()
        self.autoPan.device_disconnected()
    
    def auto_connect(self):
        """
        Once application loaded, initiate the auto connect 
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.comPan.auto_connect()