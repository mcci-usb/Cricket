import wx

import sys
from sys import platform

# Own modules
from uiGlobals import *
import dev3141Window
import dev3201Window
import dev2101Window
import dev2301Window
import loopWindow
import logWindow
import autoWindow

# import panels
from leftPanel import *
from rightPanel import *
from midPanel import *


class UiPanel(wx.Panel):
    """
    A class UiPanel with init method
    the UiPanel navigate to UIApp name
    """ 
    def __init__(self, parent):
        """
        Uipanel created
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
        Returns:
            None
        """
        super(UiPanel, self).__init__(parent)

        wx.GetApp().SetAppName("Cricket")

        self.parent = parent
        # set back ground colour White
        self.SetBackgroundColour('White')

        self.font_size = DEFAULT_FONT_SIZE

        # MAC OS X
        if platform == "darwin":
            self.font_size = MAC_FONT_SIZE
        # Sets the font for this window
        self.SetFont(wx.Font(self.font_size, wx.SWISS, wx.NORMAL, wx.NORMAL,
                             False,'MS Shell Dlg 2'))

        self.hb_outer = wx.BoxSizer(wx.HORIZONTAL)

        self.vb_center = wx.BoxSizer(wx.VERTICAL) # for general widgets
        self.vb_left = wx.BoxSizer(wx.VERTICAL)  # for multiple switches
        self.vb_right = wx.BoxSizer(wx.VERTICAL)  # for serial logs

        self.lpanel = LeftPanel(self)
        self.vb_left.Add((0,25), 0, wx.EXPAND)
        self.vb_left.Add(self.lpanel, 0, wx.ALIGN_LEFT | wx.EXPAND)
        self.vb_left.Add((0,10), 0, wx.EXPAND)

        self.cpanel = MidPanel(self)
        self.vb_center.Add(self.cpanel, 0, wx.ALIGN_LEFT | wx.EXPAND)

        self.rpanel = RightPanel(self)
        self.vb_right.Add(self.rpanel, 1, wx.ALIGN_LEFT | wx.EXPAND)

        self.hb_outer.Add((10,0), 0, wx.EXPAND)
        self.hb_outer.Add(self.vb_left, 0, wx.ALIGN_LEFT | wx.EXPAND)
        self.hb_outer.Add((10,0), 0, wx.EXPAND)
        self.hb_outer.Add(self.vb_center, 0, wx.ALIGN_LEFT | wx.EXPAND)
        self.hb_outer.Add((10,0), 0, wx.EXPAND)
        self.hb_outer.Add(self.vb_right, 0, wx.ALIGN_LEFT | wx.EXPAND)
        self.hb_outer.Add((10,0), 0, wx.EXPAND)

        self.con_flg = None

        self.SetSizer(self.hb_outer)
        self.SetAutoLayout(True)
        self.hb_outer.Fit(self)\

        self.lpanel.Hide()

        self.Layout()

    def update_slog_panel(self, cnt):
        self.rpanel.update_slog_panel(cnt)
        self.Layout()

    def show_selected(self, swstr):
        self.cpanel.show_selected(swstr)

    def add_switches(self, swlist):
        if len(swlist) > 1:
            self.lpanel.add_switches(swlist)
            self.lpanel.Show()
            self.cpanel.hide_switch()
        else:
            self.lpanel.Hide()
            self.cpanel.show_switch()
        self.Layout()
        

    def update_uc_panels(self):
        """
        Here updated the user computer panel depend on the connecting 
        Model devices.
        also termianate the switching Control Compter server,
        and terminate the Test Host Computer server,
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
        Returns:
            None
        """
        self.cpanel.update_uc_panels()
        self.Layout()

 
    def update_server_panel(self):
        """
        here USB tree window and Log window update the on selection server
        with SCC and THC servers.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        #self.hboxm.Hide(self.vboxr)
        self.logPan.show_usb_ctrls(False)
        self.vboxl.Show(self.logPan)
        self.hboxm.Show(self.vboxl)
        self.vboxl.Hide(self.hboxdl)
        self.Layout()

    def update_cc_panels(self):
        """
        when selecting Switching Control Computer server menu,
        its starts the Siwting control computer server.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.parent.startCcServer()
        
    def update_hc_panels(self):
        """
        when selecting Test Host Computer server menu,
        its starts the Test Host computer server.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.parent.startHcServer()
    
    def remove_all_panels(self):
        """
        Remove or Hide the the logwinodow and USB Tree view window.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.hboxm.Hide(self.vboxl)
        #self.hboxm.Hide(self.vboxr)
        self.Layout()

    def remove_dev_panels(self):
        """
        Remove or Hide the the all Model 3141, 3201, 2101, 2301 windows panels.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.vboxdl.Hide(self.dev2301Pan)
        self.vboxdl.Hide(self.dev3201Pan)
        self.vboxdl.Hide(self.dev3141Pan)
        self.vboxdl.Hide(self.dev2101Pan)

    def PrintLog(self, strin):
        """
        print data/status on logwindow 

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            strin: data in String format
        Returns:
            None
        """
        self.cpanel.logPan.print_on_log(strin)
    
    def get_enum_delay(self):
        """
        Get the USB Enumaration delay 

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            String - USB Enumeration delay 
        """
        return self.logPan.get_enum_delay()
      
    def get_delay_status(self):
        """
        Get the status of USB device Enumeration delay check box

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            Boolean - Status of the delay check box
        """
        return self.logPan.get_delay_status()
    
    def get_interval(self):
        """
        Get the interval parameter of Auto Mode

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            String - Auto Mode interval
        """
        return self.autoPan.get_interval()
    
    def set_interval(self, strval):
        """
        Update/Set the Auto Mode interval

        Args: 
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            strval: interval value in Sting format
        Returns:
            None
        """
        self.autoPan.set_interval(strval)
    
    def disable_usb_scan(self):
        """
        Disable the USB device scan by uncheck the check box

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns: 
            None
        """
        self.logPan.disable_usb_scan()
    
    def get_loop_param(self):
        """
        Get the Loop Window prameters

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            return None
        """
        return self.loopPan.get_loop_param()
    
    def get_auto_param(self):
        """
        Get the Auto Window prameters

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns: 
            return None
        """
        return self.autoPan.get_auto_param()
    
    def set_period(self, strval):
        """
        Set the period for Loop Window

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            strval: Period value in String format
        Returns:
            return None
        """
        self.loopPan.set_period(strval)

    def set_port_list(self, ports):
        """
        Set the ports list for Loop Window and Auto Window

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            ports: upated the ports list
        Returns:
            return None
        """
        self.loopPan.set_port_list(ports)
        self.autoPan.set_port_count(ports)
    
    def port_on(self, port, stat):
        """
        Port On/Off command from Loop and Auto Window

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            port: device port number
            stat: port on status will updated 
        Returns:
            None
        """
        self.devObj[self.parent.selDevice].port_on(port, stat)
    
    def update_controls(self, mode):
        """
        Update the controls based on the mode
        
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            mode: mode controls
        Returns:
            None
        """
        self.devObj[self.parent.selDevice].update_controls(mode)
        self.loopPan.update_controls(mode)
        self.autoPan.update_controls(mode)
        self.logPan.update_controls(mode)
    
    def device_connected(self):
        """
        Once device connected, Model Window get updated with selected Model

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        for dev in range(len(DEVICES)):
            if dev == self.parent.selDevice:
                self.vboxdl.Show(self.devObj[self.parent.selDevice])
            else:
                self.vboxdl.Hide(self.devObj[dev])
        self.Layout()
        self.devObj[self.parent.selDevice].device_connected()
    
    def device_disconnected(self):
        """
        Once device disconnected, disable all controls in Model, Loop 
        and Auto Window

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.devObj[self.parent.selDevice].device_disconnected()
        self.loopPan.device_disconnected()
        self.autoPan.device_disconnected()
    
    def auto_connect(self):
        """
        Once application loaded, initiate the auto connect 
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.comPan.auto_connect()