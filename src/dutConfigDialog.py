from random import choice, choices
import wx

import serial.tools.list_ports
import os
from sys import platform
import re

import configdata

from uiGlobals import IMG_ICON

class DutConfigDialog(wx.Frame):
    def __init__(self, top, dut):
        wx.Frame.__init__(self,None, size=(360,620))

        self.SetBackgroundColour("White")
        self.SetTitle('DUT Config Dialog')
        self.dut = dut
        self.top = top

        self.dut_key = list(self.dut.keys())[0]
        self.dut_type = self.dut[self.dut_key]["interface"]
        self.dut_settings = self.dut[self.dut_key][self.dut_type]
        
        self.vboxParent = wx.BoxSizer(wx.VERTICAL)
        
        self.InitSelectionType()
        self.InitSerialConfig()
        self.InitTcpConfig()
        self.InitDataToWatch()        
        
        self.vboxParent.AddMany([
            (self.vboxRead, 0, wx.EXPAND | wx.ALL, 10),
            (self.vboxSerial, 0, wx.EXPAND | wx.ALL, 10),
            (self.vboxTcp, 0, wx.EXPAND | wx.ALL, 10),
            (self.vboxLog, 0, wx.EXPAND | wx.ALL, 10)
        ])

        self.SetSizer(self.vboxParent)

        self.cb_list = self.filter_port()
        base = os.path.abspath(os.path.dirname(__file__))
        self.SetIcon(wx.Icon(base+"/icons/"+IMG_ICON))
        
        self.UpdateData()

        self.Show()
        self.Layout()


        #--------------------- ---EVENT BIND--- #---------------------
    def filter_port(self):
        """
        filter the Comports list from list UI supported Switch with same VID and PID.
        Args:
            No argument
        Return:
            port_name -  list of availablable port numbers and serial number of 
            the 2101     
        """
        usb_hwid_str = ["USB VID:PID=045E:0646", "USB VID:PID=2341:0042"]
        comlist = serial.tools.list_ports.comports()
        port_name = []

        for port, desc, hwid in sorted(comlist):
            res = [True for gnhwid in usb_hwid_str if(gnhwid in hwid)]
            if(not res):
                port_name.append(port)
        return port_name
    
    
    def InitSelectionType(self):
        self.hboxdr6 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxdrn = wx.BoxSizer(wx.HORIZONTAL)

        bc = wx.StaticBox(self, -1, "Settings", size = (400, 200))
        self.vboxRead = wx.StaticBoxSizer(bc, wx.VERTICAL)
        self.rbtn_ser = wx.RadioButton(self, -1, label='Serial',style = wx.RB_GROUP )
        self.rbtn_tcp = wx.RadioButton(self, -1, label='Network(TCP)')
        self.btn_savetype = wx.Button(self, -1, label='Save', size= (65,25))
        
        self.ihboxdr6 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.ihboxdr6.Add(self.rbtn_ser, flag=wx.LEFT, border=10)
        self.ihboxdr6.Add(self.rbtn_tcp, flag=wx.LEFT, border = 10)
        self.ihboxdr6.Add(self.btn_savetype, flag=wx.LEFT, border=30)
        
        self.hboxdr6.Add(self.ihboxdr6, flag=wx.ALIGN_CENTER_VERTICAL)

        self.st_nameSut = wx.StaticText(self, -1, "Name of DUT")
        self.tc_nameSut = wx.TextCtrl(self, -1, " ", size = (135, 23))
        self.ihboxdrn = wx.BoxSizer(wx.HORIZONTAL)
        self.ihboxdrn.Add(self.st_nameSut, flag=wx.LEFT, border=10)
        self.ihboxdrn.Add(self.tc_nameSut, flag=wx.LEFT, border=10)
        self.hboxdrn.Add(self.ihboxdrn, flag=wx.ALIGN_CENTER_VERTICAL)

        self.vboxRead.AddMany([            
            (self.hboxdr6, 1, wx.EXPAND | wx.ALL, 5),
            (self.hboxdrn, 1, wx.EXPAND | wx.ALL, 5)
        ])

        self.btn_savetype.Bind(wx.EVT_BUTTON, self.SaveTypeName)

        self.rbtn_ser.Bind(wx.EVT_RADIOBUTTON, self.OnSerial)
        self.rbtn_tcp.Bind(wx.EVT_RADIOBUTTON, self.OnNetowrk)

        self.tc_nameSut.SetValue(self.dut[self.dut_key]["name"])


    def InitTcpConfig(self):
        ab = wx.StaticBox(self, -1, "TCP Settings", size = (400, 200))
        self.vboxTcp = wx.StaticBoxSizer(ab, wx.VERTICAL)
        self.st_tcp = wx.StaticText(self, -1, "Will be implemented in future", size = (180, 15))

        self.hboxtcp = wx.BoxSizer(wx.HORIZONTAL)

        self.hboxtcp.Add(self.st_tcp, flag=wx.LEFT, border=10)

        self.vboxTcp.AddMany([
            (self.hboxtcp, 1, wx.EXPAND | wx.ALL, 5),
        ])

    def InitSerialConfig(self):
        ab = wx.StaticBox(self, -1, "COM Port Settings", size = (400, 200))
        self.vboxSerial = wx.StaticBoxSizer(ab, wx.VERTICAL)
        self.cb_list = self.filter_port()
        cb_brate = ["9600", "19200", "38400", "57600", "115200"]
        cb_dbits = ["5","6","7","8"]
        cb_sbits = ["1", "1.5", "2"]
        cb_parity = ["Even", "Mark", "None", "Odd", "Space"]
        cb_pechar = ["(ignore)", "35 ('#')", "42 ('*')", "63 ('?')"]

        self.hboxdrx = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxdr2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxdr3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxdr4 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxdr5 = wx.BoxSizer(wx.HORIZONTAL)

        self.st_port = wx.StaticText(self, -1, "Select Port ", size = (60, 15))
        self.cb_list = [" "]
        self.cb_switch = wx.ComboBox(self, -1, choices = self.cb_list, size = (65,-1))
        self.btn_ref = wx.Button(self, -1, "Refresh", (-1, -1))
    
        self.ihboxdr2 = wx.BoxSizer(wx.HORIZONTAL)
        self.ihboxdr2.Add(self.st_port, flag=wx.LEFT , border=0)
        self.ihboxdr2.Add(self.cb_switch, flag=wx.LEFT, border = 10)
        self.ihboxdr2.Add(self.btn_ref, flag=wx.LEFT, border = 30)

        self.hboxdr2.Add(self.ihboxdr2, flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL, border= 10)
        self.hboxdr2.Add(0,1,0)

        self.st_baud = wx.StaticText(self, -1, "Baud Rate ", size = (60, 15))
        self.st_databits = wx.StaticText(self, -1, "Data Bits")
        
        self.cb_baud = wx.ComboBox(self,
                                     size=(65,-1),
                                     style = wx.TE_PROCESS_ENTER, choices=cb_brate)
        self.cb_Databits = wx.ComboBox(self,
                                     size=(65,-1),
                                     style = wx.TE_PROCESS_ENTER, choices = cb_dbits)

        self.ihboxdr3 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.ihboxdr3.Add(self.st_baud, flag=wx.LEFT, border=10)
        self.ihboxdr3.Add(self.cb_baud, flag=wx.LEFT, border = 10)
        self.ihboxdr3.Add(self.st_databits, flag=wx.LEFT, border=30)
        self.ihboxdr3.Add(self.cb_Databits, flag=wx.LEFT, border = 10)
        self.hboxdr3.Add(self.ihboxdr3, flag=wx.ALIGN_CENTER_VERTICAL)
        
        self.ihboxdr4 = wx.BoxSizer(wx.HORIZONTAL)
        self.st_Parity = wx.StaticText(self, -1, "Parity ", size = (60, 15))
        self.st_StopBits = wx.StaticText(self, -1, "Stop Bits")
        
        self.cb_Parity = wx.ComboBox(self,
                                     size=(65,-1),
                                     style = wx.TE_PROCESS_ENTER, choices=cb_parity)
        self.cb_StopBits = wx.ComboBox(self,
                                     size=(65,-1),
                                     style = wx.TE_PROCESS_ENTER, choices=cb_sbits)
        
        self.ihboxdr4.Add(self.st_Parity, flag=wx.LEFT, border=10)
        self.ihboxdr4.Add(self.cb_Parity, flag=wx.LEFT, border = 10)
        self.ihboxdr4.Add(self.st_StopBits, flag=wx.LEFT, border=30)
        self.ihboxdr4.Add(self.cb_StopBits, flag=wx.LEFT, border = 10)
        self.hboxdr4.Add(self.ihboxdr4, flag=wx.ALIGN_CENTER_VERTICAL)
        
        self.ihboxdrx = wx.BoxSizer(wx.HORIZONTAL)
        self.st_pechar = wx.StaticText(self, -1, "Parity Error Char.")
        self.cb_pechar = wx.ComboBox(self,
                                     size=(65,-1),
                                     style = wx.TE_PROCESS_ENTER, choices=cb_pechar)
        self.ihboxdrx.Add(self.st_pechar, flag=wx.LEFT, border=10)
        self.ihboxdrx.Add(self.cb_pechar, flag=wx.LEFT, border = 10)
        self.hboxdrx.Add(self.ihboxdrx, flag=wx.ALIGN_CENTER_VERTICAL)

        self.ihboxdr5 = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_saveser = wx.Button(self, -1, "Save", size = (65, 25))
        self.ihboxdr5.Add(self.btn_saveser, flag=wx.LEFT, border = 140)
        self.hboxdr5.Add(self.ihboxdr5, flag=wx.ALIGN_CENTER_VERTICAL )

        self.vboxSerial.AddMany([
            (self.hboxdr2, 1, wx.EXPAND | wx.ALL, 5),
            (self.hboxdr3,1,wx.EXPAND | wx.ALL, 5),
            (self.hboxdr4,1,wx.EXPAND | wx.ALL, 5),
            (self.hboxdrx,1,wx.EXPAND | wx.ALL, 5),
            (self.hboxdr5,1,wx.EXPAND | wx.ALL, 5),
        ])

        self.InitSelectionCtrl()

    def InitDataToWatch(self):
        self.hboxdr7 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_ap = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxdr8 = wx.BoxSizer(wx.HORIZONTAL)

        cb_action = ["stop sequence", "count match"]

        ca = wx.StaticBox(self, -1, "Data to Watch", size = (400, 200))
        self.vboxLog = wx.StaticBoxSizer(ca, wx.VERTICAL)

        self.ihboxdr7 = wx.BoxSizer(wx.HORIZONTAL)        
        self.tc_data = wx.TextCtrl(self, 0, "", style = wx.TE_MULTILINE,
                                     size = (300,90))        
        self.hboxdr7.Add(self.tc_data, flag=wx.LEFT | 
                        wx.ALIGN_CENTER_VERTICAL, border=10)   
        self.btn_savedtow = wx.Button(self, -1, "Save", size = (65, 25))
        self.hboxdr8.Add(self.btn_savedtow, flag=wx.LEFT | 
                        wx.ALIGN_CENTER_VERTICAL, border=120)

        self.st_action = wx.StaticText(self, -1, "Match action")
        self.cb_action = wx.ComboBox(self,
                                     size=(130,-1),
                                     style = wx.TE_PROCESS_ENTER, choices=cb_action)

        self.hbox_ap.Add(self.st_action, flag=wx.LEFT, border=10)
        self.hbox_ap.Add(self.cb_action, flag=wx.LEFT, border = 10)

        self.vboxLog.AddMany([
            (self.hboxdr7, 1, wx.EXPAND | wx.ALL),
            ((0,20), 0, wx.EXPAND),
            (self.hbox_ap, 1, wx.EXPAND | wx.ALL),
            (self.hboxdr8, 1, wx.EXPAND | wx.ALL)
        ])

        self.btn_savedtow.Bind(wx.EVT_BUTTON, self.SaveDataToWatch)

        faultList = None
        action = None
        try:
            faultList = self.dut[self.dut_key]["faultseq"]
            action = self.dut[self.dut_key]["action"]
        except:
            action = "None"

        self.cb_action.SetValue(action)

        faultstr = []
        for fault in faultList:
            faultstr.append(' "'+fault+'"')

        mystr = ','.join(map(str, faultstr))

        self.tc_data.SetValue(mystr)

    def InitSelectionCtrl(self):
        serkeys = list(self.dut_settings.keys())
        if(len(serkeys) == 0):
            self.dut_settings = self.dut[self.dut_key]["default"]["serial"]
              
        self.cb_switch.SetValue(self.dut_settings["port"])
        self.cb_baud.SetValue(self.dut_settings["baud"])
        self.cb_Parity.SetValue(self.dut_settings["parity"])
        self.cb_Databits.SetValue(str(self.dut_settings["databits"]))
        self.cb_pechar.SetValue(self.dut_settings["parerrcheck"])
        self.cb_StopBits.SetValue(str(self.dut_settings["stopbits"]))
        
        self.btn_ref.Bind(wx.EVT_BUTTON, self.RefreshConfig)
        self.btn_saveser.Bind(wx.EVT_BUTTON, self.SaveConfig)

    def SaveTypeName(self, event):
        type = "tcp"
        name = self.tc_nameSut.GetValue()
        if(self.rbtn_ser.GetValue()):
            type = "serial"

        self.dut[self.dut_key]["name"] = name
        self.dut[self.dut_key]["interface"] = type
        
        configdata.set_sut_base_data(self.dut)
        self.save_done_dialog("DUT name saved")
        
    def SaveDataToWatch(self, event):
        fadata = self.tc_data.GetValue()
        fault_list = re.findall(r'"([^"]*)"', fadata)

        action = self.cb_action.GetValue()
    
        findict = {self.dut_key : {"faultseq": fault_list, "action": action}}
        
        configdata.set_sut_watch_data(findict)
        self.top.updt_dut_config(findict)
        self.save_done_dialog("Data config saved")

    def UpdateData(self):
        
        if(self.dut_type == "serial"):
            self.rbtn_ser.SetValue(True)
            self.vboxParent.Hide(self.vboxTcp)
        else:
            self.rbtn_tcp.SetValue(True)
            self.vboxParent.Hide(self.vboxSerial)
                
    def OnSerial(self, event):
        btn = event.GetEventObject()
    
    def OnNetowrk(self, event):
        btn = event.GetEventObject()

    def Onselectcom(self, e):
        self.cb = e.GetEventObject()

    def Onselectbaud(self, e):
        self.cb = e.GetEventObject()
    
    def Onselectdatabits(self, e):
        self.cb = e.GetEventObject()
    
    def Onselectstopbits(self, e):
        self.cb = e.GetEventObject()

    def SaveConfig(self, e):
        strcom = self.cb_switch.GetValue()
        strbr = self.cb_baud.GetValue()
        strdb = self.cb_Databits.GetValue()
        strpar = self.cb_Parity.GetValue()
        strsb = self.cb_StopBits.GetValue()
        strpec = self.cb_pechar.GetValue()

        dutconfig = {"port": strcom, "baud": strbr, "databits": strdb, 
                     "parity": strpar, "stopbits": strsb, "parerrcheck": strpec}

        findict = {self.dut_key : {"serial": dutconfig}}
    
        configdata.set_sut_config_data(findict)
        self.top.updt_dut_config(findict)

        self.save_done_dialog("Serial config saved")
           
    def RefreshConfig(self, e):
        self.cb_list = self.filter_port()
        self.cb_switch.Clear()
        for cport in self.cb_list:
            self.cb_switch.Append(cport)
        self.cb_switch.SetSelection(0)

    def save_config_data(self, cdata):
        self.top.save_config_data(cdata)

    def read_config_data(self):
        return self.top.get_config_data()

    def save_done_dialog(self, msg):
        title = ("DUT Config Dialog")
        dlg = wx.MessageDialog(self, msg, title, wx.OK)
        dlg.ShowModal()