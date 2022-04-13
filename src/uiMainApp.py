##############################################################################
# 
# Module: uiMainApp.py
#
# Description:
#     Main Application body for the MCCI USB Switch 3201,MCCI USB Switch 3141 
#     and MCCI USB Switch 2101 GUI Application
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
#    V2.5.0 Fri Jan 07 2022 17:40:05   Seenivasan V
#       Module created
##############################################################################
# Lib imports
import wx
import serial
import webbrowser
import shelve

# Built-in imports
import os
import sys
from sys import platform
from pathlib import Path
from os import getenv

from wx.core import ITEM_CHECK

# Own modules
from uiGlobals import *
import dev3141Window
import dev3201Window
import dev2101Window
import dev2301Window
import loopWindow
import logWindow
import autoWindow

import getusb

from aboutDialog import *
from comDialog import *
from setDialog import *
from portDialog import *
#from ccServer import *

import vbusChart

import devControl
import serialDev
import control2101
import devServer

import thControl
import thServer

import search

##############################################################################
# Utilities
##############################################################################
class MultiStatus (wx.StatusBar):
    """
    A class Multistatus with init method
    This code pattern is run common in all Python files that
    to be executed as a script imported in another modules.
    """
    def __init__ (self, parent):
        """
        Associates a status bar with the frame.

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
        Returns:
            None
        """
        wx.StatusBar.__init__(self, parent, -1)
        # Sets the number of field count "5"
        self.SetFieldsCount(5)
        # Sets the widths of the fields in the status bar.
        self.SetStatusWidths([-1, -1, -3, -2, -10])

class UiPanel(wx.Panel):
    """
    A class UiPanel with init method
    the UiPanel navigate to UIApp name
    """ 
    def __init__(self, parent):
        """
        Uipanel created
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
        Returns:
            None
        """
        super(UiPanel, self).__init__(parent)

        wx.GetApp().SetAppName("Cricket")

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

        self.logPan = logWindow.LogWindow(self, parent)
        self.loopPan = loopWindow.LoopWindow(self, parent)
        #self.comPan = comWindow.ComWindow(self, parent)
        self.autoPan = autoWindow.AutoWindow(self, parent)
        
        self.dev3141Pan = dev3141Window.Dev3141Window(self, parent)
        self.dev3201Pan = dev3201Window.Dev3201Window(self, parent)
        self.dev2101Pan = dev2101Window.Dev2101Window(self, parent)
        self.dev2301Pan = dev2301Window.Dev2301Window(self, parent)

        self.devObj = []  
        # Device panel added
        self.devObj.append(self.dev3141Pan)
        self.devObj.append(self.dev3201Pan)
        self.devObj.append(self.dev2101Pan)
        self.devObj.append(self.dev2301Pan)

        
        # Creating Sizers
        self.vboxdl = wx.BoxSizer(wx.VERTICAL)
        self.vboxdl.Add(self.dev3141Pan, 0, wx.EXPAND)
        self.vboxdl.Add(self.dev3201Pan, 0, wx.EXPAND)
        self.vboxdl.Add(self.dev2301Pan, 0, wx.EXPAND)
        self.vboxdl.Add(self.dev2101Pan, 0, wx.EXPAND)

        self.vboxdl.Add(0, 10, 0)
        self.vboxdl.Add(self.autoPan, 1, wx.EXPAND)

        self.hboxdl = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxdl.Add(self.vboxdl, 1 ,wx.ALIGN_LEFT | wx.EXPAND)
        self.hboxdl.Add((20,0), 0, wx.EXPAND)
        self.hboxdl.Add(self.loopPan, 0, wx.EXPAND)
        
        self.vboxl = wx.BoxSizer(wx.VERTICAL)
        self.vboxl.Add((0,20), 0, wx.EXPAND)
        self.vboxl.Add(self.hboxdl, 0 ,wx.ALIGN_LEFT | wx.EXPAND)
        self.vboxl.Add((0,10), 0, 0)
        self.vboxl.Add(self.logPan, 1, wx.EXPAND)
        self.vboxl.Add((0,20), 0, wx.EXPAND)

        self.vboxr = wx.BoxSizer(wx.VERTICAL)
        self.vboxr.Add((0,20), 0, wx.EXPAND)
        self.vboxr.Add((0,20), 0, wx.EXPAND)

       # BoxSizer fixed with Horizontal
        self.hboxm = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxm.Add((20,0), 1, wx.EXPAND)
        self.hboxm.Add(self.vboxl, 1, wx.EXPAND)
        self.hboxm.Add((20,0), 1, wx.EXPAND)
        self.hboxm.Add(self.vboxr, 1, wx.EXPAND)
        self.hboxm.Add((20,0), 1, wx.EXPAND)
        
        # Set size of frame
        self.SetSizer(self.hboxm)
        
        # Setting Layouts
        self.SetAutoLayout(True)
        self.hboxm.Fit(self)
        self.Layout()

    def update_uc_panels(self):
        """
        Here updated the user computer panel depend on the connecting 
        Model devices.
        also termianate the switching Control Compter server,
        and terminate the Test Host Computer server,
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
        Returns:
            None
        """
        self.vboxl.Show(self.vboxl)
        self.vboxl.Show(self.hboxdl)
        self.hboxm.Show(self.vboxr)
        self.vboxdl.Hide(self.dev2301Pan)
        self.vboxdl.Hide(self.dev3201Pan)
        self.vboxdl.Hide(self.dev3141Pan)
        self.logPan.show_usb_ctrls(True)
        self.vboxl.Show(self.logPan)
        self.Layout()
        self.parent.terminateCcServer()
        self.parent.terminateHcServer()
 
    def update_server_panel(self):
        """
        here USB tree window and Log window update the on selection server
        with SCC and THC servers.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.hboxm.Hide(self.vboxr)
        self.logPan.show_usb_ctrls(False)
        self.vboxl.Show(self.logPan)
        self.hboxm.Show(self.vboxl)
        self.vboxl.Hide(self.hboxdl)
        self.Layout()

    def update_cc_panels(self):
        """
        when selecting Switching Control Computer server menu,
        its starts the Siwting control computer server.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.parent.startCcServer()
        
    def update_hc_panels(self):
        """
        when selecting Test Host Computer server menu,
        its starts the Test Host computer server.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.parent.startHcServer()
    
    def remove_all_panels(self):
        """
        Remove or Hide the the logwinodow and USB Tree view window.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.hboxm.Hide(self.vboxl)
        self.hboxm.Hide(self.vboxr)
        self.Layout()

    def remove_dev_panels(self):
        """
        Remove or Hide the the all Model 3141, 3201, 2101, 2301 windows panels.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.vboxdl.Hide(self.dev2301Pan)
        self.vboxdl.Hide(self.dev3201Pan)
        self.vboxdl.Hide(self.dev3141Pan)
        self.vboxdl.Hide(self.dev2101Pan)

    def PrintLog(self, strin):
        """
        print data/status on logwindow 

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            strin: data in String format
        Returns:
            None
        """
        self.logPan.print_on_log(strin)
    
    def get_enum_delay(self):
        """
        Get the USB Enumaration delay 

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            String - USB Enumeration delay 
        """
        return self.logPan.get_enum_delay()
      
    def get_delay_status(self):
        """
        Get the status of USB device Enumeration delay check box

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            Boolean - Status of the delay check box
        """
        return self.logPan.get_delay_status()
    
    def get_interval(self):
        """
        Get the interval parameter of Auto Mode

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            String - Auto Mode interval
        """
        return self.autoPan.get_interval()
    
    def set_interval(self, strval):
        """
        Update/Set the Auto Mode interval

        Args: 
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            strval: interval value in Sting format
        Returns:
            None
        """
        self.autoPan.set_interval(strval)
    
    def disable_usb_scan(self):
        """
        Disable the USB device scan by uncheck the check box

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns: 
            None
        """
        self.logPan.disable_usb_scan()
    
    def get_loop_param(self):
        """
        Get the Loop Window prameters

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            return None
        """
        return self.loopPan.get_loop_param()
    
    def get_auto_param(self):
        """
        Get the Auto Window prameters

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns: 
            return None
        """
        return self.autoPan.get_auto_param()
    
    def set_period(self, strval):
        """
        Set the period for Loop Window

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            strval: Period value in String format
        Returns:
            return None
        """
        self.loopPan.set_period(strval)

    def set_port_list(self, ports):
        """
        Set the ports list for Loop Window and Auto Window

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            ports: upated the ports list
        Returns:
            return None
        """
        self.loopPan.set_port_list(ports)
        self.autoPan.set_port_count(ports)
    
    def port_on(self, port, stat):
        """
        Port On/Off command from Loop and Auto Window

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            port: device port number
            stat: port on status will updated 
        Returns:
            None
        """
        self.devObj[self.parent.selDevice].port_on(port, stat)
    
    def update_controls(self, mode):
        """
        Update the controls based on the mode
        
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            mode: mode controls
        Returns:
            None
        """
        self.devObj[self.parent.selDevice].update_controls(mode)
        self.loopPan.update_controls(mode)
        self.autoPan.update_controls(mode)
        self.logPan.update_controls(mode)
    
    def device_connected(self):
        """
        Once device connected, Model Window get updated with selected Model

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        for dev in range(len(DEVICES)):
            if dev == self.parent.selDevice:
                self.vboxdl.Show(self.devObj[self.parent.selDevice])
            else:
                self.vboxdl.Hide(self.devObj[dev])
        self.Layout()
        self.devObj[self.parent.selDevice].device_connected()
    
    def device_disconnected(self):
        """
        Once device disconnected, disable all controls in Model, Loop 
        and Auto Window

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.devObj[self.parent.selDevice].device_disconnected()
        self.loopPan.device_disconnected()
        self.autoPan.device_disconnected()
    
    def auto_connect(self):
        """
        Once application loaded, initiate the auto connect 
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.comPan.auto_connect()

class UiMainFrame (wx.Frame):
    """
    A UiMainFrame is a window of size and position usually changed by user
    """
    def __init__ (self, parent, title):
        """
        MainFrame initialization

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
            title: Ui title name uodate
        Returns:
            None
        """
        # super(UiMainFrame, self).__init__(parent, title=title)
        wx.Frame.__init__(self, None, id = wx.ID_ANY,
                          title = "MCCI "+APP_NAME+" UI - "+
                          VERSION_STR, pos=wx.Point(80,5),
                          size=wx.Size(630, 710), style= wx.SYSTEM_MENU | 
                          wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX)

        self.ytop = DEFAULT_YPOS
        if sys.platform == 'darwin':
            self.ytop = YPOS_MAC

        self.SetPosition((80,self.ytop))

        self.SetMinSize((630, 710))
        self.SetMaxSize((630, 710))
        self.CenterOnScreen()


        self.init_flg = True

        self.ldata = {}

        self.devCtrl = None
        self.thCtrl = None

        self.ccflag = False

        self.selPort = {}
        
        self.selBaud = None
        self.selDevice = None

        self.ccserver = None
        self.ccclient = None
        self.listencc = None

        self.ccconfig = None

        self.hcserver = None
        self.hcclient = None
        self.listenhc = None

        self.devHand = serialDev.SerialDev(self)

        self.usbHand = control2101.Dev2101(self)

        self.mode = MODE_MANUAL

        self.con_flg = False
        self.vdata = None
        self.adata = None
        self.vgraph = False
        self.agraph = False

        self.stype = READ_CONFIG

        self.dev_list = []

        self.masterList = []
        
        self.panel = UiPanel(self)
        
        self.menuBar = wx.MenuBar()
        
        # If its not darwin or MAC OS
        if sys.platform != 'darwin':
           # Setting up the menu.
           self.fileMenu = wx.Menu()
           # fileMenu.Append(ID_MENU_FILE_NEW,   "&New Window\tCtrl+N")
           self.fileMenu.Append(ID_MENU_FILE_CLOSE, "&Close \tAlt+F4")

        self.comMenu = wx.Menu()
        self.comMenu.Append(ID_MENU_MODEL_CONNECT, "Connect")
        self.comMenu.Append(ID_MENU_MODEL_DISCONNECT, "Disconnect")

        # config menu
        self.configMenu = wx.Menu()        
        self.ucmenu = self.configMenu.Append(ID_MENU_CONFIG_UC, 
                            "User Computer", kind = ITEM_CHECK)
        self.ccmenu = self.configMenu.Append(ID_MENU_CONFIG_SCC, 
                            "Switch Control Computer", kind = ITEM_CHECK)
        self.hcmenu = self.configMenu.Append(ID_MENU_CONFIG_THC,
                            "Test Host Computer", kind = ITEM_CHECK)

        # Set Menu   
        self.setMenu = wx.Menu()
        self.setMenu.Append(ID_MENU_SET_SCC, "Switch Control Computer")
        self.setMenu.Append(ID_MENU_SET_THC, "Test Host Computer")

        self.volsAmps = wx.Menu()
        base = os.path.abspath(os.path.dirname(__file__))
        qmiamps = wx.MenuItem(self.volsAmps, ID_MENU_GRAPH, "VBUS V/I Plot")

        qmiamps.SetBitmap(wx.Bitmap(base+"/icons/"+IMG_WAVE))
        self.volsAmps.Append(qmiamps)

        # Creating the help menu
        self.helpMenu = wx.Menu()
        self.abc = self.helpMenu.Append(ID_MENU_HELP_3141, "Visit Model 3141")
        self.helpMenu.Append(ID_MENU_HELP_3201, "Visit MCCI USB Switch 3201")
        self.helpMenu.Append(ID_MENU_HELP_2101, "Visit MCCI USB Switch 2101")
        self.helpMenu.Append(ID_MENU_HELP_2301, "Visit MCCI USB Switch 2301")
        self.helpMenu.AppendSeparator()
        self.helpMenu.Append(ID_MENU_HELP_WEB, "MCCI Website")
        self.helpMenu.Append(ID_MENU_HELP_PORT, "MCCI Support Portal")
        self.helpMenu.AppendSeparator()
        
        # MAC OS X
        if sys.platform == 'darwin':
            self.helpMenu.Append(wx.ID_ABOUT, "About Cricket")
        else:
            self.helpMenu.Append(ID_MENU_HELP_ABOUT, "About...")
        
        if sys.platform == 'darwin':
            self.winMenu = wx.Menu()
            self.winMenu.Append(ID_MENU_WIN_MIN, "&Minimize\tCtrl+M")
            self.winMenu.AppendCheckItem(ID_MENU_WIN_SHOW,
                                       "&Cricket\tAlt+Ctrl+1")
            self.winMenu.Check(ID_MENU_WIN_SHOW, True) 

        # Create menubar
        if sys.platform != 'darwin':
            self.menuBar.Append(self.fileMenu,    "&File")
        else:
            self.menuBar.Append(self.winMenu,    "&Window")
       
        self.menuBar.Append(self.configMenu, "&Config System")
        self.menuBar.Append(self.setMenu, "&Settings")
        self.menuBar.Append(self.comMenu,     "&MCCI USB Switch")
        self.menuBar.Append(self.volsAmps, "&VBUS V/I Monitor")
        self.menuBar.Append(self.helpMenu,    "&Help")

        # First we create a menubar object.
        self.SetMenuBar(self.menuBar)
        
        # set menubar
        self.menuBar = self.GetMenuBar()
        self.update_connect_menu(True)

        # Create the statusbar
        self.statusbar = MultiStatus(self)
        self.SetStatusBar(self.statusbar)
        self.UpdateAll(["Port", "", ""])
        
        # Set events to Menu
        # Self.Bind(wx.EVT_MENU, self.MenuHandler)
        self.Bind(wx.EVT_MENU, self.OnCloseWindow, id=ID_MENU_FILE_CLOSE)
        self.Bind(wx.EVT_MENU, self.OnSelectScc, id=ID_MENU_SET_SCC)
        self.Bind(wx.EVT_MENU, self.OnSelectThc, id=ID_MENU_SET_THC)

        self.Bind(wx.EVT_MENU, self.SelectUC, self.ucmenu)
        self.Bind(wx.EVT_MENU, self.SelectCC, self.ccmenu)
        self.Bind(wx.EVT_MENU, self.SelectHC, self.hcmenu)

        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_3141)
        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_3201)
        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_2101)
        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_2301)
        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_WEB)
        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_PORT)
        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnHideWindow, id=ID_MENU_WIN_MIN)
        self.Bind(wx.EVT_MENU, self.OnShowWindow, id=ID_MENU_WIN_SHOW)
        self.Bind(wx.EVT_MENU, self.OnConnect, id=ID_MENU_MODEL_CONNECT)
        self.Bind(wx.EVT_MENU, self.OnDisconnect, id=ID_MENU_MODEL_DISCONNECT)

        self.Bind(wx.EVT_CLOSE, self.OnAppClose)

        self.Bind(wx.EVT_MENU, self.OnConnectGraph, id = ID_MENU_GRAPH)
        EVT_RESULT(self, self.RunServerEvent)

        # Timer for monitor the connected devices
        self.timer_lp = wx.Timer(self)
        # Bind the timer event to handler
        self.Bind(wx.EVT_TIMER, self.DeviceMonitor, self.timer_lp)
        
        self.timer_auc = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.TriggerConnections, self.timer_auc)

        if sys.platform == 'darwin':
            self.Bind(wx.EVT_MENU, self.OnAboutWindow, id=wx.ID_ABOUT)
            self.Bind(wx.EVT_ICONIZE, self.OnIconize)
            self.Bind(wx.EVT_MENU, self.OnClose, id=wx.ID_EXIT)

        base = os.path.abspath(os.path.dirname(__file__))
        self.SetIcon(wx.Icon(base+"/icons/"+IMG_ICON))
        self.Show()
        
        td, usbList = getusb.scan_usb()
        self.save_usb_list(usbList)
        self.update_usb_status(td)
        self.print_on_log("Reading Configuration ...\n")

        try:
            self.LoadDevice()
            
        except:
            self.ldata['port'] = None
            self.ldata['device'] = None
            
            self.ldata['uc'] = True
            self.ldata['cc'] = True
            self.ldata['hc'] = True
            
            self.ldata['sccif'] = "network"
            self.ldata['sccid'] = "No host"
            self.ldata['sccpn'] = "2021"
            
            self.ldata['thcif'] = "network"
            self.ldata['thcid'] = "No host"
            self.ldata['thcpn'] = "2022"

            self.ldata['ssccif'] = "network"
            self.ldata['ssccpn'] = "2021"
            
            self.ldata['sthcif'] = "network"
            self.ldata['sthcpn'] = "2022"

        self.print_on_log("Loading Configuration\n")
        self.update_config_menu()
        self.update_settings_menu()
        self.timer_auc.Start(2000)

    def RunServerEvent(self, event):
        """
        serching the port event handling indicates 
        server is connecting that port
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: searching the event with server.
        Returns:
            None
        """
        if event.data is None:
            self.print_on_log("\nNo Server Event")
        else:
            if event.data == "search":
                self.print_on_log("\nSearch Event")
                self.dev_list.clear()
                self.dev_list = search.search_port(self.usbHand)
            else:
                self.print_on_log("\nUnknown Server Event")

    def auto_connect(self):
        """
        Do connect device automatically if the last connected device is 
        available

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        if(self.ldata['port'] != None and self.ldata['device'] != None):
            self.print_on_log("Auto connecting initiated ...\n")
            self.selPort = self.ldata['port']
            self.selDevice = self.ldata['device']
            self.stype = AUTO_CONNECT
            self.timer_auc.Start(500)
    
    def auto_connect_service(self):        
        if devControl.connect_device(self):
            self.device_connected()
        else:
            self.print_on_log("Auto connection failed\n")
                
    def update_config_menu(self):
        """
        update the Config system menu checked User compuer and 
        unchecked user computer menu.
        checked Control computer and uncheck control computer.
        checked test host computer and uncheck test host computer
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        test = 0x03
        if self.ldata['uc']:
            self.ucmenu.Check(True)
        else:
            self.ucmenu.Check(False)

        if self.ldata['cc']:
            self.ccmenu.Check(True)
        else:
            self.ccmenu.Check(False)

        if self.ldata['hc']:
            self.hcmenu.Check(True)
        else:
            self.hcmenu.Check(False)
    
    def OnClickHelp(self, event):
        """
        Virtual event handlers, overide them in your derived class
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: event handler for helpmenu
        Returns:
            None
        """
        id = event.GetId()
        if(id == ID_MENU_HELP_3141):
            webbrowser.open("https://mcci.com/usb/dev-tools/model-3141/",
                            new=0, autoraise=True)
        elif(id == ID_MENU_HELP_3201):
            webbrowser.open("https://mcci.com/usb/dev-tools/3201-enhanced"
                            "-type-c-connection-exerciser/",
                            new=0, autoraise=True)
        elif(id == ID_MENU_HELP_2101):
            webbrowser.open(
            "https://mcci.com/usb/dev-tools/2101-usb-connection-exerciser/",
                            new=0, autoraise=True)
        elif(id == ID_MENU_HELP_2301):
            webbrowser.open("https://mcci.com/usb/dev-tools/model-2301/",
                            new=0, autoraise=True)       
        elif(id == ID_MENU_HELP_WEB):
            webbrowser.open("https://mcci.com/", new=0, autoraise=True)
        elif(id == ID_MENU_HELP_PORT):
            webbrowser.open("https://portal.mcci.com/portal/home", new=0,
                            autoraise=True)
        elif(id == ID_MENU_HELP_ABOUT):
            self.OnAboutWindow(event)
    
    def UpdateStatusBar (self):
        """
        Update the device status in status bar, when connect/disconnect

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.statusbar.Refresh()
        self.statusbar.Update()
    
    def UpdateAll (self, textList):
        """
        Status bar update - All fields

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            textList: set the status bar
        Returns:
            None
        """
        for i in range(len(textList)):
            self.SetStatusText(textList[i], i)
        self.UpdateStatusBar()
    
    def UpdatePort (self):
        """
        Status bar update - Port number

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        if self.selDevice == DEV_2101:
            self.SetStatusText("USB", SB_PORT_ID)
        else:
            self.SetStatusText(self.selPort, SB_PORT_ID)
        self.UpdateStatusBar()
    
    def UpdateDevice (self):
        """
        Status bar update - Device(Model) Name

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.SetStatusText(DEVICES[self.selDevice], SB_DEV_ID)
        self.UpdateStatusBar()  
    
    def UpdateSingle(self, newStr, idx):
        """
        Status bar update - Any of One field

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            newStr: status updated in strings
            idx: update id
        Returns:
            None
        """
        self.SetStatusText(newStr, idx)
        self.UpdateStatusBar()
    
    def OnAboutWindow(self, event):
        """
        Virtual event handlers, overide them in your derived class
        About UI Software

        Args:
           self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event:event handler for about menu window
        Returns:
            None
        """
        dlg = AboutDialog(self, self)
        dlg.ShowModal()
        dlg.Destroy()
    
    def OnAppClose (self, event):
        """
        Virtual event handlers, overide them in your derived class
        for Mac Close

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event:event handler for Mac close
        Returns:
            None
        """
        self.terminateHcServer()
        self.terminateCcServer()
        self.Destroy()
    
    def OnCloseWindow (self, event):
        """
        Virtual event handlers, overide them in your derived class
        for Window Close

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event:event handler for window close
        Returns:
            None
        """ 
        # Close this window
        self.terminateHcServer()
        self.terminateCcServer()
        self.Close(True)
    
    def OnIconize (self, event):
        """
        Virtual event handlers, overide them in your derived classmenu

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: Event Handler for Menu
        Returns:
            None
        """
        # Close this window
        if self.IsIconized():
            self.winMenu.Check(ID_MENU_WIN_SHOW, False)
        else:
            self.winMenu.Check(ID_MENU_WIN_SHOW, True)
        event.Skip()
 
    def OnHideWindow (self, event):
        """
        Event Handler hide the window

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event:hide the win menu
        Returns:
            None
        """
        # Close this window
        self.winMenu.Check(ID_MENU_WIN_SHOW, False)
        self.Iconize(True)
    
    def OnShowWindow (self, event):
        """
        Event Handler for showing window

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event:show window
        Returns:
            None
        """
        # Close this window
        self.winMenu.Check(ID_MENU_WIN_SHOW, True)
        self.Iconize(False)

    def OnConnect (self, event):
        """
        click on Connect sub menu under the manage model menu, 
        shows the dialog box with connecting device.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: search and connect event.
        Returns:
            None
        """
        self.print_on_log("Search Devices ...\n")
        dlg = ComDialog(self, self)
        dlg.ShowModal()
        dlg.Destroy()

    def OnDisconnect (self, event):
        """
        click on disconnect menu the connecting device is disconnect.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: event handling on disconnect menu.
        Returns:
            None
        """
        self.device_no_response()
    
    def OnClose(self, event):
        """
        click on close application termiante
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: event handling on closing menu.
        Returns:
            None
        """

        self.terminateHcServer()
        self.terminateCcServer()
        wx.Exit()

    def OnConnectGraph(self, event):
        """
        click on volts and amps menu then open the menu with plot frame
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: event handling onconnect menu.
        Returns:
            None
        """
        self.vgraph = True
        self.agraph = True
        self.dlg = vbusChart.VbusChart(self, self)
        self.dlg.Show()
        
    def device_no_response(self):
        """
        once disconnect the device the connecting device is not responding.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.device_disconnected()
        self.selPort = None
        self.con_flg = False
        #self.devHand.close()
        devControl.disconnect_device(self)
        # Set label button name as Connect
        srlist = []
        srlist.append("Port")
        srlist.append("")
        srlist.append("")
        srlist.append("Disconnected")
        self.UpdateAll(srlist)
        # Print on logwindow
        self.print_on_log("MCCI USB Switch "+DEVICES[self.selDevice]
                              +" Disconnected!\n")
        self.update_connect_menu(True)
        self.set_mode(MODE_MANUAL)
        self.StoreDevice()
            
    def save_usb_list(self, mlist):
        """
        Keep USB device list in a list - reference list

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            mlist:save the list of file
        Returns:
            None
        """
        self.masterList = mlist[:]  
    
    def get_usb_list(self):
        """
        Get usb device list

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            masterList- Added or removed device list
        """
        return self.masterList
    
    def print_on_log(self, strin):
        """
        Show data in Log Window

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            strin: data in String format
        Returns:
            return None
        """
        self.panel.PrintLog(strin)
    
    def get_enum_delay(self):
        """
        Get USB device Enumeration delay

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            Enumeration delay in String format
        """
        return self.panel.get_enum_delay()
    
    def get_delay_status(self):
        """
        Get Checkbox status of USB Enumeration delay option

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            Boolean: True - if Checked, False - if unchecked
        """
        return self.panel.get_delay_status()
    
    def get_loop_param(self):
        """
        Get Loop Window delay parameters

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            Loop delay in String format
        """
        return self.panel.get_loop_param()
    
    def get_auto_param(self):
        """
        Get Auto Window delay parameters

        Args  
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            Auto Window paramaeter in String format
        """
        return self.panel.get_auto_param()
    
    def set_period(self, strval):
        """
        Set Loop Mode period

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            strval:string format update field
        Returns:
            None
        """
        self.panel.set_period(strval)
    
    def set_port_list(self, ports):
        """
        Set Port list for loop Window port selection

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            ports: port list updated
        Returns:
            None
        """
        self.panel.set_port_list(ports)
    
    def get_interval(self):
        """
        Get Auto mode time interval

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            Auto mode interval in String format
        """
        return self.panel.get_interval()
    
    def set_interval(self, strval):
        """
        Set Auto mode time interval when override by USB delay warning

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            strval:update the interval i string format
        Returns:
            None
        """
        self.panel.set_interval(strval)

    def set_mode(self, mode):
        """
        Called by Loop Window, Device Window and COM Window
        When Normal-Auto-Loop trasition

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            mode: set the mode in Modle device
        Returns:
            None
        """
        self.mode = mode
        self.panel.update_controls(mode)
    
    def disable_usb_scan(self):
        """
        Called by device window based on USB delay warning selection

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.panel.disable_usb_scan()

    def port_on(self, port, stat):
        """
        Port ON/OFF command from Loop Window

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            port:selecting the port
            stat:port status update
        Returns:
            None
        """
        self.panel.port_on(port, stat)
    
    def device_connected(self):
        """
        intervalCalled by COM Window when devide get connected

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.con_flg = True
        self.UpdatePort()
        # Device update info
        self.UpdateDevice()
        self.UpdateSingle("Connected", 3)
        # Print on logwindow
        self.print_on_log("MCCI USB Switch "+DEVICES[self.selDevice]
                                              +" Connected!\n")
       
        self.panel.device_connected()
        self.StoreDevice()
        self.update_connect_menu(False)
        self.set_mode(MODE_MANUAL)
        self.update_port_timer()

    def update_connect_menu(self, status):
        """
        Enabled the  manage model menubar.
        update the status first Connect menu in True state, 
        Disconnect menu Disable state.
        update the status device connect then disconnect menu enabled.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            status: update the status connect and 
            disconnect menu enable or disable state
        Returns:
            None
        """
        if status:
            self.menuBar.Enable(ID_MENU_MODEL_CONNECT, True)
            self.menuBar.Enable(ID_MENU_MODEL_DISCONNECT, False)
        else:
            self.menuBar.Enable(ID_MENU_MODEL_CONNECT, True)
            self.menuBar.Enable(ID_MENU_MODEL_DISCONNECT, True)

    def device_disconnected(self):
        """
        Called by COM Window when the device get disconnected

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.panel.device_disconnected()
        self.update_connect_menu(True)
    
    def update_usb_status(self, dl):
        """
        Update plugged USB device list in Status bar.
        Called by usbDev.py

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            d1:list updated
        Returns:
            None
        """
        strUsb = " USB Devices     Host Controller: {d1}     ".\
                 format(d1=str(dl[0])) + \
                 "Hub: {d2}     ".format(d2=str(dl[1])) + \
                 "Peripheral: {d3}".format(d3=str(dl[2]))
        
        self.UpdateSingle(strUsb, 4)

    def save_file (self, contents, extension):
        """
        Export the LogWindow/USBTreeWindow content to a file
        Called by LogWindow and USB Tree View Window

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns: 
            return- success for file save in directiry
        """
        # Save a file
        self.dirname=""
        dlg = wx.FileDialog(self, "Save as", self.dirname, "", extension, 
                            wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            wx.BeginBusyCursor()

            dirname = dlg.GetDirectory()
            filename = os.path.join(dirname, dlg.GetFilename())

            if (os.path.isdir(dirname) and os.access(dirname, os.X_OK | 
                                                     os.W_OK)):
                self.dirname = dirname
            try:
                f = open(filename, 'w')
                f.write(contents)
                f.close()
            except IOError:
                options = wx.OK | wx.ICON_ERROR
                dlg_error = wx.MessageDialog(self,
                                           "Error saving file\n\n" + strerror,
                                           "Error",
                                           options)
                dlg_error.ShowModal()
                dlg_error.Destroy()

        dlg.Destroy()

        if (wx.IsBusy()):
            wx.EndBusyCursor()
        return
    
    def StoreDevice(self):
        """
        Store the device configuration
        ings
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        # This is also a base class of shelve and it accepts
        # the filename as it’s parameter not a dict object like others. 
        # This is the base class of shelve which stores pickled object values 
        # in dict objects and string objects as key.

        lpath = self.get_user_data_dir()
        dpath = os.path.join(lpath, "MCCI", "Cricket")

        os.makedirs(dpath, exist_ok=True)
        fpath = os.path.join(dpath, "CricketSettings.txt")
        
        ds = shelve.open(fpath)
        ds['port'] = self.selPort
        ds['device'] = self.selDevice

        ds['uc'] = self.ldata['uc']
        ds['cc'] = self.ldata['cc']
        ds['hc'] = self.ldata['hc']

        ds['sccif'] = self.ldata['sccif']
        ds['sccid'] = self.ldata['sccid']
        ds['sccpn'] = self.ldata['sccpn']
 
        ds['ssccif'] = self.ldata['ssccif']
        ds['ssccpn'] = self.ldata['ssccpn']
        ds['sthcif'] = self.ldata['sthcif']
        ds['sthcpn'] = self.ldata['sthcpn']

        ds['thcif'] = self.ldata['thcif']
        ds['thcid'] = self.ldata['thcid']
        ds['thcpn'] = self.ldata['thcpn']
        ds.close()

    def OnSelectScc (self, event):
        """
        if User computer menu ISCHECKED , Switch control 
        computer act as SCC server
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: event handling on disconnect menu.
        Returns: event hanlding connecitng SCC menu
            None
        """
        dlg = None
        if self.ucmenu.IsChecked():
            dlg = SetDialog(self, self, "scc")
        else:
            dlg = PortDialog(self, self, "scc")

        dlg.ShowModal()
        dlg.Destroy()
        self.StoreDevice()

    def OnSelectThc (self, event):
        """
        if User computer menu ISCHECKED , Test host computer act as THC server
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: event handling on disconnect menu.
        Returns: event hanlding connecitng THC menu
            None
        """
        dlg = None
        if self.ucmenu.IsChecked():
            dlg = SetDialog(self, self, "thc")
        else:
            dlg = PortDialog(self, self, "thc")

        dlg.ShowModal()
        dlg.Destroy()
        self.StoreDevice()

    def SelectUC(self, event):
        """
        if select User computer menu ISCHECKED its act as User computer UI.
        if UNCHECKED Switching control computer and Test host computer,
        its automatically setting menu SCC, THC enabled.s
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: event handling on disconnect menu.
        Returns: event hanlding connecitng UC menu
            None
        """
        if self.ucmenu.IsChecked():
            self.ldata['uc'] = True
        else:
            self.ldata['uc'] = False
        self.StoreDevice()
        self.update_settings_menu()

    def SelectCC(self, event):
        """
        if select Switch control computer menu ISCHECKED its act as SCC server.
        if UNCHECKED User computer and Test host computer,
        its automatically setting menu SCC is enable THC is Disable
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: event handling on disconnect menu.
        Returns: event hanlding connecitng SCC menu
            None
        """
        if self.ccmenu.IsChecked():
            self.ldata['cc'] = True
        else:
            self.ldata['cc'] = False
        self.StoreDevice()
        self.update_settings_menu()

    def SelectHC(self, event):
        """
        if select Test host computer menu ISCHECKED its act as THC server.
        if UNCHECKED User computer and SCC computer,
        its automatically setting menu THC is enable SCC is Disable
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: event handling on disconnect menu.
        Returns: event hanlding connecitng THC menu
            None
        """
        if self.hcmenu.IsChecked():
            self.ldata['hc'] = True
        else:
            self.ldata['hc'] = False
        self.StoreDevice()
        self.update_settings_menu()

    def update_settings_menu(self):
        """
        if UC menu ISCHECKED and SCC menu ISCHECKED
         the Setting menu SCC is Disabled.
        if UC menu ISCHECKED and SCC menu UNCHECKED 
         the Setting menu SCC is enabled.
        if UC menu ISCHECKED and THC menu ISCHECKED
         the Setting menu THC is Disabled.
        if UC menu ISCHECKED and THC menu UNCHECKED 
        the Setting menu THC is enabled.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: event handling on disconnect menu.
        Returns: event hanlding connecitng SCC menu
            None
        """
        if self.ucmenu.IsChecked():
            if self.ccmenu.IsChecked():
                self.update_scc_menu(False)
            else:
                self.update_scc_menu(True)
            if self.hcmenu.IsChecked():
                self.update_thc_menu(False)
            else:
                self.update_thc_menu(True)
        else:
            if self.ccmenu.IsChecked():
                self.update_scc_menu(True)
            else:
                self.update_scc_menu(False)
            if self.hcmenu.IsChecked():
                self.update_thc_menu(True)
            else:
                self.update_thc_menu(False)

        self.update_manage_model(self.ucmenu.IsChecked())

        if self.ucmenu.IsChecked():
            self.panel.update_uc_panels()
        else:
            if self.ccmenu.IsChecked() or self.hcmenu.IsChecked():
                self.panel.update_server_panel()
                if self.ccmenu.IsChecked():
                    self.panel.update_cc_panels()
                if self.hcmenu.IsChecked():
                    self.panel.update_hc_panels()
            else:
                self.panel.remove_all_panels()

    def update_settings_menu_old(self):
        """
        if UC menu checked  and SCC menu unchecked the
         scc menu not checked then update setting SCC enabled.
        if UC menu ISCHECKED and THC menu ISCHECKED 
        the Setting menu THC is Disabled.
        if UC menu ISCHECKED and THC menu UNCHECKED
         the Setting menu THC is enabled.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns: 
            None
        """
        if self.ucmenu.IsChecked() and not self.ccmenu.IsChecked():
            self.update_scc_menu(True)
        else:
            self.update_scc_menu(False)

        if self.ucmenu.IsChecked() and not self.hcmenu.IsChecked():
            self.update_thc_menu(True)
        else:
            self.update_thc_menu(False)

        self.update_manage_model(self.ucmenu.IsChecked())

        if self.ucmenu.IsChecked():
            self.panel.update_uc_panels()
        else:
            if self.ccmenu.IsChecked() or self.hcmenu.IsChecked():
                self.panel.update_server_panel()
                if self.ccmenu.IsChecked():
                    self.panel.update_cc_panels()
                if self.hcmenu.IsChecked():
                    self.panel.update_hc_panels()
            else:
                self.panel.remove_all_panels()

    def update_scc_menu(self, status):
        """
        update the SCC menu either depends on status enabled or disabled.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: event handling on disconnect menu.
            status: either scc enable or scc disable
        Returns: 
            None
        """
        if status:
            self.menuBar.Enable(ID_MENU_SET_SCC, True)
        else:
            self.menuBar.Enable(ID_MENU_SET_SCC, False)

    def update_thc_menu(self, status):
        """
        update the THC menu either depends on status enabled or disabled.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: event handling on disconnect menu.
            status: either THC enable or THC disable
        Returns: 
            None
        """
        if status:
            self.menuBar.Enable(ID_MENU_SET_THC, True)
        else:
            self.menuBar.Enable(ID_MENU_SET_THC, False)
        
    def update_manage_model(self, status):
        """
        update the manage model menu, if User 
        computer is checked manage model enable.
        suppose UI run with server manage model is disable.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: event handling on disconnect menu.
            status: either scc enable or scc disable
        Returns: 
            None
        """
        if status:
            self.menuBar.EnableTop(3, True)
        else:
            self.menuBar.EnableTop(3, False)

    def LoadDevice(self):
        """
        load the device list for last device disconnect 
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """

        lpath = self.get_user_data_dir()
        dpath = os.path.join(lpath, "MCCI", "Cricket")

        os.makedirs(dpath, exist_ok=True)
        fpath = os.path.join(dpath, "CricketSettings.txt")
        
        ds = shelve.open(fpath)
        self.ldata['port'] = ds['port']
        self.ldata['device'] = ds['device']
        
        self.ldata['uc'] = ds['uc']
        self.ldata['cc'] = ds['cc']
        self.ldata['hc'] = ds['hc']
        
        self.ldata['sccif'] = ds['sccif']
        self.ldata['sccid'] = ds['sccid']
        self.ldata['sccpn'] = ds['sccpn']

        self.ldata['thcif'] = ds['thcif']
        self.ldata['thcid'] = ds['thcid']
        self.ldata['thcpn'] = ds['thcpn']

        self.ldata['ssccif'] = ds['ssccif']
        self.ldata['ssccpn'] = ds['ssccpn']

        self.ldata['sthcif'] = ds['sthcif']
        self.ldata['sthcpn'] = ds['sthcpn']

        ds.close()

    def startCcServer(self):
        """
        when Unchecked UC and THC menu, the SCC controlling the server
        once start the server control computer listening from UC client.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns: 
            None
        """
        if self.ccserver == None:
            self.ccserver = devServer.ServerCc("", int(self.ldata['ssccpn']))
            strin = "Control Computer Listening: "+self.ccserver.bind_addr
            self.panel.PrintLog(strin+"\n")
            
            self.listencc = devServer.StayAccept(self)
            self.listencc.start()

    def startHcServer(self):
        """
        when Unchecked UC and SCC menu, the THC controlling the server
        once start the server Test Host computer listening from UC client.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns: 
            None
        """
        if self.hcserver == None:
            self.hcserver = thServer.ServerHc("", int(self.ldata['sthcpn']))
            strin = "Host Computer Listening: "+self.hcserver.bind_addr
            self.panel.PrintLog(strin+"\n")
            
            self.listenhc = thServer.StayAccept(self)
            self.listenhc.start()

    def terminateHcServer(self):
        """
        suppose Clent is not listening HC server,
        host computer server is close the connection.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns: 
            None
        """
        if self.hcserver != None:  
            self.listenhc.close_connection()
            del self.listenhc
            self.listenhc = None
            self.hcserver.close()
            del self.hcserver
            self.hcserver = None

    def terminateCcServer(self):
        """
        suppose Clent is not listening CC server, control
        computer server is close the connection.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns: 
            None
        """
        if self.ccserver != None:  
            self.listencc.close_connection()
            del self.listencc
            self.listencc = None
            self.ccserver.close()
            del self.ccserver
            self.ccserver = None

    def update_port_timer(self):
        """
        updating the Port timer in all switching model
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns: 
            None
        """

        if self.ucmenu.IsChecked() and self.ccmenu.IsChecked():
            if(not self.timer_lp.IsRunning()):
                self.timer_lp.Start(700)
        else:
            self.timer_lp.Stop()

    def TriggerConnections(self, e):
        self.timer_auc.Stop()
        if self.stype == READ_CONFIG:
            devControl.SetDeviceControl(self)
            thControl.SetDeviceControl(self)
            if self.ldata['uc']:
                self.auto_connect()
        elif self.stype == AUTO_CONNECT:
            self.auto_connect_service()

    def DeviceMonitor(self, e):
        """
        updating the Disconnect window when plug out the Device
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            e:event assign with button
        Returns: 
            None
        """
        if self.ucmenu.IsChecked() and self.ccmenu.IsChecked():
            if self.con_flg:
                self.timer_lp.Stop()
                plist = search.check_port(self.usbHand)
                if self.selPort in plist:
                    self.timer_lp.Start(700)
                else:
                    self.con_flg = False
                    # Print the message
                    wx.MessageBox("MCCI USB Switch Disconnected !", "Port Error", wx.OK)
                    self.device_no_response()
                
    def get_user_data_dir(self):
        """
        getting usr directory path, code and installer executes in Local Path
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns: 
            dpath: local directory path
        """
        if sys.platform == "win32":
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
            dir_,_ = winreg.QueryValueEx(key, "Local AppData")
            dpath = Path(dir_).resolve(strict=False)
        elif sys.platform == "darwin":
            dpath = Path('~/Library/Application Support/').expanduser()
        else:
            dpath = Path(getenv('XDG_DATA_HOME', "~/.local/lib")).expanduser()
        return dpath

def EVT_RESULT(win, func):
    """
    event function window cant hang
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns: 
        None
    """
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func) 

class UiApp(wx.App):
    """
    UiApp wx.App object has been created in order to ensure 
    that the gui platform and wx Widgets have been fully initialized.
    """
    def OnInit (self):
        """
        Override OnInit to do applicaition initialization
        to ensure that the system, toolkit and wxWidgets are fully 
        initialized.

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            True - appilcation initialization
        """
        return True
    
    def CustInit(self):
        """
        Showing the title on UI frame with UI title name

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.frame = UiMainFrame(parent=None, title="MCCI - Cricket UI")
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)

def run():
    """
    Enty point of the application which initialise the UiApp Class
    
    Args: None
    Returns: None
    """
    app = UiApp()
    app.CustInit()
    app.MainLoop()