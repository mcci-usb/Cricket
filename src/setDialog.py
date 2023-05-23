
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
#    V4.0.0 Wed May 25 2023 17:00:00   Seenivasan V 
#       Module created
##############################################################################

# Built-in imports
import socket

# Lib imports
import wx
import threading

# Own modules
from uiGlobals import *
import devControl

CC_PORT = 2021
HC_PORT = 2022

##############################################################################
# Utilities
##############################################################################
class ScanNwThread(threading.Thread):
    """
    A class ScannNwThread with init method.
    using Threading in Scanning the network from client and server.
    """
    def __init__(self, port, txtsysip, txtctrl, btnScan, name="NwScanThread"):
        """
        adding event with threading.

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            port: network port number.
            txtsysip: system listening own system ip
            txtctrl: maually enter ipaddress in network,
            name: name as NwScanThread. 
        Returns:
            None:
        """
        self._stopevent = threading.Event()

        self.port = port
        self.txtctrl = txtctrl
        self.txtsysip = txtsysip
        self.btnScan = btnScan
        
        threading.Thread.__init__(self, name=name)
 
    def run(self):
        """
        thread running

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None

        """
        subnet = self.get_network_subnet()[0]
        self.txtsysip.SetLabel(str(subnet))
        ips = str(subnet).split(".")
        strsn = str(ips[0])+"."+str(ips[1])+"."+str(ips[2])
        portip = "No Node found"
        for ip in range(1, 255):
            if self._stopevent.isSet( ):
                break
            host = strsn+"."+str(ip)
            try:
                s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.3)
                result = s.connect((host, self.port))
                portip = host
                s.close()
                break
            except:
                s.close()
        self.txtctrl.SetValue(portip)
        self.btnScan.SetLabel("scan network")    

    def join(self, timeout = None):
        """
        join the thread event

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            timeout: timer is running between start and stop
        Returns:
            None
        """
        self._stopevent.set()

    def get_network_subnet(self):
        """
        getting the hostcomputer network subnet with ipaddress.

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            hostcomputer ipaddress
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 88))
        return (s.getsockname())


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

        self.scan_flg = False
        self.searchthread = None

        self.hbox_rb = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_portip = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_nw = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_adrr = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_btn = wx.BoxSizer(wx.HORIZONTAL)
        
        self.rb_tc = wx.RadioButton(self, -1, "Serial  ")
        self.rb_nwc = wx.RadioButton(self, -1, "Network (TCP)")

        self.st_port = wx.StaticText(self, -1, 'port address',size = (65, -1))
        self.tc_port = wx.TextCtrl(self, -1 , ' ', size = (70, 25))

        self.btn_scan = wx.Button(self, -1, 'scan network', size = (94,25))
        self.tc_nwcip = wx.ComboBox(self,
                                     size=(130, -1),
                                     style=wx.CB_DROPDOWN)
        self.tc_scan = wx.StaticText(self, -1, '', size = (10,10))

        self.st_gaddr  = wx.StaticText (self, -1, 'System IP')
        self.st_sysip = wx.StaticText(self, -1, '_ _ _ _', size = (130, -1))

        self.btn_save = wx.Button(self, -1, 'save', size = (60,25))

        self.hbox_rb.Add(self.rb_tc, 0, flag=wx.ALIGN_LEFT | wx.LEFT | 
                       wx.ALIGN_CENTER_VERTICAL, border=20)

        self.hbox_rb.Add(self.rb_nwc, 0, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 40)
        
        self.hbox_portip.Add(self.st_port, 0, flag=wx.ALIGN_LEFT | wx.LEFT | 
                       wx.ALIGN_CENTER_VERTICAL, border=20)

        self.hbox_portip.Add(self.tc_port, 0, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 33)

        self.hbox_nw.Add(self.btn_scan, 0, flag=wx.ALIGN_LEFT | wx.LEFT | 
                       wx.ALIGN_CENTER_VERTICAL, border=18)
        self.hbox_nw.Add(self.tc_nwcip, 0,flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 20)
        self.hbox_nw.Add(self.tc_scan, 0,flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 10)
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
            (self.hbox_nw, 1, wx.EXPAND | wx.ALL),
            (0,20,0),
            (self.hbox_adrr, 1, wx.EXPAND | wx.ALL),
            (0,20,0),
            (self.hbox_btn, 1, wx.EXPAND | wx.ALL),
            (0,20,0)
            ])

        self.btn_scan.Bind(wx.EVT_BUTTON, self.ScanNetwork)
        self.btn_save.Bind(wx.EVT_BUTTON, self.SaveSettings)
        
        self.initDialog()
        self.SetSizerAndFit(self.vbox)
        # Determines whether the Layout function will be called 
        # Automatically when the window is resized.
        self.SetAutoLayout(True)

    def initDialog(self):
        """
        initiating the netowork dialog windows

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        # if self.type == "scc":
        #     if self.top.ldata['sccif'] == "network":
        #         self.rb_nwc.SetValue(True)
        #     else:
        #         self.rb_tc.SetValue(True)
        #     self.tc_nwcip.SetValue(self.top.ldata['sccid'])
        #     self.tc_port.SetValue(self.top.ldata['sccpn'])
        # else:
        #     if(self.top.ldata['thcif'] == "network"):
        #         self.rb_nwc.SetValue(True)
        #     else:
        #         self.rb_tc.SetValue(True)
        #     self.tc_nwcip.SetValue(self.top.ldata['thcid'])
        #     self.tc_port.SetValue(self.top.ldata['thcpn'])

        # self.st_sysip.SetLabel(str(self.get_network_subnet()[0]))
        pass

    def ScanNetwork(self, e):
        """
        Scanning the network from Client and Server.

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            e: event in scan network button
        Returns:
            None

        """
        if self.scan_flg == False:
            self.StartNwScan()
        else:
            self.StopNwScan()

    def StartNwScan(self):
        """
        start the server network scanning

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.scan_flg = True
        self.btn_scan.SetLabel("stop scan")
        
        devControl.ResetDeviceControl(self.top)

        portstr = self.tc_port.GetValue()
        
        self.tc_nwcip.SetValue("searching network")
        
        if self.type == "thc":
            port = HC_PORT
        else:
            port = CC_PORT

        try:
            port = int(portstr)
        except:
            self.tc_port.SetValue(str(port))

        if self.searchthread != None:
            del self.searchthread
        self.searchthread = ScanNwThread(port, self.st_sysip, self.tc_nwcip, self.btn_scan)
        self.searchthread.start()
        
    def StopNwScan(self):
        """
        stop the scanning network

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.btn_scan.SetLabel("scan network")
        self.scan_flg = False 
        self.searchthread.join()  
    
    def SaveSettings(self, e):
        """
        save the Ipaddress and port number.

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            e: click on save button save the Dialog box window.
        Returns:
            None
        """
        iftype = 'serial'
        rbval = self.rb_nwc.GetValue()
        if(rbval):
            iftype = "network"
        
        devaddr = self.tc_nwcip.GetValue()
        portno = self.tc_port.GetValue()

        if self.type == "scc":
            self.top.ldata['sccif'] = iftype
            self.top.ldata['sccid'] = devaddr
            self.top.ldata['sccpn'] = portno
        else:
            self.top.ldata['thcif'] = iftype
            self.top.ldata['thcid'] = devaddr
            self.top.ldata['thcpn'] = portno

        self.Destroy()
        self.parent.EndModal(True)
    
    def get_network_subnet(self):
        """
        getting the subnet mask hostcomputer ipaddress.

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 88))
        return (s.getsockname())
        
                
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
            type: dialog box
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