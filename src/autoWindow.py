#======================================================================
# (c) 2020  MCCI, Inc.
#----------------------------------------------------------------------
# Project : UI3141/3201 Application
# File    : loopWindow.py
#----------------------------------------------------------------------
# Loop Window for Switch 3141 and 3201
#======================================================================

#======================================================================
# IMPORTS
#======================================================================
import wx

import serialDev
import usbDev

from uiGlobals import *


#======================================================================
# COMPONENTS
#======================================================================

class AutoWindow(wx.Window):
    def __init__(self, parent, top):
        wx.Window.__init__(self, parent)

        self.SetBackgroundColour("White")

        #self.SetMinSize((200,200))

        self.parent = parent
        self.top = top

        self.pcnt = 0

        self.total_ports = 1

        self.period = 0
        self.duty = 0
        self.cycle = 0

        self.OnTime = 0
        self.OffTime = 0
        self.cycleCnt = 0

        self.On_flg = False

        self.start_flg = False

        self.usb_flg = False

        self.pulse_flg = False

        self.auto_flg = False

        self.dlist = []

        self.portno = 0

        self.timer = wx.Timer(self)
        self.timer_usb = wx.Timer(self)

        self.st_si   = wx.StaticText(self, -1, "Interval",style = wx.ALIGN_CENTER_VERTICAL | 
                                     wx.ALIGN_RIGHT, size=(60,-1))
        self.tc_ival   = wx.TextCtrl(self, ID_TC_INTERVAL, "1000", 
                                     size=(50,-1), style = wx.TE_CENTRE |
                                     wx.TE_PROCESS_ENTER,
                                     validator=NumericValidator(), 
                                     name="ON/OFF period")
        self.st_ms   = wx.StaticText(self, -1, "ms", size=(30,15), 
                                     style = wx.ALIGN_CENTER)
        self.st_duty   = wx.StaticText(self, -1, "Duty", 
                                       style = wx.ALIGN_CENTER_VERTICAL  | 
                                       wx.ALIGN_RIGHT, size=(60,-1))
        self.tc_duty   = wx.TextCtrl(self, ID_TC_DUTY, "50", size=(50,-1), 
                                     style = wx.TE_CENTRE | wx.TE_PROCESS_ENTER,
                                     validator=NumericValidator(), 
                                     name="ON/OFF period")
        self.st_ps   = wx.StaticText(self, -1, "%", size=(30,15), 
                                     style = wx.ALIGN_CENTER)

        self.btn_auto = wx.Button(self, ID_BTN_AUTO, "Auto", size=(60,25))

        self.tc_ival.SetMaxLength(5)
        self.tc_duty.SetMaxLength(2)
        
        self.tc_ival.SetToolTip(wx.ToolTip("Switching Interval. Min: 1 sec, "
                                           "Max: 60 sec"))
        self.btn_auto.SetToolTip(wx.ToolTip("On/Off each Port "
                                            "for a interval until stop"))

        sb = wx.StaticBox(self, -1, "Auto Mode")
        
        self.bs_vbox = wx.StaticBoxSizer(sb,wx.VERTICAL)

        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        self.hbox1.Add(self.st_si, 0, flag=wx.ALIGN_RIGHT | wx.LEFT | 
                       wx.ALIGN_CENTER_VERTICAL, border=20)
        self.hbox1.Add(self.tc_ival, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 10)
        self.hbox1.Add(self.st_ms, flag=wx.ALIGN_LEFT | 
                       wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.Add(self.btn_auto, 0, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 20)
        self.hbox2.Add(self.st_duty, flag=wx.LEFT |  wx.ALIGN_RIGHT |
                       wx.ALIGN_CENTER_VERTICAL, border=20)
        self.hbox2.Add(self.tc_duty,0, wx.ALIGN_CENTER | 
                       wx.LEFT, border=10)
        self.hbox2.Add(self.st_ps,0, wx.ALIGN_CENTER_VERTICAL)

        self.bs_vbox.AddMany([
            (0,10,0),
            (self.hbox1, 1, wx.EXPAND | wx.ALL),
            (0,10,0),
            (self.hbox2, 1, wx.EXPAND),
            (0,10,0)
            ])

        self.SetSizer(self.bs_vbox)
        self.bs_vbox.Fit(self)
        self.Layout()

        self.btn_auto.Bind(wx.EVT_BUTTON, self.OprAuto)
        self.Bind(wx.EVT_TIMER, self.TimerServ, self.timer)
        self.Bind(wx.EVT_TIMER, self.UsbTimer, self.timer_usb)

        self.enable_controls(True)


    # Event Handler for Auto Button
    def OprAuto(self, evt):
        if(self.auto_flg):
            self.stop_auto()
        else:
            if(self.usb_dly_warning() and self.onoff_dly_warning()):
                self.start_auto()

    # Start Auto Mode
    def start_auto(self):
        self.auto_flg = True
        self.btn_auto.SetLabel("Stop")
        self.top.set_mode(MODE_AUTO)
        self.Auto_strat_msg()
        if(self.timer.IsRunning() == False):
            self.timer.Start(int(self.get_interval()))

    # Stop Auto Mode
    def stop_auto(self):
        self.auto_flg = False
        self.btn_auto.SetLabel("Auto")
        self.top.set_mode(MODE_MANUAL)
        self.top.print_on_log("Auto Mode Stopped!\n")
        self.timer.Start(1)

    # Timer Event for Port ON/OFF in Auto Mode
    def TimerServ(self, evt):
        if self.top.con_flg:
            self.pulse_flg = True
            if(self.usb_flg == False):
                self.timer.Stop()
                self.pulse_flg = False
                if(self.On_flg):
                    self.port_on(self.pcnt+1, False)
                    self.On_flg = False
                    if self.auto_flg:
                        self.timer.Start(self.OffTime)
                else:
                    self.pcnt = self.pcnt + 1
                    if(self.pcnt >= self.total_ports):
                        self.pcnt = 0
                    self.port_on(self.pcnt+1, True)
                    if self.auto_flg:
                        self.timer.Start(self.OnTime)
                        self.On_flg = True

    # Port ON/OFF command send to Connected Device Module
    def port_on(self, portno, stat):
        self.top.port_on(portno, stat)
        if(self.top.get_delay_status()):
            self.keep_delay()

    # USB delay Timer start
    def keep_delay(self):
        self.usb_flg = True
        self.timer_usb.Start(int(self.top.get_enum_delay()))

    # Startup Message for Auto Mode
    def Auto_strat_msg(self):
        self.get_all_three()
        lmstr = "Auto Mode start : ON-Time = {d1} ms,".\
                format(d1=int(self.OnTime)) + \
                " OFF-Time = {d2} ms\n".\
                format(d2=int(self.OffTime)) 
        self.top.print_on_log(lmstr)

    # Calculate Port ON Time and OFF Time from Interval and Duty
    def get_all_three(self):
        self.interval = int(self.get_interval())
        self.duty = int(self.get_duty())

        self.OnTime = self.interval* (self.duty/100)
        self.OffTime = self.interval - self.OnTime

    # Send ON, OFF Time and Duty to USB Tree Window for USB delay validation
    def get_auto_param(self):
        self.get_all_three()
        return self.OnTime, self.OffTime, self.duty

    # Read Interval from Input text
    def get_interval(self):
        tival = self.tc_ival.GetValue()
        if(tival == ""):
            tival = "1000"
        ival = int(tival)
        if(ival < 1000):
            ival = 1000
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
            duty = "50"
        ival = int(duty)
        if(ival == 0):
            ival = 1
        
        self.tc_duty.SetValue(str(ival))
        return self.tc_duty.GetValue()

    # Set Port list to Combo box when Device gets connected
    def set_port_count(self, port):
        self.total_ports = port

    # USB Tree View Changes Timer Service
    def UsbTimer(self, e):
        self.timer_usb.Stop()
        try:
            usbDev.get_tree_change(self.top)
        except:
            self.top.print_on_usb("USB Read Error!")
        self.usb_flg = False
        
        if(self.auto_flg == True & self.pulse_flg == True):
            self.timer.Start(1)

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

    # Check ON/OFF Time interval if it is < 500 msec popup a warning message
    def onoff_dly_warning(self):
        self.get_all_three()
        if (self.OnTime < 500 or self.OffTime < 500):
            title = ("Port ON/OFF time warning!")
            msg = ("For Device safety, it is recommended to keep "
                       "Port ON/OFF time > 500 msec."
                       "\nClick Yes if you wish to continue"
                       "\nClick No to exit the Auto mode")
            dlg = wx.MessageDialog(self, msg, title, wx.NO|wx.YES)
            if(dlg.ShowModal() == wx.ID_YES):
                return True
            else:
                return False
        return True

    # Enable/Disable widgets when mode changed
    def update_controls(self, mode):
        if mode == MODE_MANUAL:
            self.enable_controls(True)
        else:
            self.enable_controls(False)

    # Enable/Disable Auto Controls
    def enable_controls(self, stat):
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
        if not self.top.con_flg:
            self.btn_auto.Disable()

    # Called when device get disconnected
    def device_disconnected(self):
        if self.auto_flg:
            self.stop_auto()
