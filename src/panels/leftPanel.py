##############################################################################
# 
# Module: leftPanel.py
#
# Description:
#     Updated the Left Panel.
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
# Revision history:
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
##############################################################################

# Lib imports
import wx
from wx.lib.scrolledpanel import ScrolledPanel

# Own modules
from switches import dev2101Window
from switches import dev3141Window
from switches import dev3142Window
from switches import dev3201Window
from switches import dev2301Window
from noSwWindow import NoSwWindow

##############################################################################
# Classes
##############################################################################
class LeftPanel(ScrolledPanel):
    """
    Left panel UI container.

    Displays connected USB switches and provides
    controls for switch operations such as connect,
    disconnect, port control, and speed settings.

    Attributes:
        parent: Parent application reference.
        swobjmap: Switch window mapping dictionary.
        multiswobj: Active switch UI objects.
    """

    def __init__(self, parent, top):
        """
        Initialize LeftPanel layout.

        Args:
            parent: Parent window.
            top: Top-level application object.
        """
        super(LeftPanel, self).__init__(parent)

        self.SetBackgroundColour("White")
        self.SetupScrolling()

        self.parent = top
        self.SetMinSize((320, 720))

        self.sb = wx.StaticBox(self, -1, "MCCI USB Switches")
        self.main_sizer = wx.StaticBoxSizer(self.sb, wx.VERTICAL)

        self.swobj = []

        self.swobjmap = {
            "3141": dev3141Window.Dev3141Window,
            "3142": dev3142Window.Dev3142Window,
            "3201": dev3201Window.Dev3201Window,
            "2301": dev2301Window.Dev2301Window,
            "2101": dev2101Window.Dev2101Window,
        }

        self.multiswobj = {}

        self.SetSizer(self.main_sizer)
        self.SetAutoLayout(True)
        self.main_sizer.Fit(self)
        self.Layout()

    # ------------------------------------------------------------------
    # UI Builders
    # ------------------------------------------------------------------
    def no_switches(self):
        """
        Display 'No Switches' window.
        """
        self.main_sizer.Clear(True)

        self.main_sizer.Add(
            NoSwWindow(self, self.parent),
            0,
            wx.ALL,
            5,
        )
        self.main_sizer.Add((0, 20), 0, wx.EXPAND)
        self.Layout()

    def switch_diconnect_form(self):
        """
        Create switch disconnect form UI.
        """
        self.swid = None
        self.swport = None
        self.swname = None

        hbox_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.cb_selsw = wx.ComboBox(
            self,
            size=(155, -1),
            style=wx.TE_PROCESS_ENTER,
        )
        hbox_sizer.Add(self.cb_selsw, 0, wx.ALL | wx.EXPAND, 5)

        self.btn_disconsw = wx.Button(self, label="Disconnect")
        hbox_sizer.Add(self.btn_disconsw, 0, wx.ALL | wx.EXPAND, 5)

        self.main_sizer.Add(hbox_sizer, 0, wx.ALL | wx.EXPAND, 5)

        self.cb_selsw.Bind(wx.EVT_COMBOBOX, self.SwitchChange)
        self.btn_disconsw.Bind(wx.EVT_BUTTON, self.on_disconnect)

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------
    def SwitchChange(self, evt):
        """
        Handle switch selection change.

        Args:
            evt: ComboBox event object.
        """
        self.swid = self.cb_selsw.GetValue()
        self.swport = self.swid.split("(")[1][:-1]
        self.swname = self.swid.split("(")[0]

    def on_disconnect(self, evt):
        """
        Disconnect selected switch.

        Args:
            evt: Button click event.
        """
        if not self.swid:
            if self.cb_selsw.GetCount() > 0:
                self.swid = self.cb_selsw.GetString(0)
                self.SwitchChange(None)

        if self.swport in self.parent.swuidict:
            self.parent.swuidict.pop(self.swport)

            if self.swname != "2101":
                self.parent.disconnect_device(self.swport)

            self.parent.update_loop_swselector()

            self.swport = None
            self.swname = None

            self.add_switches(self.parent.swuidict)

            self.parent.print_on_log(
                "MCCI USB Switch is Disconnected!\n"
            )

    # ------------------------------------------------------------------
    # Switch Management
    # ------------------------------------------------------------------
    def update_sw_selector(self, swdict):
        """
        Update switch selector dropdown.

        Args:
            swdict: Switch dictionary.
        """
        for key, val in swdict.items():
            swstr = val + "(" + key + ")"
            self.cb_selsw.Append(swstr)

        self.cb_selsw.SetSelection(0)

    def add_switches(self, swlist):
        """
        Add switch panels dynamically.

        Args:
            swlist: Switch list dictionary.
        """
        if len(swlist) > 0:
            self.main_sizer.Clear(True)
            self.switch_diconnect_form()
            self.multiswobj.clear()

            for key, value in swlist.items():
                self.multiswobj[key] = self.swobjmap[value](
                    self,
                    self.parent,
                    key,
                )

            self.update_sw_selector(self.parent.swuidict)

            for key, value in self.multiswobj.items():
                self.main_sizer.Add(value, 0, wx.ALL, 5)
                self.main_sizer.Add((0, 10), 0, wx.EXPAND)

        else:
            self.no_switches()

        self.main_sizer.Add((0, 20), 0, wx.EXPAND)
        self.Layout()

    # ------------------------------------------------------------------
    # Switch Controls
    # ------------------------------------------------------------------
    def port_on(self, swkey, port, stat):
        """
        Control switch port state.

        Args:
            swkey: Switch key.
            port: Port number.
            stat: ON/OFF status.
        """
        self.multiswobj[swkey].port_on(port, stat)

    def set_speed(self, swkey, speed):
        """
        Set switch speed.

        Args:
            swkey: Switch key.
            speed: Speed value.
        """
        self.multiswobj[swkey].set_speed(speed)

    def read_param(self, swkey, param):
        """
        Read switch parameter.

        Args:
            swkey: Switch key.
            param: Parameter name.
        """
        self.multiswobj[swkey].read_param(param)
