##############################################################################
# 
# Module: serialLogWindow.py
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

# Lib imports
import wx

# Own modules
from uiGlobals import *
from datetime import datetime

import wx
import threading

import configdata
# from sutConfigDialogOld import *
from sutConfigDialog import *
import serial.tools.list_ports

import sutThread
import queue

from threading import Thread
import time

ERR1 = "Non-secure Usage Fault"
ERR2 = "FATAL ERROR: Secure Fault"
ERR3 = "osTimerNew() failed"
################################ Evt Listener ################################
def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_SUT_SL_DATA_ID, func)

class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_SUT_SL_DATA_ID)
        self.data = data 

###################### Thread to Look for data in the queue ###################
class TestThread(Thread):
    """Test Worker Thread Class."""
        
    #----------------------------------------------------------------------
    def __init__(self, wxObject, inqueue):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self.wxObject = wxObject
        self.run_flg = True
        self.serialdev = None
        self.queue = inqueue
        self.start()    # start the thread
        
    #----------------------------------------------------------------------
    def run(self):
        """Run Worker Thread."""
        # This is the code executing in the new thread.
        wx.PostEvent(self.wxObject, ResultEvent("\nBegin SUT Monitoring..."))
        
        while(self.run_flg):
            var = None
            try:
                var = self.queue.get(False)
            except queue.Empty:
                pass
            else:
                # print(var)
                # if(var.find(ERR1) != -1 or var.find(ERR2) != -1 or var.find(ERR3) != -1):
                #     wx.PostEvent(self.wxObject, ResultEvent("Error Squence found"))
                # else:
                #     wx.PostEvent(self.wxObject, ResultEvent(var))
                wx.PostEvent(self.wxObject, ResultEvent(var))
            time.sleep(0.01)
        wx.PostEvent(self.wxObject, ResultEvent("\nExit SUT Monitoring..."))

    def stop(self):
        self.run_flg = False



##############################################################################
# Utilities
##############################################################################
class SutLogWindow(wx.Window):
    """
    A class logWindow with init method

    To show the all actions while handling ports of devices 
    """
    def __init__(self, parent, top, sut):
        """
        logWindow values displayed for all Models 3201, 3141,2101 
        Args:
            self: The self parameter is a reference to the current .
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
            top: creates an object
        Returns:
            None
        """
        wx.Window.__init__(self, parent)
        # SET BACKGROUND COLOUR TO White
        self.SetBackgroundColour("White")
        self.SetMinSize((480,330))

        self.top = top
        self.sut = sut

        key = list(self.sut.keys())[0]

        self.name = self.sut[key]["name"]
        self.sutType = self.sut[key]["interface"]
        self.sutSettings = self.sut[key][self.sutType]
        self.sutFaultMsg = self.sut[key]["faultseq"]

        sb = wx.StaticBox(self, -1, self.name)

        self.con_flg = False

        self.totline = 0

        self.vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)

        self.btn_save = wx.Button(self, ID_BTN_SL_SAVE, "Save",
                                        size=(60, -1))  
        self.btn_clear = wx.Button(self, ID_BTN_SL_CLEAR, "Clear",
                                         size=(60, 25))
        self.btn_config = wx.Button(self, ID_BTN_SL_CONFIG, "Config",
                                        size=(60, -1))
        self.btn_connect = wx.Button(self, ID_BTN_SL_CONNECT, "Connect",
                                        size=(60, -1))   

        self.scb = wx.TextCtrl(self, -1, style= wx.TE_MULTILINE, 
                                         size=(-1,-1))
        self.scb.SetEditable(False)
        self.scb.SetBackgroundColour((255,255,255))
        
        # Tooltips display text over an widget elements
        # set tooltip for switching interval and auto buttons.
        self.btn_save.SetToolTip(wx.
                      ToolTip("Save Log content into a text file"))

        # Create BoxSizer as horizontal
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.wait_flg = False

        self.hbox.Add(30,0,0)
        self.hbox.Add(self.btn_config, 0, wx.ALIGN_LEFT | 
                                         wx.ALIGN_CENTER_VERTICAL)
        self.hbox.Add(20,0,0)
        self.hbox.Add(self.btn_connect, 0, wx.ALIGN_LEFT | 
                                         wx.ALIGN_CENTER_VERTICAL)
        self.hbox.Add(80,0,1)
        self.hbox.Add(self.btn_clear, 0, wx.ALIGN_LEFT | 
                                         wx.ALIGN_CENTER_VERTICAL)
        self.hbox.Add(20,0,0)
        self.hbox.Add(self.btn_save, 0, wx.ALIGN_LEFT | 
                                         wx.ALIGN_CENTER_VERTICAL)
        
        self.szr_top = wx.BoxSizer(wx.VERTICAL)
        self.szr_top.AddMany([
            (5,0,0),
            (self.scb, 1, wx.EXPAND),
            (5,0,0)
            ])

        self.vbox.AddMany([
            (self.hbox, 0, wx.ALIGN_LEFT),
            (10,5,0),
            (self.szr_top, 1, wx.EXPAND),
            (0,0,0)
            ])

        self.plist = self.filter_port()
        # print(self.plist)

        self.btn_config.Bind(wx.EVT_BUTTON, self.OnSutConfig)
        self.btn_connect.Bind(wx.EVT_BUTTON, self.OnSutConnect)
        self.btn_clear.Bind(wx.EVT_BUTTON, self.OnSutClear)
        self.btn_save.Bind(wx.EVT_BUTTON, self.OnSutSave)
        # Set size of frame
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.Layout()

        self.dpath = configdata.get_user_data_dir()
        self.fpath = configdata.get_file_path()
        self.read_config_data()

        if self.sutType == "serial":
            self.print_com_config()
        # self.save_config_data()

        self.queue = queue.Queue(0)
        self.mySut = None
       # self.myser = myserial.mySerial(self.queue)
        self.mythread = None
        EVT_RESULT(self, self.updateDisplay)


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

    def print_on_log(self, strin):
        self.scb.AppendText(strin)

    def print_com_config(self):
        strout = ""
        strout += self.sutSettings["port"]+", "
        strout += self.sutSettings["baud"]+", "
        strout += self.sutSettings["databits"]+", "
        strout += self.sutSettings["parity"]+", "
        strout += self.sutSettings["stopbits"]
        self.print_on_log(strout)

    def push_com_default(self):
        cdata = {"comPort": "COM0", "baudRate": "9600", "dataBits": "8", "parity": "None", 
                 "stopBits": "1", "parityErrChk": "(ignore)", 
                 "faultMsg": {"1": "Non-secure Usage Fault", "2": "FATAL ERROR: SecureFault", 
                 "3": "osTimerNew() failed"}}
        return cdata

    def read_config_data(self):
        # self.sutConfig = configdata.read_config(self.fpath)
        sutset = list(self.sutSettings.keys())
        
        if(len(sutset) == 0):
            self.sutSettings = self.push_com_default()

    def get_config_data(self):
        return self.sutSettings

    def save_config_data(self, cdata):
        configdata.save_config(self.fpath, cdata)
        self.sutSettings = cdata

    def OnSutConfig(self, e):
        dlg = SutConfigDialog(self, self.sut)
        dlg.Show()

    def OnSutConnect(self, e):
        if(not self.con_flg):
            self.mythread = TestThread(self, self.queue)
            self.mySut = sutThread.SutThread(self.com_port_stopped, self.top, self.queue, self.sut)
        
            # self.scb.SetValue("Thread started!")
            self.mySut.start()
            self.con_flg = True
            self.btn_connect.SetLabel("Disconnect")
        else:
            self.con_flg = False
            self.btn_connect.SetLabel("Connect")
            self.mySut.stop()
            self.mythread.stop()

    def OnSutClear(self, e):
        self.scb.SetValue('')
        self.totline = 0

    def com_port_stopped(self):
        self.mySut = None
        self.mySut = sutThread.SutThread(self.com_port_stopped, self.top, self.queue, self.sut)
        self.mySut.start()
        self.con_flg = True
        self.btn_connect.SetLabel("Disconnect")


    def OnSutSave(self, e):
        title = ("Save the Log!")
        msg = ("Sorry, not implemented!")
        dlg = wx.MessageDialog(self, msg, title, wx.OK)
        dlg.ShowModal()

    def updateDisplay(self, msg):
        """
        Receives data from thread and updates the display
        """
        self.totline += 1
        t = msg.data
        self.scb.AppendText("%s" % t)
        self.btn_save.SetLabel(str(self.totline))
        