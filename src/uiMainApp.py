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
#    V2.6.0 Wed Apr 20 2022 17:00:00   Seenivasan V
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

import getusb
import getTb
from copy import deepcopy

from aboutDialog import *
from comDialog import *
from setDialog import *
from portDialog import *
#from ccServer import *

# import panels
from uiPanel import *


import vbusChart

import devControl
import devServer

import thControl
import thServer

import search

import configdata

from cricketlib import searchswitch

from cricketlib import switch3141
from cricketlib import switch3201
from cricketlib import switch2101
from cricketlib import switch2301


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
        self.SetStatusWidths([-2, -2, -2, -2, -10])

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
                          size=wx.Size(980, 780))
        self.ytop = DEFAULT_YPOS
        if sys.platform == 'darwin':
            self.ytop = YPOS_MAC

        self.SetPosition((80,self.ytop))

        # self.SetMinSize((630, 710))
        # self.SetMaxSize((630, 710))
        self.CenterOnScreen()

        self.read_configs()
        self.declare_globals()        

        self.panel = UiPanel(self)
        self.darwin_dependent()
       
        self.build_menu_bar()
        self.build_config_menu()
        self.build_set_menu()
        self.build_com_menu()
        self.build_tool_menu()
        self.build_help_menu()
        #self.darwin_dependent()
        
        self.SetMenuBar(self.menuBar)
        # self.menuBar.EnableTop(4, False)
        
        self.menuBar = self.GetMenuBar()
        self.update_connect_menu(True)

        self.init_statusBar()

        self.define_events()
        EVT_RESULT(self, self.RunServerEvent)

        # Timer for monitor the connected devices
        self.timer_lp = wx.Timer(self)
        # Bind the timer event to handler
        self.Bind(wx.EVT_TIMER, self.DeviceMonitor, self.timer_lp)
        
        self.timer_auc = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.TriggerConnections, self.timer_auc)

        base = os.path.abspath(os.path.dirname(__file__))
        self.SetIcon(wx.Icon(base+"/icons/"+IMG_ICON))
        self.Show()

        self.init_usbTreeImage()
        
        self.print_on_log("Reading Configuration ...\n")

        config_data = configdata.read_all_config()
                
        self.action = 0
 
        self.print_on_log("Loading Configuration\n")
        
        self.update_config_menu()
        self.update_other_menu()

        self.Bind(wx.EVT_MENU_HIGHLIGHT, self.OnFocusSUT1, id=ID_MENU_SUT1)

        self.timer_auc.Start(2000)

    def init_usbTreeImage(self):
        # scan and save ThunderBolt USB device
        if sys.platform == "darwin":
            tbList = getTb.scan_tb()
            self.save_tb_list(tbList)
    
    def init_statusBar(self):
         # Create the statusbar
        self.statusbar = MultiStatus(self)
        self.SetStatusBar(self.statusbar)
        self.UpdateAll(["Port", "", ""])
    
    def darwin_dependent(self):
        if sys.platform == 'darwin':
            self.winMenu = wx.Menu()
            self.winMenu.Append(ID_MENU_WIN_MIN, "&Minimize\tCtrl+M")
            self.winMenu.AppendCheckItem(ID_MENU_WIN_SHOW,
                                       "&Cricket\tAlt+Ctrl+1")
            self.winMenu.Check(ID_MENU_WIN_SHOW, True) 

            self.Bind(wx.EVT_MENU, self.OnAboutWindow, id=wx.ID_ABOUT)
            self.Bind(wx.EVT_ICONIZE, self.OnIconize)
            self.Bind(wx.EVT_MENU, self.OnClose, id=wx.ID_EXIT)

    def build_config_menu(self):
        # config menu
        self.ucmenu = self.configMenu.Append(ID_MENU_CONFIG_UC, 
                            "User Computer", kind = ITEM_CHECK)
        self.ccmenu = self.configMenu.Append(ID_MENU_CONFIG_SCC, 
                            "Switch Control Computer", kind = ITEM_CHECK)
        self.hcmenu = self.configMenu.Append(ID_MENU_CONFIG_THC,
                            "Test Host Computer", kind = ITEM_CHECK)

    def build_set_menu(self):
        # Set Menu   
        self.setMenu.Append(ID_MENU_SET_SCC, "Switch Control Computer")
        self.setMenu.Append(ID_MENU_SET_THC, "Test Host Computer")
    
    def read_configs(self):
        self.config_data = configdata.read_all_config()
        
        self.myrole = self.config_data["myrole"]
        self.ucConfig = self.config_data["uc"]
        self.suts = self.config_data["sut"]
        self.ccConfig = self.config_data["cc"]
        self.thcConfig = self.config_data["thc"]

    def declare_globals(self):
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

        self.logserver = None
        self.logclient = None
        self.listenlog = None

        self.mode = MODE_MANUAL

        self.con_flg = False
        self.fault_flg = False
        self.vdata = None
        self.adata = None
        self.vgraph = False
        self.agraph = False

        self.stype = READ_CONFIG

        self.dev_list = []
        self.switch_list = []

        self.masterList = []
        self.tbMasterList = None

        self.handlers = {}
        self.swuidict ={}

        self.swobjmap = {"3141": switch3141.Switch3141, "3201": switch3201.Switch3201, 
                          "2101": switch2101.Switch2101, "2301": switch2301.Switch2301}

    def define_events(self):
        self.Bind(wx.EVT_MENU, self.OnCloseWindow, id=ID_MENU_FILE_CLOSE)
        self.Bind(wx.EVT_MENU, self.OnSelectScc, id=ID_MENU_SET_SCC)
        self.Bind(wx.EVT_MENU, self.OnSelectThc, id=ID_MENU_SET_THC)

        self.Bind(wx.EVT_MENU, self.UpdateConfig, self.ucmenu)
        self.Bind(wx.EVT_MENU, self.UpdateConfig, self.ccmenu)
        self.Bind(wx.EVT_MENU, self.UpdateConfig, self.hcmenu)

        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnHideWindow, id=ID_MENU_WIN_MIN)
        self.Bind(wx.EVT_MENU, self.OnShowWindow, id=ID_MENU_WIN_SHOW)
        self.Bind(wx.EVT_MENU, self.OnConnect, id=ID_MENU_MODEL_CONNECT)
        self.Bind(wx.EVT_MENU, self.OnDisconnect, id=ID_MENU_MODEL_DISCONNECT)

        self.Bind(wx.EVT_CLOSE, self.OnAppClose)

        self.Bind(wx.EVT_MENU, self.OnConnectGraph, id = ID_MENU_GRAPH)

    def OnFocusSUT1(self, event):
        print("\nOn Focus")

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
            self.usbHand.ready = True

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

    def update_slog_menu(self):
        if self.ucmenu.IsChecked() == True or self.ccmenu.IsChecked() == True:
            self.sl1menu.Check(self.suts["nodes"]["sut1"])
            self.sl2menu.Check(self.suts["nodes"]["sut2"])
            self.menuBar.Enable(ID_MENU_CONFIG_SL1, True)
            self.menuBar.Enable(ID_MENU_CONFIG_SL2, True)

        else:
            self.menuBar.Enable(ID_MENU_CONFIG_SL1, False)
            self.menuBar.Enable(ID_MENU_CONFIG_SL2, False)

    def build_menu_bar(self):
        self.menuBar = wx.MenuBar()

        self.configMenu = wx.Menu()
        self.comMenu = wx.Menu()
        self.setMenu = wx.Menu()
        self.toolMenu = wx.Menu()
        self.slogMenu = wx.Menu()
        self.helpMenu = wx.Menu()
        # self.toolMenu = wx.Menu()
        self.sutMenu = wx.Menu()
        
        # If its not darwin or MAC OS
        if sys.platform != 'darwin':
           # Setting up the menu.
           self.fileMenu = wx.Menu()
           # fileMenu.Append(ID_MENU_FILE_NEW,   "&New Window\tCtrl+N")
           self.fileMenu.Append(ID_MENU_FILE_CLOSE, "&Close \tAlt+F4")

        # Create menubar
        if sys.platform != 'darwin':
            self.menuBar.Append(self.fileMenu,    "&File")
        else:
            self.menuBar.Append(self.winMenu,    "&Window")
       
        self.menuBar.Append(self.configMenu, "&Config System")
        self.menuBar.Append(self.setMenu, "&Settings")
        self.menuBar.Append(self.comMenu,     "&MCCI USB Switch")

        self.menuBar.Append(self.toolMenu, "&Tools")

        # MAC OS X
        if sys.platform == 'darwin':
            self.helpMenu.Append(wx.ID_ABOUT, "About Cricket")
        else:
            self.helpMenu.Append(ID_MENU_HELP_ABOUT, "About...")
        
        self.menuBar.Append(self.helpMenu,    "&Help")

    
    def build_tool_menu(self):
        base = os.path.abspath(os.path.dirname(__file__))
        qmiamps = wx.MenuItem(self.toolMenu, ID_MENU_GRAPH, "VBUS V/I Plot")
        qmiamps.SetBitmap(wx.Bitmap(base+"/icons/"+IMG_WAVE))
        self.toolMenu.Append(qmiamps)

        self.sutMenuBar = wx.Menu()
        self.sutMenuBar.Append(ID_MENU_SUT1, "DUT Log Window-1", kind = ITEM_CHECK)
        self.sutMenuBar.Append(ID_MENU_SUT2, "DUT Log Window-2", kind = ITEM_CHECK)
        self.toolMenu.Append(wx.ID_ANY, "&DUT-Log", self.sutMenuBar)
        
        
        self.Bind(wx.EVT_MENU, self.SelectSUT, id=ID_MENU_SUT1)
        self.Bind(wx.EVT_MENU, self.SelectSUT, id=ID_MENU_SUT2)
        self.toolMenu.Enable(ID_MENU_GRAPH, False)

    # def increaseSize(self):
    #     self.Refresh()
    #     self.SetMaxSize((1200, 710))
    #     self.Layout()
        


    def SelectSUT(self, event):
        obj = event.GetEventObject()
        self.suts["nodes"]["sut1"] = True if obj.MenuItems[0].IsChecked() else False
        self.suts["nodes"]["sut2"] = True if obj.MenuItems[1].IsChecked() else False
        self.update_slog_panel()
        # self.increaseSize()

    def SelectSUT1(self):
        self.suts["nodes"]["sut1"] = True if self.sl1menu.IsChecked() else False
        self.suts["nodes"]["sut2"] = True if self.sl2menu.IsChecked() else False
        self.update_slog_panel()
    
    def SelectSUT2(self):
        self.suts["nodes"]["sut1"] = True if self.sl1menu.IsChecked() else False
        self.suts["nodes"]["sut2"] = True if self.sl2menu.IsChecked() else False
        self.update_slog_panel()

    def build_com_menu(self):
        self.comMenu.Append(ID_MENU_MODEL_CONNECT, "Connect")
        self.comMenu.Append(ID_MENU_MODEL_DISCONNECT, "Disconnect")
        
    def build_help_menu(self):
        # Creating the help menu
        self.abc = self.helpMenu.Append(ID_MENU_HELP_3141, "Visit MCCI USB Switch 3141")
        self.helpMenu.Append(ID_MENU_HELP_3201, "Visit MCCI USB Switch 3201")
        self.helpMenu.Append(ID_MENU_HELP_2101, "Visit MCCI USB Switch 2101")
        self.helpMenu.Append(ID_MENU_HELP_2301, "Visit MCCI USB Switch 2301")
        self.helpMenu.AppendSeparator()
        self.helpMenu.Append(ID_MENU_HELP_WEB, "MCCI Website")
        self.helpMenu.Append(ID_MENU_HELP_PORT, "MCCI Support Portal")
        self.helpMenu.AppendSeparator()

        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_3141)
        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_3201)
        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_2101)
        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_2301)
        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_WEB)
        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_PORT)

    def build_sut_menu(self):
        nodes = list(self.suts["nodes"].keys())
        
        sutnames = []
        for node in nodes:
            sutnames.append(self.suts[node]["name"])


        self.sl1menu = self.slogMenu.Append(ID_MENU_CONFIG_SL1, 
                            sutnames[0], kind = ITEM_CHECK)
        self.sl2menu = self.slogMenu.Append(ID_MENU_CONFIG_SL2, 
                            sutnames[1], kind = ITEM_CHECK)
        self.menuBar.Append(self.slogMenu, "&View ")  
    
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
        self.ucmenu.Check(self.myrole["uc"])
        self.ccmenu.Check(self.myrole["cc"])
        self.hcmenu.Check(self.myrole["thc"])

    
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
        self.saveMenus()
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
        self.saveMenus()
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
        wx.BeginBusyCursor()

        self.print_on_log("Search Switches ...\n")
        self.dev_list.clear()
        self.dev_list = searchswitch.get_switches()

        if (wx.IsBusy()):
            wx.EndBusyCursor()

        # self.dev_list = devControl.search_device(self)
        self.dev_list = self.dev_list["switches"]
        
        if(len(self.dev_list) > 1):
            self.print_on_log("Switches found ...\n")
            dlg = ComDialog(self, self)
            dlg.ShowModal()
            dlg.Destroy()
        elif(len(self.dev_list) == 1):
            self.print_on_log("Switch found ...\n")
            swname = self.dev_list[0]["model"]
            swid = self.dev_list[0]["port"]
            devControl.connect_device(self, {swname: swid})
            self.panel.add_switches(self.swuidict)
            self.update_loop_swselector()
            self.set_mode(MODE_MANUAL)
            self.print_on_log("Switch "+swname+" ("+swid+") connected!\n")
        else:
            self.print_on_log("No Switches found ...\n")
        self.Refresh()

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

        self.saveMenus()
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
    
    # Multiple Switches

    def add_switch_dialogs(self):
        swlist = []
        
        for idx in range(len(self.switch_list)):
            # nswlist.append(self.switch_list[idx].split('(')[0])
            swname = self.switch_list[idx].split('(')[0]
            swdict = {}
            swdict[swname] = self.switch_list[idx].split('(')[1][:-1]
            swlist.append(swdict)

        for swdict in swlist:
            devControl.connect_device(self, swdict)

        self.panel.add_switches(self.swuidict)
        self.update_loop_swselector()
        self.set_mode(MODE_MANUAL)

        self.Refresh()

    def add_switch_dialogs_batch(self, swDict):
        swlist = []

        swkeys = list(swDict.keys())

        for swkey in swkeys:
            swdict = {swDict[swkey] : swkey }
            swlist.append(swdict)

        for swdict in swlist:
            devControl.connect_device(self, swdict)

        self.panel.add_switches(self.swuidict)
        self.update_loop_swselector()
        self.set_mode(MODE_MANUAL)

        self.Refresh()

    def update_loop_swselector(self):
        # update selected switch list loop panel's switch selector
        self.panel.cpanel.autoPan.update_sw_selector(self.swuidict)
        self.panel.cpanel.loopPan.update_sw_selector(self.swuidict)

    
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

    def save_tb_list(self, mlist):
        self.tbMasterList = deepcopy(mlist)
        
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

    def get_tb_list(self):
        return self.tbMasterList
    
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
        self.con_flg = True
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

    def port_on(self, swkey, port, stat):
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
        self.panel.port_on(swkey, port, stat, len(self.swuidict))

    def set_speed(self, swkey, speed):
        self.panel.set_speed(swkey, speed)

    def read_param(self, swkey, param):
        self.panel.read_param(swkey, param)

    def get_usb_tree(self):
        try:
            thControl.get_tree_change(self)
        except:
            self.print_on_log("USB Read Error!")

    def compareReqSw(self, swDict, exist_sw):
        swkeys = list(swDict.keys())
        swvals = list(swDict.values())

        avail = {}
        for pair in exist_sw:
            avail[pair["port"]] = pair["model"]

        for port in swkeys:
            try:
                if swDict[port] != avail[port]:
                    return False
            except:
                return False
        return True
    
    def createBatchPanel(self, swDict):
        exist_sw = []
        try:
            exist_sw = self.dev_list
        except:
            exist_sw = []

        if len(exist_sw) < len(swDict):
            self.print_on_log("Batch Mode - Search Switches ...\n")
            self.SetCursor(wx.Cursor(wx.CURSOR_WAIT))
            self.dev_list.clear()
            self.dev_list = searchswitch.get_switches()
            self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
            try:
                self.dev_list = self.dev_list["switches"]
                if self.compareReqSw(swDict, self.dev_list):
                    self.add_switch_dialogs_batch(swDict)
                    return True
                else:
                    return False
            except:
                return False
        else:
            return True
    
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
        self.enable_graph_menu(True)

    def enable_graph_menu(self, status):
        if status == False:
            self.toolMenu.EnableTop(0, False)
        else:
            if DEVICES[self.selDevice] == "3141":
                self.toolMenu.EnableTop(0, False)
            elif DEVICES[self.selDevice] == "3201":
                self.toolMenu.EnableTop(0, True)
            elif DEVICES[self.selDevice] == "2101":
                self.toolMenu.EnableTop(0, False)
            elif DEVICES[self.selDevice] == "2301":
                self.toolMenu.EnableTop(0, True)
    
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
        self.enable_graph_menu(False)
    
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

        ds['sl1'] = self.ldata['sl1']
        ds['sl2'] = self.ldata['sl2']
        ds.close()

    def OnSelectScc (self, event):
        """
        if User computer menu ISCHECKED , Swicth control 
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
            dlg = PortDialog(self, self, {"cc": self.ccConfig})

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
            dlg = PortDialog(self, self, {"thc": self.thcConfig})

        dlg.ShowModal()
        dlg.Destroy()
        self.StoreDevice()


    def update_slog_panel(self):
        if self.ucmenu.IsChecked() or self.ccmenu.IsChecked():
            self.panel.update_slog_panel(self.suts)
        else:
            self.panel.update_slog_panel({})
        self.Refresh()
    
    def SelectSUTW1(self, event):
        self.suts["nodes"]["sut1"] = True if self.sl1menu.IsChecked() else False
        self.suts["nodes"]["sut2"] = True if self.sl2menu.IsChecked() else False
        self.update_slog_panel()
        
    def SelectSUTW2(self, event):
        self.suts["nodes"]["sut1"] = True if self.sl1menu.IsChecked() else False
        self.suts["nodes"]["sut2"] = True if self.sl2menu.IsChecked() else False
        self.update_slog_panel()
        
    def UpdateConfig(self, event):
        self.myrole["uc"] = True if self.ucmenu.IsChecked() else False
        self.myrole["cc"] = True if self.ccmenu.IsChecked() else False
        self.myrole["thc"] = True if self.hcmenu.IsChecked() else False

        self.update_other_menu()
        self.panel.update_panels(self.myrole, self.suts)

    def saveMenus(self):
        findict = {"myrole": self.myrole, "sut": {"nodes": self.suts["nodes"]}}
        configdata.set_base_config_data(findict)

    def derive_menu_stat(self):
        ccstat = False
        hcstat = False
        sutstat = False
        if(self.myrole["uc"]):
            if(not self.myrole["cc"]):
                ccstat = True
            if(not self.myrole["thc"]):
                hcstat = True
        else:
            ccstat = True
            hcstat = True
            
        if(self.myrole["uc"] or self.myrole["cc"]):
            sutstat = True
        return [ccstat, hcstat, sutstat]

    def update_other_menu(self):
        [ccstat, hcstat, sutstat] = self.derive_menu_stat()
        self.update_scc_menu(ccstat)
        self.update_thc_menu(hcstat)
        self.update_manage_model(self.myrole["uc"])

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
        pass

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

    def startLogServer(self):
        if self.logserver == None:
            self.logserver = logServer.ServerLog("", int(self.ldata['sthcpn']))
            strin = "Host Computer Listening: "+self.hcserver.bind_addr
            self.panel.PrintLog(strin+"\n")
            
            self.listenhc = thServer.StayAccept(self)
            self.listenhc.start()

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
            # if self.ldata['uc']:
            #     self.auto_connect()
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

    def WhenErrorOccurred(self):
        print("Error Occurred in Mainwindow")

    def action_reset(self):
        self.action = 0

    def action_count(self):
        self.action += 1
        return self.action

    def action_summary(self):
        self.print_on_log("Total match found : "+str(self.action)+"\n")

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