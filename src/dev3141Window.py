##############################################################################
# 
# Module: dev3141Window.py
#
# Description:
#     Device specific functions and UI for interfacing Model 3141 with GUI
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

# Built-in imports
import os

# Own modules
import serialDev
import usbDev
from uiGlobals import *

PORTS = 2

##############################################################################
# Utilities
##############################################################################
"""
A class dev3141Window with init method

the dev3141Window navigate to Super speed and High speed enable 
or disable options.
"""
class Dev3141Window(wx.Panel):
    """
    Device specific functions and UI for interfacing Model 3141 with GUI 
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
        
        self.parent = parent
        self.top = top

        self.pcnt = 0

        self.duty = 0
        self.OnTime = 0
        self.OffTime = 0

        self.On_flg = False
        self.auto_flg = False
        self.pulse_flg = False

        self.usb_flg = False 
        # The Timer class allows you to execute code at specified intervals.
        self.timer = wx.Timer(self)
        self.timer_usb = wx.Timer(self)
        self.timer_do = wx.Timer(self)
        # Call this to give the sizer a minimal size.
        self.SetMinSize((290, 170))
        # create a staticbox naming as  Model2101
        sb = wx.StaticBox(self, -1, "Model 3141")

        self.vbox = wx.StaticBoxSizer(sb,wx.VERTICAL)
        # BoxSizer fixed with Horizontal
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxs1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox5 = wx.BoxSizer (wx.HORIZONTAL)
        
        self.st_p1 = wx.StaticText(self, -1, "Port 1", size = (-1,-1))
        self.st_p2 = wx.StaticText(self,-1, "Port 2", size = (-1,-1))
        
        base = os.path.abspath(os.path.dirname(__file__))
        self.picf = wx.Bitmap (base+"/icons/"+IMG_BTN_OFF, wx.BITMAP_TYPE_ANY)
        self.picn = wx.Bitmap (base+"/icons/"+IMG_BTN_ON, wx.BITMAP_TYPE_ANY)
        
        self.btn_p1 = wx.BitmapButton(self, 0, self.picf, size= (-1,-1))
        self.btn_p2 = wx.BitmapButton(self, 1, self.picf, size= (-1,-1))
        
        self.st_ss   = wx.StaticText(self, -1, "SuperSpeed")
        self.rbtn_ss1 = wx.RadioButton(self, ID_RBTN_SS1, "Enable", 
                                       style=wx.RB_GROUP)
        self.rbtn_ss0 = wx.RadioButton(self, ID_RBTN_SS0, "Disable")
        self.stlbl_do = wx.StaticText(self, -1, "Orientation : ", 
                                style=wx.ALIGN_CENTER_VERTICAL, size=(-1,-1))
        self.st_do   = wx.StaticText(self, -1, " --- ", 
                                    style=wx.ALIGN_CENTER_VERTICAL, size=(-1, -1))
        
        self.btnStat = [False, False]


        self.hboxp1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxp2 = wx.BoxSizer(wx.HORIZONTAL)

        self.hboxp1.Add(self.st_p1,0, flag=wx.LEFT | 
                        wx.ALIGN_CENTER_VERTICAL, border=0)
        self.hboxp1.Add(self.btn_p1, flag=wx.LEFT, border = 10)
        
        self.hboxp2.Add(self.st_p2, 0, flag= wx.ALIGN_CENTER_VERTICAL | 
                        wx.LEFT, border = 0)
        self.hboxp2.Add(self.btn_p2, flag=wx.LEFT,  border = 10)


        self.hboxs1.Add(self.hboxp1, flag=wx.LEFT, border=20)
        self.hboxs1.Add((0,0), 1, wx.EXPAND)
        self.hboxs1.Add(self.hboxp2, flag=wx.RIGHT , border=20)
        
        self.hbox2.Add(self.st_ss,0 , flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL,border=20 )
        self.hbox2.Add(self.rbtn_ss1, flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL,
                       border = 20)
        self.hbox2.Add(self.rbtn_ss0, flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 
                       border=18)

        self.hbox3.Add(self.stlbl_do, flag=wx.LEFT, border=20 )
        self.hbox3.Add(self.st_do, flag= wx.LEFT, border=10)
                
        self.vbox.AddMany([
            (0,20,0),
            (self.hboxs1, 1, wx.EXPAND | wx.ALL),
            (0,15,0),
            (self.hbox2, 1, wx.EXPAND),
            (0,10,0),
            (self.hbox3, 1, wx.EXPAND)
            ])

        # set size of frame
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.Layout()
        
        # bind the button event to handler
        self.Bind(wx.EVT_RADIOBUTTON, self.PortSpeedChanged)
        self.Bind(wx.EVT_BUTTON,self.OnOffPort, self.btn_p1)
        self.Bind(wx.EVT_BUTTON,self.OnOffPort, self.btn_p2)
        # bind the timer event to handler
        self.Bind(wx.EVT_TIMER, self.UsbTimer, self.timer_usb)
        self.Bind(wx.EVT_TIMER, self.DoTimer, self.timer_do)

        self.rbtn = []
        self.rbtn.append(self.btn_p1)
        self.rbtn.append(self.btn_p2)

        self.enable_controls(False)
    
    """
    Event Handler for 2 Port Switches

    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        e:The event parameter in the dev3141Window method is an 
        object specific to a particular event type.
        event hanlder for OnOffPort switch
    Returns:
        return None
    """

    # Event Handler for 2 Port Switches
    def OnOffPort (self, e):
        # Returns the object (usually a window) associated,
        # with the event, if any.
        co = e.GetEventObject()
        # Returns the identifier associated with,
        # this event, such as a button command id.
        cbi = co.GetId()
        if self.top.mode == MODE_MANUAL and not self.usb_flg:
            self.port_on_manual(cbi)
    
    """
    Event handler for Speed change Radio buttons
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        e:The event parameter in the dev3141Window method is an 
        object specific to a particular event type.
        Event Handler for Port Speed Change
    Returns:
        return None
    """
    def PortSpeedChanged(self, e):
        # Returns the object (usually a window) associated
        # with the event, if any
        rb = e.GetEventObject()
        # Returns the identifier associated with, 
        # this event, such as a button command id.
        id = rb.GetId()

        if id == ID_RBTN_SS1:
            # return superspeed
            self.speed_cmd(1)
        elif id == ID_RBTN_SS0:
            # returs highspeed 
            self.speed_cmd(0)
    
    """
    Timer Event for USB Tree View Changes

    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        e:The event parameter in the dev3141Window method is an 
        object specific to a particular event type.
        Timer Event for USB Tree View Changes
    Returns:
        return None
    """
    def UsbTimer(self, e):
        self.timer_usb.Stop()
        try:
            usbDev.get_tree_change(self.top)
        except:
            # to print on usb tree view change "USB Read Error!"
            self.top.print_on_usb("USB Read Error!")
        self.usb_flg = False

    """
    Timer Event for USB Tree View Changes

    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        e:The event parameter in the dev3141Window method is an 
        object specific to a particular event type.
        event handler to orientation
    Returns:
        return None
    """  
    def DoTimer(self, e):
        self.timer_do.Stop()
        # check orientation
        self.get_orientation()
    """
    Port ON in Manual Mode

    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        port: manually controlling the ports.
        control the porn On manually asfter 3sec status
        updated for check orientation
    Returns:
        return None
    """  
    def port_on_manual(self, port):
        for i in range (len (self.rbtn)):
            if(port == i):
                self.btnStat[port] = not self.btnStat[port]
                self.port_on(port+1, self.btnStat[port])
                if(self.btnStat[port]):
                   self.timer_do.Start(3000)
                else:
                   self.timer_do.Stop()
            else:
                self.btnStat[i] = False
    """
    Port ON/OFF in Auto and Loop Mode, while in Loop Mode Command received 
    Command received from Loop Window
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        port: ports update
        stat: return status for port on cmd and port led update
    Returns:
        return None
    """  
    def port_on(self, port, stat):
        if(stat):
            self.port_on_cmd(port)
        else:
            self.port_off_cmd(port)
        self.port_led_update(port-1, stat)

        if(self.top.mode == MODE_MANUAL):
            if(self.top.get_delay_status()):
                self.keep_delay()
    """
    Port ON Command

    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        pno: port number updated print in logwindow
    Returns:
        return None
    """
    def port_on_cmd(self, pno):
        cmd = 'port'+' '+str(pno)+'\r\n'
        res, outstr = serialDev.send_port_cmd(self.top.devHand, cmd)
        if res == 0:
            outstr = outstr.replace('p', 'P')
            outstr = outstr.replace('1', '1 ON')
            outstr = outstr.replace('2', '2 ON')
            outstr = outstr[:-2] + "; Other Ports are OFF\n"
            self.top.print_on_log(outstr)
            if self.top.mode == MODE_MANUAL:
                self.enable_do_controls(True)
    """
    Port OFF Command

    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        pno: port number updated 
    Returns:
        return None
    """   
    def port_off_cmd(self, pno):
        cmd = 'port'+' '+'0'+'\r\n'
        res, outstr = serialDev.send_port_cmd(self.top.devHand, cmd)
        if res == 0:
            outstr = outstr.replace('p', 'P')
            outstr = outstr.replace('0', ""+str(pno)+" OFF")
            self.top.print_on_log(outstr)
            self.enable_do_controls(False)
    
    """
    Add Delay in Port ON/OFF based on USB option

    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """ 
    def keep_delay(self):
        self.usb_flg = True
        self.timer_usb.Start(int(self.top.get_enum_delay()))
    
    """
    Update the Port Indication

    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        port: port ON/OFF updated
        stat: return status for port led status indication
    Returns:
        return None
    """      
    def port_led_update(self, pno, stat):
        if(stat):
            for i in range(2):
                if(i == pno):
                    self.rbtn[i].SetBitmap(self.picn)
                else:
                    self.rbtn[i].SetBitmap(self.picf)
        else:
            for i in range(2):
                self.rbtn[i].SetBitmap(self.picf)
    
    """
    Called when changing the Mode - Called by set_mode

    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        mode: update mode controls
    Returns:
        return None
    """
    def update_controls(self, mode):
        if mode == MODE_MANUAL:
            self.enable_controls(True)
        else:
            self.enable_controls(False)
    
    """
    Enable/Disable All Widgets in UI3141

    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        stat: updated the status for widgets enable/disable
    Returns:
        return None
    """
    def enable_controls(self, stat):
        if not self.top.con_flg:
            stat = False
        self.enable_port_controls(stat)
        self.enable_speed_controls(stat)
        self.enable_do_controls(stat)
    """
    Enable/Diasble 2 Port Switch

    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        stat: updated the status port switch enable/disable
    Returns:
        return None
    """   
    def enable_port_controls(self, stat):
        stat = self.top.con_flg
        if(stat):
            self.btn_p1.Enable()
            self.btn_p2.Enable()
        else:
            self.btn_p1.Disable()
            self.btn_p2.Disable()
    
    """
    Enable/Disale Speed controls

    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        stat: updated the status for superspeed enable/disable
    Returns:
        return None
    """
    def enable_speed_controls(self, stat):
        if(stat):
            self.rbtn_ss0.Enable()
            self.rbtn_ss1.Enable()
        else:
            self.rbtn_ss0.Disable()
            self.rbtn_ss1.Disable()
    
    """
    Enable/Disable Device Orientation Controls

    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        stat: updated the status for enable/disable 
        device orientation controls
    Returns:
        return None
    """
    def enable_do_controls(self, stat):
        pass
    """
    Speed change command to 3141 Device
    Args:
        self: The self parameter is a reference to the current
        instance of the class,and is used to access variables
        that belongs to the class.
        val: port command update based on Speed Selection. 
    Returns:
        return None
    """
    def speed_cmd(self,val):
        cmd = 'superspeed'+' '+str(val)+'\r\n'
        res, outstr = serialDev.send_port_cmd(self.top.devHand,cmd)
        if res == 0:
            outstr = outstr.replace('s', 'S')
            outstr = outstr.replace('1', 'Enabled')
            outstr = outstr.replace('0', 'Disabled')
        self.top.print_on_log(outstr)

    """
    Get Device Orientation from the Status 
    Args:
        self: The self parameter is a reference to the current
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def get_orientation(self):    
        strin = "--"
        res, outstr = serialDev.send_status_cmd(self.top.devHand)
        if res == 0:
            restr = outstr.split('\n')
            cc1detect = None
            cc1led = None
            for instr in restr:
                if 'CC1 detect:' in instr:
                    fstr = instr.split('0x')
                    cc1detect = int(fstr[1], 16)
                elif 'CC1 led:' in instr:
                    lstr = instr.split(':')
                    cc1led = int(lstr[1])
                    break
            if cc1led == 0 and cc1detect < 20:
                strin = "Flip"
            elif cc1led == 1 and cc1detect > 20:
                strin = "Normal"
            
            self.update_carrier(strin)
            self.top.print_on_log("Device Orientation : "+strin+"\n")
            #self.top.print_on_log("Device Orientation : "+str(cc1led)+",
            #  "+str(cc1detect)+", "+strin+"\n")
        else:
            self.update_carrier(strin)
            strin = "Device Error"
            self.top.print_on_log("Device Orientation : "+strin+"\n")
    """
    Display the Carrier direction in UI
    Args:
        self: The self parameter is a reference to the current
        instance of the class,and is used to access variables
        that belongs to the class.
        str: display the string for update carrier 
    Returns:
        return None
    """
    def update_carrier(self, str):
        self.st_do.SetLabel(str)
    
    """
    Called by Com Window When Device Connected
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def device_connected(self):
        if(self.top.con_flg):
            res, outstr = serialDev.read_port_cmd(self.top.devHand)
            if res == 0 and outstr == '':
                res, outstr = serialDev.read_port_cmd(self.top.devHand)
            if res == 0:
                if(outstr != ''):
                    self.init_ports(int(outstr))
                self.top.UpdateSingle("", 2)
                self.enable_controls(True)
                self.top.set_port_list(PORTS)
            else:
                self.top.print_on_log("No response from 3141,\
                                       please connect again!\n")
                self.enable_controls(False) 
    
    """
     Called by Com Window When Device get DisConnected
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """  
    def device_disconnected(self):
        if self.auto_flg:
            self.auto_flg = False
            self.btn_auto.SetLabel("Start")
            self.timer.Stop()
    
    """
     During connect map the indication to the device status
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        port: update the port led 
    Returns:
        return None
    """  
    def init_ports(self, port):
        if(port == 0):
            self.port_led_update(port, False)
        else:
            self.port_led_update(port-1, True)
            self.btnStat[port-1] = True