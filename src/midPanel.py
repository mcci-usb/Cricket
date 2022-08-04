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


class MidPanel(wx.Panel):
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
        super(MidPanel, self).__init__(parent)

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

        self.logPan = logWindow.LogWindow(self, parent)
        self.loopPan = loopWindow.LoopWindow(self, parent)
        #self.comPan = comWindow.ComWindow(self, parent)
        self.autoPan = autoWindow.AutoWindow(self, parent)
        
        self.dev3141Pan = dev3141Window.Dev3141Window(self, parent)
        self.dev3201Pan = dev3201Window.Dev3201Window(self, parent)
        self.dev2101Pan = dev2101Window.Dev2101Window(self, parent)
        self.dev2301Pan = dev2301Window.Dev2301Window(self, parent)

        self.sw_dict = {"3141": self.dev3141Pan, "3201": self.dev3201Pan, 
                        "2101": self.dev2101Pan, "2301": self.dev2301Pan }

        self.devObj = []  
        # Device panel added
        self.devObj.append(self.dev3141Pan)
        self.devObj.append(self.dev3201Pan)
        self.devObj.append(self.dev2101Pan)
        self.devObj.append(self.dev2301Pan)

        
        # Creating Sizers
        self.vboxdl = wx.BoxSizer(wx.VERTICAL)
        self.vboxdl.Add(self.dev3141Pan, 0, wx.EXPAND)
        self.vboxdl.Add(self.dev3201Pan, 0, wx.EXPAND)
        self.vboxdl.Add(self.dev2301Pan, 0, wx.EXPAND)
        self.vboxdl.Add(self.dev2101Pan, 0, wx.EXPAND)

        self.vboxdl.Add(0, 10, 0)
        self.vboxdl.Add(self.autoPan, 1, wx.EXPAND)

        self.hboxdl = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxdl.Add(self.vboxdl, 1 ,wx.ALIGN_LEFT | wx.EXPAND)
        self.hboxdl.Add((20,0), 0, wx.EXPAND)
        self.hboxdl.Add(self.loopPan, 0, wx.EXPAND)
        
        self.vboxl = wx.BoxSizer(wx.VERTICAL)
        self.vboxl.Add((0,20), 0, wx.EXPAND)
        self.vboxl.Add(self.hboxdl, 0 ,wx.ALIGN_LEFT | wx.EXPAND)
        self.vboxl.Add((0,10), 0, 0)
        self.vboxl.Add(self.logPan, 1, wx.EXPAND)
        self.vboxl.Add((0,20), 0, wx.EXPAND)


       # BoxSizer fixed with Horizontal
        self.hboxm = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxm.Add((20,0), 0, wx.EXPAND)
        self.hboxm.Add(self.vboxl, 1, wx.EXPAND)
        self.hboxm.Add((20,0), 0, wx.EXPAND)
        # self.hboxm.Add(self.vboxr, 1, wx.EXPAND)
        # self.hboxm.Add((20,0), 1, wx.EXPAND)
        
        # Set size of frame
        self.SetSizer(self.hboxm)
        
        # Setting Layouts
        self.SetAutoLayout(True)
        self.hboxm.Fit(self)
        self.Layout()

    def show_selected(self, swstr):
        self.hide_switch()
        self.vboxdl.Show(self.sw_dict[swstr])
        self.Layout()

    def hide_switch(self):
        self.vboxdl.Hide(self.dev2301Pan)
        self.vboxdl.Hide(self.dev3201Pan)
        self.vboxdl.Hide(self.dev3141Pan)
        self.vboxdl.Hide(self.dev2101Pan)
        self.Layout()

    def show_switch(self):
        self.vboxdl.Hide(self.dev2301Pan)
        self.vboxdl.Show(self.dev3201Pan)
        self.vboxdl.Hide(self.dev3141Pan)
        self.vboxdl.Hide(self.dev2101Pan)
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
        self.vboxl.Show(self.vboxl)
        self.vboxl.Show(self.hboxdl)
        #self.hboxm.Show(self.vboxr)
        self.vboxdl.Hide(self.dev2301Pan)
        self.vboxdl.Hide(self.dev3201Pan)
        self.vboxdl.Hide(self.dev3141Pan)
        self.logPan.show_usb_ctrls(True)
        self.vboxl.Show(self.logPan)
        self.Layout()
        # self.parent.terminateCcServer()
        # self.parent.terminateHcServer()
 
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
        self.logPan.print_on_log(strin)
    
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