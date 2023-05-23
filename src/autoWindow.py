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
#     V4.0.0 Wed May 25 2023 17:00:00   Seenivasan V
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

        self.con_flg = None

        self.swid = None
        self.swkey = None

    
        self.portno = 0
        self.cbPorts = []
        self.psel = []
        # The Timer class allows you to execute code at specified intervals.
        self.timer = wx.Timer(self)
        self.timer_usb = wx.Timer(self)

        
        # Oct 08 2022
        self.hb_sw = wx.BoxSizer(wx.HORIZONTAL)
        self.hb_port = wx.BoxSizer(wx.HORIZONTAL)
        self.hb_intv = wx.BoxSizer(wx.HORIZONTAL)
        self.hb_duty = wx.BoxSizer(wx.HORIZONTAL)
        self.hb_btn = wx.BoxSizer(wx.HORIZONTAL)
        
        self.st_switch  = wx.StaticText(self, -1, "Select Switch ", size=(-1, -1), 
                                      style = wx.ALIGN_LEFT)
        self.cb_switch = wx.ComboBox(self,
                                     size=(155,-1),
                                     style = wx.TE_PROCESS_ENTER)

        # self.hb_sw.Add(self.st_switch, 0, flag = wx.LEFT | wx.Top, border=5)
        # self.hb_sw.Add(self.cb_switch, 0, flag = wx.LEFT | wx.Top, border=5)
        self.hb_sw.AddMany([
            (self.st_switch, 0, wx.EXPAND),
            ((20,0), 1, wx.EXPAND),
            (self.cb_switch, 0, wx.EXPAND),
            ((-1,0), 1, wx.EXPAND)
            ])


        self.cb_port = wx.StaticText(self, -1, "Port")
        self.cb_p1 = wx.CheckBox(self, -1, "1")
        self.cb_p1.Disable()     
        self.cb_p2 = wx.CheckBox(self, -1, "2")
        self.cb_p2.Disable()
        self.cb_p3 = wx.CheckBox(self, -1, "3")
        self.cb_p3.Disable()
        self.cb_p4 = wx.CheckBox(self, -1, "4")
        self.cb_p4.Disable()

        self.hb_port.AddMany([
            ((40,0), 0, wx.EXPAND),
            (self.cb_port, 0, wx.EXPAND),
            ((28,0), 0, wx.EXPAND),
            (self.cb_p1, 0, wx.EXPAND),
            ((10,0), 0, wx.EXPAND),
            (self.cb_p2, 0, wx.EXPAND),
            ((10,0), 0, wx.EXPAND),
            (self.cb_p3, 0, wx.EXPAND),
            ((10,0), 0, wx.EXPAND),
            (self.cb_p4, 0, wx.EXPAND),
            ((-1,0), 1, wx.EXPAND)
            ])

        self.cbPorts.append(self.cb_p1)
        self.cbPorts.append(self.cb_p2)
        self.cbPorts.append(self.cb_p3)
        self.cbPorts.append(self.cb_p4)

        self.st_si   = wx.StaticText(self, -1, "Interval",
                                     style = wx.ALIGN_CENTER_VERTICAL | 
                                     wx.ALIGN_LEFT, size=(-1,-1))
        self.tc_ival   = wx.TextCtrl(self, ID_TC_INTERVAL, "2000", 
                                     size=(50,-1), style = wx.TE_CENTRE |
                                     wx.TE_PROCESS_ENTER,
                                     validator=NumericValidator(), 
                                     name="ON/OFF period")
        self.st_ms   = wx.StaticText(self, -1, "ms", size=(-1,15), 
                                     style = wx.ALIGN_CENTER)

        self.hb_intv.AddMany([
            ((20,0), 0, wx.EXPAND),
            (self.st_si, 0, wx.EXPAND),
            ((30,0), 0, wx.EXPAND),
            (self.tc_ival, 0, wx.EXPAND),
            ((10,0), 0, wx.EXPAND),
            (self.st_ms, 0, wx.EXPAND),
            ((-1,0), 1, wx.EXPAND)
            ])


        self.st_duty   = wx.StaticText(self, -1, "    Duty", 
                                       style = wx.ALIGN_CENTER_VERTICAL | 
                                       wx.ALIGN_LEFT, size=(-1,-1))
        self.tc_duty   = wx.TextCtrl(self, ID_TC_DUTY, "50", size=(50,-1), 
                                     style = wx.TE_CENTRE |
                                     wx.TE_PROCESS_ENTER,
                                     validator=NumericValidator(), 
                                     name="ON/OFF period")
        self.st_ps   = wx.StaticText(self, -1, "%", size=(-1,15), 
                                     style = wx.ALIGN_CENTER)


        self.hb_duty.AddMany([
            ((20,0), 0, wx.EXPAND),
            (self.st_duty, 0, wx.EXPAND),
            ((30,0), 0, wx.EXPAND),
            (self.tc_duty, 0, wx.EXPAND),
            ((10,0), 0, wx.EXPAND),
            (self.st_ps, 0, wx.EXPAND),
            ((-1,0), 1, wx.EXPAND)
            ])

        self.btn_auto = wx.Button(self, ID_BTN_AUTO, "Auto", size=(60,25))
        self.hb_btn.AddMany([
            ((-1,0), 1, wx.EXPAND),
            (self.btn_auto, 0, wx.EXPAND),
            ((-1,0), 1, wx.EXPAND)
            ])

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
        # sb = wx.StaticBox(self, -1, "Auto Mode")
        # Creates a boxsizer is vertical

        self.hb_outer = wx.BoxSizer(wx.HORIZONTAL)
        self.vb_contnr = wx.BoxSizer(wx.VERTICAL)

        self.vb_contnr.Add((0,-1), 1, wx.EXPAND)
        self.vb_contnr.Add(self.hb_sw, 0, wx.EXPAND)
        self.vb_contnr.Add((0,-1), 1, wx.EXPAND)
        self.vb_contnr.Add(self.hb_port, 0, wx.EXPAND)
        self.vb_contnr.Add((0,-1), 1, wx.EXPAND)
        self.vb_contnr.Add(self.hb_intv, 0, wx.EXPAND)
        self.vb_contnr.Add((0,-1), 1, wx.EXPAND)
        self.vb_contnr.Add(self.hb_duty, 0, wx.EXPAND)
        self.vb_contnr.Add((0,-1), 1, wx.EXPAND)
        self.vb_contnr.Add(self.hb_btn, 0, wx.EXPAND)
        self.vb_contnr.Add((0,-1), 1, wx.EXPAND)

        self.hb_outer.AddMany([
            ((-1,0), 1, wx.EXPAND),
            (self.vb_contnr, 1, wx.EXPAND),
            ((-1,0), 1, wx.EXPAND),
            ])


        # Set size of frame
        self.SetSizer(self.hb_outer)
        # Set size of frame
        self.hb_outer.Fit(self)
        self.Layout()
        
        self.cb_switch.Bind(wx.EVT_COMBOBOX, self.SwitchChange, self.cb_switch)
        # Bind the button event to handler
        self.btn_auto.Bind(wx.EVT_BUTTON, self.OprAuto)
        # Bind the timer event to handler
        self.Bind(wx.EVT_TIMER, self.TimerServ, self.timer)
        # Bind the usbtimer event to handler
        self.Bind(wx.EVT_TIMER, self.UsbTimer, self.timer_usb)
        self.Bind(wx.EVT_CHECKBOX, self.auto_ports_enable_p1, self.cb_p1)
        self.Bind(wx.EVT_CHECKBOX, self.auto_ports_enable_p1, self.cb_p2)
        self.Bind(wx.EVT_CHECKBOX, self.auto_ports_enable_p1, self.cb_p3)
        self.Bind(wx.EVT_CHECKBOX, self.auto_ports_enable_p1, self.cb_p4)

        self.enable_controls(True)

    def update_sw_selector(self, swdict):
        self.cb_switch.Clear()
        for key, val in swdict.items():
            swstr = ""+val+"("+key+")"
            self.cb_switch.Append(swstr)
        self.cb_switch.SetSelection(0)
        self.Update_port_count()
        self.con_flg = True


    def Update_port_count(self):
        self.swid = self.cb_switch.GetValue()
        self.swkey = self.swid.split("(")[1][:-1]
        swname = self.swid.split("(")[0]
        self.set_port_count(portCnt[swname])
    
    def SwitchChange(self, evt):
        self.Update_port_count()

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
        self.set_port_list()
        if(len(self.psel) == 0):
            title = ("No Ports Selected")
            msg = ("Please Select a Port to Continue Auto Mode "
                    )
            dlg = wx.MessageDialog(self, msg, title, wx.OK)
            dlg.ShowModal()
            return

        self.auto_flg = True
        # The Lablel to set name as Stop
        self.btn_auto.SetLabel("Stop")
        self.disable_ports()
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
        self.enable_ports()

        # Print the string in logwindow
        self.top.print_on_log("Auto Mode Stopped!\n")
        self.timer.Start(1)

    def auto_ports_enable_p1(self, event):
        """
        auto ports binding the events handling
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: if check the ports its enable
        Returns:
            None
        """
        pass

    def set_port_list(self):
        """
        adding all selected ports in a List, used for the AutoMode 
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.psel.clear()
        if self.cb_p1.IsChecked():
            self.psel.append(1)
        if self.cb_p2.IsChecked():
            self.psel.append(2)
        if self.cb_p3.IsChecked():
            self.psel.append(3)
        if self.cb_p4.IsChecked():
            self.psel.append(4)
    
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
                    self.port_on(self.psel[self.pcnt], False)
                    self.On_flg = False
                    if self.auto_flg:
                        self.timer.Start(self.OffTime)
                else:
                    self.pcnt = self.pcnt + 1
                    if(self.pcnt >= len(self.psel)):
                        self.pcnt = 0
                    self.port_on(self.psel[self.pcnt], True)
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
        self.top.port_on(self.swkey, portno, stat)
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

        self.OnTime = int(self.interval* (self.duty/100))
        self.OffTime = int(self.interval - self.OnTime)
    
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
        self.set_ports()

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
        self.usb_flg = False
        try:
            thControl.get_tree_change(self.top)
        except:
            self.top.print_on_log("USB Read Error!")
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
        Check ON/OFF Time interval if it is < 1000 msec popup a warning message

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            Boolean: True - when wish to continue the Auto mode
            False - when wish to exit the Auto mode
        """ 
        self.get_all_three()
        if (self.OnTime < 1000 or self.OffTime < 1000):
            title = ("Port ON/OFF time warning!")
            msg = ("For Device safety, it is recommended to keep "
                       "Port ON/OFF time > 1000 msec."
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
        if not self.con_flg:
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

    def enable_ports(self):

        """
        while starting the Auto mode (Connecting Device) 
        all check boxes are disable.
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.

        Returns:
            None
        """
        if self.total_ports == 1:
            self.cb_p1.Enable()
        elif self.total_ports == 2:
            self.cb_p1.Enable()
            self.cb_p2.Enable()
        elif self.total_ports == 4:
            self.cb_p1.Enable()
            self.cb_p2.Enable()
            self.cb_p3.Enable()
            self.cb_p4.Enable()

    def disable_ports(self):

        """
        while starting the Auto mode (Connecting Device) 
        all check boxes are disable.
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.

        Returns:
            None
        """
        self.cb_p1.Disable()
        self.cb_p2.Disable()
        self.cb_p3.Disable()
        self.cb_p4.Disable()

    def set_ports(self):
        """
       called  when device gets connected , all ports of the  
       connected device are enabled and excess port controls are unchecked
       and disabled
        
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            stat: the status is which port selection 
        Returns:
            None
        """
        if self.total_ports == 1:
            self.cb_p1.Enable()
            self.cb_p1.SetValue(True)
            self.cb_p2.SetValue(False)
            self.cb_p3.SetValue(False)
            self.cb_p4.SetValue(False)
            self.cb_p2.Disable()
            self.cb_p3.Disable()
            self.cb_p4.Disable()
        elif self.total_ports == 2:
            self.cb_p1.Enable()
            self.cb_p2.Enable()
            self.cb_p1.SetValue(True)
            self.cb_p2.SetValue(True)
            self.cb_p3.SetValue(False)
            self.cb_p4.SetValue(False)
            self.cb_p3.Disable() 
            self.cb_p4.Disable()
        elif self.total_ports == 4:
            self.cb_p1.Enable()
            self.cb_p2.Enable()
            self.cb_p3.Enable()
            self.cb_p4.Enable()
            self.cb_p1.SetValue(True)
            self.cb_p2.SetValue(True)
            self.cb_p3.SetValue(True)
            self.cb_p4.SetValue(True)