import wx
import threading
import configdata

class SetNetwork(wx.Panel):
    def __init__(self, parent, ctype):
        # wx.Panel.__init__(self, parent, title="Network Configuration", size=(550, 480),
        #                    style=wx.DEFAULT_DIALOG_STYLE)
        super(SetNetwork, self).__init__(parent)
        
        self.SetBackgroundColour("White")
        
        self.ctype = ctype
        
        # self.config_data = configdata.read_all_config()
        
        # print("------------->>>>>: ", self.config_data["uc"]["mynodes"]["mycc"], self.config_data["uc"]["mynodes"]["mythc"])
        
        
        # self.vboxParent = wx.BoxSizer(wx.VERTICAL)
        self.set_network()

    
    def set_port(self):
        self.config_data = configdata.read_all_config()
        
        # self.port = self.config_data["uc"]["mynodes"]["mycc"], self.config_data["uc"]["mynodes"]["mythc"]
        self.port = None
        if self.ctype == "SCC":
            self.port = self.config_data["cc"]["tcp"]["port"]
            self.sip = self.config_data["cc"]["tcp"]["ip"]
        else:
            self.port = self.config_data["thc"]["tcp"]["port"]
            self.sip = self.config_data["thc"]["tcp"]["ip"]
            
        print("##Server Type: ", self.ctype)
        print("####Server Config: ", self.port)
        
        self.scc_tc_port.SetValue(self.port)
        self.scc_tc_sip.SetValue(self.sip)
        
        # for data in self.port:
        #     if 'control computer' in data.get('name', '').lower():
        #         # This is the condition for 'control computer'
        #         self.scc_tc_port.SetValue(data.get('tcp', {}).get('port', ''))
        #         print(f"Found 'control computer': Set port to {data.get('tcp', {}).get('port', '')}")
                
        #     elif 'test host computer' in data.get('name', '').lower():
        #         # This is the condition for 'test host computer'
        #         self.scc_tc_port.SetValue(data.get('tcp', {}).get('port', ''))
        #         print(f"Found 'test host computer': Set port to {data.get('tcp', {}).get('port', '')}")
                
        #     else:
        #         # Handle the case when neither 'control computer' nor 'test host computer' is present
        #         print("Neither 'control computer' nor 'test host computer' found.")
            
    def set_network(self):
        self.SetBackgroundColour("White")
        # self.SetMinSize((480,520))

        # self.top = top
        # Create static box with naming of Log Window
        sb = wx.StaticBox(self, -1,"Set Network")

        # Create StaticBoxSizer as vertical
        self.vbox1 = wx.StaticBoxSizer(sb, wx.VERTICAL)
        

        self.scc_st_port = wx.StaticText(self, -1, self.ctype+" Port" ,size = (65, -1))
        # self.scc_tc_port = wx.TextCtrl(self, -1, "1234", size = (65, -1))
        self.scc_tc_port = wx.TextCtrl(self, -1, " ", size = (60, -1))
        self.scc_st_sip = wx.StaticText(self, -1, self.ctype+" IP",size = (60, -1))
        self.scc_tc_sip = wx.TextCtrl(self, -1, " ",size = (95, -1))
        
        self.btn_save= wx.Button(self, -1, "Save", size = (60, -1))
        
        self.set_port()
        
    
        # Create BoxSizer as horizontal
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.wait_flg = False
        
        self.hbox2.Add(self.scc_st_port, 0, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 5)
        self.hbox2.Add(self.scc_tc_port, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 10)
        self.hbox2.Add(self.scc_st_sip, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 15)
        self.hbox2.Add(self.scc_tc_sip, 0, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 0)
        
        self.hbox2.Add(self.btn_save, 0, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 20)
       
        # self.szr_top = wx.BoxSizer(wx.VERTICAL)
        
        self.btn_save.Bind(wx.EVT_BUTTON, self.SaveNetworkComp)
      
        self.vbox1.AddMany([
            (self.hbox2, 0, wx.ALIGN_LEFT),
            (10,5,0)
            ])
        # Set size of frame
        self.SetSizer(self.vbox1)
        self.vbox1.Fit(self)
        self.Layout()
    
    # def get_nw_scc_config():
    # # Assuming you have a way to store and retrieve the configuration
    # # For example, using a global variable or a configuration file
    #     config = {
    #         "ip": "x.x.x.x",  # Replace with your actual IP address
    #         "port": "1122"     # Replace with your actual port number
    #     }
    #     return config
    
    
    def load_network_config(self):
        # Load the network configuration based on the ctype (SCC or THC)
        config = {}
        if self.ctype == "SCC":
            config = configdata.get_nw_scc_config()
        elif self.ctype == "THC":
            config = configdata.get_nw_thc_config()

        # Update the GUI with the loaded configuration
        if config:
            self.scc_tc_sip.SetValue(config.get("ip", ""))
            self.scc_tc_port.SetValue(config.get("port", ""))
            
    def SaveNetworkComp(self, e):
        print("Setnetwork-saved!!!")
        devaddr = self.scc_tc_sip.GetValue()
        portno = self.scc_tc_port.GetValue()
        if self.ctype == "SCC":
            configdata.set_scc_config({"type": "tcp", "ip": devaddr, "port": portno})
            print("Save-Done-scc!!!")
        elif self.ctype == "THC":
            configdata.set_thc_config({"type": "tcp", "ip": devaddr, "port": portno})
            print("Save-Done-thc!!!")
        
        