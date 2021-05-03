##############################################################################
# 
# Module: treeWindow.py
#
# Description:
#     Tree Window - Show the device list whic are recently removed or attached
#                   device difference between to consecutive request(scan)
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
#     V2.3.0 Wed April 28 2021 18:50:10 seenivasan
#       Module created
##############################################################################
# Lib imports
import wx
import threading
from datetime import datetime

# Own modules
import usbDev
from uiGlobals import *

##############################################################################
# Utilities
##############################################################################
class UsbTreeWindow(wx.Window):
    """
    A class UsbTreeWindow with init method
    wxWindow is the base class for all windows and 
    represents any visible object on screen.
    """
    def __init__(self, parent, top):
        """
        Tree Window - Show the list of USB devices connected/disconnected
        recently from the USB bus 

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

        # Set background colour white
        self.SetBackgroundColour("White")

        self.top = top
        # Creating Horizontal box sizer
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        self.wait_flg = False
        # Creating staticbox with naming as " USB Device Tree View Changes"
        sb = wx.StaticBox(self, -1,"USB Device Tree View Changes")
        # Creating Vertical box sizer
        self.vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)

        self.chk_box = wx.CheckBox(self, -1, label='Enable')

        self.chk_ts = wx.CheckBox(self, -1, label='Show Timestamp')

        self.st_delay   = wx.StaticText(self, -1, " Delay ", 
                                        style=wx.ALIGN_CENTER)

        self.tc_delay   = wx.TextCtrl(self, -1, "1000", size=(50,-1), 
                                      style = wx.TE_CENTRE |
                                      wx.TE_PROCESS_ENTER,
                                      validator=NumericValidator(),
                                      name="Enumeration Delay")

        self.st_ms   = wx.StaticText(self, -1, "ms", size=(30,15), 
                                     style = wx.ALIGN_CENTER)

        self.btn_clear = wx.Button(self, ID_BTN_UCLEAR, "Clear", 
                                   size=(60, -1))

        self.btn_ref = wx.Button(self, ID_BTN_AUTO, "Refresh", size=(55,-1))

        self.btn_save = wx.Button(self, -1, "Save", size=(55,-1))

        self.st_td   = wx.StaticText(self, -1, " Total Device : ", 
                                     style=wx.ALIGN_CENTER)
        self.st_tdp  = wx.StaticText(self, -1, " --- ", style=wx.ALIGN_CENTER)

        self.st_tr   = wx.StaticText(self, -1, " Readable : ", 
                                     style=wx.ALIGN_CENTER)
        self.st_trp  = wx.StaticText(self, -1, " --- ", style=wx.ALIGN_CENTER)

        self.st_te   = wx.StaticText(self, -1, " Error : ", 
                                     style=wx.ALIGN_CENTER)
        self.st_tep  = wx.StaticText(self, -1, " --- ", style=wx.ALIGN_CENTER)

        
        self.scb = wx.TextCtrl(self, -1, style= wx.TE_MULTILINE, 
                               size=(-1,-1))
        # Makes the text item editable or read-only
        self.scb.SetEditable(False)
        self.scb.SetBackgroundColour((255,255,255))
        
        # Tooltips display text over an widget elements
        # Set tooltip for switching interval and auto buttons.
        self.tc_delay.SetToolTip(wx.ToolTip("USB device scan delay. Min:"
                                             "100 msec, Max: 60 sec"))
        self.btn_save.SetToolTip(wx.ToolTip("Save USB device Log into"
                                            " a text file"))

        self.hbox.Add(10,30,0)
        self.hbox.Add(self.chk_box,0, wx.ALIGN_CENTRE_VERTICAL)
        self.hbox.Add(20,0,0)
        self.hbox.Add(self.st_delay,0, wx.ALIGN_CENTRE_VERTICAL)
        self.hbox.Add(self.tc_delay,0, wx.ALIGN_CENTRE_VERTICAL)
        self.hbox.Add(self.st_ms,0, wx.ALIGN_CENTRE_VERTICAL)
        self.hbox.Add(20,0,0)
        self.hbox.Add(self.btn_ref, 0, flag=wx.RIGHT, border = 10)

        self.hbox2.Add(10,30,0)
        self.hbox2.Add(self.st_td,0, wx.ALIGN_CENTRE_VERTICAL)
        self.hbox2.Add(self.st_tdp,0, wx.ALIGN_CENTRE_VERTICAL)
        self.hbox2.Add(30,0,0)
        self.hbox2.Add(self.st_tr,0, wx.ALIGN_CENTRE_VERTICAL)
        self.hbox2.Add(self.st_trp,0, wx.ALIGN_CENTRE_VERTICAL)
        self.hbox2.Add(30,0,0)
        self.hbox2.Add(self.st_te,0, wx.ALIGN_CENTRE_VERTICAL)
        self.hbox2.Add(self.st_tep,0, wx.ALIGN_CENTRE_VERTICAL)

        self.hbox3.Add(10,30,0)
        self.hbox3.Add(self.chk_ts,0, wx.ALIGN_CENTRE_VERTICAL)
        self.hbox3.Add(23,0,0)
        self.hbox3.Add(self.btn_clear, 0, wx.ALIGN_RIGHT)
        self.hbox3.Add(34,0,0)
        self.hbox3.Add(self.btn_save,0, flag=wx.RIGHT, border=10)
        
        # Bind the button event to handler
        self.btn_ref.Bind(wx.EVT_BUTTON, self.RefreshUsbBus)

        # Bind the button event to handler
        self.btn_clear.Bind(wx.EVT_BUTTON, self.ClearUsbWindow)
        
        # Bind the button event to handler
        self.btn_save.Bind(wx.EVT_BUTTON, self.SaveUsbLog)
        
        # Self.tc_delay.Bind(wx.EVT_TEXT_ENTER, self.OnEnterDelay)
        self.chk_box.Bind(wx.EVT_CHECKBOX, self.OnCheckBox)
        
        # This function sets the maximum number of characters
        # The user can enter into the control.
        self.tc_delay.SetMaxLength(5)

        self.szr_top = wx.BoxSizer(wx.VERTICAL)
        self.szr_top.AddMany([
            (5,0,0),
            (self.scb, 1, wx.EXPAND),
            (5,0,0)
            ])

        self.vbox.AddMany([
            (self.hbox, 0, wx.ALIGN_LEFT | wx.ALIGN_TOP),
            (self.hbox2, 0, wx.ALIGN_LEFT),
            (10, 7, 0),
            (self.hbox3, 0, wx.EXPAND),
            (10, 0, 0),
            (self.szr_top, 1, wx.ALIGN_LEFT | wx.ALIGN_BOTTOM | wx.EXPAND)
            ])
        
        # Hide the vertical box sizer
        self.vbox.Hide(self.hbox2)
        # Set size of frame
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.Layout()

    def SaveUsbLog(self, e):
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
        content = self.scb.GetValue()
        self.top.save_file(content, "*.txt")

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
  
    def ClearUsbWindow(self, e):
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
        try:
            usbDev.get_tree_change(self.top)
        except:
            # print message
            self.print_on_usb("USB Read Error!")
        self.wait_flg = False
        self.btn_ref.Enable()
    
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
        dtstr = ct.strftime("%Y-%m-%d  %H:%M:%S.%f")
        cstr = "[" + dtstr[:-3] + "]  "
        return cstr
    
    def print_on_usb(self, strin):
        """
        print the data in usb tree view window
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            strin: USB device list in String format.
        Returns:
            None
        """
        ctstr = "\n"
        # Gets the state of a state checkbox.
        if(self.chk_ts.GetValue() == True):
            ctstr = ctstr + self.get_time_stamp()
        ctstr = ctstr + strin
        self.scb.AppendText(ctstr)
   
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
        if(self.chk_box.GetValue() == True):
            return True
        else:
            return False
    
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
        self.chk_box.SetValue(False)
    
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
            onTime, offTime, duty = self.top.get_loop_param()
            if(int(onTime) >= int(offTime)):
                if(int(offTime) < int(self.get_enum_delay())):
                    duty = 100 - duty
                    ndly = int((int(self.get_enum_delay())*100)/duty)
                    self.top.set_period(str(ndly))
            else:
                if(int(onTime) < int(self.get_enum_delay())):
                    ndly = int((int(self.get_enum_delay())*100)/duty)
                    self.top.set_period(str(ndly))

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
            
            '''if(int(self.top.get_interval()) < int(self.get_enum_delay())):
                self.top.set_interval(self.get_enum_delay())'''
    
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
            self.chk_box.Enable()
            self.tc_delay.Enable()
        else:
            self.chk_box.Disable()
            self.tc_delay.Disable()
