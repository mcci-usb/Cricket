# -*- coding: utf-8 -*-
##############################################################################
# 
# Module: dutLogWindow.py
#
# Description:
#     To log the data of DUT information.
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
# Revision history:
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
# import defaultconfig

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
    Register DUT result event handler.

    Detailed Description:
        Connects a custom DUT result event to the
        specified callback function within the
        wxPython event framework.

        This mechanism enables asynchronous
        communication between worker threads
        and the UI thread.

    Args:
        win:
            wxPython window instance that will
            receive the event notifications.

        func:
            Callback function to handle the
            result event data.

    Returns:
        None
    """
    win.Connect(-1, -1, EVT_DUT_SL_DATA_ID, func)

class ResultEvent(wx.PyEvent):
    """
    Custom Result Event Class.

    Description:
        Encapsulates DUT monitoring data and
        transfers it safely from worker threads
        to the UI event loop.

    Attributes:
        data:
            Payload data received from DUT thread.
    """
    def __init__(self, data):
        """
        Initialize result event.

        Args:
            self:
                Reference to the current instance.

            data:
                DUT monitoring data payload.

        Returns:
            None

        Raises:
            None
        """
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_DUT_SL_DATA_ID)
        self.data = data 

class TestThread(Thread):
    """
    DUT Queue Monitoring Thread.

    Description:
        Continuously monitors DUT data queue and
        posts received messages to the UI display
        using wxPython events.
    """

    def __init__(self, wxObject, inqueue):
        """
        Initialize monitoring thread.

        Args:
            self:
                Thread instance reference.

            wxObject:
                wxPython window to receive events.

            inqueue:
                Queue object containing DUT data.

        Returns:
            None

        Raises:
            None
        """
        Thread.__init__(self)
        self.wxObject = wxObject
        self.run_flg = True
        self.serialdev = None
        self.queue = inqueue
        self.start()    # start the thread
  
    def run(self):
        """
        Execute DUT monitoring loop.

        Detailed Description:
            Continuously polls the DUT data queue
            and forwards received data to the UI
            through custom result events.

        Args:
            self:
                Thread instance reference.

        Returns:
            None
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
        Stop monitoring thread execution.

        Detailed Description:
            Terminates the monitoring loop by
            disabling the thread run flag.

        Args:
            self:
                Thread instance reference.

        Returns:
            None
            self.run_flg = False
        """


##############################################################################
# Utilities
##############################################################################
class DutLogWindow(wx.Window):
    """
    DUT Log Monitoring Window.

    Description:
        Displays DUT communication logs and
        provides controls for connection,
        configuration, monitoring, and log
        management operations.
    """
    def __init__(self, parent, top, sut):
        """
        Initialize DUT log window UI.

        Detailed Description:
            Creates DUT monitoring interface
            including log display, control buttons,
            serial communication handlers, and
            monitoring thread integration.

        Args:
            self:
                Reference to current instance.

            parent:
                Parent UI container.

            top:
                Main application controller.

            sut:
                DUT configuration dictionary.

        Returns:
            None
        """
        # udict = {"msudp": {"uname": self.username, "pwd": self.password}}
        udict = {'dut1': {'name': '', 'faultseq': [], 
                          'action': 'None', 
                          'interface': 'serial', 
                          'serial': {'port': 'None', 'baud': '9600', 'databits': '8', 'parity': 'none', 'stopbits': '1', 'parerrcheck': 'ignore'}, 
                          'tcp': {}, 
                          'default': {'serial': {'port': 'None', 'baud': '9600', 'parity': 'none', 'databits': 8, 'stopbits': '1', 'parerrcheck': 'ignore'}, 'tcp': {}}}}
        
       
        wx.Window.__init__(self, parent)
        # SET BACKGROUND COLOUR TO White
        self.SetBackgroundColour("White")
        self.SetMinSize((480,330))

        self.name = "dut"
        self.top = top
        self.sut = udict
        # self.sut = udict2
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
        Filter available COM ports.

        Detailed Description:
            Retrieves system COM ports and excludes
            specific VID/PID USB switch devices
            from the selectable list.

        Args:
            self:
                DutLogWindow instance reference.

        Returns:
            list:
                Filtered COM port names.
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
        Append text to DUT log display.

        Args:
            self:
                Window instance reference.

            strin:
                Text string to append to log.

        Returns:
            None
        """
        self.scb.AppendText(strin)

    def print_com_config(self):
        """
        Display serial configuration in log.

        Detailed Description:
            Formats DUT serial communication
            parameters and prints them into
            the monitoring log window.

        Args:
            self:
                Window instance reference.

        Returns:
            None

        Raises:
            None
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
        Provide default serial configuration.

        Detailed Description:
            Returns fallback serial settings
            when no stored configuration exists.

        Args:
            self:
                Window instance reference.

        Returns:
            dict:
                Default communication parameters.

        Raises:
            None
        """
        cdata = {"comPort": "COM0", "baudRate": "9600", "dataBits": "8", "parity": "None", 
                 "stopBits": "1", "parityErrChk": "(ignore)", 
                 "faultMsg": {"1": "Non-secure Usage Fault", "2": "FATAL ERROR: SecureFault", 
                 "3": "osTimerNew() failed"}}
        return cdata

    def read_config_data(self):
        """
        Load DUT configuration data.

        Detailed Description:
            Validates stored DUT configuration.
            Applies default configuration if
            settings are missing.

        Args:
            self:
                Window instance reference.

        Returns:
            None

        Raises:
            None
        """
        # pass
        sutset = list(self.sutSettings.keys())
        
        if(len(sutset) == 0):
            self.sutSettings = self.push_com_default()

    def get_config_data(self):
        """
        Retrieve DUT communication configuration.

        Args:
            self:
                Window instance reference.

        Returns:
            dict:
                Current DUT configuration settings.

        Raises:
            None
        """
        return self.sutSettings

    def updt_dut_config(self, dutdict):
        """
        Update DUT configuration in controller.

        Args:
            self:
                Window instance reference.

            dutdict:
                Updated DUT configuration dictionary.

        Returns:
            None

        Raises:
            None
        """
        self.top.updt_dut_config(dutdict)

    def save_config_data(self, cdata):
        """
        Persist DUT configuration to storage.

        Args:
            self:
                Window instance reference.

            cdata:
                Configuration dictionary to save.

        Returns:
            None

        Raises:
            None
        """
        configdata.save_config(self.fpath, cdata)
        self.sutSettings = cdata
    
    def OnDutConfig(self, e):
        """
        Open DUT configuration dialog.

        Detailed Description:
            Retrieves current DUT configuration
            and launches configuration window.

        Args:
            self:
                Window instance reference.

            e:
                Button click event object.

        Returns:
            None

        Raises:
            None
        """
        dutno = list(self.sut.keys())[0]
        self.sut = self.top.get_dut_config(dutno)
        dlg = DutConfigDialog(self, self.sut)
        dlg.Show()

    def openComPort(self):
        """
        Open DUT serial communication port.

        Detailed Description:
            Applies configured serial parameters
            and attempts to establish connection
            with DUT device.

        Args:
            self:
                Window instance reference.

        Returns:
            None

        Raises:
            SerialException:
                If port opening fails.
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
        Handle DUT connect / disconnect action.

        Detailed Description:
            Establishes or terminates DUT serial
            communication and monitoring threads.

        Args:
            self:
                Window instance reference.

            e:
                Button click event.

        Returns:
            None

        Raises:
            None
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
        Clear DUT log display.

        Args:
            self:
                Window instance reference.

            e:
                Button click event.

        Returns:
            None

        Raises:
            None
        """
        self.scb.SetValue('')
        self.totline = 0

    def com_port_stopped(self):
        """
        Handle unexpected COM port disconnection.

        Detailed Description:
            Attempts automatic reconnection and
            restarts DUT monitoring thread.

        Args:
            self:
                Window instance reference.

        Returns:
            None

        Raises:
            None
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
        Save DUT log content to file.

        Args:
            self:
                Window instance reference.

            e:
                Button click event.

        Returns:
            None

        Raises:
            None
        """
        content = self.scb.GetValue()
        self.top.save_file(content, "*.txt")
        
    def OnSutclose(self, e):
        """
        Close DUT log window.

        Detailed Description:
            Notifies parent controller to close
            DUT session and release resources.

        Args:
            self:
                Window instance reference.

            e:
                Button click event.

        Returns:
            None

        Raises:
            None
        """
        self.top.request_dut_close(list(self.sut.keys())[0])

    def updateDisplay(self, msg):
        """
        Update DUT log display from thread data.

        Detailed Description:
            Receives asynchronous monitoring data
            and appends it to the log window.

        Args:
            self:
                Window instance reference.

            msg:
                ResultEvent containing DUT data.

        Returns:
            None

        Raises:
            None
        """

        self.totline += 1
        t = msg.data
        self.scb.AppendText("%s" % t)
        
class dutDialog(wx.Dialog):
    
    def __init__ (self, parent, top):
        """
        Initialize DUT dialog window.

        Args:
            self:
                Dialog instance reference.

            parent:
                Parent window reference.

            top:
                Main controller reference.

        Returns:
            None

        Raises:
            None
        """
        
        wx.Dialog.__init__(self, parent, -1, "Switch 3141 Firmware Update",
                           size=wx.Size(100, 100),
                           style=wx.STAY_ON_TOP|wx.DEFAULT_DIALOG_STYLE,
                           name="MCCI USB Switch Search Dialog")

        self.top = top
        self.win = DutLogWindow(self, top)

        # Sizes the window to fit its best size.
        self.Fit()
        self.CenterOnParent(wx.BOTH)
    
    def OnOK (self, evt):
        """
        Handle dialog OK action.

        Args:
            self:
                Dialog instance reference.

            evt:
                Button click event.

        Returns:
            None

        Raises:
            None
        """
        
    # Returns numeric code to caller
        self.EndModal(wx.ID_OK)
     
    def OnSize (self, evt):
        """
        Handle dialog resize event.

        Args:
            self:
                Dialog instance reference.

            evt:
                Resize event object.

        Returns:
            None

        Raises:
            None
        """
        self.Layout()
    