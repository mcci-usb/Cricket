##############################################################################
# 
# Module: midPanel.py
#
# Description:
#     Updated the Mid Panel
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
# Revision history:
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
##############################################################################

# Built-in imports
import sys
from sys import platform

# Lib imports
import wx

# Own modules
from uiGlobals import *
from features.modes import loopWindow
from features.modes import autoWindow
from features.modes import batchWindow
import logWindow

##############################################################################
# Utilities
##############################################################################
class MidPanel(wx.Panel):
    """
    Middle panel UI container.

    Manages operational modes such as Auto, Loop,
    and Batch along with logging window and USB
    enumeration controls.

    Attributes:
        parent: Parent application reference.
        autoPan: Auto mode panel.
        loopPan: Loop mode panel.
        batchPan: Batch mode panel.
        logPan: Logging window panel.
    """

    def __init__(self, parent, top, portno):
        """
        Initialize MidPanel layout.

        Args:
            parent: Parent window reference.
            top: Top-level application object.
            portno: Port number identifier.
        """
        super(MidPanel, self).__init__(parent)

        self.SetMaxSize((540, -1))

        wx.GetApp().SetAppName("Cricket")

        self.parent = top
        self.SetBackgroundColour("White")

        self.font_size = DEFAULT_FONT_SIZE

        if platform == "darwin":
            self.font_size = MAC_FONT_SIZE

        self.SetFont(
            wx.Font(
                self.font_size,
                wx.SWISS,
                wx.NORMAL,
                wx.NORMAL,
                False,
                "MS Shell Dlg 2",
            )
        )

        self.portno = portno

        self.logPan = logWindow.LogWindow(self, self.parent)
        self.hboxdl = wx.BoxSizer(wx.HORIZONTAL)

        nb = wx.Notebook(self)

        self.autoPan = autoWindow.AutoWindow(nb, top)
        self.loopPan = loopWindow.LoopWindow(nb, top)
        self.batchPan = batchWindow.BatchWindow(nb, top)

        nb.AddPage(self.autoPan, "Auto Mode")
        nb.AddPage(self.loopPan, "Loop Mode")
        nb.AddPage(self.batchPan, "Batch Mode")

        self.hboxdl.Add(nb, 1, wx.EXPAND)

        self.vboxl = wx.BoxSizer(wx.VERTICAL)
        self.vboxl.Add((0, 20), 0, wx.EXPAND)
        self.vboxl.Add(self.hboxdl, 0, wx.ALIGN_LEFT | wx.EXPAND)
        self.vboxl.Add((0, 10), 0, 0)
        self.vboxl.Add(self.logPan, 1, wx.EXPAND)
        self.vboxl.Add((0, 20), 0, wx.EXPAND)

        self.hboxm = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxm.Add((20, 0), 0, wx.EXPAND)
        self.hboxm.Add(self.vboxl, 1, wx.EXPAND)
        self.hboxm.Add((20, 0), 0, wx.EXPAND)

        self.SetSizer(self.hboxm)
        self.SetAutoLayout(True)
        self.hboxm.Fit(self)
        self.Layout()

    def update_cc_panels(self):
        """
        Start Switching Control Computer server.
        """
        self.parent.startCcServer()

    def update_hc_panels(self):
        """
        Start Test Host Computer server.
        """
        self.parent.startHcServer()

    def remove_all_panels(self):
        """
        Hide log window and USB tree view.
        """
        self.hboxm.Hide(self.vboxl)
        self.Layout()

    def remove_mode_panels(self):
        """
        Hide mode panels and USB controls.
        """
        self.vboxl.Hide(self.hboxdl)
        self.hide_usb_enum_controls()
        self.Layout()

    def hide_usb_enum_controls(self):
        """
        Hide USB enumeration controls.
        """
        self.logPan.show_usb_ctrls(False)

    def show_usb_enum_controls(self):
        """
        Show USB enumeration controls.
        """
        self.logPan.show_usb_ctrls(True)
        self.Layout()

    def show_mode_panels(self):
        """
        Display mode panels.
        """
        self.vboxl.Show(self.hboxdl)
        self.show_usb_enum_controls()
        self.Layout()

    def PrintLog(self, strin):
        """
        Print message on log window.

        Args:
            strin: Log message string.
        """
        self.logPan.print_on_log(strin)

    def get_enum_delay(self):
        """
        Get USB enumeration delay.

        Returns:
            str: Enumeration delay value.
        """
        return self.logPan.get_enum_delay()

    def get_delay_status(self):
        """
        Get delay checkbox status.

        Returns:
            bool: Delay status.
        """
        return self.logPan.get_delay_status()

    def get_interval(self):
        """
        Get Auto mode interval.

        Returns:
            str: Interval value.
        """
        return self.autoPan.get_interval()

    def set_interval(self, strval):
        """
        Set Auto mode interval.

        Args:
            strval: Interval value.
        """
        self.autoPan.set_interval(strval)

    def disable_usb_scan(self):
        """
        Disable USB scanning.
        """
        self.logPan.disable_usb_scan()

    def get_loop_param(self):
        """
        Get loop parameters.

        Returns:
            dict: Loop configuration.
        """
        return self.loopPan.get_loop_param()

    def get_auto_param(self):
        """
        Get auto parameters.

        Returns:
            dict: Auto configuration.
        """
        return self.autoPan.get_auto_param()

    def set_loop_param(self, onTime, offTime):
        """
        Set loop timing parameters.

        Args:
            onTime: ON duration.
            offTime: OFF duration.
        """
        self.loopPan.set_loop_param(onTime, offTime)

    def set_port_list(self, ports):
        """
        Set port list.

        Args:
            ports: List of ports.
        """
        self.loopPan.set_port_list(ports)
        self.autoPan.set_port_count(ports)

    def port_on(self, swkey, port, stat):
        """
        Control port ON/OFF.

        Args:
            swkey: Switch key.
            port: Port number.
            stat: ON/OFF status.
        """
        self.swobj[swkey].port_on(port, stat)

    def device_connected(self):
        """
        Handle device connected event.
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
        Handle device disconnected event.
        """
        self.devObj[self.parent.selDevice].device_disconnected()
        self.loopPan.device_disconnected()
        self.autoPan.device_disconnected()

    def auto_connect(self):
        """
        Initiate auto connection.
        """
        self.comPan.auto_connect()
