##############################################################################
# 
# Module: loopWindow.py
#
# Description:
#     Loop Window for Switch Model3201,Model3141, Model2101
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

# Own modules
import thControl

from uiGlobals import *
import devControl as model

##############################################################################
# Utilities
##############################################################################
class LoopWindow(wx.Window):
    """
    A class loopWindow with init method
    Switching Ports of Slected Model in a Loop
    """
    def __init__(self, parent, top):
        """
        Loop Window for Switch Model3201,Model3141, Model2101 
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

        # SET BACKGROUND COLOUR TO White
        self.SetBackgroundColour("White")

        # Self.SetMinSize((200,200))

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

        self.swid = None
        self.swkey = None

        self.portno = 0

        # Oct 08 2022
        self.hb_sw = wx.BoxSizer(wx.HORIZONTAL)
        self.hb_port = wx.BoxSizer(wx.HORIZONTAL)
        self.hb_peri = wx.BoxSizer(wx.HORIZONTAL)
        self.hb_duty = wx.BoxSizer(wx.HORIZONTAL)
        self.hb_repe = wx.BoxSizer(wx.HORIZONTAL)
        self.hb_finc = wx.BoxSizer(wx.HORIZONTAL)
        self.hb_btn = wx.BoxSizer(wx.HORIZONTAL)


        self.st_switch   = wx.StaticText(self, -1, "Select Switch ", size=(-1, -1), 
                                      style = wx.ALIGN_LEFT)
        
        self.cb_switch = wx.ComboBox(self,
                                     size=(145,-1),
                                     style = wx.TE_PROCESS_ENTER)

        self.hb_sw.AddMany([
            (self.st_switch, 0, wx.EXPAND),
            ((20,0), 1, wx.EXPAND),
            (self.cb_switch, 0, wx.EXPAND),
            ((-1,0), 1, wx.EXPAND)
            ])


        self.st_port   = wx.StaticText(self, -1, "Select Port", size=(-1,15), 
                                      style = wx.ALIGN_LEFT)
        self.cb_psel = wx.ComboBox(self,
                                     size=(53,-1),
                                     style = wx.TE_PROCESS_ENTER)

        
        self.hb_port.AddMany([
            ((10,0), 0, wx.EXPAND),
            (self.st_port, 0, wx.EXPAND),
            ((25,0), 0, wx.EXPAND),
            (self.cb_psel, 0, wx.EXPAND),
            ((-1,0), 1, wx.EXPAND)
            ])

        
        self.st_per   = wx.StaticText(self, -1, "ON Time", size=(-1,15), 
                                      style = wx.ALIGN_LEFT)
        self.tc_per   = wx.TextCtrl(self, ID_TC_PERIOD, "1000", size=(50,-1), 
                                    style = wx.TE_CENTRE |
                                    wx.TE_PROCESS_ENTER,
                                    validator=NumericValidator(), 
                                    name="ON/OFF period")
        self.st_ms   = wx.StaticText(self, -1, "ms", size=(-1,15), 
                                     style = wx.ALIGN_CENTER)

        self.hb_peri.AddMany([
            ((22,0), 0, wx.EXPAND),
            (self.st_per, 0, wx.EXPAND),
            ((23,0), 0, wx.EXPAND),
            (self.tc_per, 0, wx.EXPAND),
            ((10,0), 0, wx.EXPAND),
            (self.st_ms, 0, wx.EXPAND),
            ((-1,0), 1, wx.EXPAND)
            ])


        self.st_duty   = wx.StaticText(self, -1, "OFF Time", size=(-1,15), 
                                       style = wx.ALIGN_LEFT)
        self.tc_duty   = wx.TextCtrl(self, ID_TC_DUTY, "1000", size=(50,-1), 
                                     style = wx.TE_CENTRE | 
                                     wx.TE_PROCESS_ENTER,
                                     validator=NumericValidator(), 
                                     name="ON/OFF period")
        self.st_ps   = wx.StaticText(self, -1, "ms", size=(-1,15), 
                                     style = wx.ALIGN_CENTER)

        self.hb_duty.AddMany([
            ((20,0), 0, wx.EXPAND),
            (self.st_duty, 0, wx.EXPAND),
            ((20,0), 0, wx.EXPAND),
            (self.tc_duty, 0, wx.EXPAND),
            ((10,0), 0, wx.EXPAND),
            (self.st_ps, 0, wx.EXPAND),
            ((-1,0), 1, wx.EXPAND)
            ])


        self.st_cycle   = wx.StaticText(self, -1, "Repeat", size=(-1,15), 
                                        style = wx.ALIGN_LEFT)
        self.tc_cycle   = wx.TextCtrl(self, ID_TC_CYCLE, "20", size=(50,-1), 
                                      style = wx.TE_CENTRE |
                                      wx.TE_PROCESS_ENTER,
                                      validator=NumericValidator(), 
                                      name="ON/OFF period")
        
        self.cb_cycle = wx.CheckBox (self, -1, label = 'Until Stopped')
        

        self.hb_repe.AddMany([
            ((26,0), 0, wx.EXPAND),
            (self.st_cycle, 0, wx.EXPAND),
            ((24,0), 0, wx.EXPAND),
            (self.tc_cycle, 0, wx.EXPAND),
            ((10,0), 0, wx.EXPAND),
            (self.cb_cycle, 0, wx.EXPAND),
            ((-1,0), 1, wx.EXPAND)
            ])


        self.st_finicnt   = wx.StaticText(self, -1, "Finished Count", size=(-1,-1))
        self.st_cnt_port   = wx.StaticText(self, -1, "----", size=(-1, -1), 
                                      style = wx.ALIGN_CENTER)

        self.hb_finc.AddMany([
            (self.st_finicnt, 0, wx.EXPAND),
            ((20,0), 0, wx.EXPAND),
            (self.st_cnt_port, 0, wx.EXPAND),
            ((-1,0), 1, wx.EXPAND)
            ])


        self.btn_start = wx.Button(self, ID_BTN_START, "Start", size=(60,25))
        self.hb_btn.AddMany([
            ((-1,0), 1, wx.EXPAND),
            (self.btn_start, 0, wx.EXPAND),
            ((-1,0), 1, wx.EXPAND)
            ])


        self.tc_per.SetToolTip(wx.ToolTip("ON/OFF Interval. Min: 1 sec, "
                                          "Max: 60 sec"))
        self.btn_start.SetToolTip(wx.ToolTip("ON/OFF a selected port for a "
                                            "interval until cycle completed"))
        
        # The wx.TextCtrl period entering upto '5' Digits
        self.tc_per.SetMaxLength(5)
        # The wx.TextCtrl duty entering upto '2' Digits
        self.tc_duty.SetMaxLength(5)
        # The wx.TextCtrl Repeat entering upto '3' Digits
        self.tc_cycle.SetMaxLength(3)
        # The wx.combobox port selection entering upto '1' Digits
        self.cb_psel.SetMaxLength(1)

        self.bs_vbox = wx.BoxSizer(wx.VERTICAL)
        
        # The Timer class allows you to execute 
        # Code at specified intervals.
        self.timer = wx.Timer(self)  
        self.timer_usb = wx.Timer(self)


        self.hb_outer = wx.BoxSizer(wx.HORIZONTAL)
        self.vb_contnr = wx.BoxSizer(wx.VERTICAL)

        self.vb_contnr.AddMany([
            ((0,20), 1, wx.EXPAND),
            (self.hb_sw, 0, wx.EXPAND),
            ((0,20), 1, wx.EXPAND),
            (self.hb_port, 0, wx.EXPAND),
            ((0,20), 1, wx.EXPAND),
            (self.hb_peri, 0, wx.EXPAND),
            ((0,20), 1, wx.EXPAND),
            (self.hb_duty, 0, wx.EXPAND),
            ((0,20), 1, wx.EXPAND),
            (self.hb_repe, 0, wx.EXPAND),
            ((0,20), 1, wx.EXPAND),
            (self.hb_finc, 0, wx.EXPAND),
            ((0,20), 1, wx.EXPAND),
            (self.hb_btn, 0, wx.EXPAND),
            ((0,20), 1, wx.EXPAND)
            ])

  
        self.hb_outer.AddMany([
            ((-1,0), 1, wx.EXPAND),
            (self.vb_contnr, 1, wx.EXPAND),
            ((-1,0), 1, wx.EXPAND),
            ])


        # Bind the button event to handler
        self.btn_start.Bind(wx.EVT_BUTTON, self.StartAuto)
        # Bind the timer event to handler
        self.Bind(wx.EVT_TIMER, self.TimerServ, self.timer)
        self.Bind(wx.EVT_TIMER, self.UsbTimer, self.timer_usb)

        self.cb_switch.Bind(wx.EVT_COMBOBOX, self.SwitchChange, self.cb_switch)
        
        # Set size of frame
        self.SetSizer(self.hb_outer)
        self.hb_outer.Fit(self)
        self.Layout()

        self.enable_controls(True)

    def update_sw_selector(self, swdict):
        self.cb_switch.Clear()
        for key, val in swdict.items():
            swstr = ""+val+"("+key+")"
            self.cb_switch.Append(swstr)
        self.cb_switch.SetSelection(0)
        self.Update_port_count()

    def Update_port_count(self):
        self.swid = self.cb_switch.GetValue()
        self.swkey = self.swid.split("(")[1][:-1]
        swname = self.swid.split("(")[0]
        self.set_port_list(portCnt[swname])

    def SwitchChange(self, evt):
        self.Update_port_count()

    def StartAuto(self, evt):
        """
        Event handler for Loop Window Start/Stop

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            evt:The event parameter in the loopwindow method is an 
            object specific to a particular event type.
            event hanlder for startAuto
        Returns:
            None
        """
        if(self.start_flg):
            # print status on Logwindow
            self.top.print_on_log("Loop Mode Interrupted\n")
            # function of loop stop
            self.stop_loop()
        else:
            # get the values for three controls
            self.get_all_three()
            if(self.usb_dly_warning() and self.onoff_dly_warning()):
                #function of start loop
                self.top.action_reset()
                self.start_loop()

    def TimerServ(self, evt):
        """
        Timer event handling device On/Off in Loop Window
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            evt:The event parameter in the loopwindow method is an 
            object specific to a particular event type.
        Returns:
            None
        """
        if self.top.con_flg:
            self.pulse_flg = True
            if(self.usb_flg == False):
                # timerstop
                self.timer.Stop()
                self.pulse_flg = False
                if(self.On_flg):
                    self.port_on(self.portno, False)
                    self.On_flg = False
                    self.cycleCnt = self.cycleCnt + 1
                    self.st_cnt_port.SetLabel(str(self.cycleCnt))
                    if(self.cb_cycle.GetValue() != True):
                        self.tc_cycle.SetValue(str(self.cycle))
                        if(self.cycleCnt >= self.cycle):
                            self.tc_cycle.SetValue(str(self.cycle))
                            # print message for loop Mode completed 
                            # once duty cycle is over
                            self.top.print_on_log("Loop Mode Completed\n")
                            self.stop_loop()
                            self.top.action_summary()
                        else:    
                            self.timer.Start(self.OffTime)
                    else:    
                        self.timer.Start(self.OffTime)
                else:
                    self.port_on(self.portno, True)
                    self.timer.Start(self.OnTime)
                    self.On_flg = True
    
    def UsbTimer(self, e):
        """
        Timer Service for USB Device Tree View Changes 
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            e:The event parameter in loopwindow method is an 
            object specific to a particular event type.
            event hanlder for UsbTimer
        Returns:
            None
        """ 
        self.timer_usb.Stop()
        try:
            thControl.get_tree_change(self.top)
        except:
            self.top.print_on_log("USB Read Error!")
        self.usb_flg = False
        
        if(self.start_flg == True & self.pulse_flg == True):
            self.timer.Start(1)
    
    def usb_dly_warning(self):
        """
        Show warning message when the USB delay is greater than Loop
        mode interval.
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            Boolean: True- when wish to continue the Loop mode, 
            False - when wish to exit the Loop mode           
        """
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
    
    def onoff_dly_warning(self):
        """
        Check ON/OFF Time interval if it is < 1000 msec 
        popup a warning message

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            Boolean: True - when wish to continue the Loop mode
            False - when wish to exit the Loop mode
        """ 
        self.get_all_three()
        if (self.OnTime < 1000 or self.OffTime < 1000):
            title = ("Port ON/OFF time warning!")
            msg = ("For Device safety, it is recommended to keep "
                       "Port ON/OFF time > 1000 msec."
                       "\nClick Yes if you wish to continue"
                       "\nClick No to exit the Loop mode")
            dlg = wx.MessageDialog(self, msg, title, wx.NO|wx.YES)
            if(dlg.ShowModal() == wx.ID_YES):
                return True
            else:
                return False
        return True
    
    def get_on_time(self):
        """
        Read the period of Loop Mode
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            Loop mode period in String format. 
        """
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
  
    def get_off_time(self):
        """
        Get Duty value of loop mode
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            Duty value in String format
        """
        # Print values of text control duty buttons True
        duty = self.tc_duty.GetValue()
        if (duty == ""):
            duty = "50"
        ival = int(duty)
        if(ival == 0):
            ival = 1
        # Set the value of duty "50"
        self.tc_duty.SetValue(str(ival))
        return self.tc_duty.GetValue()
    
    def get_cycle(self):
        """
        Get Cycle value of loop mode
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            Cycle value in String format
        """
        cycle = self.tc_cycle.GetValue()
        if (cycle == ""):
            cycle = "20"
        cval = int(cycle)
        if(cval < 1):
            cval = 1

        self.tc_cycle.SetValue(str(cval))
        return self.tc_cycle.GetValue()

    def get_all_three(self):
        """
        Get Period, Duty and Cycle values then
        calculate ON Time and OFF Time
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.OnTime = int(self.get_on_time())
        self.OffTime = int(self.get_off_time())
        self.cycle = int(self.get_cycle())

    def get_loop_param(self):
        """
        Get the loop mode parameters
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            OnTime, OffTime, and Duty in String format
        """
        self.get_all_three()
        return self.OnTime, self.OffTime

    def set_loop_param(self, onTime, offTime):
        self.tc_per.SetValue(str(onTime))
        self.tc_duty.SetValue(str(offTime))

    def start_loop(self):
        """
        Start Loop Mode
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.cval = self.cb_psel.GetValue()
        self.portno = int(self.cval)
        self.start_flg = True
        self.top.set_mode(MODE_LOOP)
        # Command for loop start message
        self.loop_start_msg()
        # Button Label name as Stop
        self.btn_start.SetLabel("Stop")
        # self.stop_loop_mode()
        if(self.timer.IsRunning() == False):
            self.cycleCnt = 0
            self.On_flg = True
            self.port_on(self.portno, True)
            # Start the timer
            self.timer.Start(self.OnTime)
    
    def loop_start_msg(self): 
        """
        Loop Mode start message print on the Log Window
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
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
    
    def stop_loop(self):
        """
        Stop Loop Mode - 1. When click stop 2. When cycle completed
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.start_flg = False
        self.btn_start.SetLabel("Start")
        self.top.set_mode(MODE_MANUAL)
        # Print the message if Loop Mode Stopped
        self.top.print_on_log("Loop Mode Stopped!\n")
        # Timer stop
        self.timer.Stop()
    
    def port_on(self, portno, stat):
        """
        Port ON/OFF command send to Connected Device Module
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            portno: port number of the Model
            stat: to update the status of Port in UI
        Returns:
            None
        """
        self.top.port_on(self.swkey, portno, stat)
        # self.top.panel.lpanel.p
        # Getting delay status
        if(self.top.get_delay_status()):
            self.keep_delay()

    def keep_delay(self):
        """
        Start the USB delay Timer
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.usb_flg = True
        self.timer_usb.Start(int(self.top.get_enum_delay()))

    def update_controls(self, mode):
        """
        Enable/Disable widgets when mode changed
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            mode: Manual Mode/Auto Mode/Loop Mode
        Returns:
            None
        """
        if mode == MODE_MANUAL:
            self.enable_controls(True)
        else:
            self.enable_controls(False)
            self.st_cnt_port.SetLabel("")
    
    def enable_controls(self, stat):
        """
        Enable control widgets

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            stat:enable for all loop mode widgets else disable
        Returns:
            None
        """
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
    
    def set_port_list(self, port):
        """
        Set Port list to in Dropdown Control, when Device gets connected

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            port: Number of ports available in the selected Model
        Returns:
            None
        """
        self.cb_psel.Clear()
        for i in range(port):
            self.cb_psel.Append(str(i+1))
        self.cb_psel.SetSelection(0)
    
    def device_disconnected(self):
        """
        Stop the Loop mode, when device get disconnected
        
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        if self.start_flg:
            self.stop_loop()