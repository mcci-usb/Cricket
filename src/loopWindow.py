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
#     V2.4.0 Wed July 14 2021 15:20:05   Seenivasan V
#       Module created
##############################################################################
# Lib imports
import wx

# Own modules
import thControl

from uiGlobals import *
import control2101 as d2101
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

        self.portno = 0

        self.cb_psel = wx.ComboBox(self,
                                     size=(53,-1),
                                     style = wx.TE_PROCESS_ENTER)
        self.st_port   = wx.StaticText(self, -1, "Port ", size=(50,15), 
                                      style = wx.ALIGN_RIGHT)
     
        
        self.st_per   = wx.StaticText(self, -1, "Period ", size=(50,15), 
                                      style = wx.ALIGN_RIGHT)
        self.tc_per   = wx.TextCtrl(self, ID_TC_PERIOD, "2000", size=(50,-1), 
                                    style = wx.TE_CENTRE |
                                    wx.TE_PROCESS_ENTER,
                                    validator=NumericValidator(), 
                                    name="ON/OFF period")
        self.st_ms   = wx.StaticText(self, -1, "ms", size=(30,15), 
                                     style = wx.ALIGN_CENTER)

        self.st_duty   = wx.StaticText(self, -1, "Duty ", size=(50,15), 
                                       style = wx.ALIGN_RIGHT)
        self.tc_duty   = wx.TextCtrl(self, ID_TC_DUTY, "50", size=(50,-1), 
                                     style = wx.TE_CENTRE | 
                                     wx.TE_PROCESS_ENTER,
                                     validator=NumericValidator(), 
                                     name="ON/OFF period")
        self.st_ps   = wx.StaticText(self, -1, "%", size=(30,15), 
                                     style = wx.ALIGN_CENTER)

        self.st_cycle   = wx.StaticText(self, -1, "Repeat ", size=(50,15), 
                                        style = wx.ALIGN_RIGHT)
        self.tc_cycle   = wx.TextCtrl(self, ID_TC_CYCLE, "20", size=(50,-1), 
                                      style = wx.TE_CENTRE |
                                      wx.TE_PROCESS_ENTER,
                                      validator=NumericValidator(), 
                                      name="ON/OFF period")
        self.st_cnt   = wx.StaticText(self, -1, "", size=(15,10), 
                                      style = wx.ALIGN_CENTER)
        self.cb_cycle = wx.CheckBox (self, -1, label = 'Until Stopped')
        self.st_repeat_cnt   = wx.StaticText(self, -1, "Finished Count", size=(-1,-1))
        self.st_cnt_port   = wx.StaticText(self, -1, "----", size=(-1, -1), 
                                      style = wx.ALIGN_CENTER)

        self.btn_start = wx.Button(self, ID_BTN_START, "Start", size=(60,25))
        
        self.tc_per.SetToolTip(wx.ToolTip("ON/OFF Interval. Min: 1 sec, "
                                          "Max: 60 sec"))
        self.btn_start.SetToolTip(wx.ToolTip("ON/OFF a selected port for a "
                                            "interval until cycle completed"))
        
        # The wx.TextCtrl period entering upto '5' Digits
        self.tc_per.SetMaxLength(5)
        # The wx.TextCtrl duty entering upto '2' Digits
        self.tc_duty.SetMaxLength(2)
        # The wx.TextCtrl Repeat entering upto '3' Digits
        self.tc_cycle.SetMaxLength(3)
        # The wx.combobox port selection entering upto '1' Digits
        self.cb_psel.SetMaxLength(1)
        
        # Creates BoxSizer in horizontal
        self.bs_psel = wx.BoxSizer(wx.HORIZONTAL)
        self.bs_pers = wx.BoxSizer(wx.HORIZONTAL)
        self.bs_duty = wx.BoxSizer(wx.HORIZONTAL)
        self.bs_cycle = wx.BoxSizer(wx.HORIZONTAL)
        self.bs_cnt = wx.BoxSizer(wx.HORIZONTAL)
        self.bs_btn = wx.BoxSizer(wx.HORIZONTAL)
        
        self.bs_psel.Add(40,0,0)
        self.bs_psel.Add(self.st_port,0, wx.ALIGN_CENTER)
        self.bs_psel.Add(15,20,0)
        self.bs_psel.Add(self.cb_psel,0, wx.ALIGN_CENTER | 
                         wx.ALIGN_CENTER_VERTICAL)
        self.bs_psel.Add(40,0,0)

        self.bs_pers.Add(40,0,0)
        self.bs_pers.Add(self.st_per,0, wx.ALIGN_CENTER_VERTICAL)
        self.bs_pers.Add(15,20,0)  #height changed here
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
        self.bs_cycle.Add(1,0,0)

        self.bs_cnt.Add(40, 0, 0)
        self.bs_cnt.Add(self.st_repeat_cnt, 0,  flag=wx.LEFT | 
                        wx.ALIGN_CENTER_VERTICAL, border=0)
        self.bs_cnt.Add(25, 50, 0)
        self.bs_cnt.Add(self.st_cnt_port,0, wx.ALIGN_CENTER | 
                       wx.LEFT, border = 0)
        self.bs_cnt.Add(1,0,0)

        self.bs_btn.Add(self.btn_start,0, flag = wx.ALIGN_CENTER_HORIZONTAL)
        self.bs_cycle.Add(10,0,0)
        self.bs_cycle.Add(self.cb_cycle, 0, wx.ALIGN_LEFT | 
                                            wx.ALIGN_CENTER_VERTICAL,
                                            border = 0)
        self.bs_cycle.Add(5,10,0)

        # Create static box with naming of Loop Mode
        sb = wx.StaticBox(self, -1, "Loop Mode")
        
        self.bs_vbox = wx.StaticBoxSizer(sb,wx.VERTICAL)
        
        # The Timer class allows you to execute 
        # Code at specified intervals.
        self.timer = wx.Timer(self)
        self.timer_usb = wx.Timer(self)

        self.bs_vbox.AddMany([
            (self.bs_psel,1, wx.EXPAND),
            (self.bs_pers, 1, wx.EXPAND),
            (self.bs_duty, 1, wx.EXPAND),
            (self.bs_cycle, 1, wx.EXPAND),
            (self.bs_cnt, 1, wx.EXPAND),
            (0,10,0),
            (self.bs_btn, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (0,10,0)
            ])
        # Bind the button event to handler
        self.btn_start.Bind(wx.EVT_BUTTON, self.StartAuto)
        # Bind the timer event to handler
        self.Bind(wx.EVT_TIMER, self.TimerServ, self.timer)
        self.Bind(wx.EVT_TIMER, self.UsbTimer, self.timer_usb)
        
        # Set size of frame
        self.SetSizer(self.bs_vbox)
        self.bs_vbox.Fit(self)
        self.Layout()

        self.enable_controls(True)

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
            self.top.print_on_usb("USB Read Error!")
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
        Check ON/OFF Time interval if it is < 500 msec 
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
        if (self.OnTime < 500 or self.OffTime < 500):
            title = ("Port ON/OFF time warning!")
            msg = ("For Device safety, it is recommended to keep "
                       "Port ON/OFF time > 500 msec."
                       "\nClick Yes if you wish to continue"
                       "\nClick No to exit the Loop mode")
            dlg = wx.MessageDialog(self, msg, title, wx.NO|wx.YES)
            if(dlg.ShowModal() == wx.ID_YES):
                return True
            else:
                return False
        return True
    
    def get_period(self):
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
  
    def set_period(self, strval):
        """
        Set Period Called by USB Tree Window when
        there is a need to override the period
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            strval: values in strings
        Returns:
            None
        """
        # Set the  value of str to True
        self.tc_per.SetValue(strval)
     
    def get_duty(self):
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
        self.period = int(self.get_period())
        self.duty = int(self.get_duty())
        self.cycle = int(self.get_cycle())

        self.OnTime = self.period * (self.duty/100)
        self.OffTime = self.period - self.OnTime
    
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
        return self.OnTime, self.OffTime, self.duty

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
        self.top.port_on(portno, stat)
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