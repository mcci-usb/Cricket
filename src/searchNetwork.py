# -*- coding: utf-8 -*-
##############################################################################
#
# Module: searchNetwork.py
#
# Description:
#     Dialog window used to scan server network IP address
#     and port availability for SCC and THC systems.
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

# Own modules
from uiGlobals import *

# Built-in imports
import threading
import socket

# Configuration imports
import configdata

CC_PORT = 2021
HC_PORT = 2022

##############################################################################
# Utilities
##############################################################################
class ScanNwThread(threading.Thread):
    """
    Thread class used for scanning network nodes.

    Performs subnet scanning to detect active
    SCC / THC servers listening on a given port.

    Attributes:
        port: Network port to scan.
        txtsysip: UI label displaying system IP.
        txtctrl: UI control displaying detected IP.
        btnScan: Scan button reference.
        completed_event: Thread stop event flag.
    """
    def __init__(self, port, txtsysip, txtctrl, btnScan, name="NwScanThread"):
        """
        Initialize network scanning thread.

        Args:
            port: Network port number.
            txtsysip: System IP display control.
            txtctrl: Network IP combo control.
            btnScan: Scan button reference.
            name: Thread name.

        Returns:
            None
        """
        self.port = port
        self.txtctrl = txtctrl
        self.txtsysip = txtsysip
        self.btnScan = btnScan
        
        self.completed_event = threading.Event()
        threading.Thread.__init__(self, name=name)
 
    def run(self):
        """
        Execute subnet scanning process.

        Searches IP range and detects
        available server nodes.

        Args:
            self: Instance reference.

        Returns:
            None
        """
        subnet = self.get_network_subnet()[0]
        wx.CallAfter(self.txtsysip.SetLabel, str(subnet))
        ips = str(subnet).split(".")
        strsn = str(ips[0])+"."+str(ips[1])+"."+str(ips[2])
        portip = "No Node found"
        for ip in range(0, 255):
            if self.completed_event.is_set():
                break
            host = strsn+"."+str(ip)
            wx.CallAfter(print, f"Searching IP: {host}")
            try:
                s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.3)
                result = s.connect((host, self.port))
                portip = host
                s.close()
                break
            except:
                s.close()
        
        wx.CallAfter(self.txtctrl.SetValue, portip)
        wx.CallAfter(self.btnScan.SetLabel, "scan network")
    
    def join(self, timeout = None):
        """
        Stop network scanning thread.

        Args:
            timeout: Optional join timeout.

        Returns:
            None
        """
        self.completed_event.set()
        super().join(timeout)

    def get_network_subnet(self):
        """
        Retrieve system subnet information.

        Args:
            self: Instance reference.

        Returns:
            tuple:
                Local system IP and port.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 88))
        return (s.getsockname())
    
class SearchNetwork(wx.Panel):
    """
    UI panel for scanning network servers.

    Provides controls to:

    - Scan SCC / THC servers
    - Configure search port
    - Detect server OS
    - Save network configuration

    Attributes:
        parent: Parent window reference.
        ctype: Configuration type (SCC / THC).
        scan_flg: Scan state flag.
        searchthread: Active scan thread.
        ostype: Selected server OS type.
    """
    def __init__(self, parent, ctype):
        """
        Initialize SearchNetwork panel.

        Args:
            parent: Parent window reference.
            ctype: Configuration type identifier.

        Returns:
            None
        """
        super(SearchNetwork, self).__init__(parent)
        
        self.SetBackgroundColour("White")
        self.ctype = ctype
        self.scan_flg = False
        self.searchthread = None
        self.ostype = "win32"
        # self.vboxParent = wx.BoxSizer(wx.VERTICAL)
        self.scan_network()
        
    def scan_network(self):
        """
        Build network scanning UI layout.

        Initializes controls for:

        - Port input
        - Scan trigger
        - OS selection
        - Save configuration

        Args:
            self: Instance reference.

        Returns:
            None
        """
        self.SetBackgroundColour("White")
        # self.SetMinSize((480,520))
        sb = wx.StaticBox(self, -1,"Scan Network")

        # Create StaticBoxSizer as vertical
        self.vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)
        self.btn_scannwc= wx.Button(self, -1, "Search "+self.ctype, size = (80, -1))
        self.st_port = wx.StaticText(self, -1, "Search Port")
        self.st_sysip = wx.StaticText(self, -1, "------")
        self.tc_port = wx.TextCtrl(self, -1, "2021",size = (50, -1))
        self.tc_nwcip = wx.ComboBox(self, -1,  size=(100,-1))
        self.btn_save= wx.Button(self, -1, "Save", size = (50, -1))

        self.st_os = wx.StaticText(self, -1, "Server OS")
        self.rb_win = wx.RadioButton(self, ID_RBTN_WIN, "Windows")
        self.rb_linux = wx.RadioButton(self, ID_RBTN_LINUX, "Linux")
        self.rb_mac = wx.RadioButton(self, ID_RBTN_MAC, "Mac")
        
        # Create BoxSizer as horizontal
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.wait_flg = False
        
        self.hbox1.Add(self.st_port, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 10)
        self.hbox1.Add(self.tc_port, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 13)
        self.hbox1.Add(10, 10, 0)
        self.hbox1.Add(self.btn_scannwc, 0, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 0)
        self.hbox1.Add(10, 10, 0)
        self.hbox1.Add(self.tc_nwcip, 0, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 15)
        self.hbox1.Add(self.st_sysip, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 10)
        
        self.hbox1.Add(self.btn_save, 0, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 62)
        
        self.hbox.Add(self.st_os, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 10)
        self.hbox.Add(self.rb_win, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 10)
        self.hbox.Add(self.rb_linux, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 10)
        self.hbox.Add(self.rb_mac, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 10)
        self.btn_scannwc.Bind(wx.EVT_BUTTON, self.ScanNetworkComp)
        self.btn_save.Bind(wx.EVT_BUTTON, self.SaveNetworkComp)

        self.Bind(wx.EVT_RADIOBUTTON, self.SelectOsChanged)
      
        self.vbox.AddMany([
            (self.hbox1, 0, wx.ALIGN_LEFT),
            (10,5,0),
            (self.hbox, 0, wx.ALIGN_LEFT),
            (10,5,0)
            ])
        # Set size of frame
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.Layout()
        self.set_param()
    
    def SaveNetworkComp(self, e):
        """
        Save scanned network configuration.

        Stores detected IP, port, and OS type.

        Args:
            e: wx Event object.

        Returns:
            None
        """
        devaddr = self.tc_nwcip.GetValue()
        portno = self.tc_port.GetValue()
        # os = self.SelectOsChanged()

        if self.ctype == "SCC":
            # configdata.set_nw_scc_config({"ip": devaddr, "port": portno, "os": })
            configdata.set_nw_scc_config({"ip": devaddr, "port": portno, "os":self.ostype})
           
        elif self.ctype == "THC":
            configdata.set_nw_thc_config({"ip": devaddr, "port": portno, "os":self.ostype})
          
    def SelectOsChanged(self, e):
        """
        Handle server OS selection change.

        Updates internal OS type based
        on selected radio button.

        Args:
            e: wx Event object.

        Returns:
            None
        """
        rb = e.GetEventObject()

        id = rb.GetId()

        if id == ID_RBTN_WIN:
            # Windows
            self.ostype = "win32"
            
        elif id == ID_RBTN_LINUX:
            # Returs highspeed
            self.ostype = "linux"

        elif id == ID_RBTN_MAC:
            # Returs highspeed
            self.ostype = "darwin"
     
    def ScanNetworkComp(self, e):
        """
        Handle scan button event.

        Starts or stops network scanning.

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
        begins subnet search.

        Args:
            self: Instance reference.

        Returns:
            None
        """
        self.scan_flg = True
        self.btn_scannwc.SetLabel("stop scan")
       
        portstr = self.tc_port.GetValue()
        
        self.tc_nwcip.SetValue("searching network")
        
        if self.ctype == "THC":
            port = HC_PORT
        else:
            port = CC_PORT

        try:
            port = int(portstr)
        except:
            self.tc_port.SetValue(str(port))

        if self.searchthread != None:
            del self.searchthread
        self.searchthread = ScanNwThread(port, self.st_sysip, self.tc_nwcip, self.btn_scannwc)

        self.searchthread.start()
            
    def StopNwScan(self):
        """
        Stop active network scanning.

        Terminates scanning thread safely.

        Args:
            self: Instance reference.

        Returns:
            None
        """
        self.btn_scannwc.SetLabel("scan network")
        self.scan_flg = False 
        self.searchthread.join()  

    def set_param(self):
        """
        Load saved network configuration.

        Initializes UI fields with stored:

        - IP address
        - Port number
        - OS type

        Args:
            self: Instance reference.

        Returns:
            None
        """
        self.config_data = configdata.read_all_config()
        
        # self.port = self.config_data["uc"]["mynodes"]["mycc"], self.config_data["uc"]["mynodes"]["mythc"]
        self.port = None
        if self.ctype == "SCC":
            self.port = self.config_data["uc"]["mynodes"]["mycc"]["tcp"]["port"]
            self.sip = self.config_data["uc"]["mynodes"]["mycc"]["tcp"]["ip"]
            self.ostype = self.config_data["uc"]["mynodes"]["mycc"]["os"]
        else:
            mythckeys = list(self.config_data["uc"]["mynodes"]["mythc"]["tcp"].keys())
            if len(mythckeys) > 0:
                self.port = self.config_data["uc"]["mynodes"]["mythc"]["tcp"]["port"]
                self.sip = self.config_data["uc"]["mynodes"]["mythc"]["tcp"]["ip"]
                self.ostype = self.config_data["uc"]["mynodes"]["mythc"]["os"]
            else:
                self.port = ""
                self.sip = ""
                self.ostype = "win32"
            
        self.tc_port.SetValue(self.port)
        self.tc_nwcip.SetValue(self.sip)
        if self.ostype == "win32":
            self.rb_win.SetValue(True)
        elif self.ostype == "linux":
            self.rb_linux.SetValue(True)
        elif self.ostype == "darwin":
            self.rb_mac.SetValue(True)