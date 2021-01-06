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

import serialDev
import usbDev

from uiGlobals import *

PORTS = 4

#======================================================================
# COMPONENTS
#======================================================================

class Dev3201Window(wx.Window):
    def __init__(self, parent, top):
        wx.Window.__init__(self, parent)
        self.SetBackgroundColour("White")

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

        self.timer = wx.Timer(self)
        self.timer_usb = wx.Timer(self)
        self.timer_va = wx.Timer(self)
        
        self.SetMinSize((290, 190))
        
        self.st_p1 = wx.StaticText(self, -1, "Port 1", size = (-1,-1))
        self.st_p2 = wx.StaticText(self,-1, "Port 2", size = (-1,-1))
        self.st_p3 = wx.StaticText(self, -1, "Port 3", size = (-1,-1))
        self.st_p4 = wx.StaticText(self, -1, "Port 4", size = (-1,-1))

        self.picf = wx.Bitmap ("./icons/btn_off.png", wx.BITMAP_TYPE_ANY)
        self.picn = wx.Bitmap ("./icons/btn_on.png", wx.BITMAP_TYPE_ANY)
        self.btn_p1 = wx.BitmapButton(self, 0, self.picf, size= (-1,-1))
        self.btn_p2 = wx.BitmapButton(self, 1, self.picf, size= (-1,-1))
        self.btn_p3 = wx.BitmapButton(self, 2, self.picf, size= (-1,-1))
        self.btn_p4 = wx.BitmapButton(self, 3, self.picf, size= (-1,-1))

        self.st_ss   = wx.StaticText(self, -1, "SuperSpeed")
        self.rbtn_ss1 = wx.RadioButton(self, ID_RBTN_SS1, "Enable", 
                                       style=wx.RB_GROUP | wx.ALIGN_CENTER)
        self.rbtn_ss0 = wx.RadioButton(self, ID_RBTN_SS0, "Disable")
        
        #self.st_si   = wx.StaticText(self, -1, "Interval")

        self.stlbl_volts = wx.StaticText(self, -1, "Bus Voltage :", size=(-1,-1))
        self.st_volts   = wx.StaticText(self, -1, " --- ", 
                                        style = wx.ALIGN_CENTER_VERTICAL)
        self.stlbl_amps = wx.StaticText(self, -1, "Bus Current:", size=(-1,-1))
        self.st_amps   = wx.StaticText(self, -1, " --- ", 
                                       style = wx.ALIGN_CENTER_VERTICAL, size=(-1,-1))
        
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

        #self.hbox1.Add(self.hboxs1, flag=wx.ALIGN_CENTER_VERTICAL )
        #self.hbox1.Add(0,1,0)
        #self.hbox1.Add(self.hboxs2, flag=wx.LEFT, border=20 )
        #self.hboxs2.Add(0,10,0)
        
        self.hbox3.Add(self.st_ss,0 , flag=wx.ALIGN_LEFT | wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 
                       border=20 )
        self.hbox3.Add(self.rbtn_ss1, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 20)
        self.hbox3.Add(self.rbtn_ss0, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT,
                       border=18)

        self.hbox5.Add(self.stlbl_volts, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border=20 )
        self.hbox5.Add(self.st_volts, flag=wx.LEFT |
                       wx.ALIGN_CENTER_VERTICAL)
        self.hbox5.Add(self.stlbl_amps, flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL |
                       wx.ALIGN_RIGHT, border=20)
        self.hbox5.Add(self.st_amps, flag=wx.LEFT| wx.ALIGN_CENTER_VERTICAL)
       
        sb = wx.StaticBox(self, -1, "Model 3201")
        self.vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)

        self.vbox.AddMany([
            (0,10,0),
            (self.hboxs1, 1, wx.EXPAND),
            (0,10,0),
            (self.hboxs2, 1, wx.EXPAND),
            (0,10,0),
            (self.hbox3, 1, wx.EXPAND),
            (self.hbox5, 1, wx.EXPAND)
            ])
       
        self.SetSizer(self.vbox)
        self.SetAutoLayout(True)
        self.vbox.Fit(self)
        self.Layout()

        
        self.Bind(wx.EVT_TIMER, self.UsbTimer, self.timer_usb)
        self.Bind(wx.EVT_TIMER, self.VaTimer, self.timer_va)
        
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
        
        self.enable_controls(False)


    # Event Handler for 4 Port Switches
    def OnOffPort (self, e):
        co = e.GetEventObject()
        cbi = co.GetId()
        if self.top.mode == MODE_MANUAL and not self.usb_flg:
            self.port_on_manual(cbi)
    
    # Event Handler for Volts Button
    def VoltsCmd(self, evt):
        self.get_voltage()

    def get_voltage(self):
        strin = "--"
        res, outstr = serialDev.send_volts_cmd(self.top.devHand)
        if res < 0:
            outstr = "Comm Error\n"
        else:
            outstr.replace(' ', '')
            vstr = outstr.split('\n')
            iv = int(vstr[0])
            fv = iv/100
            outstr = str(fv) + "V"
            self.update_volts(outstr)
        self.top.print_on_log("Volts : "+outstr+"\n")

    # Event Handler for Amps Button
    def AmpsCmd(self, evt):
        self.get_amps()

    def get_amps(self):
        strin = "--"
        res, outstr = serialDev.send_amps_cmd(self.top.devHand)
        if res < 0:
            outstr = "Comm Error\n"
        else:
            outstr.replace(' ', '')
            astr = outstr.split('\n')
            sstr = astr[0][:1]
            rstr = astr[0][1:]
            ia = int(rstr) 
            fa =  ia/100 
            ss = ""
            if(sstr == '1'):
                ss = "-"
            outstr = ss + str(fa) + "A"

            self.update_amps(outstr)
        self.top.print_on_log("Amps : "+outstr+"\n")

    # Event handler for Speed change Radio buttons
    def PortSpeedChanged(self, e):
        rb = e.GetEventObject()
        id = rb.GetId()

        if id == ID_RBTN_SS1:
            self.speed_cmd(1)
        elif id == ID_RBTN_SS0:
            self.speed_cmd(0)

    # Timer Event for USB Tree View Changes
    def UsbTimer(self, e):
        self.timer_usb.Stop()
        try:
            usbDev.get_tree_change(self.top)
        except:
            self.top.print_on_usb("USB Read Error!")
        self.usb_flg = False

    # Timer Event for USB Tree View Changes
    def VaTimer(self, e):
        self.timer_va.Stop()
        self.get_voltage()
        self.get_amps()

    # Port ON in Manual Mode
    def port_on_manual(self, port):
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

        self.enable_ss_controls(port, stat)

    # Port ON Command
    def port_on_cmd(self, pno):
        cmd = 'port'+' '+str(pno)+'\r\n'
        res, outstr = serialDev.send_port_cmd(self.top.devHand, cmd)
        if res == 0:
            outstr = outstr.replace('p', 'P')
            outstr = outstr.replace('1', '1 ON')
            outstr = outstr.replace('2', '2 ON')
            outstr = outstr.replace('3', '3 ON')
            outstr = outstr.replace('4', '4 ON')
            outstr = outstr[:-2] + "; Other Ports are OFF\n"
            self.top.print_on_log(outstr)
        
    # Port OFF Command   
    def port_off_cmd(self, pno):
        cmd = 'port'+' '+'0'+'\r\n'
        res, outstr = serialDev.send_port_cmd(self.top.devHand, cmd)
        if res == 0:
            outstr = outstr.replace('p', 'P')
            outstr = outstr.replace('0', ""+str(pno)+" OFF")
            self.top.print_on_log(outstr)
    
    # Enable/Disable the Speed Button based on Ports
    def enable_ss_controls(self, port, stat):
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

    # Add Delay in Port ON/OFF based on USB option
    def keep_delay(self):
        self.usb_flg = True
        self.timer_usb.Start(int(self.top.get_enum_delay()))

    # Update the Port Indication
    def port_led_update(self, port, stat):
        if(stat):
            for i in range(4):
                if(i == port):
                    self.rbtn[port].SetBitmap(self.picn)
                else:
                    self.rbtn[i].SetBitmap(self.picf)
        else:
            for i in range(4):
                self.rbtn[i].SetBitmap(self.picf)

    # Called when changing the Mode - Called by set_mode
    def update_controls(self, mode):
        if mode == MODE_MANUAL:
            self.enable_controls(True)
        else:
            self.enable_controls(False)

    # Enable/Disable All Widgets in UI3201
    def enable_controls(self, stat):
        if not self.top.con_flg:
            stat = False
        self.enable_port_controls(stat)
        self.enable_speed_controls(stat)
        self.enable_va_controls(stat)
        
    # Enable/Diasble 4 Port Switches
    def enable_port_controls(self, stat):
        stat = self.top.con_flg
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

    # Enable/Disale Speed controls
    def enable_speed_controls(self, stat):
        if(stat):
            self.rbtn_ss0.Enable()
            self.rbtn_ss1.Enable()
        else:
            self.rbtn_ss0.Disable()
            self.rbtn_ss1.Disable()

    # Enable/Disable Volt/Amp Controls
    def enable_va_controls(self, stat):
        pass
        '''if(stat):
            self.btn_amps.Enable()
            self.btn_volts.Enable()
        else:
            self.btn_amps.Disable()
            self.btn_volts.Disable()'''

    # Print the Voltage level in Label
    def update_volts(self, str):
        self.st_volts.SetLabel(str)

    # Print the Amps level in Label
    def update_amps(self, str):
        self.st_amps.SetLabel(str)

    # Speed change command to 3141 Device
    def speed_cmd(self,val):
        cmd = 'superspeed'+' '+str(val)+'\r\n'
        print("\nSpeedCmd: ",cmd)
        res, outstr = serialDev.send_port_cmd(self.top.devHand,cmd)
        print("\nSpeed Result: ", res, outstr)
        if res == 0:
            outstr = outstr.replace('s', 'S')
            outstr = outstr.replace('1', 'Enabled')
            outstr = outstr.replace('0', 'Disabled')
        self.top.print_on_log(outstr)
    
    # Called by Com Window When Device Connected
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
                self.top.print_on_log("No response from 3201, please connect again!\n")
                self.enable_controls(False)

    def device_disconnected(self):
        if self.auto_flg:
            self.auto_flg = False
            self.btn_auto.SetLabel("Start")
            self.timer.Stop()

    # During connect map the indication to the device status
    def init_ports(self, port):
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