
##############################################################################
# 
# Module: setDialog.py
#
# Description:
#     Dialog to display system setup configuration
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
#     Seenivasan V, MCCI Corporation June 2021
#
# Revision history:
#     V2.3.14 Wed July 12 2021 15:20:05   Seenivasan V 
#       Module created
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
    A  class AboutWindow with init method
    The AboutWindow navigate to MCCI Logo with naming of 
    application UI "Criket",Version and copyright info.  
    """
    def __init__ (self, parent, top, type):
        """
        AboutWindow that contains the about dialog elements.

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
            top: creates an object
        Returns:
            None
        """
        wx.Window.__init__(self, parent, -1,
                           size=wx.Size(400,300),
                           style=wx.CLIP_CHILDREN,
                           name=type)

        self.top = top

        self.type = type
        self.parent = parent

        self.nwip = None

        self.hbox_rb = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_portip = wx.BoxSizer(wx.HORIZONTAL)
        #self.hbox_nw = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_adrr = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_btn = wx.BoxSizer(wx.HORIZONTAL)
        
        self.rb_tc = wx.RadioButton(self, -1, "Serial  ")
        self.rb_nwc = wx.RadioButton(self, -1, "Network (TCP)")

        self.st_port = wx.StaticText(self, -1, 'port address', size = (65, -1))
        self.tc_port = wx.TextCtrl(self, -1 , ' ', size = (70, 25))

        self.st_gaddr  = wx.StaticText (self, -1, 'System IP')
        self.st_sysip = wx.StaticText(self, -1, '_ . _ . _ . _', size = (130, -1))

        self.btn_save = wx.Button(self, -1, 'save', size = (60,25))

        self.btn_save.Bind(wx.EVT_BUTTON, self.SaveSettings)
        
        self.hbox_rb.Add(self.rb_tc, 0, flag=wx.ALIGN_RIGHT | wx.LEFT | 
                       wx.ALIGN_CENTER_VERTICAL, border=20)

        self.hbox_rb.Add(self.rb_nwc, 0, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 40)
        

        self.hbox_portip.Add(self.st_port, 0, flag=wx.ALIGN_RIGHT | wx.LEFT | 
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
        #self.initDialog1()

        #self.SetSizer(self.vbox)
        self.SetSizerAndFit(self.vbox)
        # Determines whether the Layout function will be called 
        # Automatically when the window is resized.
        self.SetAutoLayout(True)


    def initDialog(self):
        if self.type == "scc":
            if self.top.ldata['ssccif'] == "network":
                self.rb_nwc.SetValue(True)
            else:
                self.rb_tc.SetValue(True)
            self.tc_port.SetValue(self.top.ldata['ssccpn'])
        else:
            if(self.top.ldata['sthcif'] == "network"):
                self.rb_nwc.SetValue(True)
            else:
                self.rb_tc.SetValue(True)
            self.tc_port.SetValue(self.top.ldata['sthcpn'])

        self.st_sysip.SetLabel(str(self.get_network_subnet()[0]))

    def SaveSettings(self, e):
        iftype = 'serial'
        rbval = self.rb_nwc.GetValue()
        if(rbval):
            iftype = "network"
        
        #devaddr = self.tc_nwcip.GetValue()
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
        return (socket.gethostbyname_ex(socket.gethostname())[2])
        
        
class PortDialog(wx.Dialog):
    """
    wxWindows application must have a class derived from wx.Dialog.
    """
    def __init__ (self, parent, top, type):
        """
        A AboutDialog is Window an application creates to 
        retrieve Cricket UI Application input.

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
            top: create a object
        Returns:
            None
        """
        title = "Switch Control Computer - Port"
        if type == "thc":
            title = "Test Host Computer - Port"

        wx.Dialog.__init__(self, parent, -1, title,
                           size=wx.Size(100, 100),
                           style=wx.STAY_ON_TOP|wx.DEFAULT_DIALOG_STYLE,
                           name="Config Dialog")

        self.top = top
        self.win = PortWindow(self, top, type)

        # Sizes the window to fit its best size.
        self.Fit()
        # Centre frame using CentreOnParent() function,
        # Show window in the center of the screen.
        # Centres the window on its parent.
        self.CenterOnParent(wx.BOTH)
    
    def OnOK (self, evt):
        """
        OnOK() event handler function retrieves the label of 
        source button, which caused the click event. 

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            evt: The event parameter in the OnOK() method is an 
            object specific to a particular event type.
        Returns:
            None        
        """
    # Returns numeric code to caller
        self.EndModal(wx.ID_OK)