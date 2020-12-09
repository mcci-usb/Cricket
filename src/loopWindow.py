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

        self.st_cycle   = wx.StaticText(self, -1, "Cycle ", size=(50,15), 
                                        style = wx.ALIGN_CENTER)
        self.tc_cycle   = wx.TextCtrl(self, ID_TC_CYCLE, "20", size=(50,-1), 
                                      style = 0,
                                      validator=NumericValidator(), 
                                      name="ON/OFF period")
        self.st_cnt   = wx.StaticText(self, -1, "", size=(30,15), 
                                      style = wx.ALIGN_CENTER)

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
        self.bs_pers.Add(15,50,0)
        self.bs_pers.Add(self.st_ms,0, wx.ALIGN_CENTER_VERTICAL)
        self.bs_pers.Add(40,0,0)

        self.bs_duty.Add(40,0,0)
        self.bs_duty.Add(self.st_duty,0, wx.ALIGN_CENTER_VERTICAL)
        self.bs_duty.Add(15,50,0)
        self.bs_duty.Add(self.tc_duty,0, wx.ALIGN_CENTER | 
                         wx.ALIGN_CENTER_VERTICAL)
        self.bs_duty.Add(15,50,0)
        self.bs_duty.Add(self.st_ps,0, wx.ALIGN_CENTER_VERTICAL)
        self.bs_duty.Add(40,0,0)

        self.bs_cycle.Add(40,0,0)
        self.bs_cycle.Add(self.st_cycle,0, wx.ALIGN_CENTER_VERTICAL)
        self.bs_cycle.Add(15,50,0)
        self.bs_cycle.Add(self.tc_cycle,0, wx.ALIGN_CENTER_VERTICAL)
        self.bs_cycle.Add(15,50,0)
        self.bs_cycle.Add(self.st_cnt,0, wx.ALIGN_CENTER_VERTICAL)
        self.bs_cycle.Add(40,0,0)

        self.bs_btn.Add(self.btn_start,0, flag = wx.ALIGN_CENTER_HORIZONTAL)

        
        sb = wx.StaticBox(self, -1, "Loop Mode")
        
        self.bs_vbox = wx.StaticBoxSizer(sb,wx.VERTICAL)

        self.timer = wx.Timer(self)
        self.timer_usb = wx.Timer(self)
        self.bs_vbox.AddMany([
            (0,5,0),
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
        #self.tc_per.Bind(wx.EVT_TEXT_ENTER, self.OnEnterPeriod)
        #self.tc_duty.Bind(wx.EVT_TEXT_ENTER, self.OnEnterDuty)
        self.Bind(wx.EVT_TIMER, self.TimerServ, self.timer)
        self.Bind(wx.EVT_TIMER, self.UsbTimer, self.timer_usb)
        
        self.SetSizer(self.bs_vbox)
        self.bs_vbox.Fit(self)
        self.Layout()

        self.update_controls()


    def StartAuto(self, evt):
        if(self.start_flg):
            self.stop_loop()
        else:
            if(self.check_valid_input()):
                self.get_all_three()
                if(self.usb_dly_warning()):
                    self.start_loop()
            else:
                wx.MessageBox('Input box left blank','Error', wx.OK)

    def TimerServ(self, evt):
        if self.top.con_flg:
            self.pulse_flg = True
            if(self.usb_flg == False):
                self.timer.Stop()
                self.pulse_flg = False
                if(self.On_flg):
                    self.port_off_cmd(self.portno)
                    self.On_flg = False
                    self.cycleCnt = self.cycleCnt + 1
                    self.st_cnt.SetLabel(str(self.cycleCnt))
                    if(self.cycleCnt >= self.cycle):
                        self.top.print_on_log("Loop Mode Completed\n")
                        self.timer.Stop()
                        self.btn_start.SetLabel("Start")
                        self.start_flg = False
                        self.enable_controls(True)
                    else:    
                        self.timer.Start(self.OffTime)
                else:
                    self.port_on_cmd(self.portno)
                    self.timer.Start(self.OnTime)
                    self.On_flg = True

    def UsbTimer(self, e):
        self.timer_usb.Stop()
        try:
            usbDev.get_tree_change(self.top)
        except:
            self.top.print_on_usb("USB Read Error!")
        self.usb_flg = False
        
        if(self.start_flg == True & self.pulse_flg == True):
            self.timer.Start(1)

    def OnEnterPeriod(self, evt):
        self.get_all_three()
        self.usb_dly_warning()
    
    def OnEnterDuty(self, evt):
        self.get_all_three()
        self.usb_dly_warning()
        
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

    def get_period(self):
        dper = self.tc_per.GetValue()
        if(dper == ""):
            dper = "1000"
        pval = int(dper)
        if(pval < 1000):
            pval = 1000
        elif(pval > 60000):
            pval = 60000

        self.tc_per.SetValue(str(pval))
        return self.tc_per.GetValue()

    def set_period(self, strval):
        self.tc_per.SetValue(strval)

    def get_duty(self):
        duty = self.tc_duty.GetValue()
        if (duty == ""):
            duty = "0"

        return duty

    def get_cycle(self):
        cycle = self.tc_cycle.GetValue()
        if (cycle == ""):
            cycle = "0"

        return cycle

    def update_controls(self):
        if(self.top.con_flg):
            self.btn_start.Enable()
        else:
            self.btn_start.Disable()

    def enable_start(self):
        self.btn_start.Enable()

    def disable_start(self):
        self.btn_start.Disable()

    def get_all_three(self):
        self.period = int(self.get_period())
        self.duty = int(self.get_duty())
        self.cycle = int(self.get_cycle())

        self.OnTime = self.period * (self.duty/100)
        self.OffTime = self.period - self.OnTime

    def get_loop_param(self):
        self.get_all_three()
        return self.OnTime, self.OffTime, self.duty

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
        return True   

    def loop_start_msg(self):
        self.get_all_three()
        lmstr = "Loop Mode start : ON-Time = {d1} ms,".\
                format(d1=int(self.OnTime)) + \
                " OFF-Time = {d2} ms,".\
                format(d2=int(self.OffTime)) + \
                " Cycle = {d3}\n".format(d3=self.cycle)
        
        self.top.print_on_log(lmstr)

    def start_loop(self):
        self.cval = self.cb_psel.GetValue()
        self.portno = int(self.cval)
        #self.portno = self.top.get_switch_port()
        self.start_flg = True
        self.loop_start_msg()
        self.btn_start.SetLabel("Stop")
        self.enable_controls(False)
        if(self.timer.IsRunning() == False):
            self.cycleCnt = 0
            self.On_flg = True
            self.port_on_cmd(self.portno)
            self.timer.Start(self.OnTime)

    def stop_loop(self):
        self.start_flg = False
        self.btn_start.SetLabel("Start")
        self.enable_controls(True)
        self.timer.Stop()
        self.top.print_on_log("Loop Mode Interrupted\n")

    def print_cycle_info(self):
        strCnt = "Cycle : {cs}\t".format(cs=str(self.cycleCnt + 1))
        self.top.print_on_log(strCnt)

    def port_on_cmd(self, pno):
        cmd = 'port'+' '+str(pno)+'\r\n'
        res, outstr = serialDev.send_port_cmd(self.top.devHand, cmd)
        if res == 0: 
            outstr = outstr.replace('p', 'P')
            outstr = outstr.replace('1', '1 ON')
            outstr = outstr.replace('2', '2 ON')
            outstr = outstr.replace('3', '3 ON')
            outstr = outstr.replace('4', '4 ON')

            self.top.port_led_update(pno-1, True)
            
            self.top.print_on_log(outstr)
        if(self.top.get_delay_status()):
            self.keep_delay()
        
    def port_off_cmd(self, pno):
        cmd = 'port'+' '+'0'+'\r\n'
        res, outstr = serialDev.send_port_cmd(self.top.devHand, cmd)
        if res == 0:
            outstr = outstr.replace('p', 'P')
            outstr = outstr.replace('0', ""+str(pno)+" OFF")

            self.top.port_led_update(pno-1, False)
            
        self.top.print_on_log(outstr)

        if(self.top.get_delay_status()):
            self.keep_delay()
    
    def keep_delay(self):
        self.usb_flg = True
        self.timer_usb.Start(int(self.top.get_enum_delay()))

    def update_controls(self):
        if(self.top.con_flg):
            self.enable_start()
        else:
            self.disable_start()
            self.timer.Stop()
            self.start_flg = False
            self.st_cnt.SetLabel("")

    def enable_loop_controls(self, stat):
        if(stat == True):
            self.tc_per.Enable()
            self.tc_duty.Enable()
            self.tc_cycle.Enable()
        else:
            self.tc_per.Disable()
            self.tc_duty.Disable()
            self.tc_cycle.Disable()

    def enable_controls(self, stat):
        self.enable_loop_controls(stat)
        self.top.enable_enum_controls(stat)
        self.top.enable_auto_controls(stat)
    
    def set_port_list(self, port):
        self.cb_psel.Clear()
        for i in range(port):
            self.cb_psel.Append(str(i+1))
        self.cb_psel.SetSelection(0)
        
 