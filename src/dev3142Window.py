##############################################################################
# 
# Module: dev3142Window.py
#
# Description:
#     Device specific functions and UI for interfacing Model 3142 with GUI
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

# Built-in imports
import os
import time

# Own modules
import devControl as model
import thControl
from uiGlobals import *

PORTS = 2

##############################################################################
# Utilities
##############################################################################
class Dev3142Window(wx.Panel):
    """
    A class dev3142Window with init method

    the dev3142Window navigate to Super speed and High speed enable 
    or disable options.
    """
    def __init__(self, parent, top, portno):
        """
        Device specific functions and UI for interfacing Model 3142 with GUI 
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
        
        self.parent = parent
        self.top = top
        self.swid = portno

        self.swtitle = "3142"
        if(len(portno)):
            self.swtitle += " ("+portno+")"

        self.fv = None
        # self.ib = None
        self.fa = None
        # self.inval = None

        self.con_flg = None

        self.pcnt = 0
        self.rport = 0

        self.duty = 0
        self.OnTime = 0
        self.OffTime = 0

        self.On_flg = False
        self.auto_flg = False
        self.pulse_flg = False

        self.con_flg = None

        self.usb_flg = False 
        # The Timer class allows you to execute code at specified intervals.
        self.timer = wx.Timer(self)
        self.timer_usb = wx.Timer(self)
        self.timer_va = wx.Timer(self)
        self.timer_vu = wx.Timer(self)
        self.timer_do = wx.Timer(self)
        self.timer_safe = wx.Timer(self)
        self.timer_port = wx.Timer(self)
        # Call this to give the sizer a minimal size.
        self.SetMinSize((290, 170))
        # Create a staticbox naming as  Model2101
    
        
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
                                    style=wx.ALIGN_CENTER_VERTICAL,
                                    size=(-1, -1))
        
        self.btnStat = [False, False]
        self.stlbl_volts = wx.StaticText(self, -1, "Bus Volts :", 
                                                   size=(-1,-1))
        self.st_volts   = wx.StaticText(self, -1, " --- ", 
                                        style = wx.ALIGN_CENTER_VERTICAL)
        self.stlbl_amps = wx.StaticText(self, -1, "Bus Current:",
                                                   size=(-1,-1))
        self.st_amps   = wx.StaticText(self, -1, " --- ", 
                                       style = wx.ALIGN_CENTER_VERTICAL, 
                                       size=(-1,-1))
        self.sb = wx.StaticBox(self, -1, self.swtitle)

        self.vbox = wx.StaticBoxSizer(self.sb,wx.VERTICAL)
        # BoxSizer fixed with Horizontal
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxs1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox5 = wx.BoxSizer (wx.HORIZONTAL)

        self.hboxp1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxp2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxs1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxs2 = wx.BoxSizer(wx.HORIZONTAL)

        self.hboxp1.Add(self.st_p1,0, flag=wx.LEFT | 
                        wx.ALIGN_CENTER_VERTICAL, border=0)
        self.hboxp1.Add(self.btn_p1, flag=wx.LEFT, border = 10)
        
        self.hboxp2.Add(self.st_p2, 0, flag= wx.ALIGN_CENTER_VERTICAL | 
                        wx.LEFT, border = 0)
        self.hboxp2.Add(self.btn_p2, flag=wx.LEFT,  border = 10)


        self.hboxs1.Add(self.hboxp1, flag=wx.LEFT, border=20)
        self.hboxs1.Add((0,0), 1, wx.EXPAND)
        self.hboxs1.Add(self.hboxp2, flag=wx.RIGHT , border=20)
        
        self.hbox2.Add(self.st_ss,0 , flag=wx.LEFT | 
                                      wx.ALIGN_CENTER_VERTICAL,border=20 )
        self.hbox2.Add(self.rbtn_ss1, flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL,
                            border = 20)
        self.hbox2.Add(self.rbtn_ss0, flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 
                            border=18)

        self.hbox3.Add(self.stlbl_do, flag=wx.LEFT, border=20 )
        self.hbox3.Add(self.st_do, flag= wx.LEFT, border=10)
        self.hbox5.Add(self.stlbl_volts, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border=20 )
        self.hbox5.Add(self.st_volts, flag=wx.LEFT |
                       wx.ALIGN_CENTER_VERTICAL)
        self.hbox5.Add(self.stlbl_amps, flag=wx.LEFT | 
                       wx.ALIGN_CENTER_VERTICAL |
                       wx.ALIGN_LEFT, border=20)
        self.hbox5.Add(self.st_amps, flag=wx.LEFT| wx.ALIGN_CENTER_VERTICAL)
       
                
        self.vbox.AddMany([
            (0,20,0),
            (self.hboxs1, 1, wx.EXPAND | wx.ALL),
            (0,15,0),
            (self.hbox2, 1, wx.EXPAND),
            (0,10,0),
            (self.hbox3, 1, wx.EXPAND),
            (0,10,0),
            (self.hbox5, 1, wx.EXPAND)
            ])

        # Set size of frame
        self.SetSizer(self.vbox)
        self.SetAutoLayout(True)
        self.vbox.Fit(self)
        self.Layout()
        
        # Bind the button event to handler
        self.Bind(wx.EVT_RADIOBUTTON, self.PortSpeedChanged)
        self.Bind(wx.EVT_BUTTON,self.OnOffPort, self.btn_p1)
        self.Bind(wx.EVT_BUTTON,self.OnOffPort, self.btn_p2)
        # Bind the timer event to handler
        self.Bind(wx.EVT_TIMER, self.UsbTimer, self.timer_usb)
        self.Bind(wx.EVT_TIMER, self.DoTimer, self.timer_do)
        self.Bind(wx.EVT_TIMER, self.VaTimer, self.timer_va)
        self.Bind(wx.EVT_TIMER, self.GraphTimer, self.timer_vu)
        self.Bind(wx.EVT_TIMER, self.SafeTimer, self.timer_safe)
        self.Bind(wx.EVT_TIMER, self.PortOnTimer, self.timer_port)

        self.rbtn = []
        self.rbtn.append(self.btn_p1)
        self.rbtn.append(self.btn_p2)

        self.con_flg = True
        self.enable_controls(True)
        self.timer_vu.Start(50)

    def update_cport(self, portno):
        self.swtitle = "3142"
        if(len(portno)):
            self.swtitle += " ("+portno+")"
        self.swid = portno
        self.sb.SetLabel(self.swtitle)
        self.Layout()
    
    def OnOffPort (self, e):
    
        # Returns the object (usually a window) associated,
        # With the event, if any.
        co = e.GetEventObject()
        # Returns the identifier associated with,
        # This event, such as a button command id.
        cbi = co.GetId()
        # self.port_on_manual(cbi)
        if self.top.mode == MODE_MANUAL and not self.usb_flg:
            self.port_on_manual(cbi)
    
    def PortSpeedChanged(self, e):
        
        # Returns the object (usually a window) associated
        # With the event, if any
        rb = e.GetEventObject()
        # Returns the identifier associated with, 
        # This event, such as a button command id.
        id = rb.GetId()

        if id == ID_RBTN_SS1:
            # Return superspeed
            self.speed_cmd(1)
        elif id == ID_RBTN_SS0:
            # Returs highspeed 
            self.speed_cmd(0)

    def UsbTimer(self, e):
       
        self.timer_usb.Stop()
        try:
            thControl.get_tree_change(self.top)
        except:
            # To print on usb tree view change "USB Read Error!"
            self.top.print_on_log("USB Read Error!")
        self.usb_flg = False

    def VoltsCmd(self, evt):
        
        self.get_voltage()
    
    def get_voltage(self):
        strin = "***"
        res, outstr = model.send_volts_cmd(self.top, self.swid)
        if res < 0:
            outstr = "Comm Error\n"
        else:
            outstr.replace(' ', '')
            if outstr != "":
                vstr = outstr.split('\r')
                nvstr = vstr[0].replace(' V', '')
                iv = float(nvstr)
                self.fv = iv
                outstr = str(self.fv) + "V"
                self.update_volts(outstr)
        
    def AmpsCmd(self, evt):
        self.get_amps()
    
    def get_amps(self):
        strin = "---"
        res, outstr = model.send_amps_cmd(self.top, self.swid)
        if res < 0:
            outstr = "Comm Error\n"
        else:
            outstr.replace(' ', '')
            if outstr != "":
                astr = outstr.split('\n')
                sstr = astr[0].replace(' mA', '')
                ia = int(sstr)
                self.fa =  ia/1000
                ss = ""
                if(sstr == '1'):
                    ss = "-"
                outstr = ss + str(self.fa) + " A"
                self.update_amps(outstr)
        
    def GraphTimer(self, e):
        
        self.timer_vu.Stop()
        # Check voltage
        if(self.top.vgraph):
            self.get_voltage()
            self.top.vdata = self.fv
        
        # Check amps
        if(self.top.agraph):
            self.get_amps()
            self.top.adata = self.fa
            # self.top.adata = self.fa
        
        self.timer_vu.Start()
  
    def DoTimer(self, e): 
        self.timer_do.Stop()
        self.get_orientation()
    
    def VaTimer(self, e):
        self.timer_va.Stop()
        # Check voltage
        self.get_voltage()
        # Check amps
        self.get_amps()

    def SafeTimer(self, e):
        self.timer_safe.Stop()
        self.usb_flg = False

    def PortOnTimer(self, e):
        self.timer_port.Stop()
        self.port_on_cmd(self.rport)

    def port_on_manual(self, port):
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
            None
        """
        for i in range (len (self.rbtn)):
            if(port == i):
                self.btnStat[port] = not self.btnStat[port]
                self.port_on(port+1, self.btnStat[port])
                if(self.btnStat[port]):
                   self.timer_do.Start(3000)
                   self.timer_va.Start(3000)
                else:
                   self.timer_do.Stop()
                   self.timer_va.Stop()
            else:
                self.btnStat[i] = False
      
    def port_on(self, port, stat):
        """
        Port On/Off and update the status
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            port: ports update
            stat: return status for port on cmd and port led update
        Returns:
            None
        """
        if self.top.con_flg == False:
            return
        if(stat):
            if self.top.mode == MODE_MANUAL:
                res, outstr = model.read_port_status(self.top, self.swid)
                if res == 0:
                    rport = int(outstr)
                    if rport > 0:
                        self.port_off_cmd(rport)
                        self.rport = port
                        self.timer_port.Start(1000)
                    else:
                        self.port_on_cmd(port)
            else:
                self.port_on_cmd(port)
        else:
            self.port_off_cmd(port)
        
        if(self.top.mode == MODE_MANUAL):
            if(self.top.get_delay_status()):
                self.keep_delay()
            else:
                self.timer_safe.Start(1000)
                self.usb_flg = True

    def set_speed(self, speed):
        if speed == "SS1":
            self.rbtn_ss1.SetValue(True)
            speed = "SS"
        else:
            self.rbtn_ss0.SetValue(True)
            speed = "HS"
            
        res, outstr = model.send_speed_cmd(self.top, self.swid+","+speed)

        if res == 0:
            outstr = outstr.replace('s', 'S')
            outstr = outstr.replace('1', 'Enabled')
            outstr = outstr.replace('0', 'Disabled')
        self.top.print_on_log(outstr)
    
    def port_on_cmd(self, pno):
        """
        Send Port ON Command

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            pno: port number updated print in logwindow
        Returns:
            None
        """
        res, outstr = model.send_port_cmd(self.top, self.swid+",on,"+str(pno))
        if res == 0:
            outstr = outstr.replace('p', 'P')
            outstr = outstr.replace('1', '1 ON')
            outstr = outstr.replace('2', '2 ON')
            outstr = outstr[:-2] + "; Other Ports are OFF\n"
            self.top.print_on_log(self.swid+": "+outstr)
            self.port_led_update(pno-1, True)

    def port_off_cmd(self, pno):
        """
        Send Port OFF Command

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            pno: port number updated 
        Returns:
            None
        """
        res, outstr = model.send_port_cmd(self.top, self.swid+",on,"+str(0))
        if res == 0:
            outstr = outstr.replace('p', 'P')
            outstr = outstr.replace('0', ""+str(pno)+" OFF")
            self.top.print_on_log(self.swid+": "+outstr)
            self.port_led_update(pno-1, False)
    
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
          
    def port_led_update(self, pno, stat):
        """
        Update the Port led Indication

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            port: port ON/OFF updated
            stat: return status for port led status indication
        Returns:
            None
        """
        if(stat):
            for i in range(2):
                if(i == pno):
                    self.rbtn[i].SetBitmap(self.picn)
                else:
                    self.rbtn[i].SetBitmap(self.picf)
        else:
            for i in range(2):
                self.rbtn[i].SetBitmap(self.picf)
    
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

    def read_port_status(self, stat):
        if stat:
            time.sleep(1)
            res, outstr = model.read_port_status(self.top, self.swid)
            
            pstat = False
            if res == 0:
                port = int(outstr)
                if port > 0:
                    port = port - 1
                    pstat = True
                    self.btnStat[port] = True
                self.port_led_update(port, pstat)
            
    def enable_controls(self, stat):
        """
        Enable/Disable All Widgets based on stat

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            stat: updated the status for widgets enable/disable
        Returns:
            None
        """
        if not self.con_flg:
            stat = False
        self.enable_port_controls(stat)
        self.enable_speed_controls(stat)
        self.enable_do_controls(stat)
        self.enable_va_controls(stat)
        self.read_port_status(stat) 
       
    def enable_port_controls(self, stat):
        """
        Enable/Diasble Port Switch widgets

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            stat: updated the status port switch enable/disable
        Returns:
            None
        """
        stat = self.con_flg
        if(stat):
            self.btn_p1.Enable()
            self.btn_p2.Enable()
        else:
            self.btn_p1.Disable()
            self.btn_p2.Disable()
    
    def enable_speed_controls(self, stat):
        """
        Enable/Disale speed controls

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

    def enable_do_controls(self, stat):
        """
        Enable/Disable Device Orientation Controls

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            stat: updated the status for enable/disable 
            device orientation controls
        Returns:
            None
        """
        pass

    def enable_va_controls(self,stat):
        pass

    
    def speed_cmd(self,val):
        """
        Speed change command to Model3142 Device
        Args:
            self: The self parameter is a reference to the current
            instance of the class,and is used to access variables
            that belongs to the class.
            val: port command update based on Speed Selection. 
        Returns:
            None
        """
        speed = "HS"
        if(val == 1):
            speed = "SS"
        res, outstr = model.send_speed_cmd(self.top, self.swid+","+speed)

        if res == 0:
            outstr = outstr.replace('s', 'S')
            outstr = outstr.replace('1', 'Enabled')
            outstr = outstr.replace('0', 'Disabled')
        self.top.print_on_log(outstr)
    
    def get_orientation(self):    
        """
        Get Device Orientation from the device status
        Args:
            self: The self parameter is a reference to the current
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        strin = "--"
        res, outstr = model.send_status_cmd(self.top, self.swid)
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
            
        else:
            self.update_carrier(strin)
            strin = "Device Error"
            self.top.print_on_log("Device Orientation : "+strin+"\n")
    
    def update_carrier(self, str):
        """
        Display the Device Orientation status in UI
        Args:
            self: The self parameter is a reference to the current
            instance of the class,and is used to access variables
            that belongs to the class.
            str: display the string for update carrier 
        Returns:
            None
        """
        self.st_do.SetLabel(str)
    def update_volts(self, str):
        self.st_volts.SetLabel(str)
    
    def update_amps(self, str):
        self.st_amps.SetLabel(str)
    
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
        if(self.top.con_flg):
            res, outstr = model.read_port_cmd(self.top)
            if res == 0 and outstr == '':
                res, outstr = model.read_port_cmd(self.top)
            if res == 0:
                if(outstr != ''):
                    self.init_ports(int(outstr))
                self.top.UpdateSingle("", 2)
                self.enable_controls(True)
                self.top.set_port_list(PORTS)
            else:
                self.top.print_on_log("No response from 3142,\
                                       please connect again!\n")
                self.enable_controls(False) 
      
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
  
    def init_ports(self, port):
        """
        During connect map the indication to the device status
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            port: update the port led 
        Returns:
            None
        """
        if(port == 0):
            self.port_led_update(port, False)
        else:
            self.port_led_update(port-1, True)
            self.btnStat[port-1] = True
   
    def read_param(self, param):
        if param == "voltage":
            self.get_voltage()
        elif param == "current":
            self.get_amps()
        
        else:
            self.top.print_on_log("Switch 3142 wouldn't support "+param+ "Command\n")