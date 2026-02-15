# -*- coding: utf-8 -*-
##############################################################################
#
# Module: dutLogWindow.py
#
# Description:
#     DUT Monitoring & Log Display Window for Supported MCCI Switch Models.
#
# Detailed Description:
#     This module implements a real-time monitoring and logging window
#     for Device Under Test (DUT) communication.#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
#
##############################################################################

# Lib imports
import wx

# Own modules
from uiGlobals import *
from datetime import datetime

import wx

import configdata

from .dutConfigDialog import DutConfigDialog

import serial.tools.list_ports

from . import dutThread
import queue

from threading import Thread
import time

ERR1 = "Non-secure Usage Fault"
ERR2 = "FATAL ERROR: Secure Fault"
ERR3 = "osTimerNew() failed"
################################ Evt Listener ################################
def EVT_RESULT(win, func):
    """
    Bind DUT Result Event Listener.

    Connects a custom DUT result event to a handler function
    within the given window.

    Args:
        win (wx.Window):
            Target window to receive the event.

        func (callable):
            Callback function to handle the event.
    """
    win.Connect(-1, -1, EVT_DUT_SL_DATA_ID, func)

class ResultEvent(wx.PyEvent):
    """
    Custom Event to Carry DUT Monitoring Data.

    This event is posted from worker threads to the GUI thread
    to safely transfer DUT log data.

    Inherits:
        wx.PyEvent
    """
    def __init__(self, data):
        """
        Initialize Result Event.

        Args:
            data (str):
                Log or monitoring data received from DUT.
        """
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_DUT_SL_DATA_ID)
        self.data = data 

###################### Thread to Look for data in the queue ###################
class TestThread(Thread):
    """
    DUT Log Queue Listener Thread.

    This worker thread continuously monitors a shared queue
    for incoming DUT log data and posts it to the GUI using
    custom wx events.

    Purpose:
        • Prevent GUI blocking
        • Enable real-time log updates
        • Handle asynchronous DUT communication

    Inherits:
        threading.Thread

    Args:
        wxObject (wx.Window):
            Target GUI window to receive log events.

        inqueue (queue.Queue):
            Queue object containing DUT log messages.
    """
        
    #----------------------------------------------------------------------
    def __init__(self, wxObject, inqueue):
        """
        Initialize Worker Thread.

        Args:
            wxObject (wx.Window):
                Window that receives posted log events.

            inqueue (queue.Queue):
                Queue used to receive DUT log messages.
        """
        Thread.__init__(self)
        self.wxObject = wxObject
        self.run_flg = True
        self.serialdev = None
        self.queue = inqueue
        self.start()    # start the thread
        
    #----------------------------------------------------------------------
    def run(self):
        """
        Execute Worker Thread Loop.

        Continuously monitors the queue for new DUT data and
        posts results to the GUI thread.

        Behavior:
            • Sends monitoring start message
            • Polls queue for log data
            • Posts data via ResultEvent
            • Sleeps briefly to reduce CPU load
            • Sends monitoring exit message on stop
        """
        # This is the code executing in the new thread.
        wx.PostEvent(self.wxObject, ResultEvent("\nBegin DUT Monitoring..."))
        
        while(self.run_flg):
            var = None
            try:
                var = self.queue.get(False)
            except queue.Empty:
                pass
            else:
                wx.PostEvent(self.wxObject, ResultEvent(var))
            time.sleep(0.01)
        wx.PostEvent(self.wxObject, ResultEvent("\nExit DUT Monitoring..."))

    def stop(self):
        """
        Stop Worker Thread Execution.

        Sets the run flag to False, terminating the monitoring loop.
        """
        self.run_flg = False


##############################################################################
# Utilities
##############################################################################
class DutLogWindow(wx.Window):
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

        self.name = "dut"
        self.top = top
        self.sut = sut
        self.parent = parent

        key = list(self.sut.keys())[0]

        self.name = self.sut[key]["name"]
        self.sutType = self.sut[key]["interface"]
        self.sutSettings = self.sut[key][self.sutType]
        self.sutFaultMsg = self.sut[key]["faultseq"]

        sb = wx.StaticBox(self, -1, self.name)

        self.con_flg = False
        self.devHand = serial.Serial()
        self.port_flg = False

        self.totline = 0

        self.vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)
        
        self.btn_close = wx.Button(self, ID_BTN_SL_SAVE, "Close",
                                        size=(60, -1))

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
        self.hbox.Add(20,0,0)
        self.hbox.Add(self.btn_close, 0, wx.ALIGN_LEFT | 
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
        
        self.btn_config.Bind(wx.EVT_BUTTON, self.OnDutConfig)
        self.btn_connect.Bind(wx.EVT_BUTTON, self.OnSutConnect)
        self.btn_clear.Bind(wx.EVT_BUTTON, self.OnSutClear)
        self.btn_save.Bind(wx.EVT_BUTTON, self.OnSutSave)
        self.btn_close.Bind(wx.EVT_BUTTON, self.OnSutclose)
        
        # Set size of frame
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.Layout()

        self.dpath = configdata.get_user_data_dir()
        self.fpath = configdata.get_file_path()
        self.read_config_data()

        if self.sutType == "serial":
            self.print_com_config()
        
        self.queue = queue.Queue(0)
        self.mySut = None
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
        """
        Append Text to Log Display.

        Args:
            strin (str):
                Text string to append to the log window.
        """
        self.scb.AppendText(strin)

    def print_com_config(self):
        """
        Display Current Serial Configuration.

        Prints configured COM port parameters to the log window.
        """
        strout = ""
        strout += self.sutSettings["port"]+", "
        strout += self.sutSettings["baud"]+", "
        strout += self.sutSettings["databits"]+", "
        strout += self.sutSettings["parity"]+", "
        strout += self.sutSettings["stopbits"]
        self.print_on_log(strout)

    def push_com_default(self):
        """
        Load Default Serial Configuration.

        Provides fallback serial settings when no configuration
        is available.

        Returns:
            dict:
                Default serial configuration dictionary.
        """
        cdata = {"comPort": "COM0", "baudRate": "9600", "dataBits": "8", "parity": "None", 
                 "stopBits": "1", "parityErrChk": "(ignore)", 
                 "faultMsg": {"1": "Non-secure Usage Fault", "2": "FATAL ERROR: SecureFault", 
                 "3": "osTimerNew() failed"}}
        return cdata

    def read_config_data(self):
        """
        Read DUT Configuration Data.

        Loads serial configuration settings. If none exist,
        default settings are applied.
        """
        sutset = list(self.sutSettings.keys())
        
        if(len(sutset) == 0):
            self.sutSettings = self.push_com_default()

    def get_config_data(self):
        """
        Retrieve Current DUT Configuration.

        Returns:
            dict:
                DUT serial configuration settings.
        """
        return self.sutSettings

    def updt_dut_config(self, dutdict):
        """
        Update DUT Configuration in Parent.

        Args:
            dutdict (dict):
                Updated DUT configuration dictionary.
        """
        self.top.updt_dut_config(dutdict)

    def save_config_data(self, cdata):
        """
        Save DUT Configuration Data.

        Persists configuration data to storage.

        Args:
            cdata (dict):
                Configuration data to save.
        """
        configdata.save_config(self.fpath, cdata)
        self.sutSettings = cdata
    
    def OnDutConfig(self, e):
        """
        Open DUT Configuration Dialog.

        Launches the DUT configuration window for editing
        communication and monitoring settings.

        Args:
            e (wx.Event):
                Button click event.
        """
        dutno = list(self.sut.keys())[0]
        self.sut = self.top.get_dut_config(dutno)
        dlg = DutConfigDialog(self, self.sut)
        dlg.Show()

    def openComPort(self):
        """
        Open Serial COM Port Connection.

        Initializes and opens the configured serial port
        using DUT communication settings.

        Updates:
            self.port_flg → Connection status flag.
        """
        self.name = list(self.sut.keys())[0]
        self.dutn = self.sut[self.name]
        self.itype = self.dutn["interface"]
        self.sconfig = self.dutn[self.itype]
        
        try:
            self.devHand.port = self.sconfig["port"]
            self.devHand.baudrate = self.sconfig["baud"]
            self.devHand.bytesize = serial.EIGHTBITS
            self.devHand.parity = serial.PARITY_NONE
            self.devHand.timeout = 0
            self.devHand.stopbits = serial. STOPBITS_ONE
        
            self.devHand.open()
            self.port_flg = True
        except:
            self.print_on_log("\nCouldn't open the port-Top")
            self.port_flg = False

    def OnSutConnect(self, e):
        """
        Handle DUT Connect / Disconnect Action.

        Establishes or terminates serial communication
        with the DUT.

        Starts/stops:
            • DUT worker thread
            • Queue monitoring thread

        Args:
            e (wx.Event):
                Button click event.
        """
        if(not self.con_flg):
            self.openComPort()
            if(self.port_flg):
                self.mythread = TestThread(self, self.queue)
                self.mySut = dutThread.DutThread(self.com_port_stopped, self.top, self.queue, self.sut, self.devHand)
                self.mySut.start()
                self.con_flg = True
                self.btn_connect.SetLabel("Disconnect")
        else:
            self.con_flg = False
            if self.port_flg:
                try:
                    self.devHand.close()
                except:
                    self.print_on_log("\nTop-Error in Port Closing")
            self.btn_connect.SetLabel("Connect")
            self.mySut.stop()
            self.mythread.stop()

    def OnSutClear(self, e):
        """
        Clear Log Display.

        Removes all text from the log window and resets
        line counters.

        Args:
            e (wx.Event):
                Button click event.
        """
        self.scb.SetValue('')
        self.totline = 0

    def com_port_stopped(self):
        """
        Handle COM Port Disconnection Event.

        Attempts to reopen the serial port and restart
        DUT monitoring threads.

        Updates connection state and UI labels accordingly.
        """
        self.mySut.stop()
        self.openComPort()
        if(self.port_flg):
            self.mySut = None
            self.mySut = dutThread.SutThread(self.com_port_stopped, self.top, self.queue, self.sut, self.devHand)
            self.mySut.start()
            self.con_flg = True
            self.btn_connect.SetLabel("Disconnect")
        else:
            self.print_on_log("\nCouldn't Open the COM Port")
            self.btn_connect.SetLabel("Connect")
            self.con_flg = False

    def OnSutSave(self, e):
        """
        Save Log Content to File.

        Exports the current log display content to a text file.

        Args:
            e (wx.Event):
                Button click event.
        """
        content = self.scb.GetValue()
        self.top.save_file(content, "*.txt")
        
    def OnSutclose(self, e):
        """
        Close DUT Log Window.

        Sends a close request to the parent application
        to remove this DUT monitoring panel.

        Args:
            e (wx.Event):
                Button click event.
        """
        self.top.request_dut_close(list(self.sut.keys())[0])

    def updateDisplay(self, msg):
        """
        Update Log Display from Thread Events.

        Receives DUT log data from worker thread events
        and appends it to the display window.

        Args:
            msg (ResultEvent):
                Event containing DUT log data.
        """
        self.totline += 1
        t = msg.data
        self.scb.AppendText("%s" % t)