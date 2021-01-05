#======================================================================
# (c) 2020  MCCI, Inc.
#----------------------------------------------------------------------
# Project : UI3141/3201 GUI Application
# File    : dev3141Window.py
#----------------------------------------------------------------------
# Device specific functions and UI for interfacing 3141 with GUI
#======================================================================

#======================================================================
# IMPORTS
#======================================================================
import wx
import os

import usbDev

import control2101 as d2101

from uiGlobals import *

PORTS = 1

#======================================================================
# 2101 Control Words
#======================================================================

CHECK_STATUS    = 0x00
DEV_RESET       = 0x01
DEV_VERSION     = 0x02
HS_CONNECT      = 0x03
DEV_CUSTOM      = 0x04
SS_CONNECT      = 0x05
DEV_DISCONNECT  = 0x06


#======================================================================
# COMPONENTS
#======================================================================

class Dev2101Window(wx.Panel):
    def __init__(self, parent, top):
        wx.Panel.__init__(self, parent)
        
        self.parent = parent
        self.top = top

        self.portcmd = SS_CONNECT

        self.SetMinSize((280, 140))

        sb = wx.StaticBox(self, -1, "Model 2101")

        self.vbox = wx.StaticBoxSizer(sb,wx.VERTICAL)

        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxs1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox5 = wx.BoxSizer (wx.HORIZONTAL)
        
        self.st_port = wx.StaticText(self, -1, "Port", size = (40, 15)) 
        self.picf = wx.Bitmap ("./icons/btn_off.png", wx.BITMAP_TYPE_ANY)
        self.picn = wx.Bitmap ("./icons/btn_on.png", wx.BITMAP_TYPE_ANY)
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
        self.hbox2.Add(self.st_ss,0 , flag=wx.ALIGN_LEFT | wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 
                       border=20 )
        self.hbox2.Add(self.rbtn_ss1, flag=wx.ALIGN_LEFT | wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border = 20)
        self.hbox2.Add(self.rbtn_ss0, flag=wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER_VERTICAL |
                       wx.ALIGN_RIGHT, border=18)

        self.tog_flg = False
        self.pulse_flg = False
        self.timer = wx.Timer(self)
        self.timer_usb = wx.Timer(self)

        self.vbox.AddMany([
            (self.hbox1, 1, wx.EXPAND | wx.ALL),
            (self.hbox2, 1, wx.EXPAND),
            ])
        
        self.Bind(wx.EVT_TIMER, self.UsbTimer, self.timer_usb)
        self.Bind(wx.EVT_RADIOBUTTON, self.PortSpeedChanged)
        self.Bind(wx.EVT_BUTTON, self.OnOffPort, self.btn_p1)
        
        self.enable_controls(True)
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.Layout()

    
    # Event Handler for 4 Port Switches
    def OnOffPort (self, e):
        co = e.GetEventObject()
        cbi = co.GetId()
        if self.top.mode == MODE_MANUAL and not self.usb_flg:
            self.port_on_manual(cbi)

    # Event Handler for Port Speed Change
    def PortSpeedChanged(self, e):
        rb = e.GetEventObject()
        id = rb.GetId()
        
        if(id >= ID_RBTN_SS0):
            id = id - ID_RBTN_SS0
            self.speed_cmd(id)

    # Timer Event for USB Tree View Changes  
    def UsbTimer(self, e):
        self.timer_usb.Stop()
        try:
            usbDev.get_tree_change(self.top)
        except:
            self.top.print_on_usb("USB Read Error!")
        self.usb_flg = False
    
    # Port ON in Manual Mode
    def port_on_manual(self, port):
        for i in range (len (self.rbtn)):
            if(port == i):
                self.btnStat[port] = not self.btnStat[port]
                self.port_on(port+1, self.btnStat[port])
            else:
                self.btnStat[i] = False

    # Port ON/OFF in Auto and Loop Mode, while in Loop Mode Command received 
    # from Loop Window
    def port_on(self, port, stat):
        if(stat):
            self.port_on_cmd(port)
        else:
            self.port_off_cmd(port)
        self.port_led_update(port-1, stat)

        if(self.top.mode == MODE_MANUAL):
            if(self.top.get_delay_status()):
                self.keep_delay()

    # Port ON Command
    def port_on_cmd(self, port):
        d2101.control_port(self.top.selPort, self.portcmd)
        self.top.print_on_log("Port ON\n")
        self.port_led_update(port, True)
        
    # Port OFF Command   
    def port_off_cmd(self, port):
        d2101.control_port(self.top.selPort, DEV_DISCONNECT)
        self.top.print_on_log("Port OFF\n")
        self.port_led_update(port, False)

    # Add Delay in Port ON/OFF based on USB option
    def keep_delay(self):
        self.usb_flg = True
        self.timer_usb.Start(int(self.top.get_enum_delay()))
        
    # Update the Port Indication
    def port_led_update(self, port, stat):
        if(stat):
            self.rbtn[0].SetBitmap(self.picn)
        else:
            self.rbtn[0].SetBitmap(self.picf)

    # Called when changing the Mode - Called by set_mode
    def update_controls(self, mode):
        if mode == MODE_MANUAL:
            self.enable_controls(True)
        else:
            self.enable_controls(False)
    
    # Enable/Disable All Widgets in 2101
    def enable_controls(self, stat):
        if not self.top.con_flg:
            stat = False
        
        self.enable_port_controls(stat)
        self.enable_speed_controls(stat)
             
    # Enable/Diasble Port Switch        
    def enable_port_controls(self, stat):
        stat = self.top.con_flg
        if(stat):
            self.btn_p1.Enable()
        else:
            self.btn_p1.Disable()

    # Enable/Disale Speed controls
    def enable_speed_controls(self, stat):
        if(stat):
            self.rbtn_ss0.Enable()
            self.rbtn_ss1.Enable()
        else:
            self.rbtn_ss0.Disable()
            self.rbtn_ss1.Disable()        
 
    # Port Command update based on Speed Selection in 2101
    def speed_cmd(self,val):
        if(val == 1):
            self.top.print_on_log("Super Speed Enabled\n")
            self.portcmd = SS_CONNECT
        else:
            self.top.print_on_log("Super Speed Disabled\n")
            self.portcmd = HS_CONNECT

    # Called by Com Window When Device Connected
    def device_connected(self):
        if self.top.con_flg:
            self.enable_controls(True)
            self.top.set_port_list(PORTS)

    # Called by Com Window When Device get DisConnected
    def device_disconnected(self):
        if self.auto_flg:
            self.auto_flg = False
            self.btn_auto.SetLabel("Start")
            self.timer.Stop()