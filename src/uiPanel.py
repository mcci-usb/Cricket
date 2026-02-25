# -*- coding: utf-8 -*-
##############################################################################
# 
# Module: uiPanel.py
#
# Description:
#     Scan the USB bus and get the list of devices attached.
#     Manages the main UI layout including left, middle, and
#     right panels for switch control, operation modes,
#     USB tree view, and DUT logs.
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
# Revision history:
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
#
##############################################################################
# Built-in imports
import sys
from sys import platform

# Lib imports
import wx

# Own modules
from uiGlobals import *
from panels import leftPanel
from panels import rightPanel
from panels import midPanel
import configdata

# import logWindow
class UiPanel(wx.Panel):
    """
    Main UI panel container.

    This panel manages and arranges the
    left, middle, and right UI panels
    including switch controls, operation
    modes, logs, and USB tree views.

    Attributes:
        parent: Parent frame reference.
        lpanel: Left panel instance.
        cpanel: Center panel instance.
        rpanel: Right panel instance.
        config_data: Loaded configuration data.
    """
    def __init__(self, parent):
        """
        Initialize the main UI panel.

        Args:
            self: Reference to the current instance.
            parent: Parent window/frame reference.

        Returns:
            None

        Raises:
            None
        """
        super(UiPanel, self).__init__(parent)

        # wx.GetApp().SetAppName("Cricket")

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

        self.lpanel = leftPanel.LeftPanel(self, self.parent)
        self.vb_left.Add((0,25), 0, wx.EXPAND)
        self.vb_left.Add(self.lpanel, 1, wx.ALIGN_LEFT | wx.EXPAND)
        self.vb_left.Add((0,10), 0, wx.EXPAND)

        self.cpanel = midPanel.MidPanel(self, self.parent, "")
        self.vb_center.Add(self.cpanel, 0, wx.ALIGN_LEFT | wx.EXPAND)

        self.rpanel = rightPanel.RightPanel(self)
        self.vb_right.Add(self.rpanel, 1, wx.EXPAND | wx.ALL)

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
        self.hb_outer.Fit(self)

        self.add_switches([])

        EVT_RESULT(self, self.StopSequence)
        self.config_data = configdata.read_all_config()

        self.Layout()

    def StopSequence(self, event):
        """
        Handle stop sequence event from DUT operations.

        Args:
            self: Reference to the current instance.
            event: Event object containing stop sequence data.

        Returns:
            None

        Raises:
            None
        """
        if(event.data != None):
            
            if event.data["action"] == "stop sequence":
                self.cpanel.PrintLog("Match found - "+event.data["match"]+"\n")
                self.parent.fault_flg = True
                self.parent.con_flg = False
            else:
                action = self.parent.action_count()
                self.cpanel.PrintLog("Match found : "+str(action)+", "+event.data["match"]+"\n")

    def update_slog_panel(self, duts):
        """
        Update DUT serial log panel.

        Args:
            self: Reference to the current instance.
            duts: DUT data dictionary/list.

        Returns:
            None

        Raises:
            None
        """
        self.rpanel.update_slog_panel(duts)
        self.Layout()

    def init_right_panel(self, pdict):
        """
        Initialize right panel layout.

        Args:
            self: Reference to the current instance.
            pdict: Panel configuration dictionary.

        Returns:
            None

        Raises:
            None
        """
        self.rpanel.init_my_panel(pdict)

    def update_right_panel(self, pdict):
        """
        Refresh right panel content.

        Args:
            self: Reference to the current instance.
            pdict: Panel configuration dictionary.

        Returns:
            None

        Raises:
            None
        """
        self.rpanel.update_my_panel(pdict)

    def update_usb4_tree(self, msusb4):
        """
        Update USB4 tree view.

        Args:
            self: Reference to the current instance.
            msusb4: USB4 topology data.

        Returns:
            None

        Raises:
            None
        """
        self.rpanel.update_usb4_tree(msusb4)
    
    def update_usb3_tree(self, msusb3):
        """
        Update USB3 tree view.

        Args:
            self: Reference to the current instance.
            msusb3: USB3 topology data.

        Returns:
            None

        Raises:
            None
        """
        # print("update_usb3_tree-uiPanel")
        self.rpanel.update_usb3_tree(msusb3)

    def show_selected(self, swstr):
        """
        Display selected switch details.

        Args:
            self: Reference to the current instance.
            swstr: Selected switch string.

        Returns:
            None

        Raises:
            None
        """
        self.cpanel.show_selected(swstr)

    def add_switches(self, swlist):
        """
        Add detected switches to left panel.

        Args:
            self: Reference to the current instance.
            swlist: List/dictionary of switches.

        Returns:
            None

        Raises:
            None
        """
        self.lpanel.add_switches(swlist)
        self.lpanel.Show()
        
    def update_uc_panels(self, sutmenu):
        """
        Update user control panels.

        Args:
            self: Reference to the current instance.
            sutmenu: SUT menu configuration.

        Returns:
            None

        Raises:
            None
        """
        self.cpanel.update_uc_panels()
        self.update_slog_panel(sutmenu)
        self.Layout()

    def update_panels(self, myrole):
        """
        Show or hide panels based on user role.

        Args:
            self: Reference to the current instance.
            myrole: Role configuration dictionary.

        Returns:
            None

        Raises:
            None
        """
        if myrole["uc"] == True:
            # SHOW all the three panels
            self.lpanel.Show()
            self.rpanel.Show()
            self.cpanel.show_mode_panels()
            # self.reSizeScreen()
            self.Layout()
        else:
            #show only the log panels
            self.lpanel.Hide()
            self.rpanel.Hide()
            self.cpanel.remove_mode_panels()
            # self.reSizeScreen()
            self.Layout()

    def PrintLog(self, strin):
        """
        Print log message to UI panels.

        Args:
            self: Reference to the current instance.
            strin: Log message string.

        Returns:
            None

        Raises:
            None
        """
        self.cpanel.logPan.print_on_log(strin)
        self.rpanel.print_on_log(strin)
    
    def get_enum_delay(self):
        """
        Get USB enumeration delay value.

        Args:
            self: Reference to the current instance.

        Returns:
            Enumeration delay value.

        Raises:
            None
        """
        return self.cpanel.logPan.get_enum_delay()
      
    def get_delay_status(self):
        """
        Get enumeration delay status.

        Args:
            self: Reference to the current instance.

        Returns:
            Boolean delay status.

        Raises:
            None
        """
        return self.cpanel.get_delay_status()
    
    def get_interval(self):
        """
        Get auto mode interval value.

        Args:
            self: Reference to the current instance.

        Returns:
            Interval value.

        Raises:
            None
        """
        return self.autoPan.get_interval()
    
    def set_interval(self, strval):
        """
        Set auto mode interval value.

        Args:
            self: Reference to the current instance.
            strval: Interval value string.

        Returns:
            None

        Raises:
            None
        """
        self.cpanel.set_interval(strval)
    
    def disable_usb_scan(self):
        """
        Disable USB scanning option.

        Args:
            self: Reference to the current instance.

        Returns:
            None

        Raises:
            None
        """
        self.cpanel.logPan.disable_usb_scan()
    
    def get_loop_param(self):
        """
        Get loop mode parameters.

        Args:
            self: Reference to the current instance.

        Returns:
            Loop parameters.

        Raises:
            None
        """
       
        return self.cpanel.get_loop_param()
    
    def get_auto_param(self):
        """
        Get auto mode parameters.

        Args:
            self: Reference to the current instance.

        Returns:
            Auto parameters.

        Raises:
            None
        """
        return self.cpanel.get_auto_param()
    
    def set_loop_param(self, onTime, offTime):
        """
        Set loop timing parameters.

        Args:
            self: Reference to the current instance.
            onTime: ON duration.
            offTime: OFF duration.

        Returns:
            None

        Raises:
            None
        """
        self.cpanel.set_loop_param(onTime, offTime)

    def set_port_list(self, ports):
        """
        Set available port list.

        Args:
            self: Reference to the current instance.
            ports: List of ports.

        Returns:
            None

        Raises:
            None
        """
        self.loopPan.set_port_list(ports)
        self.autoPan.set_port_count(ports)

    def port_on(self, swkey, port, stat, swcnt):
        """
        Control switch port state.

        Args:
            self: Reference to the current instance.
            swkey: Switch identifier.
            port: Port number.
            stat: Port status.
            swcnt: Switch count.

        Returns:
            None

        Raises:
            None
        """
        self.lpanel.port_on(swkey, port, stat)

    def set_speed(self, swkey, speed):
        """
        Set switch speed mode.

        Args:
            self: Reference to the current instance.
            swkey: Switch identifier.
            speed: Speed mode.

        Returns:
            None

        Raises:
            None
        """
        self.lpanel.set_speed(swkey, speed)

    def read_param(self, swkey, param):
        """
        Read switch parameter.

        Args:
            self: Reference to the current instance.
            swkey: Switch identifier.
            param: Parameter name.

        Returns:
            None

        Raises:
            None
        """
        self.lpanel.read_param(swkey, param)

    def createBatchPanel(self, swDict):
        """
        Create batch operation panel.

        Args:
            self: Reference to the current instance.
            swDict: Switch configuration dictionary.

        Returns:
            None

        Raises:
            None
        """
        self.lpanel.createBatchPanel(swDict)

    def update_controls(self, mode):
        """
        Update UI controls based on mode.

        Args:
            self: Reference to the current instance.
            mode: Operation mode.

        Returns:
            None

        Raises:
            None
        """ 
        self.cpanel.loopPan.update_controls(mode)
        self.cpanel.autoPan.update_controls(mode)
        self.cpanel.logPan.update_controls(mode)
    
    def device_connected(self):
        """
        Handle device connection event.

        Args:
            self: Reference to the current instance.

        Returns:
            None

        Raises:
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
        Handle device disconnection event.

        Args:
            self: Reference to the current instance.

        Returns:
            None

        Raises:
            None
        """
        self.devObj[self.parent.selDevice].device_disconnected()
        self.loopPan.device_disconnected()
        self.autoPan.device_disconnected()
    
    def auto_connect(self):
        """
        Trigger auto-connect operation.

        Args:
            self: Reference to the current instance.

        Returns:
            None

        Raises:
            None
        """
        self.comPan.auto_connect()

    def updt_dut_config(self, dutno):
        """
        Update DUT configuration.

        Args:
            self: Reference to the current instance.
            dutno: DUT number.

        Returns:
            None

        Raises:
            None
        """
        self.parent.updt_dut_config(dutno)

    def get_dut_config(self, dutno):
        """
        Get DUT configuration.

        Args:
            self: Reference to the current instance.
            dutno: DUT number.

        Returns:
            DUT configuration data.

        Raises:
            None
        """
        return self.parent.get_dut_config(dutno)

    def request_dut_close(self, dutname):
        """
        Request DUT session close.

        Args:
            self: Reference to the current instance.
            dutname: DUT name.

        Returns:
            None

        Raises:
            None
        """
        self.parent.request_dut_close(dutname)

    def save_file(self, content, ftype):
        """
        Save content to file.

        Args:
            self: Reference to the current instance.
            content: File content.
            ftype: File type.

        Returns:
            None

        Raises:
            None
        """
        self.parent.save_file(content, ftype)
    
def EVT_RESULT(win, func):
    """
    Bind DUT result event.

    Args:
        win: Target window.
        func: Callback function.

    Returns:
        None

    Raises:
        None
    """
    win.Connect(-1, -1, EVT_DUT_SL_ERR_ID, func) 
