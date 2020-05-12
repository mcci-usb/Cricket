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

class Dev3201Window(wx.Window):
    def __init__(self, parent, top):
        wx.Window.__init__(self, parent)
        self.SetBackgroundColour("White")

        self.parent = parent
        self.top = top

        self.SetMinSize((270, 240))

        self.rbtn_p1 = wx.RadioButton(self, ID_RBTN_P1, "Port 1", 
                                      style=wx.RB_GROUP)
        self.tc_led1   = wx.TextCtrl(self, -1, " ", size=(13,13))
        self.rbtn_p2 = wx.RadioButton(self, ID_RBTN_P2, "Port 2")
        self.tc_led2   = wx.TextCtrl(self, -1, " ", size=(13,13))
        self.btn_tog = wx.Button(self, ID_BTN_ONOFF, "ON",size=(55,25))

        self.rbtn_p3 = wx.RadioButton(self, ID_RBTN_P3, "Port 3")
        self.tc_led3   = wx.TextCtrl(self, -1, " ", size=(13,13))
        self.rbtn_p4 = wx.RadioButton(self, ID_RBTN_P4, "Port 4")
        self.tc_led4   = wx.TextCtrl(self, -1, " ", size=(13,13))

        self.st_ss   = wx.StaticText(self, -1, "SuperSpeed")
        self.rbtn_ss1 = wx.RadioButton(self, ID_RBTN_SS1, "Enable", 
                                       style=wx.RB_GROUP)
        self.rbtn_ss0 = wx.RadioButton(self, ID_RBTN_SS0, "Disable")
        
        self.st_si   = wx.StaticText(self, -1, "Interval")
        self.tc_ival   = wx.TextCtrl(self, ID_TC_INTERVAL, "1000", 
                                     size=(50,-1), style = 0,
                                     validator=NumericValidator(), 
                                     name="ON/OFF period")
        self.st_ms   = wx.StaticText(self, -1, "ms", size=(30,15), 
                                     style = wx.ALIGN_CENTER)
        self.btn_auto = wx.Button(self, ID_BTN_AUTO, "Auto", size=(60,25))


        self.st_info   = wx.StaticText(self, -1, 
                                       "Check Bus Voltage and Current ", 
                                       style = wx.ALIGN_CENTER)
        self.btn_volts = wx.Button(self, ID_BTN_VOLTS, "Volts", size=(50,25))
        self.st_volts   = wx.StaticText(self, -1, " --- ", 
                                        style = wx.ALIGN_CENTER)
        self.btn_amps = wx.Button(self, ID_BTN_AMPS, "Amps", size=(50,25))
        self.st_amps   = wx.StaticText(self, -1, " --- ", 
                                       style = wx.ALIGN_CENTER)

        self.tc_ival.SetToolTip(wx.ToolTip("Switching Interval. Min: 1 sec, "
                                           "Max: 60 sec"))
        self.btn_auto.SetToolTip(wx.ToolTip("Switch between All Ports "
                                            "for a interval until stop"))
        
        self.p1 = 0
        self.p2 = 0

        self.pcnt = 0

        self.usb_flg = False

        self.timer = wx.Timer(self)
        self.timer_usb = wx.Timer(self)

        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxi = wx.BoxSizer(wx.HORIZONTAL)

        self.led = []
        self.rbtn = []
        self.btnStat = False

        self.led.append(self.tc_led1)
        self.led.append(self.tc_led2)
        self.led.append(self.tc_led3)
        self.led.append(self.tc_led4)

        self.rbtn.append(self.rbtn_p1)
        self.rbtn.append(self.rbtn_p2)
        self.rbtn.append(self.rbtn_p3)
        self.rbtn.append(self.rbtn_p4)

        for i in range(4):
            self.led[i].SetBackgroundColour("black")
            self.led[i].SetEditable(False)

        self.hbox1.Add(self.tc_led1, flag=wx.ALIGN_LEFT |   
                       wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=20 )
        self.hbox1.Add(self.rbtn_p1, 1, flag=wx.ALIGN_CENTER_VERTICAL | 
                       wx.LEFT , border=3)
        self.hbox1.Add(self.tc_led2, flag=wx.ALIGN_CENTER | wx.LEFT, 
                       border = 10)
        self.hbox1.Add(self.rbtn_p2, flag=wx.ALIGN_CENTER_VERTICAL| wx.LEFT, 
                       border=3)
        self.hbox1.Add(0,0,0)
        self.hbox1.Add(self.btn_tog, flag=wx.RIGHT | wx.LEFT | wx.ALIGN_RIGHT,
                       border=18)

        self.hbox2.Add(self.tc_led3, flag=wx.ALIGN_LEFT |   
                       wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=20 )
        self.hbox2.Add(self.rbtn_p3, flag=wx.ALIGN_CENTER_VERTICAL | 
                       wx.LEFT, border=3)
        self.hbox2.Add(self.tc_led4, flag=wx.ALIGN_CENTER | wx.LEFT, 
                       border = 15)
        self.hbox2.Add(self.rbtn_p4, flag=wx.ALIGN_CENTER_VERTICAL| wx.LEFT, 
                       border=3)

        self.hbox3.Add(self.st_ss, 1, flag=wx.ALIGN_LEFT | wx.LEFT | 
                       wx.EXPAND, border=20 )
        self.hbox3.Add(self.rbtn_ss1, flag=wx.ALIGN_LEFT )
        self.hbox3.Add(self.rbtn_ss0, flag=wx.RIGHT | wx.LEFT |
                       wx.ALIGN_RIGHT, border=18)

        self.hbox4.Add(self.st_si, 0, flag=wx.ALIGN_LEFT | wx.LEFT | 
                       wx.ALIGN_CENTER_VERTICAL, border=20)
        self.hbox4.Add(self.tc_ival, flag=wx.ALIGN_CENTER_VERTICAL | 
                       wx.LEFT, border = 10 )
        self.hbox4.Add(self.st_ms, flag=wx.ALIGN_LEFT | 
                       wx.ALIGN_CENTER_VERTICAL )
        self.hbox4.Add(self.btn_auto, 0, flag=wx.ALIGN_RIGHT | 
                       wx.LEFT, border = 30)

        self.hboxi.Add(self.st_info, flag=wx.ALIGN_LEFT | wx.LEFT, border=20 )

        self.hbox5.Add(self.btn_volts, flag=wx.ALIGN_LEFT | 
                       wx.LEFT, border=20 )
        self.hbox5.Add(self.st_volts, flag=wx.ALIGN_LEFT | wx.LEFT | 
                       wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=20)
        self.hbox5.Add(self.btn_amps, flag=wx.RIGHT |
                       wx.ALIGN_RIGHT, border=20)
        self.hbox5.Add(self.st_amps, flag=wx.ALIGN_LEFT | 
                       wx.ALIGN_CENTER_VERTICAL)
        
        sb = wx.StaticBox(self, -1, "Model 3201")
        self.vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)

        self.vbox.AddMany([
            (10,12,0),
            (self.hbox1, 0, wx.EXPAND | wx.ALL),
            (0,15,0),
            (self.hbox2, 0, wx.EXPAND),
            (0,20,0),
            (self.hbox3, 0, wx.EXPAND),
            (0,12,0),
            (self.hboxi, 0, wx.EXPAND),
            (0,5,0),
            (self.hbox5, 0, wx.EXPAND),
            (0,22,0),
            (self.hbox4, 0, wx.EXPAND),
            (10,10,0)
            ])
       
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.Layout()

        self.btn_auto.Bind(wx.EVT_BUTTON, self.OprAuto)
        self.btn_volts.Bind(wx.EVT_BUTTON, self.VoltsCmd)
        self.btn_amps.Bind(wx.EVT_BUTTON, self.AmpsCmd)
        self.Bind(wx.EVT_TIMER, self.TimerServ, self.timer)
        self.Bind(wx.EVT_TIMER, self.UsbTimer, self.timer_usb)
        self.btn_tog.Bind(wx.EVT_BUTTON, self.OnOffPort)

        self.Bind(wx.EVT_RADIOBUTTON, self.PortSpeedChanged)

        self.rbtn_p1.SetValue(True)
        self.rbtn_ss1.SetValue(True)
        self.port = 1

        self.update_controls()


    def OprAuto(self, evt):
        if(self.top.auto_flg):
            self.stop_auto()
        else:
            self.start_auto()

    def VoltsCmd(self, evt):
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

    def AmpsCmd(self, evt):
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

    def TimerServ(self, evt):
        if(self.top.con_flg):
            if(self.usb_flg == False):
                self.on_port(self.pcnt)
        
                self.pcnt = self.pcnt + 1
                if(self.pcnt >= 4):
                    self.pcnt = 0
        else:
            self.stop_auto()
            self.disable_buttons()

    def UsbTimer(self, e):
        self.timer_usb.Stop()
        usbDev.get_tree_change(self.top)
        self.rbtn_p1.Enable()
        self.rbtn_p2.Enable()
        self.rbtn_p3.Enable()
        self.rbtn_p4.Enable()
        self.btn_tog.Enable()
        self.usb_flg = False 

    def OnOffPort(self, evt):
        if self.usb_flg == False:
            self.btnStat = not self.btnStat
            if(self.btnStat):
                self.disable_all_rb()
                self.port_on_cmd(self.port)
            else:
                self.enable_all_rb()
                self.port_off_cmd(self.port)
            self.update_port_stat()

    def PortSpeedChanged(self, e):
        rb = e.GetEventObject()
        id = rb.GetId()

        if(id >= ID_RBTN_SS0):
            id = id - ID_RBTN_SS0
            self.speed_cmd(id)
        else:
            id = id - ID_RBTN_P1
            self.port = id + 1
            self.check_ss_support()

    def disable_all_rb(self):
        self.btn_tog.SetLabel('OFF')
        self.rbtn_p1.Disable()
        self.rbtn_p2.Disable()
        self.rbtn_p3.Disable()
        self.rbtn_p4.Disable()
        self.rbtn_ss0.Disable()
        self.rbtn_ss1.Disable()

    def enable_all_rb(self):
        self.btn_tog.SetLabel('ON')
        self.rbtn_p1.Enable()
        self.rbtn_p2.Enable()
        self.rbtn_p3.Enable()
        self.rbtn_p4.Enable()
        self.rbtn_ss0.Enable()
        self.rbtn_ss1.Enable()

    def update_port_stat(self):
        if(self.btnStat):
            self.btn_tog.SetLabel('OFF')
            for i in range(4):
                if(i == (self.port - 1)):
                    self.led[i].SetBackgroundColour('Red')
                else:
                    self.led[i].SetBackgroundColour('black')
                self.led[i].SetLabel("")
                self.rbtn[i].Disable()    
            self.rbtn_ss0.Disable()
            self.rbtn_ss1.Disable()
        else:
            self.btn_tog.SetLabel('ON')
            for i in range(4):
                self.led[i].SetBackgroundColour('black')
                self.led[i].SetLabel("")
                self.rbtn[i].Enable()
            self.rbtn_ss0.Enable()
            self.rbtn_ss1.Enable()

    def check_ss_support(self):
        if(self.port > 2):
            self.rbtn_ss0.Disable()
            self.rbtn_ss1.Disable()
        else:
            self.rbtn_ss0.Enable()
            self.rbtn_ss1.Enable()

    def get_switch_port(self):
        return self.port

    def update_volts(self, str):
        self.st_volts.SetLabel(str)

    def update_amps(self, str):
        self.st_amps.SetLabel(str)

    def get_interval(self):
        tival = self.tc_ival.GetValue()
        if (tival == ""):
            tival = "0"
        return tival

    def stop_auto(self):
        self.btn_auto.SetLabel("Auto")
        self.enable_port_ctrl()
        self.top.enable_start()
        self.top.auto_flg = False
        self.timer.Stop()
        self.port_off_cmd(self.pcnt+1)
        self.btnStat = False
        self.btn_tog.SetLabel('ON')
        self.update_port_stat()

    def start_auto(self):
        self.top.auto_flg = True
        self.btn_auto.SetLabel("Stop")
        if(self.timer.IsRunning() == False):
            self.disable_port_ctrl()
            self.top.disable_start()
            self.tog_flg = False
            self.timer.Start(int(self.get_interval()))

    def speed_cmd(self,val):
        cmd = 'superspeed'+' '+str(val)+'\r\n'
        res, outstr = serialDev.send_port_cmd(self.top.devHand,cmd)
        if res == 0:
            outstr = outstr.replace('s', 'S')
            outstr = outstr.replace('1', 'Enabled')
            outstr = outstr.replace('0', 'Disabled')
        
        self.top.print_on_log(outstr)

    def port_on_cmd(self, pno):
        cmd = 'port'+' '+str(pno)+'\r\n'
        res, outstr = serialDev.send_port_cmd(self.top.devHand, cmd)
        if res == 0:
            outstr = outstr.replace('p', 'P')
            outstr = outstr.replace('1', '1 ON')
            outstr = outstr.replace('2', '2 ON')
            outstr = outstr.replace('3', '3 ON')
            outstr = outstr.replace('4', '4 ON')
            if(self.top.auto_flg):
                outstr = outstr[:-2] + "; Other Ports are OFF\n"
            self.top.print_on_log(outstr)
        
        if(self.top.get_delay_status()):
            self.keep_delay()
        
    def port_off_cmd(self, pno):
        cmd = 'port'+' '+'0'+'\r\n'
        res, outstr = serialDev.send_port_cmd(self.top.devHand, cmd)
        if res == 0:
            outstr = outstr.replace('p', 'P')
            outstr = outstr.replace('0', ""+str(pno)+" OFF")
            self.top.print_on_log(outstr)
        
        if(self.top.get_delay_status()):
            self.keep_delay()

    def keep_delay(self):
        self.btn_tog.Disable()
        self.rbtn_p1.Disable()
        self.rbtn_p2.Disable()
        self.rbtn_p3.Disable()
        self.rbtn_p4.Disable()
        self.usb_flg = True
        self.timer_usb.Start(int(self.top.get_enum_delay()))

    def disable_model(self):
        self.btn_tog.Disable()
        self.rbtn_p1.Disable()
        self.rbtn_p2.Disable()
        self.rbtn_p3.Disable()
        self.rbtn_p4.Disable()
        
        self.btn_volts.Disable()
        self.btn_amps.Disable()
        self.rbtn_ss0.Disable()
        self.rbtn_ss1.Disable()
        self.btn_auto.Disable()

    def enable_model(self):
        self.btn_tog.Enable()
        self.rbtn_p1.Enable()
        self.rbtn_p2.Enable()
        self.rbtn_p3.Enable()
        self.rbtn_p4.Enable()
        self.btn_volts.Enable()
        self.btn_amps.Enable()
        self.btn_auto.Enable()
        self.check_ss_support()

    def update_controls(self):
        if(self.top.con_flg):
            #self.top.UpdateSingle("3201 Switch", 2)
            self.top.UpdateSingle("", 2)
            self.top.print_on_log("3201 Switch Connected!\n")
            self.btn_tog.Enable()
            self.btn_volts.Enable()
            self.btn_amps.Enable()
            self.btn_auto.Enable()
            self.rbtn_ss1.SetValue(True)
            if(self.top.init_flg):
                self.speed_cmd(self.get_speed_input())
                self.top.init_flg = False
        else:
            self.disable_buttons()
    
    def disable_buttons(self):
        self.btn_tog.Disable()
        self.btn_volts.Disable()
        self.btn_amps.Disable()
        self.btn_auto.Disable()

        for i in range(len(self.led)):
            self.led[i].SetBackgroundColour('black')
            self.led[i].SetLabel("")
        
    def get_speed_input(self):
        if(self.rbtn_ss1.GetValue()):
            return 1
        else:
            return 0

    def disable_auto(self):
        self.rbtn_p1.Disable()
        self.rbtn_p2.Disable()
        self.rbtn_p3.Disable()
        self.rbtn_p4.Disable()
        self.btn_auto.Disable()
        self.btn_volts.Disable()
        self.btn_amps.Disable()
        self.btn_tog.Disable()
        
    def enable_auto(self):
        self.rbtn_p1.Enable()
        self.rbtn_p2.Enable()
        self.rbtn_p3.Enable()
        self.rbtn_p4.Enable()
        self.btn_auto.Enable()
        self.btn_volts.Enable()
        self.btn_amps.Enable()
        self.btn_tog.Enable()
        
    def disable_port_ctrl(self):
        self.rbtn_p1.Disable()
        self.rbtn_p2.Disable()
        self.rbtn_p3.Disable()
        self.rbtn_p4.Disable()
        self.rbtn_ss0.Disable()
        self.rbtn_ss1.Disable()
        
    def enable_port_ctrl(self):
        self.rbtn_p1.Enable()
        self.rbtn_p2.Enable()
        self.rbtn_p3.Enable()
        self.rbtn_p4.Enable()
        self.check_ss_support()

    def on_port(self, pno):
        self.port_on_cmd(pno+1)
        self.update_led_status(pno)

    def update_led_status(self, pno):
         for i in range(len(self.led)):
            if(i == pno):
                self.led[i].SetBackgroundColour("red")
            else:
                self.led[i].SetBackgroundColour("black")
            self.led[i].SetLabel("")

    def port_led_update(self, pno, stat):
        if(stat):
            for i in range(4):
                if(i == pno):
                    self.led[i].SetBackgroundColour('Red')
                else:
                    self.led[i].SetBackgroundColour('black')
                self.led[i].SetLabel("")
        else:
            for i in range(4):
                self.led[i].SetBackgroundColour('black')
                self.led[i].SetLabel("")