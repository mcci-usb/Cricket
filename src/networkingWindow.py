##############################################################################
# 
# Module: networkingWindow.py
#
# Description:
#     This dialog is created for network configuration.
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
#    V4.3.0 Mon Jan 22 2024 17:00:00   Seenivasan V 
#       Module created
##############################################################################

import wx
import configdata
import socket
import threading

import searchNetwork
import setNetwork
# import SetNetwork

class NetConfigDialog(wx.Dialog):
    def __init__(self, parent, myrole):
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
        self.vbnws = wx.BoxSizer(wx.VERTICAL)
                
    def InitSelectionType(self):
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
        #  Set the initial state of the radio buttons
        # self.rbtn_single.SetValue(not self.myrole["uc"])
        # self.rbtn_multi.SetValue(self.myrole["uc"])
    

    def SearchnwType(self):
        
        # self.hb_center = wx.BoxSizer(wx.VERTICAL)
        # self.hb_center.Add((0,25), 0, wx.EXPAND)
        
        self.search_nw = searchNetwork.SearchNetwork(self, self.parent)
        
        self.vboxl = wx.BoxSizer(wx.VERTICAL)
        # self.vboxl.Add((0,10), 0, wx.EXPAND)
        self.vboxl.Add((0,5), 0, 0)
        self.vboxl.Add(self.search_nw, 1, wx.EXPAND)
        self.vboxl.Add((0,5), 0, wx.EXPAND)
    
    def SetnwType(self):
        
        # self.hb_center = wx.BoxSizer(wx.VERTICAL)
        # self.hb_center.Add((0,25), 0, wx.EXPAND)
        
        self.set_nw = setNetwork.SetNetwork(self, self.parent)
        
        self.vboxl2 = wx.BoxSizer(wx.VERTICAL)
        # self.vboxl2.Add((0,10), 0, wx.EXPAND)
        self.vboxl2.Add((0,5), 0, 0)
        self.vboxl2.Add(self.set_nw, 1, wx.EXPAND)
        self.vboxl2.Add((0,5), 0, wx.EXPAND)
        
    def insertScanNw(self, ctype):
        self.search_nw = searchNetwork.SearchNetwork(self, ctype)
        self.vbnws.Add((0,5), 0, 0)
        self.vbnws.Add(self.search_nw, 1, wx.EXPAND)
        self.vbnws.Add((0,5), 0, wx.EXPAND)

    
    def insertSetNw(self, ctype):
        self.set_nw = setNetwork.SetNetwork(self, ctype)
        
        self.vbnws.Add((0,5), 0, 0)
        self.vbnws.Add(self.set_nw, 1, wx.EXPAND)
        self.vbnws.Add((0,5), 0, wx.EXPAND)

    def saveinsertion(self):
        self.btn_save = wx.Button(self, -1, "Save All")
        # self.btn_cancel = wx.Button(self, -1, "Close")
        
        self.Bind(wx.EVT_BUTTON, self.Onsave, self.btn_save)
        # self.Bind(wx.EVT_BUTTON, self.Onclose, self.btn_cancel)
 
        self.vboxsave = wx.BoxSizer(wx.HORIZONTAL)
        self.vboxsave.AddMany([
            (200, 0, 0),
            (self.btn_save, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL),
            # (10, 50, 0)
            # (self.btn_cancel, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL),
            # (10, 50, 0)
        ])
        
    
    def Onsave(self, e):
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
        bin_str = f"{int(self.thc_flg)}{int(self.scc_flg)}{int(self.uc_flg)}"
        mystat = int(bin_str, 2)
        return mystat
    
    def clearNwPanel(self):
        self.vbnws.Clear(True)
        self.Layout()
    
    def switch_nw_case(self, swopt):
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
        cstate = self.get_comp_config()
        self.clearNwPanel()
        self.switch_nw_case(cstate)
        self.Layout()
       
    def onRadioButton(self, evet):
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
        self.cb_uc.Enable(enable)
        self.cb_scc.Enable(enable)
        self.cb_thc.Enable(enable)
        
    def on_uc_checkbox(self, evt):
        self.uc_flg = self.cb_uc.GetValue()
        self.alter_panel()
            
    def on_scc_checkbox(self, evt):
        self.scc_flg = self.cb_scc.GetValue()
        self.alter_panel()
    
    def on_thc_checkbox(self, evt):
        self.thc_flg = self.cb_thc.GetValue()
        self.alter_panel()
      
    def alter_panel(self):
        self.alter_nw_panel()
        
    def update_controls(self):
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
