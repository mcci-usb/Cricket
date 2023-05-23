##############################################################################
# 
# Module: dev3201Window.py
#
# Description:
#     Device specific functions and UI for interfacing Model 3201 with GUI
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
#     V4.0.0 Wed May 25 2023 17:00:00   Seenivasan V
#       Module created
##############################################################################
# Lip imports
import wx

# Built-in imports
import os
import time

# Own modules
import devControl as model
import thControl
from uiGlobals import *

PORTS = 4

##############################################################################
# Utilities
##############################################################################
class Dev3201Window(wx.Window):
    """
    A class dev3201Window with init method

    The dev3201Window navigate to Super speed and High speed enable 
    or disable options.
    """
    def __init__(self, parent, top, portno):
        """
        Device specific functions and UI for interfacing Model 3201 with GUI 
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
        self.SetBackgroundColour("White")

        self.parent = parent
        self.top = top
        self.swid = portno

        self.swtitle = "3201"
        if(len(portno)):
            self.swtitle += " ("+portno+")"

        self.fv = None
        self.fa = None

        self.con_flg = None

        self.pcnt = 0
        self.rport = 0

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
        self.timer_va = wx.Timer(self)
        self.timer_vu = wx.Timer(self)
        self.timer_safe = wx.Timer(self)
        self.timer_port = wx.Timer(self)
        # Call this to give the sizer a minimal size.
        self.SetMinSize((290, 190))
        
        self.st_p1 = wx.StaticText(self, -1, "Port 1", size = (-1,-1))
        self.st_p2 = wx.StaticText(self,-1, "Port 2", size = (-1,-1))
        self.st_p3 = wx.StaticText(self, -1, "Port 3", size = (-1,-1))
        self.st_p4 = wx.StaticText(self, -1, "Port 4", size = (-1,-1))

        base = os.path.abspath(os.path.dirname(__file__))
        self.picf = wx.Bitmap (base+"/icons/"+IMG_BTN_OFF, wx.BITMAP_TYPE_ANY)
        self.picn = wx.Bitmap (base+"/icons/"+IMG_BTN_ON, wx.BITMAP_TYPE_ANY)

        self.btn_p1 = wx.BitmapButton(self, 0, self.picf, size= (-1,-1))
        self.btn_p2 = wx.BitmapButton(self, 1, self.picf, size= (-1,-1))
        self.btn_p3 = wx.BitmapButton(self, 2, self.picf, size= (-1,-1))
        self.btn_p4 = wx.BitmapButton(self, 3, self.picf, size= (-1,-1))

        self.st_ss   = wx.StaticText(self, -1, "SuperSpeed")
        self.rbtn_ss1 = wx.RadioButton(self, ID_RBTN_SS1, "Enable", 
                                       style=wx.RB_GROUP | wx.ALIGN_CENTER)
        self.rbtn_ss0 = wx.RadioButton(self, ID_RBTN_SS0, "Disable")
        
        #self.st_si   = wx.StaticText(self, -1, "Interval")

        self.stlbl_volts = wx.StaticText(self, -1, "Bus Voltage :", 
                                                   size=(-1,-1))
        self.st_volts   = wx.StaticText(self, -1, " --- ", 
                                        style = wx.ALIGN_CENTER_VERTICAL)
        self.stlbl_amps = wx.StaticText(self, -1, "Bus Current:",
                                                   size=(-1,-1))
        self.st_amps   = wx.StaticText(self, -1, " --- ", 
                                       style = wx.ALIGN_CENTER_VERTICAL, 
                                       size=(-1,-1))
        # BoxSizer fixed with Horizontal
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxi = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox6 = wx.BoxSizer(wx.HORIZONTAL)

        self.hboxp1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxp2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxp3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxp4 = wx.BoxSizer(wx.HORIZONTAL)

        self.hboxs1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxs2 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.hboxp1.Add(self.st_p1,0, flag=wx.LEFT | 
                        wx.ALIGN_CENTER_VERTICAL, border=0)
        self.hboxp1.Add(self.btn_p1, flag=wx.LEFT, border = 10)
        
        self.hboxp2.Add(self.st_p2, 0, flag= wx.ALIGN_CENTER_VERTICAL | 
                        wx.LEFT, border = 0)
        self.hboxp2.Add(self.btn_p2, flag=wx.LEFT,  border = 10)
        
        self.hboxp3.Add(self.st_p3, flag=wx.ALIGN_LEFT | wx.LEFT | 
                        wx.ALIGN_CENTER_VERTICAL, border=0)
        self.hboxp3.Add(self.btn_p3, flag=wx.LEFT,  border = 10)
    
        self.hboxp4.Add(self.st_p4, 0, flag=wx.ALIGN_LEFT | 
                        wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 0)
        self.hboxp4.Add(self.btn_p4, flag=wx.LEFT,  border = 10)

        self.hboxs1.Add(self.hboxp1, flag=wx.LEFT, border=20)
        self.hboxs1.Add((0,0), 1, wx.EXPAND)
        self.hboxs1.Add(self.hboxp2, flag=wx.RIGHT , border=20)

        self.hboxs2.Add(self.hboxp3, flag=wx.LEFT, border=20)
        self.hboxs2.Add((0,0), 1, wx.EXPAND)
        self.hboxs2.Add(self.hboxp4, flag=wx.RIGHT, border=20)

        self.hbox3.Add(self.st_ss,0 , flag=wx.ALIGN_LEFT | wx.LEFT 
                       | wx.ALIGN_CENTER_VERTICAL, 
                       border=20 )
        self.hbox3.Add(self.rbtn_ss1, flag=wx.ALIGN_CENTER_VERTICAL | 
                                                 wx.LEFT, border = 20)
        self.hbox3.Add(self.rbtn_ss0, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT,
                       border=18)

        self.hbox5.Add(self.stlbl_volts, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border=20 )
        self.hbox5.Add(self.st_volts, flag=wx.LEFT |
                       wx.ALIGN_CENTER_VERTICAL)
        self.hbox5.Add(self.stlbl_amps, flag=wx.LEFT | 
                       wx.ALIGN_CENTER_VERTICAL |
                       wx.ALIGN_LEFT, border=20)
        self.hbox5.Add(self.st_amps, flag=wx.LEFT| wx.ALIGN_CENTER_VERTICAL)
       
        self.sb = wx.StaticBox(self, -1, self.swtitle)
        self.vbox = wx.StaticBoxSizer(self.sb, wx.VERTICAL)

        self.vbox.AddMany([
            (0,10,0),
            (self.hboxs1, 1, wx.EXPAND),
            (0,10,0),
            (self.hboxs2, 1, wx.EXPAND),
            (0,10,0),
            (self.hbox3, 1, wx.EXPAND),
            (self.hbox5, 1, wx.EXPAND)
            ])
        # Set size of frame
        self.SetSizer(self.vbox)
        self.SetAutoLayout(True)
        self.vbox.Fit(self)
        self.Layout()

        # Bind the timer event to handler
        self.Bind(wx.EVT_TIMER, self.UsbTimer, self.timer_usb)
        self.Bind(wx.EVT_TIMER, self.VaTimer, self.timer_va)
        self.Bind(wx.EVT_TIMER, self.GraphTimer, self.timer_vu)
        self.Bind(wx.EVT_TIMER, self.SafeTimer, self.timer_safe)
        self.Bind(wx.EVT_TIMER, self.PortOnTimer, self.timer_port)
        
        # Bind the button event to handler
        self.Bind(wx.EVT_RADIOBUTTON, self.PortSpeedChanged)
        self.Bind(wx.EVT_BUTTON, self.OnOffPort, self.btn_p1)
        self.Bind(wx.EVT_BUTTON, self.OnOffPort, self.btn_p2)
        self.Bind(wx.EVT_BUTTON, self.OnOffPort, self.btn_p3)
        self.Bind(wx.EVT_BUTTON, self.OnOffPort, self.btn_p4)

        self.rbtn = []
        self.rbtn.append(self.btn_p1)
        self.rbtn.append(self.btn_p2)
        self.rbtn.append(self.btn_p3)
        self.rbtn.append(self.btn_p4)

        self.btnStat = [False, False, False, False]
        
        self.con_flg = True
        self.enable_controls(True)

        self.timer_vu.Start(50)

    def update_cport(self, portno):
        self.swtitle = "3201"
        if(len(portno)):
            self.swtitle += " ("+portno+")"
        self.swid = portno
        self.sb.SetLabel(self.swtitle)
        self.Layout()

    def OnOffPort (self, e):
        """
        Event Handler for port On/Off method 

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            e:The event parameter in the dev3201Window method is an 
            object specific to a particular event type.
            event hanlder for OnOffPort switch
        Returns:
            None
        """
        co = e.GetEventObject()
        cbi = co.GetId()
        if self.top.mode == MODE_MANUAL and not self.usb_flg:
            self.port_on_manual(cbi)
    
    def VoltsCmd(self, evt):
        """
        Send the device voltage command

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            evt:The event parameter in the dev3201Window method is an 
            object specific to a particular event type.
            Event Handler for Volts Button
        Returns:
            None
        """
        self.get_voltage()

    def get_voltage(self):
        """
        Get device voltage and display 

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        strin = "***"
        res, outstr = model.send_volts_cmd(self.top, self.swid)
        if res < 0:
            outstr = "Comm Error\n"
        else:
            outstr.replace(' ', '')
            if outstr != "":
                vstr = outstr.split('\n')
                iv = int(vstr[0])
                self.fv = iv/100
                outstr = str(self.fv) + "V"
                self.update_volts(outstr)
        # self.top.print_on_log("Volts : "+outstr+"\n")


    def AmpsCmd(self, evt):
        """
        Send the device amps command

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            evt:The event parameter in the dev3201Window method is an 
            object specific to a particular event type.
            Event Handler for Amps Button
        Returns:
            None
        """
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
                sstr = astr[0][:1]
                rstr = astr[0][1:]
                ia = int(rstr) 
                self.fa =  ia/100 
                ss = ""
                if(sstr == '1'):
                    ss = "-"
                outstr = ss + str(self.fa) + "A"
            self.update_amps(outstr)
        # self.top.print_on_log("Amps : "+outstr+"\n")
    
    def PortSpeedChanged(self, e):
        """
        Event handler, port speed change update

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            e:The event parameter in the dev3201Window method is an 
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

        if id == ID_RBTN_SS1:
            # Return superspeed
            self.speed_cmd(1)
        elif id == ID_RBTN_SS0:
            # Returs highspeed
            self.speed_cmd(0)
    
    def UsbTimer(self, e):
        """
        Timer Event for USB Tree View Changes

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            e:The event parameter in the dev3201 method is an 
            object specific to a particular event type.
            Timer Event for USB Tree View Changes
        Returns:
            None
        """
        self.timer_usb.Stop()
        try:
            thControl.get_tree_change(self.top)
        except:
            # to print on usb tree view change "USB Read Error!"
            self.top.print_on_usb("USB Read Error!")
        self.usb_flg = False
    
    def VaTimer(self, e):
        
        self.timer_va.Stop()
        # Check voltage
        self.get_voltage()
        # Check amps
        self.get_amps()

    def GraphTimer(self, e):
        """
        once start the volts and amps plotting timer start from here.

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            e: event handling of volts and amps.
        Returns:
            None
       """
        self.timer_vu.Stop()
        # Check voltage
        if(self.top.vgraph):
            self.get_voltage()
            self.top.vdata = self.fv
        
        # Check amps
        if(self.top.agraph):
            self.get_amps()
            self.top.adata = self.fa
        
        self.timer_vu.Start()
      
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
                   self.timer_va.Start(3000)
                else:
                   self.timer_va.Stop()
            else:
                self.btnStat[i] = False
    
    def SafeTimer(self, e):
        self.timer_safe.Stop()
        self.usb_flg = False

    def PortOnTimer(self, e):
        self.timer_port.Stop()
        self.port_on_cmd(self.rport)


    def port_on(self, port, stat):
        """
        Port ON/OFF in Auto and Loop Mode, while in Loop Mode
        Command received from Loop Window
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
            # Here port on command
            else:
                self.port_on_cmd(port)
        else:
            # Here port off command
            self.port_off_cmd(port)
        

        if(self.top.mode == MODE_MANUAL):
            if(self.top.get_delay_status()):
                self.keep_delay()
            else:
                self.timer_safe.Start(1000)
                self.usb_flg = True

        self.enable_ss_controls(port, stat)
    
    def port_on_cmd(self, pno):
        """
        Sending the device Port ON Command

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
            outstr = outstr.replace('3', '3 ON')
            outstr = outstr.replace('4', '4 ON')
            outstr = outstr[:-2] + "; Other Ports are OFF\n"
            self.top.print_on_log(outstr)
            self.port_led_update(pno-1, True)


    def port_off_cmd(self, pno):
        """
        Sendng the Port OFF Command

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
            self.top.print_on_log(outstr)
            self.port_led_update(pno-1, False)

    def set_speed(self, speed):
        """
        Send device Speed command to 3201
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            val: sending the speed command
        Returns:
            None
        """
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

    
    def enable_ss_controls(self, port, stat):
        """
        Enable/Disale Superspeed and Highspeed controls

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            port:ports update
            stat:updated the status for superspeed and highspeed  
            enable/disable
        Returns:
            None
        """
        if self.top.mode == MODE_MANUAL:
            if stat:
                if(port > 2):
                    self.rbtn_ss0.Disable()
                    self.rbtn_ss1.Disable()
                else:
                    self.rbtn_ss0.Enable()
                    self.rbtn_ss1.Enable() 
            else:
                self.rbtn_ss0.Enable()
                self.rbtn_ss1.Enable()

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
        Update the Port Led On/Off Indication

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
            for i in range(4):
                if(i == port):
                    self.rbtn[port].SetBitmap(self.picn)
                else:
                    self.rbtn[i].SetBitmap(self.picf)
        else:
            for i in range(4):
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
        Enable/Disable All Widgets of 3201,
        usb device speed and update volts,amps.

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
        self.enable_va_controls(stat)
        self.read_port_status(stat)
    
    def enable_port_controls(self, stat):
        """
        Enable/Diasble Port controls 
        
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
            self.btn_p3.Enable()
            self.btn_p4.Enable()
        else:
            self.btn_p1.Disable()
            self.btn_p2.Disable()
            self.btn_p3.Disable()
            self.btn_p4.Disable()
    
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
    
    def enable_va_controls(self, stat):
        """
        Enable/Disable Volt/Amp Controls

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            stat: updated the status for volts and amps
        Returns:
            None
        """
        pass
        '''if(stat):
            self.btn_amps.Enable()
            self.btn_volts.Enable()
        else:
            self.btn_amps.Disable()
            self.btn_volts.Disable()'''
    
    def update_volts(self, str):
        """
        update the voltage level of Port

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            str: update in Volts
        Returns:
            None
        """
        # SetLabel as volts
        self.st_volts.SetLabel(str)
    
    def update_amps(self, str):
        """
        update the Amps level of Port

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            str: updated in Amps
        Returns:
            None
        """
        # SetLabel as Amps
        self.st_amps.SetLabel(str)

    # Speed change command to 3201 Device
    def speed_cmd(self,val):
        """
        Send device Speed command to 3201
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            val: sending the speed command
        Returns:
            None
        """
        speed = "HS"
        if(val == 1):
            speed = "SS"
        res, outstr = model.send_speed_cmd(self.top, self.swid+","+speed)

        # cmd = 'superspeed'+' '+str(val)+'\r\n'
        # res, outstr = model.send_port_cmd(self.top, cmd)
        if res == 0:
            outstr = outstr.replace('s', 'S')
            outstr = outstr.replace('1', 'Enabled')
            outstr = outstr.replace('0', 'Disabled')
        self.top.print_on_log(outstr)
    
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
        if(self.con_flg):
            time.sleep(1)
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
                self.top.print_on_log("No response from 3201,\
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
        During device connect, map the indication to the device status
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
            self.enable_ss_controls(port, False)
        else:
            self.port_led_update(port-1, True)
            self.btnStat[port-1] = True
            self.enable_ss_controls(port, True)
        if(port > 2):
            self.rbtn_ss0.SetValue(True)
        else:
            self.rbtn_ss1.SetValue(True)

    def read_param(self, param):
        if param == "voltage":
            self.get_voltage()
        elif param == "current":
            self.get_amps()
        else:
            self.top.print_on_log("Switch 3201 wouldn't support "+param+ "Command\n")