
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
#     V2.4.0-2 Wed April 28 2021 18:50:10 seenivasan 
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

CC_PORT = 5566
HC_PORT = 5567

##############################################################################
# Utilities
##############################################################################
class SetWindow(wx.Window):
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
        self.hbox_nw = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_btn = wx.BoxSizer(wx.HORIZONTAL)
        
        self.rb_tc = wx.RadioButton(self, -1, "Serial  ")
        self.rb_nwc = wx.RadioButton(self, -1, "Network (TCP)")

        self.btn_scan = wx.Button(self, -1, 'scan network', size = (80,25))
        self.tc_nwcip = wx.ComboBox(self,
                                     size=(130, -1),
                                     style=wx.CB_DROPDOWN)
        self.tc_scan = wx.StaticText(self, -1, '', size = (40,25))

        self.btn_save = wx.Button(self, -1, 'save', size = (60,25))

        self.btn_scan.Bind(wx.EVT_BUTTON, self.ScanNetwork)
        self.btn_save.Bind(wx.EVT_BUTTON, self.SaveSettings)


        self.hbox_rb.Add(self.rb_tc, 0, flag=wx.ALIGN_RIGHT | wx.LEFT | 
                       wx.ALIGN_CENTER_VERTICAL, border=20)

        self.hbox_rb.Add(self.rb_nwc, 0, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 40)

        self.hbox_nw.Add(self.btn_scan, 0, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 20)
        self.hbox_nw.Add(self.tc_nwcip, 0,flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 20)
        self.hbox_nw.Add(self.tc_scan, 0,flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 20)

        self.hbox_btn.Add(self.btn_save, 0, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 80)
                       
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.vbox.AddMany ([
            (0,10,0),
            (self.hbox_rb, 1, wx.EXPAND | wx.ALL),
            (0,20,0),
            (self.hbox_nw, 1, wx.EXPAND | wx.ALL),
            (0,20,0),
            (self.hbox_btn, 1, wx.EXPAND | wx.ALL),
            (0,20,0)
            ])

        self.initDialog()

        #self.SetSizer(self.vbox)
        self.SetSizerAndFit(self.vbox)
        # Determines whether the Layout function will be called 
        # Automatically when the window is resized.
        self.SetAutoLayout(True)


    def initDialog(self):
        if self.type == "scc":
            if self.top.ldata['sccif'] == "network":
                self.rb_nwc.SetValue(True)
            else:
                self.rb_tc.SetValue(True)
            self.tc_nwcip.SetValue(self.top.ldata['sccid'])
        else:
            if(self.top.ldata['thcif'] == "network"):
                self.rb_nwc.SetValue(True)
            else:
                self.rb_tc.SetValue(True)
            self.tc_nwcip.SetValue(self.top.ldata['thcid'])


    def ScanNetwork(self, e):
        devControl.ResetDeviceControl(self.top)
        self.tc_nwcip.SetValue("searching network")
        
        port = CC_PORT
        if self.type == "thc":
            port = HC_PORT
        
        self.nwip = self.scan_server(port)
        self.tc_nwcip.SetValue(self.nwip)
    

    def SaveSettings(self, e):
        iftype = 'serial'
        rbval = self.rb_nwc.GetValue()
        if(rbval):
            iftype = "network"
        
        devaddr = self.tc_nwcip.GetValue()
        if self.type == "scc":
            self.top.ldata['sccif'] = iftype
            self.top.ldata['sccid'] = devaddr
        else:
            self.top.ldata['thcif'] = iftype
            self.top.ldata['thcid'] = devaddr
        self.Destroy()
        self.parent.EndModal(True)
    
    def get_network_subnet(self):
        return (socket.gethostbyname_ex(socket.gethostname())[2])
        
    def scan_server(self, port):
        subnet = self.get_network_subnet()[0]
        ips = str(subnet).split(".")
        strsn = str(ips[0])+"."+str(ips[1])+"."+str(ips[2])
        portip = "No Node found"
        for ip in range(1, 255):
            host = strsn+"."+str(ip)
            try:
                s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.3)
                result = s.connect((host, port))
                portip = host
                s.close()
                break
            except:
                s.close()
        return portip
        

class SetDialog(wx.Dialog):
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
        title = "Switch Control Computer"
        if type == "thc":
            title = "Test Host Computer"

        wx.Dialog.__init__(self, parent, -1, title,
                           size=wx.Size(100, 100),
                           style=wx.STAY_ON_TOP|wx.DEFAULT_DIALOG_STYLE,
                           name="Config Dialog")

        self.top = top
        self.win = SetWindow(self, top, type)

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
