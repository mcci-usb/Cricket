##############################################################################
# 
# Module: dev2101Window.py
#
# Description:
#     Device specific functions and UI for interfacing Model 2101 with GUI
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
#Lib imports
import wx

# Built-in imports
import os

# Own modules
import usbDev
import control2101 as d2101
from uiGlobals import *

PORTS = 1

##############################################################################
# 2101 Control Words
##############################################################################

CHECK_STATUS    = 0x00
DEV_RESET       = 0x01
DEV_VERSION     = 0x02
HS_CONNECT      = 0x03
DEV_CUSTOM      = 0x04
SS_CONNECT      = 0x05
DEV_DISCONNECT  = 0x06


##############################################################################
# Utilities
##############################################################################
class Dev2101Window(wx.Panel):
    """
    A class Dev2101Window with init method

    the Dev2101Window navigate to Super speed and High speed enable 
    or disable options.
    """
    def __init__(self, parent, top):
        """
        Device specific functions and UI for interfacing Model 2101 with GUI
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
            top: create a object
        Returns:
            None
        """
        wx.Panel.__init__(self, parent)
        
        self.parent = parent
        self.top = top
        # Port command for SuperSpeed
        self.portcmd = SS_CONNECT
        # Call this to give the sizer a minimal size.
        self.SetMinSize((280, 140))
        # Create a staticbox naming as  Model2101 
        sb = wx.StaticBox(self, -1, "Model 2101")
        # BoxSizer fixed with Vertical
        self.vbox = wx.StaticBoxSizer(sb,wx.VERTICAL)
        # BoxSizer fixed with Horizontal
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxs1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox5 = wx.BoxSizer (wx.HORIZONTAL)
        
        self.st_port = wx.StaticText(self, -1, "Port", size = (40, 15)) 
        
        base = os.path.abspath(os.path.dirname(__file__))
        self.picf = wx.Bitmap (base+"/icons/"+IMG_BTN_OFF, wx.BITMAP_TYPE_ANY)
        self.picn = wx.Bitmap (base+"/icons/"+IMG_BTN_ON, wx.BITMAP_TYPE_ANY)
        
        self.btn_p1 = wx.BitmapButton(self, 0, self.picf,size= (-1,-1))
        self.st_ss   = wx.StaticText(self, -1, "SuperSpeed")
        self.rbtn_ss1 = wx.RadioButton(self, ID_RBTN_SS1, "Enable", 
                                       style=wx.RB_GROUP)
        self.rbtn_ss0 = wx.RadioButton(self, ID_RBTN_SS0, "Disable")
        
        self.duty = 0
        self.OnTime = 0
        self.OffTime = 0

        self.On_flg = False
        self.auto_flg = False

        self.usb_flg = False
    
        self.rbtn = []
        self.rbtn.append(self.btn_p1)
        
        self.btnStat = [ False ]
        
        self.hboxs1.Add(self.st_port, flag=wx.ALIGN_CENTER_VERTICAL | 
                       wx.LEFT , border=20)
        
        self.hboxs1.Add(self.btn_p1, flag=wx.ALIGN_CENTER_VERTICAL | 
                       wx.LEFT, border = 0)
 
        self.hbox1.Add(self.hboxs1, flag=wx.ALIGN_CENTER_VERTICAL )
        self.hbox1.Add(0,1,0)
        self.hbox2.Add(self.st_ss,0 , flag=wx.ALIGN_LEFT | wx.LEFT | 
                                      wx.ALIGN_CENTER_VERTICAL,  
                                      border=20 )
        self.hbox2.Add(self.rbtn_ss1, flag=wx.ALIGN_LEFT | wx.LEFT | 
                                      wx.ALIGN_CENTER_VERTICAL, border = 20)
        self.hbox2.Add(self.rbtn_ss0, flag=wx.RIGHT | wx.LEFT | 
                                      wx.ALIGN_CENTER_VERTICAL |
                                      wx.ALIGN_RIGHT, border=18)

        self.tog_flg = False
        self.pulse_flg = False
        # The Timer class allows you to execute code at specified intervals.
        self.timer = wx.Timer(self)
        self.timer_usb = wx.Timer(self)

        self.vbox.AddMany([
            (self.hbox1, 1, wx.EXPAND | wx.ALL),
            (self.hbox2, 1, wx.EXPAND),
            ])
        # Bind the button event to handler
        self.Bind(wx.EVT_TIMER, self.UsbTimer, self.timer_usb)
        # Bind the button event to handler
        self.Bind(wx.EVT_RADIOBUTTON, self.PortSpeedChanged)
        # Bind the button event to handler
        self.Bind(wx.EVT_BUTTON, self.OnOffPort, self.btn_p1)
        
        self.enable_controls(True)
        # Set size of frame
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.Layout()
    def OnOffPort (self, e):
        """
        Event Handler for single Port Switches On and Off

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            e:The event parameter in the dev2101Window method is an 
            object specific to a particular event type.
            event hanlder for OnOffPort switch
        Returns:
            None
        """
        # Returns the object (usually a window) associated,
        # With the event, if any.
        co = e.GetEventObject()
        # Returns the identifier associated with,
        # This event, such as a button command id.
        cbi = co.GetId()
        if self.top.mode == MODE_MANUAL and not self.usb_flg:
            self.port_on_manual(cbi)
    def PortSpeedChanged(self, e):
        """
        Event Handler for Port Speed Change for Highspeed and Superspeed

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            e:The event parameter in the dev2101Window method is an 
            object specific to a particular event type.
            Event Handler for Port Speed Change
        Returns:
            None
        """
        # Returns the object (usually a window) associated
        # with the event, if any
        rb = e.GetEventObject()
        # Returns the identifier associated with, 
        # This event, such as a button command id.
        id = rb.GetId()
        
        if(id >= ID_RBTN_SS0):
            id = id - ID_RBTN_SS0
            self.speed_cmd(id)
      
    def UsbTimer(self, e):
        """
        Usb timer set to the switching a ports On and Off
        Timer Event for USB Tree View Changes

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            e:The event parameter in the dev2101Window method is an 
            object specific to a particular event type.
            Timer Event for USB Tree View Changes
        Returns:
            None
        """
        self.timer_usb.Stop()
        try:
            usbDev.get_tree_change(self.top)
        except:
            # To print on usb tree view change "USB Read Error!"
            self.top.print_on_usb("USB Read Error!")
        self.usb_flg = False
      
    def port_on_manual(self, port):
        """
        Port ON in Manual Mode

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            port: manually controlling the ports.
        Returns:
            None
        """
        for i in range (len (self.rbtn)):
            if(port == i):
                self.btnStat[port] = not self.btnStat[port]
                self.port_on(port+1, self.btnStat[port])
            else:
                self.btnStat[i] = False
    
    def port_on(self, port, stat):
        """
        Port ON/OFF in Auto and Loop Mode, while in Loop Mode Command 
        received from Loop Window, also button state change.

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            port: ports update
            stat: return status for port on cmd and port led update
        Returns:
            None
        """  
        if(stat):
            self.port_on_cmd(port)
        else:
            self.port_off_cmd(port)
        self.port_led_update(port-1, stat)

        if(self.top.mode == MODE_MANUAL):
            if(self.top.get_delay_status()):
                self.keep_delay()
     
    def port_on_cmd(self, port):
        """
        send the Port ON Command

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            port: to select the port in Loop mode,
            print Port ON in log windwo
        Returns:
            None
        """ 
        d2101.control_port(self.top.selPort, self.portcmd)
        # print port ON 
        self.top.print_on_log("Port ON\n")
        self.port_led_update(port, True)
       
    def port_off_cmd(self, port):
        """
        send the Port OFF Command

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            port: to select the port in Loop mode,
            print Port OFF in Log window
        Returns:
            None
        """
        d2101.control_port(self.top.selPort, DEV_DISCONNECT)
        self.top.print_on_log("Port OFF\n")
        self.port_led_update(port, False)
           
    def keep_delay(self):
        """
        Add Delay in Port ON/OFF based on USB option

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.usb_flg = True
        self.timer_usb.Start(int(self.top.get_enum_delay()))
         
    def port_led_update(self, port, stat):
        """
        Update the Port led On/Off Indication

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            port: port ON/OFF updated
            stat: return status for port led status updated 
        Returns:
            None
        """
        if(stat):
            self.rbtn[0].SetBitmap(self.picn)
        else:
            self.rbtn[0].SetBitmap(self.picf)
    
    def update_controls(self, mode):
        """
        Called when changing the Mode - Called by set_mode

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            mode: update mode controls
        Returns:
            None
        """         
        if mode == MODE_MANUAL:
            self.enable_controls(True)
        else:
            self.enable_controls(False)
            
    def enable_controls(self, stat):
        """
        Enable/Disable All Widgets in 2101

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            stat: updated the status for widgets enable/disable
        Returns:
            None
        """
        if not self.top.con_flg:
            stat = False
        
        self.enable_port_controls(stat)
        self.enable_speed_controls(stat)

    def enable_port_controls(self, stat):
        """
        Enable/Diasble Port Switch

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            stat: updated the status port switch enable/disable
        Returns:
            None
        """              

        stat = self.top.con_flg
        if(stat):
            self.btn_p1.Enable()
        else:
            self.btn_p1.Disable()
       
    def enable_speed_controls(self, stat):
        """
        Enable/Disale Speed controls

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            stat: updated the status for superspeed enable/disable
        Returns:
            None
        """
        if(stat):
            self.rbtn_ss0.Enable()
            self.rbtn_ss1.Enable()
        else:
            self.rbtn_ss0.Disable()
            self.rbtn_ss1.Disable()        
       
    def speed_cmd(self,val):
        """
        Port Command update based on Speed Selection in 2101
        Args:
            self: The self parameter is a reference to the current
            instance of the class,and is used to access variables
            that belongs to the class.
            val: port command update based on Speed Selection. 
        Returns:
            None
        """
        if(val == 1):
            self.top.print_on_log("Super Speed Enabled\n")
            self.portcmd = SS_CONNECT
        else:
            self.top.print_on_log("Super Speed Disabled\n")
            self.portcmd = HS_CONNECT
       
    def device_connected(self):
        """
        Called by Com Window When Device Connected
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        if self.top.con_flg:
            self.enable_controls(True)
            self.top.set_port_list(PORTS)
       
    def device_disconnected(self):
        """
        Called by Com Window When Device get DisConnected
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        if self.auto_flg:
            self.auto_flg = False
            self.btn_auto.SetLabel("Start")
            self.timer.Stop()