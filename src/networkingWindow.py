# -*- coding: utf-8 -*-
##############################################################################
#
# Module: networkingWindow.py
#
# Description:
#     Network configuration dialog for Cricket UI.
#
#     This dialog allows users to configure single or multi-computer
#     network setups including:
#         • User Computer (UC)
#         • Switch Control Computer (SCC)
#         • Test Host Computer (THC)
#
#     Provides options to scan network devices, configure IP/Port,
#     and store system network roles.
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
import threading

# Lib imports
import wx

# Own modules
import configdata
import searchNetwork
import setNetwork

class NetConfigDialog(wx.Dialog):
    """
    Network Configuration Dialog.

    Provides UI controls to configure system networking mode
    and assign roles for different computers in the Cricket setup.

    Supports:
        • Single computer configuration
        • Multi-computer (network) configuration
        • Network scanning
        • IP/Port setup

    Attributes:
        parent: Parent application window.
        myrole: Current system role configuration.
        config_data: Loaded configuration data.
        uc_flg: User computer selection flag.
        scc_flg: Switch Control Computer selection flag.
        thc_flg: Test Host Computer selection flag.
    """
    def __init__(self, parent, myrole):
        """
        Initialize Network Configuration dialog.

        Args:
            parent: Parent window reference.
            myrole: Dictionary containing current role settings.

        Returns:
            None
        """
        wx.Dialog.__init__(self, parent, title="Network Configuration", size=(640, 680),
                           style=wx.DEFAULT_DIALOG_STYLE)
        
        self.parent = parent
        self.myrole = myrole
        self.nw_wins = []
        
        self.uc_flg = False
        self.scc_flg = False
        self.thc_flg = False
        
        self.SetBackgroundColour("White")
        # self.myrole = myrole
        self.scan_sc_flg = False
        self.scan_th_flg = False
        self.vboxParent = wx.BoxSizer(wx.VERTICAL)
        
        self.config_data = configdata.read_all_config()
        
        self.InitSelectionType()
        self.Selection_computer()
        
        self.saveinsertion()
        
        self.Initnwconfig()
        
        self.vboxParent.AddMany([
            (self.hbsmc, 0, wx.EXPAND | wx.ALL, 10),
            (self.vbcsel, 0, wx.EXPAND | wx.ALL, 10),
            (self.vbnws,1, wx.EXPAND | wx.ALL, 10),
            # (self.vboxl2,1, wx.EXPAND | wx.ALL, 10),
            (self.vboxsave,1, wx.EXPAND | wx.ALL, 10),
            
        ])
        
        self.SetSizer(self.vboxParent)
        self.Show()
        self.Layout()
        self.update_controls()
        self.alter_nw_panel()
   
    def Initnwconfig(self):
        """
        Initialize network configuration container sizer.

        Args:
            self: Instance reference.

        Returns:
            None
        """
        self.vbnws = wx.BoxSizer(wx.VERTICAL)
                
    def InitSelectionType(self):
        """
        Create selection controls for system configuration type.

        Provides radio buttons for:
            • Single Computer
            • Network Computer

        Args:
            self: Instance reference.

        Returns:
            None
        """
        self.hbsmc = wx.BoxSizer(wx.HORIZONTAL)
        
        bc = wx.StaticBox(self, -1, "Settings", size = (400, 200))
        self.hbsmc = wx.StaticBoxSizer(bc, wx.HORIZONTAL)
        self.rbtn_single = wx.RadioButton(self, -1, label='Single Computer')
        self.rbtn_multi = wx.RadioButton(self, -1, label='Network Computer')
        
        self.Bind(wx.EVT_RADIOBUTTON, self.onRadioButton)
    
        self.hbsmc.AddMany([            
            (self.rbtn_single, 1, wx.EXPAND | wx.ALL, 5),
            (self.rbtn_multi, 1, wx.EXPAND | wx.ALL, 5)
        ])
    
    def Selection_computer(self):
        """
        Create computer role selection controls.

        Allows enabling/disabling:
            • User Computer
            • Switch Control Computer
            • Test Host Computer

        Args:
            self: Instance reference.

        Returns:
            None
        """
        ab = wx.StaticBox(self, -1, "Computer Settings", size = (400, 200))
        self.vbcsel = wx.StaticBoxSizer(ab, wx.VERTICAL)
        
        self.cb_uc= wx.CheckBox(self, -1, "User Computer")
        self.cb_scc = wx.CheckBox(self, -1, "Switch Control Computer (SCC)")
        self.cb_thc = wx.CheckBox(self, -1, "Test Host Computer (THC)")
        
        self.cb_uc.Bind(wx.EVT_CHECKBOX, self.on_uc_checkbox)
        self.cb_scc.Bind(wx.EVT_CHECKBOX, self.on_scc_checkbox)
        self.cb_thc.Bind(wx.EVT_CHECKBOX, self.on_thc_checkbox)
        self.vbcsel.AddMany([
            (self.cb_uc, 1, wx.EXPAND | wx.ALL, 5),
            (self.cb_scc, 1, wx.EXPAND | wx.ALL, 5),
            (self.cb_thc, 1, wx.EXPAND | wx.ALL, 5)
        ])
        
    def SearchnwType(self):
        """
        Insert network search panel.

        Loads SearchNetwork UI for scanning
        available network systems.

        Args:
            self: Instance reference.

        Returns:
            None
        """       
        self.search_nw = searchNetwork.SearchNetwork(self, self.parent)
        self.vboxl = wx.BoxSizer(wx.VERTICAL)
        # self.vboxl.Add((0,10), 0, wx.EXPAND)
        self.vboxl.Add((0,5), 0, 0)
        self.vboxl.Add(self.search_nw, 1, wx.EXPAND)
        self.vboxl.Add((0,5), 0, wx.EXPAND)
    
    def SetnwType(self):
        """
        Insert network configuration panel.

        Loads SetNetwork UI for manual
        IP and port configuration.

        Args:
            self: Instance reference.

        Returns:
            None
        """
        
        self.set_nw = setNetwork.SetNetwork(self, self.parent)
        self.vboxl2 = wx.BoxSizer(wx.VERTICAL)
        # self.vboxl2.Add((0,10), 0, wx.EXPAND)
        self.vboxl2.Add((0,5), 0, 0)
        self.vboxl2.Add(self.set_nw, 1, wx.EXPAND)
        self.vboxl2.Add((0,5), 0, wx.EXPAND)
        
    def insertScanNw(self, ctype):
        """
        Insert scan network panel dynamically.

        Args:
            ctype: Computer type (SCC / THC).

        Returns:
            None
        """
        self.search_nw = searchNetwork.SearchNetwork(self, ctype)
        self.vbnws.Add((0,5), 0, 0)
        self.vbnws.Add(self.search_nw, 1, wx.EXPAND)
        self.vbnws.Add((0,5), 0, wx.EXPAND)

    def insertSetNw(self, ctype):
        """
        Insert manual network setup panel.

        Args:
            ctype: Computer type (SCC / THC).

        Returns:
            None
        """
        self.set_nw = setNetwork.SetNetwork(self, ctype)
        self.vbnws.Add((0,5), 0, 0)
        self.vbnws.Add(self.set_nw, 1, wx.EXPAND)
        self.vbnws.Add((0,5), 0, wx.EXPAND)

    def saveinsertion(self):
        """
        Create Save button section.

        Adds control to store all
        configured network settings.

        Args:
            self: Instance reference.

        Returns:
            None
        """
        self.btn_save = wx.Button(self, -1, "Save All")
        # self.btn_cancel = wx.Button(self, -1, "Close")
        
        self.Bind(wx.EVT_BUTTON, self.Onsave, self.btn_save)
        # self.Bind(wx.EVT_BUTTON, self.Onclose, self.btn_cancel)
 
        self.vboxsave = wx.BoxSizer(wx.HORIZONTAL)
        self.vboxsave.AddMany([
            (200, 0, 0),
            (self.btn_save, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL),
            
        ])
        
    def Onsave(self, e):
        """
        Save network configuration settings.

        Stores selected mode and computer roles
        into configuration database.

        Args:
            e: Button click event.

        Returns:
            dict: Saved configuration data.
        """
        self.config = {"mode": 'single', "uc": True, "scc": True, "thc": True}
        single_flg = False

        # single_flg = self.rbtn_ser.GetValue()
        if single_flg == False:
            self.config["mode"] = 'multi'
            self.mc = self.cb_uc.GetValue()
            self.scc = self.cb_scc.GetValue()
            self.thc = self.cb_thc.GetValue()
            self.config["uc"] = self.mc
            self.config["scc"] = self.scc
            self.config["thc"] = self.thc
            
        configdata.set_network_config(self.config)
        # configdata.set_net_base_data(self.dut)
        
        self.EndModal(wx.ID_OK)
        
        return self.config
    
    def get_comp_config(self):
        """
        Compute binary state of computer selections.

        Returns:
            int: Encoded selection state value.
        """
        bin_str = f"{int(self.thc_flg)}{int(self.scc_flg)}{int(self.uc_flg)}"
        mystat = int(bin_str, 2)
        return mystat
    
    def clearNwPanel(self):
        """
        Clear all network panels.

        Args:
            self: Instance reference.

        Returns:
            None
        """
        self.vbnws.Clear(True)
        self.Layout()
    
    def switch_nw_case(self, swopt):
        """
        Load network panels based on selection state.

        Args:
            swopt: Encoded selection state.

        Returns:
            None
        """
        # self.onRadioButton()
        if swopt == 0x00 or swopt == 0x07:
            pass
        elif swopt == 0x01:
            self.insertScanNw("SCC")
            self.insertScanNw("THC")
        elif swopt == 0x02:
            self.insertSetNw("SCC")
        elif swopt == 0x03:
            self.insertScanNw("THC")
        elif swopt == 0x04:
            self.insertSetNw("THC")
        elif swopt == 0x05:
            self.insertScanNw("SCC")
        elif swopt == 0x06:
            self.insertSetNw("SCC")
            self.insertSetNw("THC")
        
    def alter_nw_panel(self):
        """
        Update network panel layout dynamically.

        Args:
            self: Instance reference.

        Returns:
            None
        """
        cstate = self.get_comp_config()
        self.clearNwPanel()
        self.switch_nw_case(cstate)
        self.Layout()
       
    def onRadioButton(self, evet):
        """
        Handle configuration mode radio selection.

        Args:
            evet: Radio button event.

        Returns:
            None
        """
        self.clearNwPanel() 
        if self.rbtn_single.GetValue():
            self.cb_uc.SetValue(True)
            self.cb_scc.SetValue(True)
            self.cb_thc.SetValue(True)
            self.enableCheckboxes(False)
              
        elif self.rbtn_multi.GetValue():
            self.cb_uc.SetValue(False)
            self.cb_scc.SetValue(False)
            self.cb_thc.SetValue(False)
            self.enableCheckboxes(True)
        
        # Trigger checkbox events manually
        self.on_uc_checkbox(wx.CommandEvent())
        self.on_scc_checkbox(wx.CommandEvent())
        self.on_thc_checkbox(wx.CommandEvent())

        self.alter_nw_panel()
        
    def enableCheckboxes(self, enable):
        """
        Enable or disable computer selection checkboxes.

        Args:
            enable: Boolean flag.

        Returns:
            None
        """
        self.cb_uc.Enable(enable)
        self.cb_scc.Enable(enable)
        self.cb_thc.Enable(enable)
        
    def on_uc_checkbox(self, evt):
        """
        Handle User Computer checkbox event.

        Args:
            evt: Checkbox event.

        Returns:
            None
        """
        self.uc_flg = self.cb_uc.GetValue()
        self.alter_panel()
            
    def on_scc_checkbox(self, evt):
        """
        Handle SCC checkbox event.

        Args:
            evt: Checkbox event.

        Returns:
            None
        """
        self.scc_flg = self.cb_scc.GetValue()
        self.alter_panel()
    
    def on_thc_checkbox(self, evt):
        """
        Handle THC checkbox event.

        Args:
            evt: Checkbox event.

        Returns:
            None
        """
        self.thc_flg = self.cb_thc.GetValue()
        self.alter_panel()
      
    def alter_panel(self):
        """
        Refresh panel layout based on role selection.

        Args:
            self: Instance reference.

        Returns:
            None
        """
        self.alter_nw_panel()
        
    def update_controls(self):
        """
        Initialize UI controls using existing role configuration.

        Args:
            self: Instance reference.

        Returns:
            None
        """
        self.rbtn_single.SetValue(self.myrole["uc"])
        self.rbtn_multi.SetValue(not self.myrole["uc"])

        self.cb_uc.SetValue(self.myrole["uc"])
        self.cb_scc.SetValue(self.myrole["cc"])
        self.cb_thc.SetValue(self.myrole["thc"])
        # Trigger corresponding checkbox events
        
        self.on_uc_checkbox(wx.CommandEvent())
        self.on_scc_checkbox(wx.CommandEvent())
        self.on_thc_checkbox(wx.CommandEvent())
        # self.alter_panel()

        if self.myrole["uc"] and self.myrole["cc"] and self.myrole["thc"]:
            self.rbtn_single.SetValue(True)
        
        elif self.myrole["uc"]:
            self.rbtn_multi.SetValue(True)
            self.alter_nw_panel()
        
        elif not self.myrole["uc"]:
            self.rbtn_multi.SetValue(True)
            self.cb_uc.Enable(True)
            self.cb_scc.Enable(True)
            self.cb_thc.Enable(True)
            
            self.uc_flg = self.cb_uc.GetValue()
            self.scc_flg = self.cb_scc.GetValue()
            self.thc_flg = self.cb_thc.GetValue()
            
        elif self.myrole["uc"] and self.myrole["cc"]:
            self.rbtn_multi.SetValue(True)
            self.cb_uc.Enable(True)
            self.cb_scc.Enable(True)
            self.cb_thc.Enable(True)
            
            self.uc_flg = self.cb_uc.GetValue()
            self.scc_flg = self.cb_scc.GetValue()
            self.thc_flg = self.cb_thc.GetValue()
            
        elif self.myrole["uc"] and self.myrole["thc"]:
            self.rbtn_multi.SetValue(True)
            self.cb_uc.Enable(True)
            self.cb_scc.Enable(True)
            self.cb_thc.Enable(True)
            
            self.uc_flg = self.cb_uc.GetValue()
            self.scc_flg = self.cb_scc.GetValue()
            self.thc_flg = self.cb_thc.GetValue()
    
        else:
            self.rbtn_single.SetValue(True)
