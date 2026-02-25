# -*- coding: utf-8 -*-
##############################################################################
#
# Module: dutConfigDialog.py
#
# Description:
#     Firmware Update Utility for Supported MCCI Switch Models.
#
# Detailed Description:
#     This module provides functionality to perform firmware updates
#     on supported switch devices through bootloader mode using
#     serial communication.
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
#
##############################################################################
import wx

import serial.tools.list_ports
import os
from sys import platform
import re

import configdata

from uiGlobals import IMG_ICON

class DutConfigDialog(wx.Frame):
    """
    DUT Configuration Dialog Window.

    This class implements a GUI dialog used to configure communication
    and monitoring settings for a Device Under Test (DUT).

    Features:
        • Interface selection (Serial / TCP)
        • Serial port configuration
        • TCP placeholder configuration
        • DUT naming
        • Fault sequence monitoring setup
        • Match action configuration

    The dialog reads existing DUT configuration data, allows the user
    to modify settings, and saves updates through the configdata module.

    Inherits:
        wx.Frame : Base window class from wxPython.

    Args:
        top (wx.Window):
            Reference to the parent/top window.

        dut (dict):
            DUT configuration dictionary containing interface,
            serial settings, and monitoring configuration.
    """
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
        iconpath = os.path.abspath(os.path.join(base, os.pardir, os.pardir))
        icon_file_path = os.path.join(iconpath+"/icons/"+ IMG_ICON)

        # Create a wx.Icon object with the specified icon file path
        icon = wx.Icon(icon_file_path)

        # Set the icon for the wx.Frame (assuming 'self' is an instance of wx.Frame)
        self.SetIcon(icon)
        
        self.UpdateData()

        self.Show()
        self.Layout()
        self.CenterOnParent(wx.BOTH)

    def filter_port(self):
        """
        Filter Available COM Ports.

        Scans all detected serial COM ports and filters out ports that match
        specific USB VID/PID combinations associated with unsupported devices.

        This ensures that only valid ports for supported switch hardware
        are displayed in the UI.

        Returns:
            list[str]:
                List of available COM port names that are allowed for selection.
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
        """
        Initialize Interface Selection Controls.

        Creates UI components for selecting the DUT communication interface
        type (Serial or TCP) and configuring the DUT name.

        UI Elements:
            • Serial / TCP radio buttons
            • DUT name text field
            • Save button for base settings

        Binds:
            • SaveTypeName()
            • OnSerial()
            • OnNetowrk()
        """
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
        """
        Initialize TCP Configuration Section.

        Creates placeholder UI components for TCP network configuration.

        Note:
            TCP communication support is planned for future implementation.
            Current UI only displays an informational message.
        """
        ab = wx.StaticBox(self, -1, "TCP Settings", size = (400, 200))
        self.vboxTcp = wx.StaticBoxSizer(ab, wx.VERTICAL)
        self.st_tcp = wx.StaticText(self, -1, "Will be implemented in future", size = (180, 15))

        self.hboxtcp = wx.BoxSizer(wx.HORIZONTAL)

        self.hboxtcp.Add(self.st_tcp, flag=wx.LEFT, border=10)

        self.vboxTcp.AddMany([
            (self.hboxtcp, 1, wx.EXPAND | wx.ALL, 5),
        ])

    def InitSerialConfig(self):
        """
        Initialize Serial Configuration Section.

        Builds UI controls required for configuring serial communication
        parameters for the DUT.

        Configuration Options:
            • COM Port selection
            • Baud rate
            • Data bits
            • Parity
            • Stop bits
            • Parity error character

        Also initializes control values from existing DUT settings.
        """
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
        """
        Initialize “Data to Watch” Configuration Section.

        Provides UI controls to configure fault sequence monitoring.

        Features:
            • Multi-line text input for fault patterns
            • Match action selection
            • Save configuration option

        Loads existing fault sequence and action settings from DUT config.
        """
        self.hboxdr7 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_ap = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxdr8 = wx.BoxSizer(wx.HORIZONTAL)

        cb_action = ["Stop sequence", "Count match"]

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

        self.st_action = wx.StaticText(self, -1, "Match Action")
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
        """
        Load Serial Settings into UI Controls.

        Populates serial configuration UI fields using stored DUT settings.

        If no settings exist, default serial configuration values are loaded.

        Also binds:
            • RefreshConfig()
            • SaveConfig()
        """
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
        """
        Save DUT Name and Interface Type.

        Stores the selected communication interface (Serial/TCP)
        and DUT display name into configuration storage.

        Updates:
            • configdata base DUT settings

        Args:
            event (wx.Event):
                Button click event.
        """
        type = "tcp"
        name = self.tc_nameSut.GetValue()
        if(self.rbtn_ser.GetValue()):
            type = "serial"

        self.dut[self.dut_key]["name"] = name
        self.dut[self.dut_key]["interface"] = type
        
        configdata.set_sut_base_data(self.dut)
        self.save_done_dialog("DUT name saved")
        
    def SaveDataToWatch(self, event):
        """
        Save Fault Sequence Monitoring Configuration.

        Extracts fault patterns from the text field and stores them
        along with the selected match action.

        Updates:
            • configdata watch configuration
            • Parent UI DUT configuration

        Args:
            event (wx.Event):
                Button click event.
        """
        fadata = self.tc_data.GetValue()
        fault_list = re.findall(r'"([^"]*)"', fadata)

        action = self.cb_action.GetValue()
    
        findict = {self.dut_key : {"faultseq": fault_list, "action": action}}
        
        configdata.set_sut_watch_data(findict)
        self.top.updt_dut_config(findict)
        self.save_done_dialog("Data config saved")

    def UpdateData(self):
        """
        Update UI Based on Interface Type.

        Shows or hides Serial/TCP configuration sections depending
        on the currently selected DUT interface.
        """
        if(self.dut_type == "serial"):
            self.rbtn_ser.SetValue(True)
            self.vboxParent.Hide(self.vboxTcp)
        else:
            self.rbtn_tcp.SetValue(True)
            self.vboxParent.Hide(self.vboxSerial)
                
    def OnSerial(self, event):
        """
        Handle Serial Interface Selection Event.

        Triggered when the Serial radio button is selected.

        Args:
            event (wx.Event):
                Radio button selection event.
        """
        btn = event.GetEventObject()
    
    def OnNetowrk(self, event):
        """
        Handle TCP Interface Selection Event.

        Triggered when the Network (TCP) radio button is selected.

        Args:
            event (wx.Event):
                Radio button selection event.
        """
        btn = event.GetEventObject()

    def Onselectcom(self, e):
        """
        Handle COM Port Selection Event.

        Captures the selected COM port from the dropdown.

        Args:
            e (wx.Event):
                ComboBox selection event.
        """
        self.cb = e.GetEventObject()

    def Onselectbaud(self, e):
        """
        Handle Baud Rate Selection Event.

        Captures the selected baud rate value.

        Args:
            e (wx.Event):
                ComboBox selection event.
        """
        self.cb = e.GetEventObject()
    
    def Onselectdatabits(self, e):
        """
        Handle Data Bits Selection Event.

        Captures the selected data bits configuration.

        Args:
            e (wx.Event):
                ComboBox selection event.
        """
        self.cb = e.GetEventObject()
    
    def Onselectstopbits(self, e):
        """
        Handle Stop Bits Selection Event.

        Captures the selected stop bits configuration.

        Args:
            e (wx.Event):
                ComboBox selection event.
        """
        self.cb = e.GetEventObject()

    def SaveConfig(self, e):
        """
        Save Serial Communication Configuration.

        Collects all selected serial parameters and stores them
        in DUT configuration.

        Updates:
            • configdata serial settings
            • Parent UI DUT configuration

        Args:
            e (wx.Event):
                Button click event.
        """
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
        """
        Refresh Available COM Ports List.

        Re-scans the system for available serial ports and updates
        the COM port dropdown list.

        Args:
            e (wx.Event):
                Button click event.
        """
        self.cb_list = self.filter_port()
        self.cb_switch.Clear()
        for cport in self.cb_list:
            self.cb_switch.Append(cport)
        self.cb_switch.SetSelection(0)

    def save_config_data(self, cdata):
        """
        Proxy Method to Save Configuration Data.

        Passes configuration data to the parent window for storage.

        Args:
            cdata (dict):
                Configuration data dictionary.
        """
        self.top.save_config_data(cdata)

    def read_config_data(self):
        """
        Read Configuration Data from Parent.

        Retrieves stored DUT configuration data.

        Returns:
            dict:
                DUT configuration dictionary.
        """
        return self.top.get_config_data()

    def save_done_dialog(self, msg):
        """
        Display Configuration Saved Dialog.

        Shows a confirmation message dialog after successful save.

        Args:
            msg (str):
                Message to display in the dialog.
        """
        title = ("DUT Config Dialog")
        dlg = wx.MessageDialog(self, msg, title, wx.OK)
        dlg.ShowModal()