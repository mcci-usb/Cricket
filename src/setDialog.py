
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
#     Seenivasan V, MCCI Corporation Mar 2020
#
# Revision history:
#     V2.3.0 Wed April 28 2021 18:50:10 seenivasan 
#       Module created
##############################################################################

# Built-in imports
import os
import socket

# Lib imports
import wx

# Own modules
from uiGlobals import *

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
                                     size=(100, -1),
                                     style=wx.CB_DROPDOWN)
        self.tc_scan = wx.StaticText(self, -1, '', size = (40,25))

        self.btn_save = wx.Button(self, -1, 'save', size = (60,25))

        #self.btn_scan.Bind(wx.EVT_BUTTON, self.ScanNetwork)
        self.btn_save.Bind(wx.EVT_BUTTON, self.SaveNetwork)


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
            if self.top.ldata['scc']:
                self.rb_nwc.SetValue(True)
            else:
                self.rb_tc.SetValue(True)
            self.tc_nwcip.SetValue(self.top.ldata['sccip'])
        else:
            if(self.top.ldata['thc'] == 0):
                self.rb_tc.SetValue(True)
            else:
                self.rb_nwc.SetValue(True)
            self.tc_nwcip.SetValue(self.top.ldata['thcip'])


    def ScanNetwork(self, e):
        self.tc_nwcip.SetValue("searching network")
        port = 5566
        if self.type == "thc":
            port = 5567
        # elif self.type == "scc":
        #     port = 5566
        self.nwip = self.scan_server(port)
        self.tc_nwcip.SetValue(self.nwip)

    def SaveNetwork(self, e):
        rbval = self.rb_nwc.GetValue()
        selip = self.tc_nwcip.GetValue()
        if self.type == "scc":
            self.top.ldata['scc'] = rbval
            self.top.ldata['sccip'] = selip
        else:
            self.top.ldata['thc'] = rbval
            self.top.ldata['thcip'] = selip
        self.Destroy()
        self.parent.EndModal(True)
        

    def scan_server(self, port):
        print("Scanning server for: ", port)
        portip = "No Node found"
        for ip in range(1, 255):
            host = "192.168.0."+str(ip)
            try:
                s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.3)
                result = s.connect((host, port))
                #ports.append(host)
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
