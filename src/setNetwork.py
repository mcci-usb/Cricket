# -*- coding: utf-8 -*-
##############################################################################
#
# Module: setNetwork.py
#
# Description:
#     Network configuration panel used to set and update
#     TCP/IP address and Port details for SCC and THC servers.
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
#
##############################################################################

# Lib imports
import wx
import threading
import socket

# Own modules
import configdata

##############################################################################
# Network Configuration Panel
##############################################################################

class SetNetwork(wx.Panel):
    """
    Network configuration UI panel.

    This panel allows the user to configure TCP/IP
    network settings such as IP address and Port
    for SCC (Switch Control Computer) and
    THC (Test Host Computer).

    Attributes:
        parent: Parent window reference.
        ctype: Configuration type (SCC / THC).
        config_data: Loaded configuration data.
    """

    def __init__(self, parent, ctype):
        """
        Initialize SetNetwork panel.

        Args:
            parent: Parent window reference.
            ctype: Configuration type identifier
                   (SCC or THC).

        Returns:
            None
        """
        super(SetNetwork, self).__init__(parent)

        self.SetBackgroundColour("White")
        self.ctype = ctype

        # Build UI
        self.set_network()

    def set_port(self):
        """
        Load and set saved network port and IP values.

        Reads configuration data and updates
        UI text controls accordingly.

        Args:
            self: Instance reference.

        Returns:
            None

        Raises:
            KeyError:
                If configuration keys are missing.
        """
        self.config_data = configdata.read_all_config()
        self.port = None

        if self.ctype == "SCC":
            self.port = self.config_data["cc"]["tcp"]["port"]
            self.sip = self.config_data["cc"]["tcp"]["ip"]
        else:
            self.port = self.config_data["thc"]["tcp"]["port"]
            self.sip = self.config_data["thc"]["tcp"]["ip"]

        self.scc_tc_port.SetValue(self.port)
        self.scc_tc_sip.SetValue(self.sip)

    def set_network(self):
        """
        Create and arrange network configuration UI controls.

        Builds layout including:
        - Port input
        - IP address input
        - Save button

        Args:
            self: Instance reference.

        Returns:
            None
        """

        self.SetBackgroundColour("White")

        # Static box container
        sb = wx.StaticBox(self, -1, "Set Network")
        self.vbox1 = wx.StaticBoxSizer(sb, wx.VERTICAL)

        # Controls
        self.scc_st_port = wx.StaticText(
            self, -1, self.ctype + " Port", size=(65, -1)
        )

        self.scc_tc_port = wx.TextCtrl(
            self, -1, " ", size=(60, -1)
        )

        self.scc_st_sip = wx.StaticText(
            self, -1, self.ctype + " IP", size=(60, -1)
        )

        self.scc_tc_sip = wx.TextCtrl(
            self, -1, "0.0.0.0 ", size=(95, -1)
        )

        self.btn_save = wx.Button(
            self, -1, "Save", size=(60, -1)
        )

        # Load saved config
        self.set_port()

        # Layout sizers
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        self.wait_flg = False

        # Add controls to layout
        self.hbox2.Add(
            self.scc_st_port, 0,
            flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT,
            border=5
        )

        self.hbox2.Add(
            self.scc_tc_port,
            flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT,
            border=10
        )

        self.hbox2.Add(
            self.scc_st_sip,
            flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT,
            border=15
        )

        self.hbox2.Add(
            self.scc_tc_sip, 0,
            flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT,
            border=0
        )

        self.hbox2.Add(
            self.btn_save, 0,
            flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT,
            border=20
        )

        # Bind events
        self.btn_save.Bind(wx.EVT_BUTTON, self.SaveNetworkComp)

        # Add to main sizer
        self.vbox1.AddMany([
            (self.hbox2, 0, wx.ALIGN_LEFT),
            (10, 5, 0)
        ])

        self.SetSizer(self.vbox1)
        self.vbox1.Fit(self)
        self.Layout()

    def load_network_config(self):
        """
        Load network configuration into UI.

        Fetches stored configuration values
        and updates text controls.

        Args:
            self: Instance reference.

        Returns:
            None
        """

        config = {}

        if self.ctype == "SCC":
            config = configdata.get_nw_scc_config()

        elif self.ctype == "THC":
            config = configdata.get_nw_thc_config()

        if config:
            self.scc_tc_sip.SetValue(config.get("ip", ""))
            self.scc_tc_port.SetValue(config.get("port", ""))

    def SaveNetworkComp(self, e):
        """
        Save network configuration settings.

        Stores updated IP address and port
        into configuration storage.

        Args:
            e: wxPython event object.

        Returns:
            None

        Raises:
            Exception:
                If configuration save fails.
        """

        devaddr = self.scc_tc_sip.GetValue()
        portno = self.scc_tc_port.GetValue()

        if self.ctype == "SCC":
            configdata.set_scc_config({
                "type": "tcp",
                "ip": devaddr,
                "port": portno
            })

        elif self.ctype == "THC":
            configdata.set_thc_config({
                "type": "tcp",
                "ip": devaddr,
                "port": portno
            })
