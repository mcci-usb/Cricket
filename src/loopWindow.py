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
import control2101 as d2101


#======================================================================
# COMPONENTS
#======================================================================

class LoopWindow(wx.Window):
    def __init__(self, parent, top):
        wx.Window.__init__(self, parent)

        self.SetBackgroundColour("White")

        #self.SetMinSize((200,200))

        self.parent = parent
        self.top = top

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

        self.dlist = []

        self.portno = 0

        self.cb_psel = wx.ComboBox(self,
                                     size=(50,-1),
                                     style = wx.TE_PROCESS_ENTER)
        self.st_port   = wx.StaticText(self, -1, "Port ", size=(50,15), 
                                      style = wx.ALIGN_CENTER)
     
        
        self.st_per   = wx.StaticText(self, -1, "Period ", size=(50,15), 
                                      style = wx.ALIGN_CENTER)
        self.tc_per   = wx.TextCtrl(self, ID_TC_PERIOD, "2000", size=(50,-1), 
                                    style = wx.TE_PROCESS_ENTER,
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

        self.st_cycle   = wx.StaticText(self, -1, "Repeat ", size=(50,15), 
                                        style = wx.ALIGN_CENTER)
        self.tc_cycle   = wx.TextCtrl(self, ID_TC_CYCLE, "20", size=(50,-1), 
                                      style = 0,
                                      validator=NumericValidator(), 
                                      name="ON/OFF period")
        self.st_cnt   = wx.StaticText(self, -1, "", size=(15,10), 
                                      style = wx.ALIGN_CENTER)
        self.cb_cycle = wx.CheckBox (self, -1, label = 'Until Stopped')

        self.btn_start = wx.Button(self, ID_BTN_START, "Start", size=(60,25))
        
        self.tc_per.SetToolTip(wx.ToolTip("ON/OFF Interval. Min: 1 sec, "
                                          "Max: 60 sec"))
        self.btn_start.SetToolTip(wx.ToolTip("ON/OFF a selected port for a "
                                             "interval until cycle completed"))
        
        self.tc_per.SetMaxLength(5)
        self.tc_duty.SetMaxLength(2)
        self.tc_cycle.SetMaxLength(3)
        self.cb_psel.SetMaxLength(1)

        self.bs_psel = wx.BoxSizer(wx.HORIZONTAL)
        self.bs_pers = wx.BoxSizer(wx.HORIZONTAL)
        self.bs_duty = wx.BoxSizer(wx.HORIZONTAL)
        self.bs_cycle = wx.BoxSizer(wx.HORIZONTAL)
        self.bs_btn = wx.BoxSizer(wx.HORIZONTAL)
        
        self.bs_psel.Add(40,0,0)
        self.bs_psel.Add(self.st_port,0, wx.ALIGN_CENTER)
        self.bs_psel.Add(15,20,0)
        self.bs_psel.Add(self.cb_psel,0, wx.ALIGN_CENTER | 
                         wx.ALIGN_CENTER_VERTICAL)
        self.bs_psel.Add(40,0,0)

        self.bs_pers.Add(40,0,0)
        self.bs_pers.Add(self.st_per,0, wx.ALIGN_CENTER_VERTICAL)
        self.bs_pers.Add(15,50,0)
        self.bs_pers.Add(self.tc_per,0, wx.ALIGN_CENTER | 
                         wx.ALIGN_CENTER_VERTICAL)
        self.bs_pers.Add(0,20,0)
        self.bs_pers.Add(self.st_ms,0, wx.ALIGN_CENTER_VERTICAL)
        self.bs_pers.Add(40,0,0)

        self.bs_duty.Add(40,0,0)
        self.bs_duty.Add(self.st_duty,0, wx.ALIGN_CENTER_VERTICAL)
        self.bs_duty.Add(15,50,0)
        self.bs_duty.Add(self.tc_duty,0, wx.ALIGN_CENTER | 
                         wx.ALIGN_CENTER_VERTICAL)
        self.bs_duty.Add(0,50,0)
        self.bs_duty.Add(self.st_ps,0, wx.ALIGN_CENTER_VERTICAL)
        self.bs_duty.Add(40,0,0)

        self.bs_cycle.Add(40,0,0)
        self.bs_cycle.Add(self.st_cycle,0, wx.ALIGN_CENTER_VERTICAL)
        self.bs_cycle.Add(15,50,0)
        self.bs_cycle.Add(self.tc_cycle,0, wx.ALIGN_CENTER_VERTICAL)
        self.bs_cycle.Add(1,20,0)
        self.bs_cycle.Add(self.st_cnt,0, wx.ALIGN_CENTER_VERTICAL)
        self.bs_cycle.Add(1,0,0)

        self.bs_btn.Add(self.btn_start,0, flag = wx.ALIGN_CENTER_HORIZONTAL)
        self.bs_cycle.Add(1,0,0)
        self.bs_cycle.Add(self.cb_cycle, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL,
                                            border = 0)
        self.bs_cycle.Add(5,10,0)

        
        sb = wx.StaticBox(self, -1, "Loop Mode")
        
        self.bs_vbox = wx.StaticBoxSizer(sb,wx.VERTICAL)

        self.timer = wx.Timer(self)
        self.timer_usb = wx.Timer(self)
        self.bs_vbox.AddMany([
            (0,0,0),
            (self.bs_psel,1, wx.EXPAND),
            (0,0,0),
            (self.bs_pers, 1, wx.EXPAND),
            (0,0,0),
            (self.bs_duty, 1, wx.EXPAND),
            (self.bs_cycle, 1, wx.EXPAND),
            (0,0,0),
            (self.bs_btn, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (0,5,0)
            ])
        self.btn_start.Bind(wx.EVT_BUTTON, self.StartAuto)
        self.Bind(wx.EVT_TIMER, self.TimerServ, self.timer)
        self.Bind(wx.EVT_TIMER, self.UsbTimer, self.timer_usb)
        
        self.SetSizer(self.bs_vbox)
        self.bs_vbox.Fit(self)
        self.Layout()

        self.enable_controls(True)


    # Loop button click event
    def StartAuto(self, evt):
        if(self.start_flg):
            self.top.print_on_log("Loop Mode Interrupted\n")
            self.stop_loop()
        else:
            if(self.check_valid_input()):
                self.get_all_three()
                if(self.usb_dly_warning()):
                    self.start_loop()
            else:
                wx.MessageBox('Input box left blank','Error', wx.OK)

    # Loop mode Timer service
    def TimerServ(self, evt):
        if self.top.con_flg:
            self.pulse_flg = True
            if(self.usb_flg == False):
                self.timer.Stop()
                self.pulse_flg = False
                if(self.On_flg):
                    self.port_on(self.portno, False)
                    self.On_flg = False
                    self.cycleCnt = self.cycleCnt + 1
                    if(self.cb_cycle.GetValue() != True):
                        self.tc_cycle.SetValue(str(self.cycle - self.cycleCnt))
                        if(self.cycleCnt >= self.cycle):
                            self.tc_cycle.SetValue(str(self.cycle))
                            self.top.print_on_log("Loop Mode Completed\n")
                            self.stop_loop()
                        else:    
                            self.timer.Start(self.OffTime)
                    else:    
                        self.timer.Start(self.OffTime)
                else:
                    self.port_on(self.portno, True)
                    self.timer.Start(self.OnTime)
                    self.On_flg = True

    # USB Tree View Changes Timer Service
    def UsbTimer(self, e):
        self.timer_usb.Stop()
        try:
            usbDev.get_tree_change(self.top)
        except:
            self.top.print_on_usb("USB Read Error!")
        self.usb_flg = False
        
        if(self.start_flg == True & self.pulse_flg == True):
            self.timer.Start(1)

    # Throws USB delay warning message, when the user wants to initiate loop mode
    def usb_dly_warning(self):
        if(self.top.get_delay_status()):
            if((int(self.OnTime) < int(self.top.get_enum_delay())) |
               (int(self.OffTime) < int(self.top.get_enum_delay()))):
                title = ("USB device tree delay warning!")
                msg = ("USB device tree delay should be less than "
                       "the Port ON and OFF Period."
                       "\nClick Yes to continue without "
                       "USB device tree changes"
                       "\nClick No to exit the Loop mode")
                dlg = wx.MessageDialog(self, msg, title, wx.NO|wx.YES)
                if(dlg.ShowModal() == wx.ID_YES):
                    self.top.disable_usb_scan()
                    return True
                else:
                    return False
        return True

    # Get ONOFF period
    def get_period(self):
        dper = self.tc_per.GetValue()
        if(dper == ""):
            dper = "50"
        pval = int(dper)
        if(pval < 50):
            pval = 50
        elif(pval > 60000):
            pval = 60000

        self.tc_per.SetValue(str(pval))
        return self.tc_per.GetValue()

    # Set Period Called by USB Tree Window when there is a need to override the period
    def set_period(self, strval):
        self.tc_per.SetValue(strval)

    # Get Duty value
    def get_duty(self):
        duty = self.tc_duty.GetValue()
        if (duty == ""):
            duty = "0"
        return duty

    # Get Cycle value
    def get_cycle(self):
        cycle = self.tc_cycle.GetValue()
        if (cycle == ""):
            cycle = "0"
        return cycle

    # Get Period, Duty and Cycle values then calculate ON Time and OFF Time
    def get_all_three(self):
        self.period = int(self.get_period())
        self.duty = int(self.get_duty())
        self.cycle = int(self.get_cycle())

        self.OnTime = self.period * (self.duty/100)
        self.OffTime = self.period - self.OnTime

    # Send ON, OFF Time and Duty to USB Tree Window for USB delay validation
    def get_loop_param(self):
        self.get_all_three()
        return self.OnTime, self.OffTime, self.duty

    # Check the input text box of Period, Duty and Cycle
    def check_valid_input(self):
        strPer = self.tc_per.GetValue()
        if(strPer == ''):
            return False
        strDuty = self.tc_duty.GetValue()
        if(strDuty == ''):
            return False 
        strCycle = self.tc_cycle.GetValue()
        if(strCycle == ''):
            return False
        strInf = self.cb_cycle.GetValue()
        if(strInf == ''):
            return False
        return True   

    # Start Loop Mode
    def start_loop(self):
        self.cval = self.cb_psel.GetValue()
        self.portno = int(self.cval)
        self.start_flg = True
        self.top.set_mode(MODE_LOOP)
        self.loop_start_msg()
        self.btn_start.SetLabel("Stop")
        #self.stop_loop_mode()
        if(self.timer.IsRunning() == False):
            self.cycleCnt = 0
            self.On_flg = True
            self.port_on(self.portno, True)
            self.timer.Start(self.OnTime)
    
    # Loop Mode start message log send to the Log Window
    def loop_start_msg(self):
        self.get_all_three()
        lmstr = "Loop Mode start : ON-Time = {d1} ms,".\
                format(d1=int(self.OnTime)) + \
                " OFF-Time = {d2} ms,".\
                format(d2=int(self.OffTime)) 
        if(self.cb_cycle.GetValue() == True):
            lmstr = lmstr +" Cycle = indefinite\n"
        else:
            lmstr = lmstr +" Cycle = {d3}\n".format(d3=self.cycle)
        self.top.print_on_log(lmstr)

    # Stop Loop Mode - 1. When click stop 2. When cycle completed
    def stop_loop(self):
        self.start_flg = False
        self.btn_start.SetLabel("Start")
        self.top.set_mode(MODE_MANUAL)
        self.timer.Stop()
     
    # Port ON/OFF command send to Connected Device Module
    def port_on(self, portno, stat):
        self.top.port_on(portno, stat)
        if(self.top.get_delay_status()):
            self.keep_delay()

    # USB delay Timer start
    def keep_delay(self):
        self.usb_flg = True
        self.timer_usb.Start(int(self.top.get_enum_delay()))

    # Enable/Disable widgets when mode changed
    def update_controls(self, mode):
        if mode == MODE_MANUAL:
            self.enable_controls(True)
        else:
            self.enable_controls(False)

    # Widgets Disable/Enable
    def enable_controls(self, stat):
        if(stat):
            self.cb_psel.Enable()
            self.tc_per.Enable()
            self.tc_duty.Enable()
            self.tc_cycle.Enable()
            self.cb_cycle.Enable()
            self.btn_start.Enable()
        else:
            self.cb_psel.Disable()
            self.tc_per.Disable()
            self.tc_duty.Disable()
            self.tc_cycle.Disable()
            self.cb_cycle.Disable()
            if self.top.mode != MODE_LOOP:
                self.btn_start.Disable()
        if not self.top.con_flg:
            self.btn_start.Disable()

    # Set Port list to Combo box when Device gets connected
    def set_port_list(self, port):
        self.cb_psel.Clear()
        for i in range(port):
            self.cb_psel.Append(str(i+1))
        self.cb_psel.SetSelection(0)

    # Called when device get disconnected
    def device_disconnected(self):
        self.stop_loop()
