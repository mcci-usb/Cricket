# -*- coding: utf-8 -*-
##############################################################################
#
# Module: dutConfigDialog.py
#
# Description:
#     DUT Configuration Dialog module.
#
#     Provides UI interface to configure DUT communication settings,
#     including:
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
# Revision history:
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
#
##############################################################################

# Built-in imports
import os
import re
from sys import platform
from random import choice, choices

# Lib imports
import wx
import serial.tools.list_ports

# Own modules
import configdata
from uiGlobals import IMG_ICON

class DutConfigDialog(wx.Frame):
    """
    DUT Configuration Dialog Window.

    Description:
        Provides a graphical configuration interface for DUT devices.

    Features:

        • Select DUT interface type (Serial / TCP)
        • Configure serial communication parameters
        • Monitor fault sequences
        • Define data-watch triggers
        • Update DUT display name
        • Save configuration to global config storage

    Parameters:
        top : Parent controller / main UI reference
        dut : DUT configuration dictionary
    """
    def __init__(self, top, dut):
        """
        Initialize DUT configuration dialog.

        Args:
            top : Main UI controller reference
            dut : DUT configuration dictionary
        """
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
        print(self.cb_list)

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


        #--------------------- ---EVENT BIND--- #---------------------
    def filter_port(self):
        """
        Filter available COM ports.

        Description:
            Filters COM ports excluding specific VID/PID devices
            (example: supported USB switches).

        Returns:
            list:
                Available COM port names.
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
        Initialize DUT interface selection controls.

        Detailed Description:
            This function creates the UI section that allows the user
            to configure the DUT interface type and display name.

            UI Components created:

                • Serial interface radio button
                • TCP interface radio button
                • DUT name text field
                • Save button for interface selection

            It also binds UI events for saving configuration
            and switching interface modes.

        Args:
            self: Reference to the current DutConfigDialog instance.

        Returns:
            None
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
        Initialize TCP configuration section.

        Detailed Description:
            This function builds the TCP configuration UI container.

            Currently, TCP configuration is a placeholder feature
            and will be implemented in future releases.

            The section displays an informational message to users.

        Args:
            self: Reference to the current DutConfigDialog instance.

        Returns:
            None
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
        Initialize Serial communication configuration controls.

        Detailed Description:
            This function builds the Serial configuration UI section
            used to configure DUT serial communication parameters.

            Parameters supported:

                • COM Port selection
                • Baud Rate
                • Data Bits
                • Parity
                • Stop Bits
                • Parity Error Character handling

            It also initializes control defaults and binds
            save/refresh event handlers.

        Args:
            self: Reference to the current DutConfigDialog instance.

        Returns:
            None
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
        Initialize Data-to-Watch monitoring configuration UI.

        Detailed Description:
            This function creates the monitoring configuration
            section used to track DUT fault sequences.

            Features provided:

                • Fault sequence input text area
                • Match action selection dropdown
                • Save monitoring configuration button

            It also loads existing monitoring configuration
            values from DUT settings if available.

        Args:
            self: Reference to the current DutConfigDialog instance.

        Returns:
            None
        """
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
        """
        Load stored serial configuration into UI controls.

        Detailed Description:
            This function populates the Serial configuration UI
            controls using stored DUT configuration values.

            If no custom configuration exists, default serial
            settings are loaded.

            It also binds:

                • Refresh button event
                • Save configuration event

        Args:
            self: Reference to the current DutConfigDialog instance.

        Returns:
            None
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
        Save DUT interface type and display name.

        Detailed Description:
            This function saves the DUT name and selected
            communication interface type (Serial / TCP).

            After saving:

                • Configuration is updated in global storage
                • Confirmation dialog is displayed

        Args:
            self: Reference to the current DutConfigDialog instance.
            event: wxPython button click event object.

        Returns:
            None
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
        Save DUT fault sequence monitoring configuration.

        Detailed Description:
            This function captures the fault sequence data entered
            in the Data-to-Watch text control and stores it into
            the global DUT configuration.

        Args:
            self: Reference to the current DutConfigDialog instance.
            event: wxPython button click event object.

        Returns:
            None

        Raises:
            None
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
        Update UI visibility based on DUT interface type.

        Detailed Description:
            This function toggles visibility of Serial and TCP
            configuration sections depending on the currently
            selected DUT interface type.

                • Shows Serial settings if interface = Serial
                • Shows TCP settings if interface = TCP

        Args:
            self: Reference to the current DutConfigDialog instance.

        Returns:
            None

        Raises:
            None
        """
        
        if(self.dut_type == "serial"):
            self.rbtn_ser.SetValue(True)
            self.vboxParent.Hide(self.vboxTcp)
        else:
            self.rbtn_tcp.SetValue(True)
            self.vboxParent.Hide(self.vboxSerial)
                
    def OnSerial(self, event):
        """
        Handle Serial interface selection event.

        Detailed Description:
            Triggered when the user selects the Serial
            radio button. Currently reserved for future
            UI behavior handling.

        Args:
            self: Reference to the current DutConfigDialog instance.
            event: wxPython radio button event object.

        Returns:
            None

        Raises:
            None
        """
        btn = event.GetEventObject()
    
    def OnNetowrk(self, event):
        """
        Handle TCP network interface selection event.

        Detailed Description:
            Triggered when the user selects the TCP
            interface radio button. Currently reserved
            for future UI behavior handling.

        Args:
            self: Reference to the current DutConfigDialog instance.
            event: wxPython radio button event object.

        Returns:
            None

        Raises:
            None
        """
        btn = event.GetEventObject()

    def Onselectcom(self, e):
        """
        Handle COM port selection event.

        Detailed Description:
            Captures the selected COM port object from
            the combo box control for further processing.

        Args:
            self: Reference to the current DutConfigDialog instance.
            e: wxPython combo box event object.

        Returns:
            None

        Raises:
            None
        """
        self.cb = e.GetEventObject()

    def Onselectbaud(self, e):
        """
        Handle Baud Rate selection event.

        Detailed Description:
            This function is triggered when the user selects
            a Baud Rate value from the dropdown control.

            It captures the selected ComboBox object and
            stores the reference for further configuration
            processing if required.

        Args:
            self: Reference to the current DutConfigDialog instance.
            e: wxPython ComboBox selection event object.

        Returns:
            None

        Raises:
            None
        """
        self.cb = e.GetEventObject()
    
    def Onselectdatabits(self, e):
        """
        Handle Data Bits selection event.

        Detailed Description:
            This function is invoked when the user selects
            the Data Bits value from the dropdown list.

            It retrieves the selected ComboBox widget
            object and stores it for later configuration
            usage or validation handling.

        Args:
            self: Reference to the current DutConfigDialog instance.
            e: wxPython ComboBox selection event object.

        Returns:
            None

        Raises:
            None
        """
        self.cb = e.GetEventObject()
    
    def Onselectstopbits(self, e):
        """
        Handle Stop Bits selection event.

        Detailed Description:
            This function executes when the user selects
            the Stop Bits configuration value from the UI.

            It captures the selected ComboBox control
            object reference for further processing
            within the serial configuration workflow.

        Args:
            self: Reference to the current DutConfigDialog instance.
            e: wxPython ComboBox selection event object.

        Returns:
            None

        Raises:
            None
        """
        self.cb = e.GetEventObject()

    def SaveConfig(self, e):
        """
        Save DUT serial communication configuration.

        Detailed Description:
            This function reads serial communication
            parameters configured in the UI and saves
            them into DUT configuration storage.

            Parameters saved include:

                • COM Port
                • Baud Rate
                • Data Bits
                • Parity
                • Stop Bits
                • Parity Error Character

            After saving:

                • Configuration is updated globally
                • Parent controller is notified
                • Confirmation dialog is displayed

        Args:
            self: Reference to the current DutConfigDialog instance.
            e: wxPython button click event object.

        Returns:
            None

        Raises:
            None
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
        Refresh available COM port list.

        Detailed Description:
            This function rescans system serial ports
            and updates the COM port dropdown list.

            Used when new DUT devices are connected.

        Args:
            self: Reference to the current DutConfigDialog instance.
            e: wxPython button click event object.

        Returns:
            None

        Raises:
            None
        """
        self.cb_list = self.filter_port()
        # print("combo_box:", self.cb_list)
        # self.cb_switch.Clear()
        for cport in self.cb_list:
            self.cb_switch.Append(cport)
        self.cb_switch.SetSelection(0)

    def save_config_data(self, cdata):
        """
        Forward configuration data to parent controller.

        Detailed Description:
            Acts as a wrapper to pass configuration
            updates to the main application controller.

        Args:
            self: Reference to the current DutConfigDialog instance.
            cdata: Configuration dictionary.

        Returns:
            None

        Raises:
            None
        """
        self.top.save_config_data(cdata)

    def read_config_data(self):
        """
        Retrieve configuration data from parent controller.

        Detailed Description:
            Requests the latest configuration data
            stored in the main application controller.

        Args:
            self: Reference to the current DutConfigDialog instance.

        Returns:
            dict:
                Current configuration data.

        Raises:
            None
        """
        return self.top.get_config_data()

    def save_done_dialog(self, msg):
        """
        Display configuration save confirmation dialog.

        Detailed Description:
            This function displays a modal message dialog
            indicating successful configuration save
            operation.

        Args:
            self: Reference to the current DutConfigDialog instance.
            msg: Confirmation message string.

        Returns:
            None

        Raises:
            None
        """
        title = ("DUT Config Dialog")
        dlg = wx.MessageDialog(self, msg, title, wx.OK)
        dlg.ShowModal()