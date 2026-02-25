# -*- coding: utf-8 -*-
##############################################################################
#
# Module: portDialog.py
#
# Description:
#     Dialog window to configure port settings for
#     Switch Control Computer (SCC) and Test Host Computer (THC).
#     Allows users to select interface type (Serial / Network)
#     and update port configuration details.
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
#
##############################################################################


# Built-in imports
import os
import socket

# Lib imports
import wx

# Own modules
from uiGlobals import *
import devControl

CC_PORT = 2021
HC_PORT = 2022

##############################################################################
# Utilities
##############################################################################
class PortWindow(wx.Window):
    """
    Port configuration window.

    This window provides UI controls to configure
    communication interface and port settings for
    SCC or THC systems.

    Attributes:
        top: Reference to main application frame.
        parent: Parent dialog window.
        cdata: Configuration data dictionary.
        type: System type (SCC / THC).
    """
    def __init__ (self, parent, top, cdata):
        """
        Initialize PortWindow UI.

        Args:
            parent: Parent dialog window.
            top: Reference to main application frame.
            cdata: Configuration data for SCC/THC.

        Returns:
            None
        """
        wx.Window.__init__(self, parent, -1,
                           size=wx.Size(400,300),
                           style=wx.CLIP_CHILDREN,
                           name=list(cdata.keys())[0])

        self.top = top

        self.type = list(cdata.keys())[0]
        self.cdata = cdata
        self.parent = parent

        self.nwip = None

        self.hbox_rb = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_portip = wx.BoxSizer(wx.HORIZONTAL)
        #self.hbox_nw = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_adrr = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_btn = wx.BoxSizer(wx.HORIZONTAL)
        
        self.rb_tc = wx.RadioButton(self, -1, "Serial  ")
        self.rb_nwc = wx.RadioButton(self, -1, "Network (TCP)")

        self.st_port = wx.StaticText(self, -1, 'port address',size = (65, -1))
        self.tc_port = wx.TextCtrl(self, -1 , ' ', size = (70, 25))

        self.st_gaddr  = wx.StaticText (self, -1, 'System IP')
        self.st_sysip = wx.StaticText(self, -1, '_ . _ . _ . _',
                                    size = (130, -1))

        self.btn_save = wx.Button(self, -1, 'save', size = (60,25))

        self.btn_save.Bind(wx.EVT_BUTTON, self.SaveSettings)
        
        self.hbox_rb.Add(self.rb_tc, 0, flag=wx.ALIGN_LEFT | wx.LEFT | 
                       wx.ALIGN_CENTER_VERTICAL, border=20)

        self.hbox_rb.Add(self.rb_nwc, 0, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 40)
        

        self.hbox_portip.Add(self.st_port, 0, flag=wx.ALIGN_LEFT | wx.LEFT | 
                       wx.ALIGN_CENTER_VERTICAL, border=20)

        self.hbox_portip.Add(self.tc_port, 0, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 33)

        self.hbox_adrr.Add(self.st_gaddr, 0, flag = wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 20 )
        self.hbox_adrr.Add(self.st_sysip, 0, flag = wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 55)
        self.hbox_btn.Add(self.btn_save, 0, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 120)
                       
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.vbox.AddMany ([
            (0,10,0),
            (self.hbox_rb, 1, wx.EXPAND | wx.ALL),
            (0,20,0),
            (self.hbox_portip, 1, wx.EXPAND | wx.ALL),
            (0,20,0),
            (self.hbox_adrr, 1, wx.EXPAND | wx.ALL),
            (0,20,0),
            (self.hbox_btn, 1, wx.EXPAND | wx.ALL),
            (0,20,0)
            ])

        self.initDialog()
        self.SetSizerAndFit(self.vbox)
        self.SetAutoLayout(True)

    def initDialog(self):
        """
        Initialize dialog controls with existing configuration.

        Updates interface selection, port value,
        and displays system IP address.

        Args:
            self: Instance reference.

        Returns:
            None
        """
        if(self.cdata[self.type]["interface"] == "tcp"):
            self.rb_nwc.SetValue(True)
        else:
            self.rb_tc.SetValue(True)
        self.tc_port.SetValue(self.cdata[self.type]["tcp"]["port"])
        self.st_sysip.SetLabel(str(self.get_network_subnet()[0]))

    def SaveSettings(self, e):
        """
        Save configured port and interface settings.

        Stores selected interface type and port
        into application configuration data.

        Args:
            e: Button click event.

        Returns:
            None
        """
        iftype = 'serial'
        rbval = self.rb_nwc.GetValue()
        if(rbval):
            iftype = "network"
        
        portno = self.tc_port.GetValue()

        if self.type == "scc":
            self.top.ldata['ssccif'] = iftype
            self.top.ldata['ssccpn'] = portno
        else:
            self.top.ldata['sthcif'] = iftype
            self.top.ldata['sthcpn'] = portno

        self.Destroy()
        self.parent.EndModal(True)
    
    def get_network_subnet(self):
        """
        Retrieve local system subnet/IP address.

        Used to display host system network details
        in the dialog window.

        Args:
            self: Instance reference.

        Returns:
            tuple: System IP information.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 88))
        return (s.getsockname())
        
class PortDialog(wx.Dialog):
    """
    Port configuration dialog container.

    Hosts the PortWindow and provides
    dialog-level controls for saving
    SCC/THC port settings.
    """
    
    def __init__ (self, parent, top, cdata):
        """
        Initialize PortDialog.

        Args:
            parent: Parent window.
            top: Reference to main application frame.
            cdata: Configuration data dictionary.

        Returns:
            None
        """
        type = list(cdata.keys())[0]
        title = "Switch Control Computer - Port"
        if type == "thc":
            title = "Test Host Computer - Port"

        wx.Dialog.__init__(self, parent, -1, title,
                           size=wx.Size(100, 100),
                           style=wx.STAY_ON_TOP|wx.DEFAULT_DIALOG_STYLE,
                           name="Config Dialog")

        self.top = top
        self.win = PortWindow(self, top, cdata)

        # Sizes the window to fit its best size.
        self.Fit()
        self.CenterOnParent(wx.BOTH)
    
    def OnOK (self, evt):
        """
        Handle OK/close event for the dialog.

        Ends the modal dialog after saving settings.

        Args:
            evt: Dialog event.

        Returns:
            None
        """
    # Returns numeric code to caller
        self.EndModal(wx.ID_OK)