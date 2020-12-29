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

        self.SetMinSize((280, 270))

        sb = wx.StaticBox(self, -1, "Model 2101")

        self.vbox = wx.StaticBoxSizer(sb,wx.VERTICAL)

        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxs1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox5 = wx.BoxSizer (wx.HORIZONTAL)
        
        self.st_port = wx.StaticText(self, -1, "Port", size = (40, 15)) 
        self.picf = wx.Bitmap ("btn_off.png", wx.BITMAP_TYPE_ANY)
        self.picn = wx.Bitmap ("btn_on.png", wx.BITMAP_TYPE_ANY)
        self.btn_p1 = wx.BitmapButton(self, 0, self.picf,size= (55,20))
        self.st_ss   = wx.StaticText(self, -1, "SuperSpeed")
        self.rbtn_ss1 = wx.RadioButton(self, ID_RBTN_SS1, "Enable", 
                                       style=wx.RB_GROUP)
        self.rbtn_ss0 = wx.RadioButton(self, ID_RBTN_SS0, "Disable")
        
        self.st_si   = wx.StaticText(self, -1, "Interval")
        self.tc_ival   = wx.TextCtrl(self, ID_TC_INTERVAL, "1000", 
                                     size=(50,-1), style = wx.TE_CENTRE |
                                     wx.TE_PROCESS_ENTER,
                                     validator=NumericValidator(), 
                                     name="ON/OFF period")
        self.st_ms   = wx.StaticText(self, -1, "ms", size=(30,15), 
                                     style = wx.ALIGN_CENTER)
        self.st_duty   = wx.StaticText(self, -1, "Duty ", size=(50,15), 
                                       style = wx.ALIGN_CENTER)
        self.tc_duty   = wx.TextCtrl(self, ID_TC_DUTY, "50", size=(50,-1), 
                                     style = wx.TE_PROCESS_ENTER,
                                     validator=NumericValidator(), 
                                     name="ON/OFF period")
        self.st_ps   = wx.StaticText(self, -1, "%", size=(30,15), 
                                     style = wx.ALIGN_CENTER)
        self.btn_auto = wx.Button(self, ID_BTN_AUTO, "Auto", size=(50,25))

        self.tc_ival.SetMaxLength(5)
        
        self.tc_ival.SetToolTip(wx.ToolTip("Switching Interval. Min: 1 sec, "
                                           "Max: 60 sec"))
        self.btn_auto.SetToolTip(wx.ToolTip("Switch between Port1 and Port2 "
                                            "for a interval until stop"))
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
        self.hbox2.Add(self.rbtn_ss1, flag=wx.ALIGN_LEFT | wx.LEFT, border = 20)
        self.hbox2.Add(self.rbtn_ss0, flag=wx.RIGHT | wx.LEFT |
                       wx.ALIGN_RIGHT, border=18)

        self.hbox4.Add(self.st_si, 0, flag=wx.ALIGN_LEFT | wx.LEFT | 
                       wx.ALIGN_CENTER_VERTICAL, border=20)
        self.hbox4.Add(self.tc_ival, flag=wx.ALIGN_CENTER_VERTICAL | 
                       wx.LEFT, border = 10)
        self.hbox4.Add(self.st_ms, flag=wx.ALIGN_LEFT | 
                       wx.ALIGN_CENTER_VERTICAL)
        self.hbox5.Add(self.st_duty, flag=wx.ALIGN_LEFT | wx.LEFT | 
                       wx.ALIGN_CENTER_VERTICAL, border=20 )
        self.hbox5.Add(self.tc_duty,0, wx.ALIGN_CENTER | 
                         wx.ALIGN_CENTER_VERTICAL)
        self.hbox5.Add(self.st_ps,0, wx.ALIGN_CENTER_VERTICAL)

        self.hbox4.Add(self.btn_auto, 0, flag =  wx.ALIGN_LEFT | wx.LEFT | 
                       wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL,
                       border = 20)
        self.tog_flg = False
        self.pulse_flg = False
        self.timer = wx.Timer(self)
        self.timer_usb = wx.Timer(self)

        self.vbox.AddMany([
            (10,20,0),
            (self.hbox1, 0, wx.EXPAND | wx.ALL),
            (0,50,0),
            (self.hbox2, 0, wx.EXPAND),
            (0,50,0),
            (self.hbox4, 0, wx.EXPAND),
            (10,10,0),
            (self.hbox5, 0, wx.EXPAND),
            (0,20,0)
            ])
        self.btn_auto.Bind(wx.EVT_BUTTON, self.OprAuto)
        
        self.Bind(wx.EVT_TIMER, self.TimerServ, self.timer)
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

    # Event Handler for Auto Button
    def OprAuto(self, evt):
        if(self.auto_flg):
            self.stop_auto()
        else:
            if(self.usb_dly_warning()):
                self.start_auto()

    # Event Handler for Port Speed Change
    def PortSpeedChanged(self, e):
        rb = e.GetEventObject()
        id = rb.GetId()
        
        if(id >= ID_RBTN_SS0):
            id = id - ID_RBTN_SS0
            self.speed_cmd(id)

    # Timer Event for Port ON/OFF in Auto Mode    
    def TimerServ(self, evt):
        if(self.top.con_flg):
            self.pulse_flg = True
            if(self.usb_flg == False):
                self.timer.Stop()
                self.pulse_flg = False
                if(self.On_flg):
                    self.port_on(1, False)
                    self.On_flg = False
                    if self.auto_flg:
                        self.timer.Start(self.OffTime)
                else:
                    self.port_on(1, True)
                    if self.auto_flg:
                        self.timer.Start(self.OnTime)
                        self.On_flg = True

    # Timer Event for USB Tree View Changes  
    def UsbTimer(self, e):
        self.timer_usb.Stop()
        try:
            usbDev.get_tree_change(self.top)
        except:
            self.top.print_on_usb("USB Read Error!")
        self.usb_flg = False
        if(self.auto_flg == True & self.pulse_flg == True):
            self.timer.Start(1)
        else:
            #self.top.enable_enum_controls(True)
            #self.btn_auto.Enable()
            #self.top.enable_start()
            pass
    
    # Startup Message for Auto Mode            
    def Auto_strat_msg(self):
        self.get_all()
        lmstr = "Auto Mode start : ON-Time = {d1} ms,".\
                format(d1=int(self.OnTime)) + \
                " OFF-Time = {d2} ms\n".\
                format(d2=int(self.OffTime)) 
        self.top.print_on_log(lmstr)
    

    # Port ON in Manual Mode
    def port_on_manual(self, port):
        for i in range (len (self.rbtn)):
            if(port == i):
                self.btnStat[port] = not self.btnStat[port]
                self.port_on(port+1, self.btnStat[port])
            else:
                self.btnStat[i] = False

    # Check USB delay while starting Auto Mode  
    def usb_dly_warning(self):
        if(int(self.get_interval()) < int(self.top.get_enum_delay())):
            if(self.top.get_delay_status()):
                title = ("USB device tree delay warning!")
                msg = ("USB device tree delay should be less than "
                       "the Port Switching Interval."
                       "\nClick Yes to continue without "
                       "USB device tree changes"
                       "\nClick No to exit the Auto mode")
                dlg = wx.MessageDialog(self, msg, title, wx.NO|wx.YES)
                if(dlg.ShowModal() == wx.ID_YES):
                    self.top.disable_usb_scan()
                    return True
                else:
                    return False
        return True

    # Port ON/OFF in Auto and Loop Mode, while in Loop Mode Command received 
    # from Loop Window
    def port_on(self, port, stat):
        if(stat):
            self.port_on_cmd(port)
        else:
            self.port_off_cmd(port)
        self.port_led_update(port-1, stat)

        if(self.top.mode != MODE_LOOP):
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
        self.enable_auto_controls(stat)
            
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

    # Enable/Disable Auto Controls
    def enable_auto_controls(self, stat):
        if(stat):
            self.btn_auto.Enable()
            self.tc_ival.Enable()
            self.tc_duty.Enable()
        else:
            if self.top.mode != MODE_AUTO:
                self.btn_auto.Disable()
            self.tc_ival.SetFocus()
            self.tc_ival.Disable()
            self.tc_duty.Disable()

    # Calculate Port ON Time and OFF Time from Interval and Duty
    def get_all(self):
        self.interval = int(self.get_interval())
        self.duty = int(self.get_duty())

        self.OnTime = self. interval* (self.duty/100)
        self.OffTime = self. interval - self.OnTime

    # Read Interval from Input text
    def get_interval(self):
        tival = self.tc_ival.GetValue()
        if(tival == ""):
            tival = "50"
        ival = int(tival)
        if(ival < 50):
            ival = 50
        elif(ival > 60000):
            ival = 60000

        self.tc_ival.SetValue(str(ival))
        return self.tc_ival.GetValue()

    # Interval override by USB Tree View Changes Delay
    def set_interval(self, strval):
        self.tc_ival.SetValue(strval)

    # Read Duty from Input text
    def get_duty(self):
        duty = self.tc_duty.GetValue()
        if (duty == ""):
            duty = "0"
        return duty
    
    # Start Auto Mode
    def start_auto(self):
        self.auto_flg = True
        self.btn_auto.SetLabel("Stop")
        self.top.set_mode(MODE_AUTO)
        self.Auto_strat_msg()
        if(self.timer.IsRunning() == False):
            self.tog_flg = False
            self.timer.Start(int(self.get_interval()))

    # Stop Auto Mode
    def stop_auto(self):
        self.auto_flg = False
        self.btn_auto.SetLabel("Auto")
        self.top.set_mode(MODE_MANUAL)
        self.top.print_on_log("Auto Mode Stopped!\n")
        self.timer.Start(1)

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
        
