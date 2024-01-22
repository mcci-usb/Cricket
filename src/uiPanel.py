##############################################################################
# 
# Module: uiPanel.py
#
# Description:
#     Scan the USB bus and get the list of devices attached
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
#     Seenivasan V, MCCI Corporation Mar 2020
#
# Revision history:
#    V4.3.0 Mon Jan 22 2024 17:00:00   Seenivasan V
#       Module created
##############################################################################

import wx

import sys
from sys import platform

# Own modules
from uiGlobals import *

# import panels
from panels import leftPanel
from panels import rightPanel
from panels import midPanel

import configdata

# import logWindow

class UiPanel(wx.Panel):
    
    def __init__(self, parent):
       
        super(UiPanel, self).__init__(parent)

        # wx.GetApp().SetAppName("Cricket")

        self.parent = parent
        # set back ground colour White
        self.SetBackgroundColour('White')

        self.font_size = DEFAULT_FONT_SIZE

        # MAC OS X
        if platform == "darwin":
            self.font_size = MAC_FONT_SIZE
        # Sets the font for this window
        self.SetFont(wx.Font(self.font_size, wx.SWISS, wx.NORMAL, wx.NORMAL,
                             False,'MS Shell Dlg 2'))

        self.hb_outer = wx.BoxSizer(wx.HORIZONTAL)

        self.vb_center = wx.BoxSizer(wx.VERTICAL) # for general widgets
        self.vb_left = wx.BoxSizer(wx.VERTICAL)  # for multiple switches
        self.vb_right = wx.BoxSizer(wx.VERTICAL)  # for serial logs

        self.lpanel = leftPanel.LeftPanel(self, self.parent)
        self.vb_left.Add((0,25), 0, wx.EXPAND)
        self.vb_left.Add(self.lpanel, 1, wx.ALIGN_LEFT | wx.EXPAND)
        self.vb_left.Add((0,10), 0, wx.EXPAND)

        self.cpanel = midPanel.MidPanel(self, self.parent, "")
        self.vb_center.Add(self.cpanel, 0, wx.ALIGN_LEFT | wx.EXPAND)

        self.rpanel = rightPanel.RightPanel(self)
        self.vb_right.Add(self.rpanel, 1, wx.ALIGN_LEFT | wx.EXPAND)

        self.hb_outer.Add((10,0), 0, wx.EXPAND)
        self.hb_outer.Add(self.vb_left, 0, wx.ALIGN_LEFT | wx.EXPAND)
        self.hb_outer.Add((10,0), 0, wx.EXPAND)
        self.hb_outer.Add(self.vb_center, 0, wx.ALIGN_LEFT | wx.EXPAND)
        self.hb_outer.Add((10,0), 0, wx.EXPAND)
        self.hb_outer.Add(self.vb_right, 0, wx.ALIGN_LEFT | wx.EXPAND)
        self.hb_outer.Add((10,0), 0, wx.EXPAND)

        self.con_flg = None

        self.SetSizer(self.hb_outer)
        self.SetAutoLayout(True)
        self.hb_outer.Fit(self)

        self.add_switches([])

        EVT_RESULT(self, self.StopSequence)
        self.config_data = configdata.read_all_config()

        self.Layout()

        # self.Bind(wx.EVT_MOVE, self.OnMove)

        # self.logPan = logWindow.LogWindow(self, parent)
        # self.vboxl = wx.BoxSizer(wx.VERTICAL)
        # self.vboxl.Add((0,20), 0, wx.EXPAND)
        # # self.vboxl.Add(self.hboxdl, 0 ,wx.ALIGN_LEFT | wx.EXPAND)
        # self.vboxl.Add((0,10), 0, 0)
        # self.vboxl.Add(self.logPan, 1, wx.EXPAND)
        # self.vboxl.Add((0,20), 0, wx.EXPAND)


       # BoxSizer fixed with Horizontal
        # self.hboxm = wx.BoxSizer(wx.HORIZONTAL)
        # self.hboxm.Add((20,0), 1, wx.EXPAND)
        # self.hboxm.Add(self.vboxl, 1, wx.EXPAND)
        # self.hboxm.Add((20,0), 1, wx.EXPAND)

    def StopSequence(self, event):
       
        if(event.data != None):
            
            if event.data["action"] == "stop sequence":
                self.cpanel.PrintLog("Match found - "+event.data["match"]+"\n")
                self.parent.fault_flg = True
                self.parent.con_flg = False
            else:
                action = self.parent.action_count()
                self.cpanel.PrintLog("Match found : "+str(action)+", "+event.data["match"]+"\n")

    def update_slog_panel(self, duts):
      
        self.rpanel.update_slog_panel(duts)
        
        self.Layout()

    def init_right_panel(self, pdict):
        
        self.rpanel.init_my_panel(pdict)

    def update_right_panel(self, pdict):
       
        self.rpanel.update_my_panel(pdict)

    def update_usb4_tree(self, msusb4):
       
        self.rpanel.update_usb4_tree(msusb4)


    def show_selected(self, swstr):
       
        self.cpanel.show_selected(swstr)

    def add_switches(self, swlist):
        
        self.lpanel.add_switches(swlist)
        self.lpanel.Show()
        
    def update_uc_panels(self, sutmenu):
       
        self.cpanel.update_uc_panels()
        self.update_slog_panel(sutmenu)
        self.Layout()


    def update_panels(self, myrole):
        if myrole["uc"] == True:
            # SHOW all the three panels
            self.lpanel.Show()
            self.rpanel.Show()
            self.cpanel.show_mode_panels()
            # self.reSizeScreen()
            self.Layout()
        else:
            #show only the log panels
            self.lpanel.Hide()
            self.rpanel.Hide()
            self.cpanel.remove_mode_panels()
            # self.reSizeScreen()
            self.Layout()

    def PrintLog(self, strin):
      
        self.cpanel.logPan.print_on_log(strin)
        self.rpanel.print_on_log(strin)
    
    def get_enum_delay(self):
      
        return self.cpanel.logPan.get_enum_delay()
      
    def get_delay_status(self):
        
        return self.cpanel.get_delay_status()
    
    def get_interval(self):
       
        return self.autoPan.get_interval()
    
    def set_interval(self, strval):
      
        self.cpanel.set_interval(strval)
    
    def disable_usb_scan(self):
        
        self.cpanel.logPan.disable_usb_scan()
    
    def get_loop_param(self):
       
        return self.cpanel.get_loop_param()
    
    def get_auto_param(self):
      
        return self.cpanel.get_auto_param()
    
    def set_loop_param(self, onTime, offTime):
      
        self.cpanel.set_loop_param(onTime, offTime)

    def set_port_list(self, ports):
       
        self.loopPan.set_port_list(ports)
        self.autoPan.set_port_count(ports)

    def port_on(self, swkey, port, stat, swcnt):
     
        self.lpanel.port_on(swkey, port, stat)

    def set_speed(self, swkey, speed):
       
        self.lpanel.set_speed(swkey, speed)

    def read_param(self, swkey, param):
        
        self.lpanel.read_param(swkey, param)

    def createBatchPanel(self, swDict):
        
        self.lpanel.createBatchPanel(swDict)

    def update_controls(self, mode):
        
        self.cpanel.loopPan.update_controls(mode)
        self.cpanel.autoPan.update_controls(mode)
        self.cpanel.logPan.update_controls(mode)
    
    def device_connected(self):
        
        for dev in range(len(DEVICES)):
            if dev == self.parent.selDevice:
                self.vboxdl.Show(self.devObj[self.parent.selDevice])
            else:
                self.vboxdl.Hide(self.devObj[dev])
        self.Layout()
        self.devObj[self.parent.selDevice].device_connected()
    
    def device_disconnected(self):
        
        self.devObj[self.parent.selDevice].device_disconnected()
        self.loopPan.device_disconnected()
        self.autoPan.device_disconnected()
    
    def auto_connect(self):
        self.comPan.auto_connect()

    def updt_dut_config(self, dutno):
        self.parent.updt_dut_config(dutno)

    def get_dut_config(self, dutno):
        return self.parent.get_dut_config(dutno)

    def request_dut_close(self, dutname):
        self.parent.request_dut_close(dutname)

    def save_file(self, content, ftype):
        
        self.parent.save_file(content, ftype)
    
def EVT_RESULT(win, func):
    
    win.Connect(-1, -1, EVT_DUT_SL_ERR_ID, func) 
