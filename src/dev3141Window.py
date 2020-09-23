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

#======================================================================
# COMPONENTS
#======================================================================

class Dev3141Window(wx.Panel):
    def __init__(self, parent, top):
        wx.Panel.__init__(self, parent)
        
        self.parent = parent
        self.top = top

        self.port = 0

        self.usb_flg = False

        self.SetMinSize((270, 240))

        sb = wx.StaticBox(self, -1, "Model 3141")

        self.vbox = wx.StaticBoxSizer(sb,wx.VERTICAL)

        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxs1 = wx.BoxSizer(wx.HORIZONTAL)

        self.rbtn_p1 = wx.RadioButton(self, ID_RBTN_P1, "Port 1", 
                                      style=wx.RB_GROUP)
        self.tc_led1   = wx.TextCtrl(self, -1, " ", size=(13,13))
        self.rbtn_p2 = wx.RadioButton(self, ID_RBTN_P2, "Port 2")
        self.tc_led2   = wx.TextCtrl(self, -1, " ", size=(13,13))
        self.btn_tog = wx.Button(self, ID_BTN_ONOFF, "ON",size=(55,25))
        
        self.st_ss   = wx.StaticText(self, -1, "SuperSpeed")
        self.rbtn_ss1 = wx.RadioButton(self, ID_RBTN_SS1, "Enable", 
                                       style=wx.RB_GROUP)
        self.rbtn_ss0 = wx.RadioButton(self, ID_RBTN_SS0, "Disable")
        self.btn_do = wx.Button(self, ID_BTN_DC, "Check Orientation", 
                                size=(-1,-1))
        self.st_do   = wx.StaticText(self, -1, " --- ", style=wx.ALIGN_CENTER)

        self.st_si   = wx.StaticText(self, -1, "Interval")
        self.tc_ival   = wx.TextCtrl(self, ID_TC_INTERVAL, "1000", 
                                     size=(50,-1), style = wx.TE_CENTRE |
                                     wx.TE_PROCESS_ENTER,
                                     validator=NumericValidator(), 
                                     name="ON/OFF period")
        self.st_ms   = wx.StaticText(self, -1, "ms", size=(30,15), 
                                     style = wx.ALIGN_CENTER)
        self.btn_auto = wx.Button(self, ID_BTN_AUTO, "Auto", size=(60,25))

        self.tc_ival.SetMaxLength(5)
        
        self.tc_ival.SetToolTip(wx.ToolTip("Switching Interval. Min: 1 sec, "
                                           "Max: 60 sec"))
        self.btn_auto.SetToolTip(wx.ToolTip("Switch between Port1 and Port2 "
                                            "for a interval until stop"))
        
        self.tc_led1.SetBackgroundColour("black")
        self.tc_led2.SetBackgroundColour("black")

        self.tc_led1.SetEditable(False)
        self.tc_led2.SetEditable(False)

        self.led = []
        self.btnStat = False

        self.led.append(self.tc_led1)
        self.led.append(self.tc_led2)

        self.hboxs1.Add(self.tc_led1, flag=wx.ALIGN_LEFT |   
                       wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=20 )
        self.hboxs1.Add(self.rbtn_p1, flag=wx.ALIGN_CENTER_VERTICAL | 
                       wx.LEFT , border=3)
        self.hboxs1.Add(self.tc_led2, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 
                       border = 10)
        self.hboxs1.Add(self.rbtn_p2, flag=wx.ALIGN_CENTER_VERTICAL| wx.LEFT, 
                       border=3)
        
        self.hbox1.Add(self.hboxs1, flag=wx.ALIGN_CENTER_VERTICAL )
        self.hbox1.Add(0,1,0)
        self.hbox1.Add(self.btn_tog, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT,
                       border=20)

        self.hbox2.Add(self.st_ss,0 , flag=wx.ALIGN_LEFT | wx.LEFT, 
                       border=20 )
        self.hbox2.Add(self.rbtn_ss1, flag=wx.ALIGN_LEFT | wx.LEFT, border = 20)
        self.hbox2.Add(self.rbtn_ss0, flag=wx.RIGHT | wx.LEFT |
                       wx.ALIGN_RIGHT, border=18)


        self.hbox3.Add(self.btn_do, flag=wx.LEFT, border=20 )
        self.hbox3.Add(self.st_do, flag=wx.ALIGN_RIGHT | 
                       wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, 
                       border=30)
                   
        self.hbox4.Add(self.st_si, 0, flag=wx.ALIGN_LEFT | wx.LEFT | 
                       wx.ALIGN_CENTER_VERTICAL, border=20)
        self.hbox4.Add(self.tc_ival, flag=wx.ALIGN_CENTER_VERTICAL | 
                       wx.LEFT, border = 10)
        self.hbox4.Add(self.st_ms, flag=wx.ALIGN_LEFT | 
                       wx.ALIGN_CENTER_VERTICAL)
        self.hbox4.Add(self.btn_auto, 0, flag=wx.ALIGN_RIGHT | 
                       wx.LEFT, border = 30)
        
        self.p1 = 0
        self.p2 = 0

        self.tog_flg = False

        self.pulse_flg = False
        
        self.timer = wx.Timer(self)
        self.timer_usb = wx.Timer(self)

        self.vbox.AddMany([
            (10,20,0),
            (self.hbox1, 0, wx.EXPAND | wx.ALL),
            (0,30,0),
            (self.hbox2, 0, wx.EXPAND),
            (0,30,0),
            (self.hbox3, 0, wx.EXPAND),
            (0,30,0),
            (self.hbox4, 0, wx.EXPAND),
            (10,10,0)
            ])
       
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.Layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.PortSpeedChanged)
        self.btn_tog.Bind(wx.EVT_BUTTON, self.OnOffPort)
        self.btn_auto.Bind(wx.EVT_BUTTON, self.OprAuto)
        self.btn_do.Bind(wx.EVT_BUTTON, self.GetStatus)
        #self.tc_ival.Bind(wx.EVT_TEXT_ENTER, self.OnEnterInterval)
        
        self.Bind(wx.EVT_TIMER, self.TimerServ, self.timer)
        self.Bind(wx.EVT_TIMER, self.UsbTimer, self.timer_usb)

        self.rbtn_p1.SetValue(True)
        self.rbtn_ss1.SetValue(True)
        self.port = 1

        self.update_controls()


    def PortSpeedChanged(self, e):
        rb = e.GetEventObject()
        lbl = rb.GetId()
        
        if(lbl == ID_RBTN_P1):
            self.port = 1
        elif(lbl == ID_RBTN_P2):
            self.port = 2
        elif(lbl == ID_RBTN_SS1):
            self.speed_cmd(1)
        elif(lbl == ID_RBTN_SS0):
            self.speed_cmd(0)

    def OnOffPort(self, evt):
        if self.usb_flg == False:
            self.btnStat = not self.btnStat
            self.btn_tog.Disable()
            self.btn_auto.Disable()
            self.top.disable_start()
            self.top.enable_enum_controls(False)
            if(self.btnStat):
                self.disable_all_rb()
                self.port_on_cmd(self.port)
            else:
                self.enable_all_rb()
                self.port_off_cmd(self.port)
            if(self.top.con_flg):
                self.update_port_stat()

    def OprAuto(self, evt):
        if(self.top.auto_flg):
            self.stop_auto()
        else:
            if(self.usb_dly_warning()):
                self.start_auto()

    def GetStatus(self, e):
        strin = "--"
        res, outstr = serialDev.send_status_cmd(self.top.devHand)
        if res == 0:
            restr = outstr.split('\n')
            for instr in restr:
                if 'CC1 detect:' in instr:
                    fstr = instr.split('0x')
                    hint = int(fstr[1], 16)
                    hv = hex(hint)
                    if(hint > 0x20):
                        strin = "Normal"
                    else:
                        strin = "Flip"

                    self.update_carrier(strin)
                    self.top.print_on_log("Device Orientation : "+strin+"\n")
                    break

    def UsbTimer(self, e):
        self.timer_usb.Stop()
        try:
            usbDev.get_tree_change(self.top)
        except:
            self.top.print_on_usb("USB Read Error!")
        self.usb_flg = False
        if(self.top.auto_flg == True & self.pulse_flg == True):
            self.timer.Start(1)
        else:
            self.btn_tog.Enable()
            self.top.enable_enum_controls(True)
            self.btn_auto.Enable()
            self.top.enable_start()

    def TimerServ(self, evt):
        if(self.top.con_flg):
            self.pulse_flg = True
            if(self.usb_flg == False):
                self.pulse_flg = False
                self.timer.Stop()
                if(self.tog_flg):
                    self.tog_flg = False
                    self.port_on_cmd(2)
                    self.tc_led1.SetBackgroundColour("black")
                    self.tc_led2.SetBackgroundColour("blue")
                    self.tc_led1.SetLabel("")
                    self.tc_led2.SetLabel("")
                    self.timer.Start(int(self.get_interval()))
                else:
                    self.tog_flg = True
                    self.port_on_cmd(1)
                    self.tc_led1.SetBackgroundColour("blue")
                    self.tc_led2.SetBackgroundColour("black")
                    self.tc_led1.SetLabel("")
                    self.tc_led2.SetLabel("")
                    self.timer.Start(int(self.get_interval()))
        else:
            self.stop_auto()
            self.disable_buttons()

    def OnEnterInterval(self, evt):
        self.usb_dly_warning()

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

    def disable_all_rb(self):
        self.btn_tog.SetLabel('OFF')
        self.rbtn_p1.Disable()
        self.rbtn_p2.Disable()
        self.rbtn_ss0.Disable()
        self.rbtn_ss1.Disable()

    def enable_all_rb(self):
        self.btn_tog.SetLabel('ON')
        self.rbtn_p1.Enable()
        self.rbtn_p2.Enable()
        self.rbtn_ss0.Enable()
        self.rbtn_ss1.Enable()

    def update_port_stat(self):
        if(self.btnStat):
            for i in range(len(self.led)):
                if i == self.port-1:
                    self.led[i].SetBackgroundColour('blue')
                else:
                    self.led[i].SetBackgroundColour('black')
                self.led[i].SetLabel("")
        else:
            self.tc_led1.SetBackgroundColour('black')
            self.tc_led2.SetBackgroundColour('black')
            self.tc_led1.SetLabel("")
            self.tc_led2.SetLabel("")

    def stop_auto(self):
        self.btn_auto.SetLabel("Auto")
        self.enable_auto_ctrl(True)
        self.top.enable_start()
        self.top.enable_enum_controls(True)
        self.top.auto_flg = False
        self.timer.Stop()
        if(self.tog_flg):
            self.port_off_cmd(1)
            self.tog_flg = False
        else:
            self.port_off_cmd(2)
        self.btnStat = False
        self.btn_tog.SetLabel('ON')
        self.update_port_stat()

    def start_auto(self):
        self.top.auto_flg = True
        self.btn_auto.SetLabel("Stop")
        self.enable_auto_ctrl(False)
        self.top.disable_start()
        self.top.enable_enum_controls(False)
        if(self.timer.IsRunning() == False):
            self.tog_flg = False
            self.timer.Start(int(self.get_interval()))

    def get_switch_port(self):
        return self.port

    def update_carrier(self, str):
        self.st_do.SetLabel(str)
        
    def speed_cmd(self,val):
        cmd = 'superspeed'+' '+str(val)+'\r\n'
        res, outstr = serialDev.send_port_cmd(self.top.devHand,cmd)
        if res == 0:
            outstr = outstr.replace('s', 'S')
            outstr = outstr.replace('1', 'Enabled')
            outstr = outstr.replace('0', 'Disabled')
            self.top.print_on_log(outstr)
      
    def port_on_cmd(self, pno):
        self.update_carrier(" --- ")
        cmd = 'port'+' '+str(pno)+'\r\n'
        res, outstr = serialDev.send_port_cmd(self.top.devHand, cmd)
        if res == 0:
            outstr = outstr.replace('p', 'P')
            outstr = outstr.replace('1', '1 ON')
            outstr = outstr.replace('2', '2 ON')
            self.btn_do.Enable()
            if(self.top.auto_flg):
                self.btn_do.Disable()
                outstr = outstr[:-2] + "; Other Ports are OFF\n"
            self.top.print_on_log(outstr)
        
        if(self.top.get_delay_status()):
            self.keep_delay()
        elif(self.top.auto_flg == False):
            self.btn_tog.Enable()
            self.top.enable_enum_controls(True)
            self.btn_auto.Enable()
            self.top.enable_start()
        
    def port_off_cmd(self, pno):
        self.update_carrier(" --- ")
        cmd = 'port'+' '+'0'+'\r\n'
        res, outstr = serialDev.send_port_cmd(self.top.devHand, cmd)
        if res == 0:
            self.btn_do.Disable()
            outstr = outstr.replace('p', 'P')
            outstr = outstr.replace('0', ""+str(pno)+" OFF")
            self.top.print_on_log(outstr)
         
        if(self.top.get_delay_status()):
            self.keep_delay()
        elif(self.top.auto_flg == False):
            self.btn_tog.Enable()
            self.top.enable_enum_controls(True)
            self.btn_auto.Enable()
            self.top.enable_start()

    def keep_delay(self):
        self.usb_flg = True
        self.timer_usb.Start(int(self.top.get_enum_delay()))

    def enable_model(self, stat):
        if(stat == True):
            self.btn_tog.Enable()
            self.rbtn_p1.Enable()
            self.rbtn_p2.Enable()
            self.rbtn_ss0.Enable()
            self.rbtn_ss1.Enable()
            self.btn_auto.Enable()
        else:
            self.btn_tog.Disable()
            self.rbtn_p1.Disable()
            self.rbtn_p2.Disable()
            self.btn_do.Disable()
            self.rbtn_ss0.Disable()
            self.rbtn_ss1.Disable()
            self.btn_auto.Disable()
    
    def update_controls(self):
        if(self.top.con_flg):
            res, outstr = serialDev.send_sn_cmd(self.top.devHand)
            if res == 0:
                self.top.UpdateSingle(outstr, 2)
                self.top.print_on_log(outstr)
                self.btn_tog.Enable()
                self.btn_auto.Enable()
                self.rbtn_ss1.SetValue(True)
                self.rbtn_p1.SetValue(True)
                if(self.top.init_flg):
                    self.speed_cmd(self.get_speed_input())
                    self.top.init_flg = False
            else:
                self.disable_buttons()
        else:
            self.disable_buttons()

    def disable_buttons(self):
        self.btn_tog.Disable()
        self.btn_tog.SetLabel("ON")
        self.btn_do.Disable()
        self.btn_auto.Disable()
        self.st_do.SetLabel(" --- ")
        self.led[0].SetBackgroundColour('black')
        self.led[0].SetLabel("")
        self.led[1].SetBackgroundColour('black')
        self.led[1].SetLabel("")
        self.rbtn_ss0.Disable()
        self.rbtn_ss1.Disable()

    def get_speed_input(self):
        if(self.rbtn_ss1.GetValue()):
            return 1
        else:
            return 0

    def disable_auto(self):
        self.rbtn_p1.Disable()
        self.rbtn_p2.Disable()
        self.btn_auto.Disable()
        self.btn_do.Disable()
        self.btn_tog.Disable()

    def enable_auto(self):
        self.rbtn_p1.Enable()
        self.rbtn_p2.Enable()
        self.btn_auto.Enable()
        self.btn_tog.Enable()

    def enable_auto_ctrl(self, stat):
        if(stat == True):
            self.rbtn_p1.Enable()
            self.rbtn_p2.Enable()
            self.btn_tog.Enable()
            self.rbtn_ss0.Enable()
            self.rbtn_ss1.Enable()
            self.tc_ival.Enable()
        else:
            self.rbtn_p1.Disable()
            self.rbtn_p2.Disable()
            self.btn_tog.Disable()
            self.rbtn_ss0.Disable()
            self.rbtn_ss1.Disable()
            self.tc_ival.Disable()

    def port_led_update(self, pno, stat):
        self.update_carrier(" --- ")
        if(stat):
            for i in range(2):
                if(i == pno):
                    self.led[i].SetBackgroundColour('blue')
                else:
                    self.led[i].SetBackgroundColour('black')
                self.led[i].SetLabel("")
        else:
            for i in range(2):
                self.led[i].SetBackgroundColour('black')
                self.led[i].SetLabel("")
    
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

    def set_interval(self, strval):
        self.tc_ival.SetValue(strval)