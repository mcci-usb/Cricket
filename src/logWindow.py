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
#    V4.0.0 Wed May 25 2023 17:00:00   Seenivasan V
#       Module created
##############################################################################
# Lib imports
import wx

# Own modules
from uiGlobals import *
from datetime import datetime

import wx
import threading


# Own modules
import thControl

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
        self.SetMinSize((480,520))

        self.top = top
        # Create static box with naming of Log Window
        sb = wx.StaticBox(self, -1,"Log Window")

        # Create StaticBoxSizer as vertical
        self.vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)
        self.chk_usb = wx.CheckBox(self, -1,
                                  label='USB Host View Changes')

        self.st_delay   = wx.StaticText(self, -1, " USB Enumeration Delay ", 
                                        style=wx.ALIGN_CENTER)

        self.tc_delay   = wx.TextCtrl(self, -1, "1000", size=(50,-1), 
                                      style = wx.TE_CENTRE |
                                      wx.TE_PROCESS_ENTER,
                                      validator=NumericValidator(),
                                      name="Enumeration Delay")

        self.st_ms   = wx.StaticText(self, -1, "ms", size=(30,15), 
                                     style = wx.ALIGN_CENTER)

        self.btn_ref = wx.Button(self, ID_BTN_AUTO, "Scan USB Change", size=(110,-1))

        self.chk_box = wx.CheckBox(self, -1, label='Show Timestamp')  
          
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
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.wait_flg = False
        
        self.hbox1.Add(self.chk_usb, 0, flag=wx.ALIGN_LEFT | wx.LEFT | 
                       wx.ALIGN_CENTER_VERTICAL, border=0)
        self.hbox1.Add(self.st_delay, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 18)
        self.hbox1.Add(self.tc_delay, flag=wx.ALIGN_LEFT | 
                       wx.ALIGN_CENTER_VERTICAL, border = 25)
        self.hbox1.Add(self.st_ms, 0, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 1)
        self.hbox1.Add(self.btn_ref,  0, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 20)
        
        self.hbox.Add(self.chk_box, 0, wx.ALIGN_LEFT | 
                                       wx.ALIGN_CENTER_VERTICAL)
        self.hbox.Add(30,0,0)

        self.hbox.Add(30,0,0)
        self.hbox.Add(self.btn_clear, 0, wx.ALIGN_LEFT | 
                                         wx.ALIGN_CENTER_VERTICAL)
        self.hbox.Add(45,0,0)
        self.hbox.Add(self.btn_save, 1, flag=wx.RIGHT , 
                                         border = 20)
        
        # Bind the button event to handler
        self.btn_clear.Bind(wx.EVT_BUTTON, self.ClearLogWindow)
        self.btn_save.Bind(wx.EVT_BUTTON, self.SaveLogWindow)

        self.btn_ref.Bind(wx.EVT_BUTTON, self.RefreshUsbBus)
        self.chk_usb.Bind(wx.EVT_CHECKBOX, self.OnCheckBox)

        self.szr_top = wx.BoxSizer(wx.VERTICAL)
        self.szr_top.AddMany([
            (5,0,0),
            (self.scb, 1, wx.EXPAND),
            (5,0,0)
            ])

        self.vbox.AddMany([
            (self.hbox1, 0, wx.ALIGN_LEFT),
            (10,5,0),
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
        Event handler for Clear button
        Clear the data in USB Device Tree View Window

        Args:
            self: The self parameter is a reference to the current 
            insance of the class,and is used to access variables
            that belongs to the class.
            e: Type of the event
        Returns:
            None
        """
        self.scb.SetValue("")
    
    def UsbThread(self):
        """
        Thread for USB tree view changes
        Start the USB device scan and list the difference catagorized by 
        Added and Removed

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
       
        self.scb.SetValue("")
    
    def SaveLogWindow(self, e):
        """
        Event handler for the save button
        Save the usb tree view Window content in a file under a directory

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            e: Type of the event
        Returns:
            None
        """
        # Get the content of the control
        content = self.scb.GetValue()
        self.top.save_file(content, "*.txt")
    
    def get_time_stamp(self):
        """
        Get System Time stamp for data log

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        
        ct = datetime.now()
        # Format using strftime 
        dtstr = ct.strftime("%Y-%m-%d  %H:%M:%S.%f")
        cstr = "[" + dtstr[:-3] + "]  "
        return cstr
     
    def print_on_log(self, strin):
        """
        print the data in Logwindow
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            strin: USB device list in String format.
        Returns:
            None
        """
        
        ctstr = ""
        # Print values of checkbox buttons True
        if(self.chk_box.GetValue() == True):
            ctstr = ctstr + self.get_time_stamp()
        ctstr = ctstr + strin
        self.scb.AppendText(ctstr)

    def RefreshUsbBus(self, e):
        """
        Event handler for Refresh button
        Start the USB device scan thread

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            e: Type of the event
        Returns:
            None
        """
        if(self.wait_flg == False):
            self.btn_ref.Disable()
            self.wait_flg = True
            threading.Thread(target=self.UsbThread).run()

    def disable_usb_scan(self):
        """
        Disble USB scan option selection
        Called when USB delay is greater than the Port Switching delay

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.chk_usb.SetValue(False)
    
    def UsbThread(self):
        """
        Thread for USB tree view changes
        Start the USB device scan and list the difference catagorized by 
        Added and Removed

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        try:
            thControl.get_tree_change(self.top)
        except:
            # print message
            self.print_on_log("rror!")
        self.wait_flg = False
        self.btn_ref.Enable()
    
    def get_enum_delay(self):
        """
        Get USB device Enumeration delay

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            String: Enumeration delay
        """
        edly = self.tc_delay.GetValue()
        
        if(edly == ""):
            edly = "100"
        dval = int(edly)
        
        if(dval < 100):
            dval = 100
        elif(dval > 60000):
            dval = 60000
        
        # Sets the new text control value.
        self.tc_delay.SetValue(str(dval))

        # Gets the contents of the control.
        return self.tc_delay.GetValue()
    
    def get_delay_status(self):
        """
        Status of the USB Enumeration delay control selection
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            True: if the check box is checked
            False: if the check box in unchecked
        """
        return self.chk_usb.GetValue()

    def OnCheckBox(self, evt):
        """
        Event handler for Checkbox button
        if enabled compare the delay parameter with Auto and Loop mode

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            evt:event handler to interval, period
        Returns:
            None
        """
        self.update_interval_period()

    def update_interval_period(self):
        """
        Override the Switching Interval period based on USB delay

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        if(self.get_delay_status()):
            update_flg = False
            onTime, offTime = self.top.get_loop_param()
            if(int(onTime) < int(self.get_enum_delay())):
                onTime = self.get_enum_delay()
                update_flg = True
            if(int(offTime) < int(self.get_enum_delay())):
                offTime = self.get_enum_delay()
                update_flg = True
            if update_flg:
                self.top.set_loop_param(onTime, offTime)

            onTime, offTime, duty = self.top.get_auto_param()
            if(int(onTime) >= int(offTime)):
                if(int(offTime) < int(self.get_enum_delay())):
                    duty = 100 - duty
                    ndly = int((int(self.get_enum_delay())*100)/duty)
                    self.top.set_interval(str(ndly))
            else:
                if(int(onTime) < int(self.get_enum_delay())): 
                    ndly = int((int(self.get_enum_delay())*100)/duty)
                    self.top.set_interval(str(ndly))
    
    def update_controls(self, mode):
        """
        update the mode option Enable/Disble USB selection widgets

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            mode: check the mode
        Returns:
            None
        """
        if(mode == MODE_MANUAL):
            self.chk_usb.Enable()
            self.tc_delay.Enable()
        else:
            self.chk_usb.Disable()
            self.tc_delay.Disable()

    def show_usb_ctrls(self, status):
        """
        show and hide usb host view widgets based on Client and Server config. 

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            status: false or true.
        Returns:
            None
        """
        if(status):
            self.vbox.Show(self.hbox1)
        else:
            self.vbox.Hide(self.hbox1)