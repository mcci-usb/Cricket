#======================================================================
# (c) 2020  MCCI, Inc.
#----------------------------------------------------------------------
# Project : UI3141/3201 GUI application
# File    : treeWindow.py
#----------------------------------------------------------------------
# Tree Window - Show the list of USB devices connected/disconnected
#======================================================================

#======================================================================
# IMPORTS
#======================================================================
import wx

import threading
from datetime import datetime

import usbDev
from uiGlobals import *

#======================================================================
# COMPONENTS
#======================================================================

class UsbTreeWindow(wx.Window):
    def __init__(self, parent, top):
        wx.Window.__init__(self, parent)
        self.SetBackgroundColour("White")

        self.top = top

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)

        self.wait_flg = False

        sb = wx.StaticBox(self, -1,"USB Device Tree View Changes")
        
        self.vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)

        self.chk_box = wx.CheckBox(self, -1, label='Enable')

        self.chk_ts = wx.CheckBox(self, -1, label='Show Timestamp')

        self.st_delay   = wx.StaticText(self, -1, " Delay ", 
                                        style=wx.ALIGN_CENTER)

        self.tc_delay   = wx.TextCtrl(self, -1, "1000", size=(50,-1), 
                                      style = wx.TE_CENTRE |
                                      wx.TE_PROCESS_ENTER,
                                      validator=NumericValidator(),
                                      name="Enumeration Delay")

        self.st_ms   = wx.StaticText(self, -1, "ms", size=(30,15), 
                                     style = wx.ALIGN_CENTER)

        self.btn_clear = wx.Button(self, ID_BTN_UCLEAR, "Clear", 
                                   size=(60, -1))

        self.btn_ref = wx.Button(self, ID_BTN_AUTO, "Refresh", size=(60,-1))

        self.btn_save = wx.Button(self, -1, "Save", size=(60,-1))

        self.st_td   = wx.StaticText(self, -1, " Total Device : ", 
                                     style=wx.ALIGN_CENTER)
        self.st_tdp  = wx.StaticText(self, -1, " --- ", style=wx.ALIGN_CENTER)

        self.st_tr   = wx.StaticText(self, -1, " Readable : ", 
                                     style=wx.ALIGN_CENTER)
        self.st_trp  = wx.StaticText(self, -1, " --- ", style=wx.ALIGN_CENTER)

        self.st_te   = wx.StaticText(self, -1, " Error : ", 
                                     style=wx.ALIGN_CENTER)
        self.st_tep  = wx.StaticText(self, -1, " --- ", style=wx.ALIGN_CENTER)

        
        self.scb = wx.TextCtrl(self, -1, style= wx.TE_MULTILINE, 
                               size=(-1,-1))

        self.scb.SetEditable(False)
        self.scb.SetBackgroundColour((255,255,255))
        
        self.tc_delay.SetToolTip(wx.ToolTip("USB device scan delay. Min:"
                                             "100 msec, Max: 60 sec"))
        self.btn_save.SetToolTip(wx.ToolTip("Save USB device Log into"
                                            " a text file"))

        self.hbox.Add(10,30,0)
        self.hbox.Add(self.chk_box,0, wx.ALIGN_CENTRE_VERTICAL)
        self.hbox.Add(20,0,0)
        self.hbox.Add(self.st_delay,0, wx.ALIGN_CENTRE_VERTICAL)
        self.hbox.Add(self.tc_delay,0, wx.ALIGN_CENTRE_VERTICAL)
        self.hbox.Add(self.st_ms,0, wx.ALIGN_CENTRE_VERTICAL)
        self.hbox.Add(33,0,0)
        self.hbox.Add(self.btn_ref, 0, flag=wx.ALIGN_RIGHT | 
                      wx.LEFT, border = 0)

        self.hbox2.Add(10,30,0)
        self.hbox2.Add(self.st_td,0, wx.ALIGN_CENTRE_VERTICAL)
        self.hbox2.Add(self.st_tdp,0, wx.ALIGN_CENTRE_VERTICAL)
        self.hbox2.Add(30,0,0)
        self.hbox2.Add(self.st_tr,0, wx.ALIGN_CENTRE_VERTICAL)
        self.hbox2.Add(self.st_trp,0, wx.ALIGN_CENTRE_VERTICAL)
        self.hbox2.Add(30,0,0)
        self.hbox2.Add(self.st_te,0, wx.ALIGN_CENTRE_VERTICAL)
        self.hbox2.Add(self.st_tep,0, wx.ALIGN_CENTRE_VERTICAL)

        self.hbox3.Add(10,30,0)
        self.hbox3.Add(self.chk_ts,0, wx.ALIGN_CENTRE_VERTICAL)
        self.hbox3.Add(23,0,0)
        self.hbox3.Add(self.btn_clear, 0, wx.ALIGN_RIGHT)
        self.hbox3.Add(34,0,0)
        self.hbox3.Add(self.btn_save,0, flag=wx.RIGHT, border=0)
        
        self.btn_ref.Bind(wx.EVT_BUTTON, self.RefreshUsbBus)
        self.btn_clear.Bind(wx.EVT_BUTTON, self.ClearUsbWindow)
        self.btn_save.Bind(wx.EVT_BUTTON, self.SaveUsbLog)
        #self.tc_delay.Bind(wx.EVT_TEXT_ENTER, self.OnEnterDelay)
        self.chk_box.Bind(wx.EVT_CHECKBOX, self.OnCheckBox)

        self.tc_delay.SetMaxLength(5)

        self.szr_top = wx.BoxSizer(wx.VERTICAL)
        self.szr_top.AddMany([
            (5,0,0),
            (self.scb, 1, wx.EXPAND),
            (5,0,0)
            ])

        self.vbox.AddMany([
            (self.hbox, 0, wx.ALIGN_LEFT | wx.ALIGN_TOP),
            (self.hbox2, 0, wx.ALIGN_LEFT),
            (10, 7, 0),
            (self.hbox3, 0, wx.EXPAND),
            (10, 0, 0),
            (self.szr_top, 1, wx.ALIGN_LEFT | wx.ALIGN_BOTTOM | wx.EXPAND)
            ])

        self.vbox.Hide(self.hbox2)

        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.Layout()


    def SaveUsbLog(self, e):
        content = self.scb.GetValue()
        self.top.save_file(content, "*.txt")

    def RefreshUsbBus(self, e):
        if(self.wait_flg == False):
            self.btn_ref.Disable()
            self.wait_flg = True
            threading.Thread(target=self.UsbThread).run()

    def ClearUsbWindow(self, e):
        self.scb.SetValue("")

    def UsbThread(self):
        try:
            usbDev.get_tree_change(self.top)
        except:
            self.print_on_usb("USB Read Error!")
        self.wait_flg = False
        self.btn_ref.Enable()

    def OnEnterDelay(self, evt):
        self.update_interval_period()

    def OnCheckBox(self, evt):
        self.update_interval_period()

    def get_time_stamp(self):
        ct = datetime.now()
        dtstr = ct.strftime("%Y-%m-%d  %H:%M:%S.%f")
        cstr = "[" + dtstr[:-3] + "]  "
        return cstr

    def print_on_usb(self, strin):
        ctstr = "\n"
        if(self.chk_ts.GetValue() == True):
            ctstr = ctstr + self.get_time_stamp()
        ctstr = ctstr + strin
        self.scb.AppendText(ctstr)

    def get_enum_delay(self):
        edly = self.tc_delay.GetValue()
        
        if(edly == ""):
            edly = "100"
        dval = int(edly)
        
        if(dval < 100):
            dval = 100
        elif(dval > 60000):
            dval = 60000

        self.tc_delay.SetValue(str(dval))
        
        return self.tc_delay.GetValue()

    def get_delay_status(self):
        if(self.chk_box.GetValue() == True):
            return True
        else:
            return False

    def disable_usb_scan(self):
        self.chk_box.SetValue(False)

    def update_interval_period(self):
        if(self.get_delay_status()):
            onTime, offTime, duty = self.top.get_loop_param()
            if(int(onTime) >= int(offTime)):
                if(int(offTime) < int(self.get_enum_delay())):
                    duty = 100 - duty
                    ndly = int((int(self.get_enum_delay())*100)/duty)
                    self.top.set_period(str(ndly))
            else:
                if(int(onTime) < int(self.get_enum_delay())):
                    ndly = int((int(self.get_enum_delay())*100)/duty)
                    self.top.set_period(str(ndly))
            
            if(int(self.top.get_interval()) < int(self.get_enum_delay())):
                self.top.set_interval(self.get_enum_delay())

    def enable_enum_controls(self, stat):
        if(stat == True):
            self.chk_box.Enable()
            self.tc_delay.Enable()
        else:
            self.chk_box.Disable()
            self.tc_delay.Disable()
