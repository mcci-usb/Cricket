# -*- coding: utf-8 -*-
##############################################################################
# 
# Module: setDialog.py
#
# Description:
#     Dialog to display system setup configuration
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
#
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
    Thread class used to scan network nodes.

    This thread scans the subnet to identify
    available SCC / THC servers listening
    on the specified port.

    Attributes:
        port: Network port to scan.
        txtsysip: UI label showing system IP.
        txtctrl: UI control displaying found IP.
        btnScan: Scan button reference.
    """
    def __init__(self, port, txtsysip, txtctrl, btnScan, name="NwScanThread"):
        """
        Initialize network scanning thread.

        Args:
            port: Network port number.
            txtsysip: System IP label control.
            txtctrl: Target IP text control.
            btnScan: Scan button reference.
            name: Thread name.

        Returns:
            None
        """
        self._stopevent = threading.Event()

        self.port = port
        self.txtctrl = txtctrl
        self.txtsysip = txtsysip
        self.btnScan = btnScan
        
        threading.Thread.__init__(self, name=name)
 
    def run(self):
        """
        Execute network scan operation.

        Scans subnet IP range and detects
        active server nodes.

        Args:
            self: Instance reference.

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
        Stop scanning thread.

        Args:
            timeout: Optional wait timeout.

        Returns:
            None
        """
        self._stopevent.set()

    def get_network_subnet(self):
        """
        Retrieve host system subnet address.

        Args:
            self: Instance reference.

        Returns:
            tuple:
                Local system IP and port.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 88))
        return (s.getsockname())

class SetWindow(wx.Window):
    """
    Configuration window for system setup.

    Provides UI to configure:

    - Interface type (Serial / Network)
    - IP address
    - Port number
    - Network scan

    Attributes:
        parent: Parent dialog reference.
        top: Main application reference.
        type: Configuration type (SCC / THC).
    """
    def __init__ (self, parent, top, type):
        """
        Initialize SetWindow UI.

        Args:
            parent: Parent dialog.
            top: Application top frame.
            type: Configuration type identifier.

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
        Initialize dialog default settings.

        Loads configuration and prepares UI.

        Args:
            self: Instance reference.

        Returns:
            None
        """
        pass

    def ScanNetwork(self, e):
        """
        Handle network scan button event.

        Starts or stops scanning based on state.

        Args:
            e: wx Event object.

        Returns:
            None
        """
        if self.scan_flg == False:
            self.StartNwScan()
        else:
            self.StopNwScan()

    def StartNwScan(self):
        """
        Start network scanning thread.

        Initializes scan parameters and
        begins subnet scanning.

        Args:
            self: Instance reference.

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
        Stop active network scanning.

        Terminates scan thread safely.

        Args:
            self: Instance reference.

        Returns:
            None
        """
        self.btn_scan.SetLabel("scan network")
        self.scan_flg = False 
        self.searchthread.join()  
    
    def SaveSettings(self, e):
        """
        Save configured interface settings.

        Stores selected interface type,
        IP address, and port number.

        Args:
            e: wx Event object.

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
        Retrieve system subnet details.

        Args:
            self: Instance reference.

        Returns:
            tuple:
                Local IP and port details.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 88))
        return (s.getsockname())
           
class SetDialog(wx.Dialog):
    """
    Dialog wrapper for SetWindow.

    Displays configuration window
    for SCC / THC setup.

    Attributes:
        parent: Parent frame reference.
        top: Application reference.
        type: Configuration type.
    """
    def __init__ (self, parent, top, type):
        """
        Initialize SetDialog window.

        Args:
            parent: Parent frame.
            top: Application top reference.
            type: Configuration type (SCC / THC).

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
        self.CenterOnParent(wx.BOTH)
    
    def OnOK (self, evt):
        """
        Handle dialog confirmation event.

        Closes dialog with OK status.

        Args:
            evt: wx Event object.

        Returns:
            None
        """
    # Returns numeric code to caller
        self.EndModal(wx.ID_OK)