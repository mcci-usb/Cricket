##############################################################################
# 
# Module: autoWindow.py
#
# Description:
#     autoWindow for Switch Model 3201, 3141, 2101, 2301
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
#     V2.3.0 Wed April 28 2021 18:50:10 seenivasan
#       Module created
##############################################################################
# Lib imports
import wx

# Own modules
import thControl
from uiGlobals import *

##############################################################################
# Utilities
##############################################################################
class AutoWindow(wx.Window):
    """
    A  class autoWindow with init method

    the autoWindow navigate to Interval with time, Duty and Auto button.
    the Auto Mode is used to switching between 
    the available Port(s) of the selected devices and time stamp.
    """
    def __init__(self, parent, top):
        """
        autoWindow that contains the about dialog elements.

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
        # The Timer class allows you to execute code at specified intervals.
        self.timer = wx.Timer(self)
        self.timer_usb = wx.Timer(self)

        self.st_si   = wx.StaticText(self, -1, "Interval",
                                     style = wx.ALIGN_CENTER_VERTICAL | 
                                     wx.ALIGN_RIGHT, size=(60,-1))
        self.tc_ival   = wx.TextCtrl(self, ID_TC_INTERVAL, "1000", 
                                     size=(50,-1), style = wx.TE_CENTRE |
                                     wx.TE_PROCESS_ENTER,
                                     validator=NumericValidator(), 
                                     name="ON/OFF period")
        self.st_ms   = wx.StaticText(self, -1, "ms", size=(30,15), 
                                     style = wx.ALIGN_CENTER)
        self.st_duty   = wx.StaticText(self, -1, "Duty", 
                                       style = wx.ALIGN_CENTER_VERTICAL | 
                                       wx.ALIGN_RIGHT, size=(60,-1))
        self.tc_duty   = wx.TextCtrl(self, ID_TC_DUTY, "50", size=(50,-1), 
                                     style = wx.TE_CENTRE |
                                     wx.TE_PROCESS_ENTER,
                                     validator=NumericValidator(), 
                                     name="ON/OFF period")
        self.st_ps   = wx.StaticText(self, -1, "%", size=(30,15), 
                                     style = wx.ALIGN_CENTER)

        self.btn_auto = wx.Button(self, ID_BTN_AUTO, "Auto", size=(60,25))

        # The wx.TextCtrl interval value length limit entering upto '5' Digits
        self.tc_ival.SetMaxLength(5)
        # The wx.TextCtrl duty value length limit entering upto '2' Digits
        self.tc_duty.SetMaxLength(2)
        
        # Tooltips display text over an widget elements
        # Set tooltip for switching interval and auto buttons.
        self.tc_ival.SetToolTip(wx.ToolTip("Switching Interval. Min: 1 sec, "
                                           "Max: 60 sec"))
        self.btn_auto.SetToolTip(wx.ToolTip("On/Off each Port "
                                            "for a interval until stop"))
        # Create static box with naming of Auto Mode
        sb = wx.StaticBox(self, -1, "Auto Mode")
        # Creates a boxsizer is vertical
        self.bs_vbox = wx.StaticBoxSizer(sb,wx.VERTICAL)
        # Creates a boxsizer is horizontal
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
        # Set size of frame
        self.SetSizer(self.bs_vbox)
        # Set size of frame
        self.bs_vbox.Fit(self)
        self.Layout()
        
        # Bind the button event to handler
        self.btn_auto.Bind(wx.EVT_BUTTON, self.OprAuto)
        # Bind the timer event to handler
        self.Bind(wx.EVT_TIMER, self.TimerServ, self.timer)
        # Bind the usbtimer event to handler
        self.Bind(wx.EVT_TIMER, self.UsbTimer, self.timer_usb)

        self.enable_controls(True)

    def OprAuto(self, evt):
        """
        if usb delay warning auto mode start or stop an 
        Event Handler for Auto Button.

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            evt: The event parameter in the AutoButton() method is an 
            object specific to a particular event type.
        Returns:
            None
        """
        if(self.auto_flg):
            self.stop_auto()
        else:
            if(self.usb_dly_warning() and self.onoff_dly_warning()):
                self.start_auto() 
    def start_auto(self):
        """
        Start Auto Mode for until stopped

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.auto_flg = True
        # The Lablel to set name as Stop
        self.btn_auto.SetLabel("Stop")
        self.top.set_mode(MODE_AUTO)
        # This function to dispaly the auto start message 
        self.Auto_strat_msg()
        if(self.timer.IsRunning() == False):
            self.timer.Start(int(self.get_interval()))
        
    def stop_auto(self):
        """
        Stop the Auto Mode 

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.auto_flg = False
        # The Lablel to set name as Auto
        self.btn_auto.SetLabel("Auto")
        # The mode set as Manual Mode.
        self.top.set_mode(MODE_MANUAL)

        # Print the string in logwindow
        self.top.print_on_log("Auto Mode Stopped!\n")
        self.timer.Start(1)
    
    def TimerServ(self, evt):
        """
        Timer Event for Port ON/OFF in Auto Mode

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            evt: The event parameter in the TimerServ() method is an 
            object specific to a particular event type.
        Returns:
            None
        """
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
    
    def port_on(self, portno, stat):
        """
        Port ON/OFF command send to Connected Device Module

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            portno:indicates the variable is a int data type.
            stat:indicates the variable is a boolean data type
            it returns status of port True and False.
        Returns:
            None
        """
        self.top.port_on(portno, stat)
        if(self.top.get_delay_status()):
            self.keep_delay()
    def keep_delay(self):
        """
        start the USB delay timer
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """ 
        self.usb_flg = True
        self.timer_usb.Start(int(self.top.get_enum_delay()))
    
    def Auto_strat_msg(self):
        """
        auto mode Start up Message for Auto Mode on logwindow.
        
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.get_all_three()
        lmstr = "Auto Mode start : ON-Time = {d1} ms,".\
                format(d1=int(self.OnTime)) + \
                " OFF-Time = {d2} ms\n".\
                format(d2=int(self.OffTime)) 
        self.top.print_on_log(lmstr)   
    
    def get_all_three(self):
        """
        Calculate Port ON Time and OFF Time from Interval and Duty
        get three time periods(On, Off) in Auto mode

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.interval = int(self.get_interval())
        self.duty = int(self.get_duty())

        self.OnTime = self.interval* (self.duty/100)
        self.OffTime = self.interval - self.OnTime
    
    def get_auto_param(self):
        """
        Send ON, OFF Time and Duty to USB Tree Window for USB delay validation

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            it return contains timer in integer 
        """
        # Its get all three parametrs 
        self.get_all_three()
        return self.OnTime, self.OffTime, self.duty
    
    def get_interval(self):
        """
        Read Interval of Auto mode

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            Auto mode interval in String format. 
        """
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
        """
        Set interval of Auto mode 

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            strval: Interval value in String format 
        Returns:
            None
        """
        # SetValue() method sets the strval as true()
        self.tc_ival.SetValue(strval)
    
    def get_duty(self):
        """
        Read the Duty % of Auto mode
        
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            Duty value in String format
        """

        duty = self.tc_duty.GetValue()
        if (duty == ""):
            duty = "50"
        ival = int(duty)
        if(ival == 0):
            ival = 1
        # SetValue() method sets the interval value as true()
        self.tc_duty.SetValue(str(ival))
        return self.tc_duty.GetValue()
    
    def set_port_count(self, port):
        """
        Set number of ports based on selected Switch Model

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            port: the port is int type holding the ports
        Returns:
            None
        """
        self.total_ports = port

    def UsbTimer(self, e):
        """
        Timer handler for USB device scan.

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            e: The event parameter in the UsbTimer() method is an 
            object specific to a particular event type.
        Returns:
            None
        """
        self.timer_usb.Stop()
        try:
            thControl.get_tree_change(self.top)
        except:
            self.top.print_on_usb("USB Read Error!")
        self.usb_flg = False
        
        if(self.auto_flg == True & self.pulse_flg == True):
            self.timer.Start(1)
    
    def usb_dly_warning(self):        
        """
        Show warning message when the USB delay is greater than Auto
        mode interval.

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            Boolean: True- when wish to continue the auto mode, 
            False - when wish to exit the auto mode
        """
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
    
    def onoff_dly_warning(self):
        """
        Check ON/OFF Time interval if it is < 500 msec popup a warning message

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            Boolean: True - when wish to continue the Auto mode
            False - when wish to exit the Auto mode
        """ 
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
    
    def update_controls(self, mode):
        """
        Enable/Disable Auto window widgets when mode changed

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            mode: the port controls manual mode for btn_auto disable
        Returns:
            None
        """
        if mode == MODE_MANUAL:
            self.enable_controls(True)
        else:
            self.enable_controls(False)
    
    def enable_controls(self, stat):
        """
        Enable/Disable Auto mode Controls

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            stat:status updated while Auto button enable.
        Returns:
            None
        """
        if(stat):
            # Auto Button is enable
            self.btn_auto.Enable()
            # Text control interval is enable
            self.tc_ival.Enable()
            # Text control duty is enable
            self.tc_duty.Enable()
        else:
            if self.top.mode != MODE_AUTO:
                self.btn_auto.Disable()
            # Set focus to TextCtrl with id
            self.tc_ival.SetFocus()
            # Text control interval is Disable
            self.tc_ival.Disable()
            # Text control duty is Disable
            self.tc_duty.Disable()
        if not self.top.con_flg:
            # Auto Button is Disable
            self.btn_auto.Disable()
   
    def device_disconnected(self):
        """
        Called when device get disconnected show Popup messgage
        
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        if self.auto_flg:
            # The device is disconnected auto mode will stop
            self.stop_auto()