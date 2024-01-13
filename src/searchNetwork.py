import wx

import threading
import socket
import configdata

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
        # self.completed_event = threading.Event()
        
         # Event to signal completion
        

        self.port = port
        self.txtctrl = txtctrl
        self.txtsysip = txtsysip
        self.btnScan = btnScan
        
        self.completed_event = threading.Event()
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
        # print("subnet:", subnet)
        # self.txtsysip.SetLabel(str(subnet))
        wx.CallAfter(self.txtsysip.SetLabel, str(subnet))
        ips = str(subnet).split(".")
        # print("-------------:", ips)
        strsn = str(ips[0])+"."+str(ips[1])+"."+str(ips[2])
        # print("Strsn---->", strsn)
        portip = "No Node found"
        for ip in range(160, 165):
            if self.completed_event.is_set():
                break
            host = strsn+"."+str(ip)
            # print("Searching IP: ", host)
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
        # self.txtctrl.SetValue(portip)
        # self.btnScan.SetLabel("scan network")
        wx.CallAfter(self.txtctrl.SetValue, portip)
        wx.CallAfter(self.btnScan.SetLabel, "scan network")
        
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
        self.completed_event.set()
        super().join(timeout)

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
    

class SearchNetwork(wx.Panel):
    def __init__(self, parent, ctype):
        # wx.Panel.__init__(self, parent, title="Network Configuration", size=(550, 480),
        #                    style=wx.DEFAULT_DIALOG_STYLE)
        super(SearchNetwork, self).__init__(parent)
        
        self.SetBackgroundColour("White")
        self.ctype = ctype
        self.scan_flg = False
        self.searchthread = None
        
        # self.vboxParent = wx.BoxSizer(wx.VERTICAL)
        self.scan_network()
        
    def scan_network(self):
        self.SetBackgroundColour("White")
        # self.SetMinSize((480,520))

        # self.top = top
        # Create static box with naming of Log Window
        sb = wx.StaticBox(self, -1,"Scan Network")

        # Create StaticBoxSizer as vertical
        self.vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)
        
        self.btn_scannwc= wx.Button(self, -1, "Search "+self.ctype, size = (80, -1))
        self.st_port = wx.StaticText(self, -1, "Search Port")
        self.st_sysip = wx.StaticText(self, -1, "------")
        self.tc_port = wx.TextCtrl(self, -1, "2021",size = (50, -1))
        self.tc_nwcip = wx.ComboBox(self,size=(100,-1))
        self.btn_save= wx.Button(self, -1, "Save", size = (50, -1))
        
    
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
       
        
        self.btn_scannwc.Bind(wx.EVT_BUTTON, self.ScanNetworkComp)
        self.btn_save.Bind(wx.EVT_BUTTON, self.SaveNetworkComp)
        
        # self.szr_top = wx.BoxSizer(wx.VERTICAL)
      
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
        print("Save Clicked !!!!")
        devaddr = self.tc_nwcip.GetValue()
        portno = self.tc_port.GetValue()
        if self.ctype == "SCC":
            configdata.set_nw_scc_config({"ip": devaddr, "port": portno})
            print("Save-Done-Scc!!!")
        elif self.ctype == "THC":
            print("Save-Done-Thc!!!")
            configdata.set_nw_thc_config({"ip": devaddr, "port": portno})
        # if self.searchthread and not self.searchthread.completed_event.is_set():
        #     # The thread is still running, handle appropriately (show a message, etc.)
        #     print("Network scanning still in progress. Cannot save.")
        # else:
        #     print("Hey getup...")
        
        
    # def SaveNetworkComp(self, e):
    #     print("Save Clicked !!!!")
    #     if self.searchthread != None:
    #         self.searchthread.join()
        
    def SaveNetworkComp_old(self, e):
        # iftype = 'network'
        # if self.scan_flg == False:
        devaddr = self.tc_nwcip.GetValue()
        portno = self.tc_port.GetValue()
        if self.ctype == "SCC":
            configdata.set_nw_scc_config({"ip": devaddr, "port": portno})
        elif self.ctype == "THC":
            configdata.set_nw_thc_config({"ip": devaddr, "port": portno})
        # print("Save Done")
        self.scan_flg = False 
        # self.searchthread.join()
        if self.searchthread != None:
            self.searchthread.join()
            del self.searchthread
            
        
    def ScanNetworkComp(self, e):
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
        self.btn_scannwc.SetLabel("stop scan")
        
        # devControl.ResetDeviceControl(self.top)

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
        # self.searchthread = ScanNwThread(port, None, self.tc_nwcip, self.btn_scannwc)
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
        self.btn_scannwc.SetLabel("scan network")
        self.scan_flg = False 
        self.searchthread.join()  
    

    def set_param(self):
        self.config_data = configdata.read_all_config()
        
        # self.port = self.config_data["uc"]["mynodes"]["mycc"], self.config_data["uc"]["mynodes"]["mythc"]
        self.port = None
        if self.ctype == "SCC":
            self.port = self.config_data["uc"]["mynodes"]["mycc"]["tcp"]["port"]
            self.sip = self.config_data["uc"]["mynodes"]["mycc"]["tcp"]["ip"]
        else:
            mythckeys = list(self.config_data["uc"]["mynodes"]["mythc"]["tcp"].keys())
            print("MythcKeys: ", mythckeys)
            if len(mythckeys) > 0:
                self.port = self.config_data["uc"]["mynodes"]["mythc"]["tcp"]["port"]
                self.sip = self.config_data["uc"]["mynodes"]["mythc"]["tcp"]["ip"]
            else:
                self.port = ""
                self.sip = ""
            
        print("##Server Type: ", self.ctype)
        print("####Server Config: ", self.port)
        
        self.tc_port.SetValue(self.port)
        self.tc_nwcip.SetValue(self.sip)
    
      