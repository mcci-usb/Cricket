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
        
        self.SetMinSize((290, 260))
        
        self.st_p1 = wx.StaticText(self, -1, "Port 1", size = (40,15))
        self.st_p2 = wx.StaticText(self,-1, "Port 2", size = (40,15))
        self.st_p3 = wx.StaticText(self, -1, "Port 3", size = (40,15))
        self.st_p4 = wx.StaticText(self, -1, "Port 4", size = (40,15))

        self.picf = wx.Bitmap ("btn_off.png", wx.BITMAP_TYPE_ANY)
        self.picn = wx.Bitmap ("btn_on.png", wx.BITMAP_TYPE_ANY)
        self.btn_p1 = wx.BitmapButton(self, 0, self.picf, size= (55,20))
        self.btn_p2 = wx.BitmapButton(self, 1, self.picf, size= (55,20))
        self.btn_p3 = wx.BitmapButton(self, 2, self.picf, size= (55,20))
        self.btn_p4 = wx.BitmapButton(self, 3, self.picf, size= (55,20))

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
        
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxi = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox6 = wx.BoxSizer(wx.HORIZONTAL)

        self.hboxs1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxs2 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.hboxs1.Add(self.st_p1,0, flag=wx.ALIGN_LEFT | wx.LEFT | 
                       wx.ALIGN_CENTER_VERTICAL, border=20 )
        
        self.hboxs1.Add(self.btn_p1, flag=wx.ALIGN_CENTER_VERTICAL | 
                       wx.LEFT,  border = -1)
        self.hboxs1.Add(self.st_p2, 0, flag=wx.ALIGN_LEFT | 
                       wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 20 )
        self.hboxs1.Add(self.btn_p2, wx.ALIGN_CENTER | 
                         wx.ALIGN_CENTER_VERTICAL, border = 85 )
        
        self.hboxs2.Add(self.st_p3, flag=wx.ALIGN_LEFT | wx.LEFT | 
                       wx.ALIGN_CENTER_VERTICAL, border=20 )
        
        self.hboxs2.Add(self.btn_p3, flag=wx.ALIGN_CENTER_VERTICAL | 
                       wx.LEFT,  border = -1)
        self.hboxs2.Add(self.st_p4, 0, flag=wx.ALIGN_LEFT | 
                       wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border = 20 )
        self.hboxs2.Add(self.btn_p4, wx.ALIGN_CENTER | 
                         wx.ALIGN_CENTER_VERTICAL, border = 85 )

        self.hbox1.Add(self.hboxs1, flag=wx.ALIGN_CENTER_VERTICAL )
        self.hbox1.Add(0,1,0)
        self.hbox2.Add(self.hboxs2, flag=wx.ALIGN_CENTER_VERTICAL )
        self.hbox1.Add(0,1,0)
        
        self.hbox3.Add(self.st_ss,0 , flag=wx.ALIGN_LEFT | wx.LEFT, 
                       border=20 )
        self.hbox3.Add(self.rbtn_ss1, flag=wx.ALIGN_LEFT | wx.LEFT, border = 20)
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
        self.hbox6.Add(self.st_duty, flag=wx.ALIGN_LEFT | wx.LEFT | 
                       wx.ALIGN_CENTER_VERTICAL, border=20)
        self.hbox6.Add(self.tc_duty,0, wx.ALIGN_CENTER | 
                         wx.ALIGN_CENTER_VERTICAL)
        self.hbox6.Add(self.st_ps,0, wx.ALIGN_CENTER_VERTICAL)

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
            (10,10,0),
            (self.hbox6, 0, wx.EXPAND ),
            (0,20,0)
            ])
       
        self.SetSizer(self.vbox)
        self.SetAutoLayout(True)
        self.vbox.Fit(self)
        self.Layout()

        self.btn_auto.Bind(wx.EVT_BUTTON, self.OprAuto)
        self.btn_volts.Bind(wx.EVT_BUTTON, self.VoltsCmd)
        self.btn_amps.Bind(wx.EVT_BUTTON, self.AmpsCmd)
        self.Bind(wx.EVT_TIMER, self.TimerServ, self.timer)
        self.Bind(wx.EVT_TIMER, self.UsbTimer, self.timer_usb)
        
        self.Bind(wx.EVT_RADIOBUTTON, self.PortSpeedChanged)
        self.Bind(wx.EVT_BUTTON, self.OnOffPort, self.btn_p1)
        self.Bind(wx.EVT_BUTTON, self.OnOffPort, self.btn_p2)
        self.Bind(wx.EVT_BUTTON, self.OnOffPort, self.btn_p3)
        self.Bind(wx.EVT_BUTTON, self.OnOffPort, self.btn_p4)

        self.tc_duty.SetMaxLength(2)

        self.rbtn = []
        self.rbtn.append(self.btn_p1)
        self.rbtn.append(self.btn_p2)
        self.rbtn.append(self.btn_p3)
        self.rbtn.append(self.btn_p4)

        self.btnStat = [False, False, False, False]
        self.rbtn_ss1.SetValue(True)
        
        self.enable_controls(False)


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

    # Event Handler for Volts Button
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

    # Event Handler for Amps Button
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

    # Event handler for Speed change Radio buttons
    def PortSpeedChanged(self, e):
        rb = e.GetEventObject()
        id = rb.GetId()

        if id == ID_RBTN_SS1:
            self.speed_cmd(1)
        elif id == ID_RBTN_SS0:
            self.speed_cmd(0)

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
                    if(self.pcnt >= 4):
                        self.pcnt = 0
                    self.port_on(self.pcnt+1, True)
                    if self.auto_flg:
                        self.timer.Start(self.OnTime)
                        self.On_flg = True

    # Timer Event for USB Tree View Changes
    def UsbTimer(self, e):
        self.timer_usb.Stop()
        usbDev.get_tree_change(self.top)
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
        self.enable_auto_controls(stat)
        
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

    # Enable/Disable Auto Controls
    def enable_auto_controls(self, stat):
        if(stat):
            self.btn_auto.Enable()
            self.tc_ival.Enable()
            self.tc_duty.Enable()
        else:
            if self.top.mode != MODE_AUTO:
                self.btn_auto.Disable()
            self.tc_ival.Disable()
            self.tc_duty.Disable()

    # Enable/Disable Volt/Amp Controls
    def enable_va_controls(self, stat):
        if(stat):
            self.btn_amps.Enable()
            self.btn_volts.Enable()
        else:
            self.btn_amps.Disable()
            self.btn_volts.Disable()

    # Calculate Port ON Time and OFF Time from Interval and Duty
    def get_all(self):
        self.interval = int(self.get_interval())
        self.duty = int(self.get_duty())

        self.OnTime = self.interval* (self.duty/100)
        self.OffTime = self.interval - self.OnTime

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

    # Print the Voltage level in Label
    def update_volts(self, str):
        self.st_volts.SetLabel(str)

    # Print the Amps level in Label
    def update_amps(self, str):
        self.st_amps.SetLabel(str)

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

    # Speed change command to 3141 Device
    def speed_cmd(self,val):
        cmd = 'superspeed'+' '+str(val)+'\r\n'
        res, outstr = serialDev.send_port_cmd(self.top.devHand,cmd)
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