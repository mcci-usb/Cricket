##############################################################################
# 
# Module: sutConfigDialog.py
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
#    V2.6.0 Wed Apr 20 2022 17:00:00   Seenivasan V
#       Module created
##############################################################################
# from curses.panel import top_panel
from random import choice, choices
import wx

import serial.tools.list_ports
import json
import os
import sys
from sys import platform

from uiGlobals import IMG_ICON
   

class SutConfigWindow(wx.Panel):

    def __init__(self, top, sut):
        wx.Panel.__init__(self, top, -1,
                          size=wx.Size(400, 400))
        

        self.SetMinSize((320, 320))
        self.SetMaxSize((320, 320))

        self.top = top

        self.sut = sut
        self.name = list(self.sut.keys())[0]
        self.sutType = sut[self.name]["type"]
        self.sutSettings = sut[self.name]["settings"]
        self.sutFaultMsg = sut[self.name]["faultMsg"]

        # self.SetMinSize((180,330))
        self.cb_list = self.filter_port()
        cb_brate = ["9600", "19200", "38400", "57600", "115200"]
        cb_dbits = ["5","6","7","8"]
        cb_sbits = ["1", "1.5", "2"]
        cb_parity = ["Even", "Mark", "None", "Odd", "Space"]
        cb_pechar = ["(ignore)", "35 ('#')", "42 ('*')", "63 ('?')"]

        sb = wx.StaticBox(self, -1, "COM Port Settings")
        self.vbox = wx.StaticBoxSizer(sb,wx.VERTICAL)

        self.btn_ref = wx.Button(self, -1, "Refresh", (-1, -1))
        # self.btn_save = wx.Button(self, -1, "Save", (-1, -1))
        
        self.st_port = wx.StaticText(self, -1, "Select Port")
        self.st_baud = wx.StaticText(self, -1, "Baud Rate")
        self.st_databits = wx.StaticText(self, -1, "Data Bits")
        self.st_Parity = wx.StaticText(self, -1, "Parity")
        self.st_StopBits = wx.StaticText(self, -1, "Stop Bits")
        self.st_pechar = wx.StaticText(self, -1, "Parity Error Char.")

        self.st_data = wx.StaticText(self, -1, "Data to watch")


        self.cb_switch = wx.ComboBox(self,
                                     size=(120,-1),
                                     style = wx.TE_PROCESS_ENTER, choices=self.cb_list)
                
        self.cb_baud = wx.ComboBox(self,
                                     size=(85,-1),
                                     style = wx.TE_PROCESS_ENTER, choices=cb_brate)

        self.cb_Databits = wx.ComboBox(self,
                                     size=(65,-1),
                                     style = wx.TE_PROCESS_ENTER, choices = cb_dbits)

        self.cb_Parity = wx.ComboBox(self,
                                     size=(85,-1),
                                     style = wx.TE_PROCESS_ENTER, choices = cb_parity)

        self.cb_StopBits = wx.ComboBox(self,
                                     size=(65,-1),
                                     style = wx.TE_PROCESS_ENTER, choices=cb_sbits)

        self.cb_pechar = wx.ComboBox(self,
                                     size=(65,-1),
                                     style = wx.TE_PROCESS_ENTER, choices=cb_pechar)

        
        # self.tc_data = wx.TextCtrl(self, -1," ", size = (280, 100))

        # self.tc_data = wx.TextCtrl(self, -1, style= wx.TE_MULTILINE, 
        #                                  size=(280,100))
        

        # self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        # self.hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        # self.hbox7 = wx.BoxSizer(wx.HORIZONTAL)
        
        

        self.hbox1.Add(0,0,0)
        self.hbox1.Add(self.st_port, flag=wx.ALIGN_CENTER_VERTICAL | 
                       wx.LEFT)
        self.hbox1.Add(5,10,0)
        self.hbox1.Add(self.cb_switch, flag=wx.ALIGN_CENTER_VERTICAL | 
                       wx.LEFT)
        self.hbox1.Add(5,0,0)
        self.hbox1.Add(self.btn_ref,0, flag=wx.LEFT | 
                        wx.ALIGN_CENTER_VERTICAL, border=0)
        
        self.hbox3.Add(0,10,0)
        self.hbox3.Add(self.st_baud, flag=wx.ALIGN_CENTER)
        
        self.hbox3.Add(5,10,0)
        self.hbox3.Add(self.cb_baud, flag=wx.ALIGN_CENTER | 
                         wx.ALIGN_CENTER_VERTICAL)

        self.hbox3.Add(10,10,0)
        self.hbox3.Add(self.st_databits, flag=wx.ALIGN_CENTER)

        self.hbox3.Add(10,10,0)
        self.hbox3.Add(self.cb_Databits, flag=wx.ALIGN_CENTER | 
                         wx.ALIGN_CENTER_VERTICAL , border=80)
        
        self.hbox4.Add(0,10,0)
        self.hbox4.Add(self.st_Parity, flag=wx.ALIGN_CENTER)

        self.hbox4.Add(30,10,0)
        self.hbox4.Add(self.cb_Parity, flag=wx.ALIGN_CENTER | 
                         wx.ALIGN_CENTER_VERTICAL, border=140)

        
        self.hbox4.Add(10,10,0)
        self.hbox4.Add(self.st_StopBits, flag=wx.ALIGN_CENTER)
        
        self.hbox4.Add(10,10,0)
        self.hbox4.Add(self.cb_StopBits, flag=wx.ALIGN_CENTER | 
                         wx.ALIGN_CENTER_VERTICAL)

        
        self.hbox5.Add(0,10,0)
        self.hbox5.Add(self.st_pechar, flag=wx.ALIGN_CENTER | 
                         wx.ALIGN_CENTER_VERTICAL)
        self.hbox5.Add(10,0,0)
        self.hbox5.Add(self.cb_pechar, flag=wx.ALIGN_CENTER | 
                         wx.ALIGN_CENTER_VERTICAL, border=140)

        
        # self.hbox6.Add(0,10,0)
        # self.hbox6.Add(self.st_data, flag=wx.ALIGN_CENTER | 
        #                  wx.ALIGN_CENTER_VERTICAL)
        # self.hbox6.Add(110,0,0)
        # self.hbox6.Add(self.btn_save,0, flag=wx.LEFT | 
        #                 wx.ALIGN_CENTER_VERTICAL, border=0)
        

        # self.hbox7.Add(self.tc_data, flag=wx.ALIGN_CENTER | 
        #                  wx.ALIGN_CENTER_VERTICAL)
        
        self.vbox.AddMany([
            (0,10,0),
            # (self.hbox, 0, wx.EXPAND | wx.ALL),
            # (10,5,0),
            
            (self.hbox1, 0, wx.EXPAND | wx.ALL),
            # (10,5,0),
            # (self.hbox2, 1, wx.EXPAND | wx.ALL),
            (10,5,0),
            (self.hbox3, 0, wx.EXPAND | wx.ALL),
            (10,5,0),
            (self.hbox4, 0, wx.EXPAND | wx.ALL),
            (10,5,0),
            (self.hbox5, 0, wx.EXPAND | wx.ALL)
            # (10,5,0),
            # (self.hbox6, 0, wx.EXPAND | wx.ALL),
            # (10,5,0),
            # (self.hbox7, 0, wx.EXPAND | wx.ALL)
            ])
        
        self.cb_list = self.filter_port()

        self.InitSelectionCtrl()
        # self.SetSizer(self.vbox)
        self.SetSizerAndFit(self.vbox)
        self.vbox.Fit(self)
        self.Layout()
        
        #--------------------- ---EVENT BIND--- #---------------------
        
        self.cb_switch.Bind(wx.EVT_COMBOBOX, self.Onselectcom)
        self.cb_baud.Bind(wx.EVT_COMBOBOX, self.Onselectbaud)
        self.cb_Databits.Bind(wx.EVT_COMBOBOX, self.Onselectdatabits)
        self.cb_StopBits.Bind(wx.EVT_COMBOBOX, self.Onselectstopbits)

        self.btn_ref.Bind(wx.EVT_BUTTON, self.RefreshConfig)
        # self.btn_save.Bind(wx.EVT_BUTTON, self.SaveConfig)

        #--------------------- ----------------- #--------
        # def OnCombo(self, event): 
        #     self.label.SetLabel("You selected"+self.combo.GetValue()+" from Combobox") 
        
        #--------------------- # Def EVENTS # ------------


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
    
    def InitSelectionCtrl(self):
        self.cb_switch.SetValue(self.sutSettings["comPort"])
        self.cb_baud.SetValue(self.sutSettings["baudRate"])
        self.cb_Parity.SetValue(self.sutSettings["parity"])
        self.cb_Databits.SetValue(self.sutSettings["dataBits"])
        self.cb_pechar.SetValue(self.sutSettings["parityErrChk"])
        self.cb_StopBits.SetValue(self.sutSettings["stopBits"])
        # self.tc_data.SetValue(json.dumps(self.sutFaultMsg))

    def Onselectcom(self, e):
        self.cb = e.GetEventObject()
        #print(self.cb.GetValue())
        # print(self.cb.GetStringSelection())
    
    def Onselectbaud(self, e):
        self.cb = e.GetEventObject()
        #print(self.cb.GetValue())
        # print(self.cb.GetStringSelection())
    
    def Onselectdatabits(self, e):
        self.cb = e.GetEventObject()
        #print(self.cb.GetValue())
        # print(self.cb.GetStringSelection())
    
    def Onselectstopbits(self, e):
        self.cb = e.GetEventObject()
        #print(self.cb.GetValue())
        # print(self.cb.GetStringSelection())

    
    def SaveConfig(self, e):
        print("Save Config")
        # strcom = self.cb_switch.GetStringSelection()
        # strbr = self.cb_baud.GetStringSelection()
        # strdb = self.cb_Databits.GetStringSelection()
        # strpar = self.cb_Parity.GetStringSelection()
        # strsb = self.cb_StopBits.GetStringSelection()
        # strpec = self.cb_pechar.GetStringSelection()

        strcom = self.cb_switch.GetValue()
        strbr = self.cb_baud.GetValue()
        strdb = self.cb_Databits.GetValue()
        strpar = self.cb_Parity.GetValue()
        strsb = self.cb_StopBits.GetValue()
        strpec = self.cb_pechar.GetValue()

        strerr = self.tc_data.GetValue()
        print("Get Fault Str: ",strerr)
        errobj = json.loads(strerr)
        print("Get Fault as JSON: ",errobj)

        sutconfig = {"comPort": strcom, "baudRate": strbr, "dataBits": strdb, 
                     "parity": strpar, "stopBits": strsb, "parityErrChk": strpec,
                     "faultMsg": errobj}

        print("Data object before saving")
        print(sutconfig)

        self.top.save_config_data(sutconfig)

           
    def RefreshConfig(self, e):
        print("Refresh Config")
        self.cb_list = self.filter_port()
        self.cb_switch.Clear()
        for cport in self.cb_list:
            self.cb_switch.Append(cport)
        self.cb_switch.SetSelection(0)
        print(self.cb_list)

class TabTwo(wx.Panel):
    def __init__(self, parent, top):
        wx.Panel.__init__(self, parent, -1,
                          size=wx.Size(200,200),
                          style=wx.CLIP_CHILDREN,
                          name="SUT Configuration-2")
        
        # self.SetMinSize((630, 710))
        # self.SetMaxSize((630, 710))
        self.top = top
    
        
        self.t = wx.StaticText(self, -1, "This Feature will be Iplemented in Future", (20, 20))


class MidPanel(wx.Panel):
    def __init__(self, parent):
        super(MidPanel, self).__init__(parent)

        self.SetBackgroundColour('White')


        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.SetSizer(self.main_sizer)

        self.main_sizer.Fit(self)
        self.Layout()

class BotPanel(wx.Panel):
    def __init__(self, parent):
        super(BotPanel, self).__init__(parent)

        self.SetBackgroundColour('Blue')

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.SetSizer(self.main_sizer)

        self.main_sizer.Fit(self)
        self.Layout()

class SutConfigDialog(wx.Frame):
    def __init__(self, parent, sut):
        wx.Frame.__init__(self, parent, -1, "SUT Configuration Dialog",
                           size=wx.Size(310, 420))

        self.top = parent

        self.SetMinSize((330, 348))
        self.SetMaxSize((330, 348))

        self.CenterOnScreen()
        

        # self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)

        self.p = wx.Panel(self)
        
        
        self.midPan = MidPanel(self)
        self.botPan = BotPanel(self)

        # self.win = SutConfigWindow(self, top)
        # self.win = TabTwo(self, top)



        # self.nb = wx.Notebook(self.p)

        # self.tab1 = SutConfigWindow(self.nb, sut)
        # self.tab2 = TabTwo(self.nb, self)

        # self.nb.AddPage(self.tab1, "Serial")
        # self.nb.AddPage(self.tab2, "TCP")
        

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizernb = wx.BoxSizer(wx.VERTICAL)
        sizermidpan = wx.BoxSizer(wx.VERTICAL)
        sizerbotpan = wx.BoxSizer(wx.VERTICAL)
        # sizernb.Add(self.nb, 1, wx.EXPAND)
        sizermidpan.Add(self.midPan, 1, wx.EXPAND)
        sizerbotpan.Add(self.botPan, 1, wx.EXPAND)

        self.p.SetSizer(sizer)

        # Sizes the window to fit its best size.
        self.Fit()

        base = os.path.abspath(os.path.dirname(__file__))
        self.SetIcon(wx.Icon(base+"/icons/"+IMG_ICON))
        self.Show()
        # self.Layout()
        # self.Show()
        # Centre frame using CentreOnParent() function,
        # Show window in the center of the screen.
        # Centres the window on its parent.
        # self.CenterOnParent(wx.BOTH)

    def save_config_data(self, cdata):
        print("SUT Dialog, save config data")
        self.top.save_config_data(cdata)

    def read_config_data(self):
        return self.top.get_config_data()

