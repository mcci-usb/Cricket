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
#    V4.0.0 Wed May 25 2023 17:00:00   Seenivasan V
#       Module created
##############################################################################
# Lib imports
import wx
import serial
import webbrowser

# Built-in imports
import os
import sys
from sys import platform
from pathlib import Path
from os import getenv

from wx.core import ITEM_CHECK

# Own modules
from uiGlobals import *

import copy

from aboutDialog import *
from comDialog import *

from features.fwupdate import firmwareUpdate
from setDialog import *
from portDialog import *
from warningMessage import *
from networkingWindow import *
#from ccServer import *
import updateDialog as updtDlg

# import panels
from uiPanel import *


# import vbusChart
from features.viplot import vbusChart

import devControl
import devServer

import thControl
import thServer

import configdata

from cricketlib import searchswitch

from cricketlib import switch3141
from cricketlib import switch3201

from cricketlib import switch2101
from cricketlib import switch2301
from cricketlib import switch3142

from usbenum import usbenumall

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
                          VERSION_STR, pos=wx.Point(0,0),
                          size=wx.Size(0, 0))
        self.ytop = DEFAULT_YPOS
        if sys.platform == 'darwin':
            self.ytop = YPOS_MAC

        self.declare_globals()        
        self.read_configs()
        
        self.panel = UiPanel(self)
        self.darwin_dependent()
       
        self.build_menu_bar()
        self.build_config_menu()
        self.build_set_menu() 
        self.build_com_menu()
        self.build_tool_menu()
        self.build_help_menu()
        
        self.SetMenuBar(self.menuBar)
        
        self.menuBar = self.GetMenuBar()
        self.update_connect_menu(True)

        self.init_statusBar()

        self.define_events()
        
        base = os.path.abspath(os.path.dirname(__file__))
        self.SetIcon(wx.Icon(base+"/icons/"+IMG_ICON))
        self.Show()

        self.init_usbTreeImage()
        
        self.print_on_log("Reading Configuration ...\n")

        self.config_data = configdata.read_all_config()
                
        self.action = 0

        self.devHand = None
        self.dutLogWindow = None
 
        self.print_on_log("Loading Configuration\n")
        
        self.update_config_menu()
        self.update_other_menu()
        self.update_slog_menu()

        self.Bind(wx.EVT_MOVE, self.OnMove)

        self.init_right_panel()

        self.initScreenSize()

        self.init_connect()

        # Targetting for new release
        self.usbenum = usbenumall.create_usb_device_enumerator()
        if "msudp" not in self.config_data:
            self.config_data["msudp"] = {"uname": None, "pwd": None}
        mslogin = self.config_data["msudp"]
        self.usbenum.set_login_credentials(mslogin["uname"], mslogin["pwd"])
        
        # Check for the latest version
        update = updtDlg.check_version()
        if update != None:
            dlg = updtDlg.UpdateDialog(self, self, update)
            dlg.ShowModal()
            dlg.Destroy()
    
        self.load_config()
        EVT_RESULT(self, self.RunServerEvent)

        # Set up the layout
        # self.setup_layout()

    def load_config(self):
        # Load the configuration from config_data
        # This is a sample, replace it with your logic to load from the actual file
        self.panel.update_panels(self.myrole)
        if self.myrole["uc"] != True:
            if self.myrole["cc"] == True:
                self.startCcServer()
            if self.myrole["thc"] == True:
                self.startHcServer() 
        self.saveScreenSize()

    def init_usbTreeImage(self):
        """
        Initializes the USB tree image by scanning and saving 
        Thunderbolt USB devices.

        Notes:
            - This function is platform-specific, 
              designed for macOS (darwin).
            - It utilizes the getTb module to scan Thunderbolt USB devices.
            - The scanned Thunderbolt devices are saved for
              further use in the USB tree.
        """
        # scan and save ThunderBolt USB device
        # if sys.platform == "darwin":
        #     tbList = getTb.scan_tb()
        #     self.save_tb_list(tbList)
        pass
    
    def init_statusBar(self):
        """
        Initializes the status bar for the main application window.

       Notes:
            - The status bar is created using the MultiStatus class.
            - The initial status is set to display information about ports.
        """
         # Create the statusbar
        self.statusbar = MultiStatus(self)
        self.SetStatusBar(self.statusbar)
        self.UpdateAll(["Port", "", ""])
    
    def darwin_dependent(self):
        """
        Handles platform-specific setup and bindings for macOS (darwin).

        Notes:
            - Creates a specific menu for the macOS platform.
            - Binds menu items and events for macOS-specific functionality.

        Dependencies:
            - Requires the system module (sys).
            - Assumes the use of wxPython for GUI components.

        """
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
        """
        Builds and configures the settings menu for computer role selection.

        Notes:
            - Appends checkable items for User Computer (UC), Switch Control Computer (SCC),
            and Test Host Computer (THC) roles.
            - Disables all three menu items for single computer setup.

        Dependencies:
            - Assumes the use of wxPython for GUI components.

        """
        # config menu
        self.ucmenu = self.configMenu.Append(ID_MENU_CONFIG_UC, 
                            "User Computer", kind = ITEM_CHECK)
        self.ccmenu = self.configMenu.Append(ID_MENU_CONFIG_SCC, 
                            "Switch Control Computer", kind = ITEM_CHECK)
        self.hcmenu = self.configMenu.Append(ID_MENU_CONFIG_THC,
                            "Test Host Computer", kind = ITEM_CHECK)

        # Diable all the three menus for single computer setup
        self.menuBar.Enable(ID_MENU_CONFIG_UC, False)
        self.menuBar.Enable(ID_MENU_CONFIG_SCC, False)
        self.menuBar.Enable(ID_MENU_CONFIG_THC, False)
    
    def read_configs(self):
        """
        Reads and initializes the configuration data.

        Notes:
            - Assumes the existence of 'configdata' module for configuration management.
            - Uses 'myrole', 'uc', 'cc', 'thc', 'dut' keys in the configuration data.
            - Sets 'cerr_flg' to True if any of the mandatory keys are missing.

        Dependencies:
            - Assumes the use of 'configdata' module for configuration management.

        """
        mpkeys = ['myrole', 'uc', 'cc', 'thc', 'dut']
        self.config_data = configdata.read_all_config()
        klist = list(self.config_data.keys())
        cerr_flg = False
        for ikey in mpkeys:
            if ikey not in klist:
                cerr_flg = True
                break

        if cerr_flg != True:
            klist = list(self.config_data['dut'].keys())
            dutkeys = ['nodes', 'dut1', 'dut2']
            cerr_flg = False
            for ikey in dutkeys:
                if ikey not in klist:
                    cerr_flg = True
                    break
        if cerr_flg == True:
            self.config_data = configdata.load_default_config()
        
        try:
            self.myrole = self.config_data["myrole"]
            self.ucConfig = self.config_data["uc"]
            self.ccConfig = self.config_data["cc"]
            self.thcConfig = self.config_data["thc"]
            self.duts = self.config_data["dut"]
            self.wdialog = self.config_data["wdialog"]
        except:
            title = ("Configuration read error!")
            msg = ("The application would not work "
                    "as expected")
            dlg = wx.MessageDialog(self, msg, title, wx.OK)
            dlg.ShowModal()
 
    def declare_globals(self):
        """
        Initializes global variables.

        Notes:
            - Assumes the need for global variables 'init_flg' and 'ldata'.

        """
        self.init_flg = True

        self.ldata = {}

        self.devCtrl = None
        self.thCtrl = None

        self.wdialog = False
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
        self.ucbusy = True

        self.masterList = None
        self.tbMasterList = None

        self.handlers = {}
        self.swuidict ={}

        self.swobjmap = {"3141": switch3141.Switch3141,"3142": switch3142.Switch3142, "2101":switch2101.Switch2101, "3201": switch3201.Switch3201, "2301": switch2301.Switch2301}
        
        self.ldata['ssccif'] = "network"
        self.ldata['ssccpn'] = "2021"
        
        self.ldata['sthcif'] = "network"
        self.ldata['sthcpn'] = "2022"   
        
        
        
    def define_events(self):
        """
        Defines event bindings for menu items and controls.

        Notes:
            - Binds menu events for window closure and configuration updates.
            - Assumes the existence of specific menu item IDs: ID_MENU_FILE_CLOSE,
            ID_MENU_SET_SCC, ID_MENU_SET_THC, and corresponding configuration menus.

        """
        self.Bind(wx.EVT_MENU, self.OnCloseWindow, id=ID_MENU_FILE_CLOSE)
        self.Bind(wx.EVT_MENU, self.OnSelectScc, id=ID_MENU_SET_SCC)
        self.Bind(wx.EVT_MENU, self.OnSelectThc, id=ID_MENU_SET_THC)
        # self.Bind(wx.EVT_MENU, self.OnWarningWindow, id=ID_MENU_SET_WARNING)

        # self.Bind(wx.EVT_MENU, self.UpdateConfig, self.ucmenu)
        # self.Bind(wx.EVT_MENU, self.UpdateConfig, self.ccmenu)
        # self.Bind(wx.EVT_MENU, self.UpdateConfig, self.hcmenu)

        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnHideWindow, id=ID_MENU_WIN_MIN)
        self.Bind(wx.EVT_MENU, self.OnShowWindow, id=ID_MENU_WIN_SHOW)
        self.Bind(wx.EVT_MENU, self.OnConnect, id=ID_MENU_MODEL_CONNECT)
        # self.Bind(wx.EVT_MENU, self.OnDisconnect, id=ID_MENU_MODEL_DISCONNECT)

        self.Bind(wx.EVT_CLOSE, self.OnAppClose)

        self.Bind(wx.EVT_MENU, self.OnConnectGraph, id = ID_MENU_GRAPH)
        self.Bind(wx.EVT_MENU, self.OnFirmwareUpdateWindow, id = ID_3141_FIRMWARE)
        self.Bind(wx.EVT_MENU, self.OnNetworkWindow, id = ID_NETWORK_MENU)
       

    def init_connect(self):
        """
        Initializes device control for Switch Control and Test Host.
        
        Notes:
            - Associates device control with the main application.
            - Assumes the existence of `devControl` and `thControl` instances.
            Make sure they are appropriately defined and accessible.
            - Optionally initiates auto-connection for the User Computer role.

        """
        devControl.SetDeviceControl(self)
        thControl.SetDeviceControl(self)
        # if self.myrole["uc"] == True:
        #     self.auto_connect()
        
    
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
                self.print_on_log("\nUser Computer Searching The Devices")
                self.dev_list.clear()
                self.dev_list = searchswitch.get_switches()
                self.ucbusy = False
            else:
                self.print_on_log("\nUnknown Server Event")


    def auto_connect(self):
        """
        Automatically searches for switches and updates the device list.

        Notes:
            - Activates a busy cursor during the search process.
            - Prints the search progress to the application log.
            - Assumes the existence of `searchswitch` module for switch discovery.
            - Modifies the instance attribute `dev_list` with the updated list.
            - Ends the busy cursor upon completion of the search.

        """
        wx.BeginBusyCursor()

        self.print_on_log("Search Switches ...\n")
        self.dev_list.clear()
        self.dev_list = searchswitch.get_switches()

        if (wx.IsBusy()):
            wx.EndBusyCursor()

        self.dev_list = self.dev_list["switches"]

        if(len(self.dev_list) > 1):
            self.print_on_log("Many Switches found ...\n")
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

    def remove_switch(self, swname):
        self.panel.remove_switch(swname)
   
    def update_slog_menu(self):
        """
        Updates the status log menu based on the selected configuration.

        Notes:
            - Checks the selected role (UC or CC) to enable or disable specific menu items.
            - Reflects the state of DUT1, DUT2, and USB4 Tree View in the menu based on the configuration data.
            - Disables menu items when neither UC nor CC is selected.

        """
        if self.ucmenu.IsChecked() == True or self.ccmenu.IsChecked() == True:
            if "rpanel" in self.config_data:
                rpanel = self.config_data["rpanel"]
                self.dutMenuBar.Check(ID_MENU_DUT1, rpanel["dut1"] if "dut1" in rpanel else False)
                self.dutMenuBar.Check(ID_MENU_DUT2, rpanel["dut2"] if "dut2" in rpanel else False)
                self.toolMenu.Check(ID_USB4_TREEVIEW, rpanel["u4tree"] if "u4tree" in rpanel else False)
            else:
                rpanel = {"dut1": False, "dut2": False, "u4tree": False}
                self.config_data["rpanel"] = rpanel
                
                
        else:
            self.dutMenuBar.Enable(ID_MENU_DUT1, False)
            self.dutMenuBar.Enable(ID_MENU_DUT2, False)
            self.toolMenu.Check(ID_USB4_TREEVIEW, False)

    def build_menu_bar(self):
        """
        Builds the main menu bar for the application.

        Description:
            - Creates menus for configuration, communication, settings, tools, status log, and help.
            - Initializes the menu bar with these menus.

        """
        self.menuBar = wx.MenuBar()

        self.configMenu = wx.Menu()
        self.comMenu = wx.Menu()
        # self.setMenu = wx.Menu()
        self.netMenu = wx.Menu()
        self.toolMenu = wx.Menu()
        self.slogMenu = wx.Menu()
        self.helpMenu = wx.Menu()
         
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
        # self.menuBar.Append(self.setMenu, "&Settings")
        self.menuBar.Append(self.netMenu, "&Settings")
        self.menuBar.Append(self.comMenu,     "&MCCI USB Switch")

        self.menuBar.Append(self.toolMenu, "&Tools")

        # MAC OS X
        if sys.platform == 'darwin':
            self.helpMenu.Append(wx.ID_ABOUT, "About Cricket")
        else:
            self.helpMenu.Append(ID_MENU_HELP_ABOUT, "About...")
        
        self.menuBar.Append(self.helpMenu,    "&Help")
    
    def build_set_menu(self):
        self.Nmenu = wx.MenuItem(self.netMenu, ID_NETWORK_MENU, "Configurations")
        self.netMenu.Append(self.Nmenu)

    
    def build_tool_menu(self):
        """
        Builds the tools menu for the application.

        Description:
            - Creates menu items for various tools, such as VBUS V/I Plot and 3141-3142 firmware update.
            - Associates icons with specific tools for visual identification.

        """
        base = os.path.abspath(os.path.dirname(__file__))
        qmiamps = wx.MenuItem(self.toolMenu, ID_MENU_GRAPH, "VBUS V/I Plot")
        qmiamps.SetBitmap(wx.Bitmap(base+"/icons/"+IMG_WAVE))
        self.toolMenu.Append(qmiamps)

        self.fware = wx.MenuItem(self.toolMenu, ID_3141_FIRMWARE, "Model 3141/3142 Firmware Update")
        self.toolMenu.Append(self.fware)

        self.dutMenuBar = wx.Menu()
        self.dutMenuBar.Append(ID_MENU_DUT1, "DUT Log Window-1", kind = ITEM_CHECK)
        self.dutMenuBar.Append(ID_MENU_DUT2, "DUT Log Window-2", kind = ITEM_CHECK)
        self.toolMenu.Append(wx.ID_ANY, "&DUT-Log", self.dutMenuBar)
        
        self.usb4t = wx.MenuItem(self.toolMenu, ID_USB4_TREEVIEW, "USB4 Tree View", kind = ITEM_CHECK)
        self.toolMenu.Append(self.usb4t)
        
        
        self.Bind(wx.EVT_MENU, self.SelectDUT, id=ID_MENU_DUT1)
        self.Bind(wx.EVT_MENU, self.SelectDUT, id=ID_MENU_DUT2)
        self.Bind(wx.EVT_MENU, self.SelectU4TREE, id=ID_USB4_TREEVIEW)
        self.toolMenu.Enable(ID_MENU_GRAPH, True)

    def OnMove(self, e):
        x, y = e.GetPosition()
        w, h = wx.DisplaySize()
        sw = self.Size[0]
        sh = self.Size[1]
        self.saveScreenSize()

    def initScreenSize(self):
       
        dw, dh = wx.DisplaySize()
        opos = self.config_data["screen"]["pos"]
        osize = self.config_data["screen"]["size"]
        if len(opos) == 0 and len(osize) == 0:
            # Initialization
            self.SetSize(SCREEN_WIDTH, SCREEN_HEIGHT)
            self.CenterOnScreen()
        else:
            self.SetPosition((opos[0], opos[1]))
            self.SetSize((osize[0], osize[1]))

    def saveScreenSize(self):
        
        px, py = self.GetPosition()
        sw, sh = self.GetSize()
        findict = {"screen": {"pos": [px, py], "size": [sw, sh]}}
        configdata.updt_screen_size(findict)

    def reSizeScreen(self):
       
        w, h = wx.DisplaySize()

        dw = int(w * 0.97)
        dh = int(h * 0.95)

        sw = self.Size[0]
        sh = self.Size[1]

        reqwidth = 950
        # if self.duts["nodes"]["dut1"] == True or self.duts["nodes"]["dut2"]:
        if self.config_data["rpanel"]["dut1"] or self.config_data["rpanel"]["dut2"] or self.config_data["rpanel"]["u4tree"]:
        # if self.config_data["myrole"]["cc"]:
            # pass
            reqwidth = 1420
            if sw < reqwidth:
                self.SetSize((reqwidth, dh))
        else:
            self.SetSize((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.CenterOnScreen()
        self.Layout()

        self.saveScreenSize()
    
    def serverResizerScreen(self):
        w, h = wx.DisplaySize()

        dw = int(w * 0.97)
        dh = int(h * 0.95)

        sw = self.Size[0]
        sh = self.Size[1]

        reqwidth = 550
        # if self.duts["nodes"]["dut1"] == True or self.duts["nodes"]["dut2"]:
        if self.config_data["myrole"]["uc"] == False:
            reqwidth = 550
            if sw < reqwidth:
                self.SetSize((reqwidth, dh))
        else:
            self.SetSize((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.CenterOnScreen()
        self.Layout()

        self.saveScreenSize()
        

    def SelectDUT(self, event):
        """
        Handle the event triggered by selecting DUT options in the menu.

        Description:
            - Prints a message indicating the Uima trigger to add DUT.
            - Retrieves the event object.
            - Updates DUT configurations based on menu item checks.
            - Updates the right panel and resizes the screen accordingly.

        Parameters:
            event (wx.Event): The event object representing the menu selection.

        """
        obj = event.GetEventObject()
        
        # self.duts["nodes"]["dut1"] = True if obj.MenuItems[0].IsChecked() else False
        # self.duts["nodes"]["dut2"] = True if obj.MenuItems[1].IsChecked() else False
        self.config_data["rpanel"]["dut1"] = True if obj.MenuItems[0].IsChecked() else False
        self.config_data["rpanel"]["dut2"] = True if obj.MenuItems[1].IsChecked() else False

        self.update_right_panel()
        self.reSizeScreen()
        
        # if not self.dutLogWindow.IsShown():
        #     obj.MenuItems[0].Check(False)
        #     obj.MenuItems[1].Check(False)

    def SelectU4TREE(self, event):
        """
        Handle the event triggered by selecting the USB4 Tree View option in the menu.

        Description:
            - Prints a message indicating the UIMP trigger to add/remove USB4 Tree View.
            - Retrieves the event object.
            - Updates USB4 Tree View configuration based on the menu item check.
            - Updates the right panel and resizes the screen accordingly.

        Parameters:
            event (wx.Event): The event object representing the menu selection.

        """
        obj = event.GetEventObject()
        
        # self.duts["nodes"]["dut1"] = True if obj.MenuItems[0].IsChecked() else False
        # self.duts["nodes"]["dut2"] = True if obj.MenuItems[1].IsChecked() else False
        self.config_data["rpanel"]["u4tree"] = True if self.usb4t.IsChecked() else False
        
        self.update_right_panel()
        self.reSizeScreen()

    def updt_dut_config(self, dutdict):
        """
        Update the DUT configuration based on the provided dictionary.

        Description:
            - Extracts the DUT key from the dictionary.
            - Iterates through the nested keys in the DUT dictionary.
            - Updates the corresponding values in the application's DUT configuration.

        Parameters:
            dutdict (dict): A dictionary containing DUT configuration information.

        """
        key = list(dutdict.keys())[0]
        nkeys = list(dutdict[key].keys())
        for nkey in nkeys:
            self.duts[key][nkey] = dutdict[key][nkey]

    def get_dut_config(self, dutno):
        """
        Get the DUT configuration for a specific DUT.

        Description:
            - Retrieves and returns the DUT configuration for the specified DUT number.

        Parameters:
            dutno (str): The DUT number for which to retrieve the configuration.

        Returns:
            dict: A dictionary containing the configuration for the specified DUT.
        """
        return {dutno: self.duts[dutno]}
    
    def request_dut_close(self, dutname):
        """
        Request to close a specific DUT.

        Description:
            - Updates the configuration data to mark the specified DUT as closed.
            - Updates the DUT-related menu items and the right panel.
            - Resizes the screen accordingly.

        Parameters:
            dutname (str): The name or identifier of the DUT to be closed.
        """
        self.config_data["dut"]["nodes"][dutname] = False
        self.config_data["rpanel"][dutname] = False
        self.update_slog_menu()
        self.update_right_panel()
        self.reSizeScreen()

    def build_com_menu(self):
        """
        Build the communication menu.

        Description:
            - Appends menu items for connecting and disconnecting models.

        Menu Items:
            - "Connect": ID_MENU_MODEL_CONNECT
            - "Disconnect": ID_MENU_MODEL_DISCONNECT
        """
        self.comMenu.Append(ID_MENU_MODEL_CONNECT, "Connect")
        # self.comMenu.Append(ID_MENU_MODEL_DISCONNECT, "Disconnect")
        
    def build_help_menu(self):
        """
        Build the help menu.

        Description:
            - Appends menu items to visit different MCCI USB Switch models.
        """
        # Creating the help menu
        self.abc = self.helpMenu.Append(ID_MENU_HELP_3141, "Visit MCCI USB Switch 3141")
        self.helpMenu.Append(ID_MENU_HELP_3142, "Visit MCCI USB Switch 3142")
        self.helpMenu.Append(ID_MENU_HELP_3201, "Visit MCCI USB Switch 3201")
        self.helpMenu.Append(ID_MENU_HELP_2101, "Visit MCCI USB Switch 2101")
        self.helpMenu.Append(ID_MENU_HELP_2301, "Visit MCCI USB Switch 2301")
        self.helpMenu.AppendSeparator()
        self.helpMenu.Append(ID_MENU_HELP_WEB, "MCCI Website")
        self.helpMenu.Append(ID_MENU_HELP_PORT, "MCCI Support Portal")
        self.helpMenu.AppendSeparator()

        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_3141)
        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_3142)
        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_3201)
        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_2101)
        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_2301)
        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_WEB)
        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_PORT)

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
        elif(id == ID_MENU_HELP_3142):
            webbrowser.open("https://store.mcci.com/collections/usb-switches/products/model3142",
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
        
    def OnNetworkWindow(self, event):
        dlg = NetConfigDialog(self, self.myrole)
        dlg.ShowModal()
        dlg.Destroy()
        self.read_configs()
        self.panel.update_panels(self.myrole)
        self.serverResizerScreen()
        self.CenterOnScreen()
        self.Refresh()
    
    

    def OnFirmwareUpdateWindow(self, event):
        """
        Handle the event triggered by selecting the firmware update option in the menu.

        Description:
            - Initializes and shows the firmware update dialog.
            - Destroys the dialog after it is closed.

        Parameters:
            event (wx.Event): The event object representing the menu selection.
        """

        dlg = firmwareUpdate.FirmwareDialog(self, self)
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
        self.dev_list = devControl.search_device(self)

        if (wx.IsBusy()):
            wx.EndBusyCursor()

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

        if not self.wdialog:
            self.show_warning_dlg()

    def disconnect_device(self, swport):
        devControl.disconnect_device(self, swport)
        
    # def OnDisconnect (self, event):
    #     """
    #     click on disconnect menu the connecting device is disconnect.
    #     Args:
    #         self: The self parameter is a reference to the current 
    #         instance of the class,and is used to access variables
    #         that belongs to the class.
    #         event: event handling on disconnect menu.
    #     Returns:
    #         None
    #     """
    #     self.device_no_response()
    
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
    
    # Multiple Switches
    def add_switch_dialogs(self):
        """
        Adds switch dialogs.

        Description:
            - Iterates through the switch list.
            - Extracts the switch name and port information from each item in the list.
            - Appends a dictionary containing the switch name and port information to the swlist.

        Returns:
            list: A list of dictionaries, each containing the switch name and port information.
        """
        swlist = []
        
        for idx in range(len(self.switch_list)):
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
        self.device_connected()

    def add_switch_dialogs_batch(self, swDict):
        """
        Adds switch dialogs in batch.

        Description:
            - Iterates through the switch dictionary.
            - Creates a dictionary with switch name as the value and switch key as the key.
            - Appends the created dictionary to the swlist.

        Parameters:
            swDict (dict): A dictionary containing switch information.

        Returns:
            list: A list of dictionaries, each containing the switch name and corresponding switch key.
        """
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
        """
        Updates the switch selector in the loop panel.

        Description:
            - Calls the update_sw_selector method for both the autoPan and loopPan components.

        """
        # update selected switch list loop panel's switch selector
        self.panel.cpanel.autoPan.update_sw_selector(self.swuidict)
        self.panel.cpanel.loopPan.update_sw_selector(self.swuidict)
        # self.panel.lpanel.update_sw_selector(self.swuidict)
    
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
        """
        Saves the ThunderBolt device list.

        Parameters:
            mlist (list): The ThunderBolt device list to be saved.

        """
        self.tbMasterList = copy.deepcopy(mlist)
        
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
        """
        Returns the saved ThunderBolt device list.

        Returns:
            list: The ThunderBolt device list.

        """
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

    def store_usb4_win_info(self, usb4dict):
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
        
        self.panel.update_usb4_tree(usb4dict)
        # pass
    
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
    
    def set_loop_param(self, onTime, offTime):
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
        self.panel.set_loop_param(onTime, offTime)
    
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
        """
        Sets the speed for a specific switch.

        Parameters:
            swkey (str): The key or identifier of the switch.
            speed (int): The speed to be set for the switch.

        """
        self.panel.set_speed(swkey, speed)

    def read_param(self, swkey, param):
        """
        Reads a specific parameter for a switch.

        Parameters:
            swkey (str): The key or identifier of the switch.
            param (str): The parameter to be read.

        """
        self.panel.read_param(swkey, param)

    def open_com_port(self, param):
        """
        Opens a communication port based on the specified parameters.

        Parameters:
            param (str): A string containing the necessary parameters for opening the port,
            separated by commas. The parameters include port, baudrate, and more.

        """
        inparam = param.split(',')
        self.devHand = serial.Serial()
        self.devHand.port = inparam[0]
        self.devHand.baudrate = int(inparam[1])
        self.devHand.bytesize = int(inparam[3])
        self.devHand.parity = serial.PARITY_NONE
        self.devHand.timeout = 0
        self.devHand.stopbits = serial. STOPBITS_ONE

        try:
            self.devHand.open()
        except:
            self.panel.PrintLog("Port Open Fail\n")
    
    def write_serial(self, param):
        """
        Writes data to the opened serial port.

        Parameters:
            param (str): The data to be written to the serial port.

        """
        try:
            param = param + '\r\n'
            self.devHand.write(param.encode())
        except serial.SerialException as e:
            pass
    
    def read_serial(self, param):
        """
        Reads data from the opened serial port and compares it with the given parameter.

        Parameters:
            param (str): The expected data to be received from the serial port.

        Returns:
            bool: True if the received data matches the expected parameter, False otherwise.

        """
        try:
            rxdata = self.devHand.readline()
            try:
                rxdata = rxdata.rstrip().decode('utf-8')
            except:
                self.panel.PrintLog("Serial Parsing Error\n")
                return False
            if(rxdata == param):
                self.panel.PrintLog("Serial Loop Success\n")
                return True
            else:
                self.panel.PrintLog("Serial Loop failed\n")
                return False
        except serial.SerialException as e:
            return False

    def compareReqSw(self, swDict, exist_sw):
        """
        Compares the requested switch configuration with the existing switch configuration.

        Parameters:
            sw_dict (dict): The dictionary representing the requested switch configuration.
            exist_sw (list): The list of dictionaries representing the existing switch configuration.

        Returns:
            bool: True if the requested switch configuration matches the existing switch configuration, False otherwise.

        """
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
        """
        Creates a batch panel based on the requested switch configuration.

        Parameters:
            sw_dict (dict): The dictionary representing the requested switch configuration.

        Returns:
            bool: True if the batch panel is successfully created, False otherwise.

        """
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
        self.enable_graph_menu()
        self.set_mode(MODE_MANUAL)
        # self.panel.device_connected()

    def enable_graph_menu(self):
        """
        Enables the VBUS V/I Plot menu based on the connected devices.

        """
        cdevices =  list(self.swuidict.values())
        if len(cdevices) > 0:
            self.set_mode(MODE_MANUAL)
            if '3142' in cdevices:
                self.toolMenu.Enable(ID_MENU_GRAPH, True)
            elif '2301' in cdevices:
                self.toolMenu.Enable(ID_MENU_GRAPH, True)
            elif '3201' in cdevices:
                self.toolMenu.Enable(ID_MENU_GRAPH, True)
            else:
                self.toolMenu.Enable(ID_MENU_GRAPH, True)

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
            # self.menuBar.Enable(ID_MENU_MODEL_DISCONNECT, True)
        else:
            self.menuBar.Enable(ID_MENU_MODEL_CONNECT, True)
            # self.menuBar.Enable(ID_MENU_MODEL_DISCONNECT, True)

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
        self.enable_graph_menu()
    
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
                 format(d1=str(dl["host"])) + \
                 "Hub: {d2}     ".format(d2=str(dl["hub"])) + \
                 "Peripheral: {d3}".format(d3=str(dl["peri"]))
        
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
        # This function was removed
        # Shelve related to store the config data
        # We have replaced the shelve with the JSON based config file
        pass

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
    
    def init_right_panel(self):
        """
        Initializes the right panel with configuration data.

        """
        pdict = {"rpanel": self.config_data["rpanel"], "dut": self.config_data["dut"]}
        self.panel.init_right_panel(pdict)

    def update_right_panel(self):
        """
        Updates the right panel based on the configuration data.

        """
        if self.ucmenu.IsChecked() or self.ccmenu.IsChecked():
            pdict = {"rpanel": self.config_data["rpanel"], "dut": self.config_data["dut"]}
        else:
            pdict = {"rpanel": {"dut1": True, "dut2": True, "u4tree": True}, "dut": {}}
        self.panel.update_right_panel(pdict)
        self.Refresh()

    def saveMenus(self):
        """
        Saves the menu configurations and screen size.

        """
        findict = {"myrole": self.myrole, "dut": {"nodes": self.duts["nodes"]}, "rpanel": self.config_data["rpanel"]}
        configdata.set_base_config_data(findict)
        self.saveScreenSize()

    def derive_menu_stat(self):
        """
        Derives the status of the config, switch control, and test host menus based on the current role.

        Returns:
            list: A list containing boolean values indicating the status of the config, switch control, and test host menus.

        """
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
        """
        Updates the config, switch control, and test host menus based on the current role.

        """
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
        pass
        # if status:
        #     self.menuBar.Enable(ID_MENU_SET_SCC, True)
        # else:
        #     pass
            # self.menuBar.Enable(ID_MENU_SET_SCC, False)

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
        pass
        # if status:
        #     self.menuBar.Enable(ID_MENU_SET_THC, True)
        # else:
        #     pass
            # self.menuBar.Enable(ID_MENU_SET_THC, False)
        
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
        #  Shelve related config storage function
        #  Replaced with JSON based config file
        #  So this function was removed
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
            ccport = self.ccConfig["tcp"]["port"]
            self.ccserver = devServer.ServerCc("", int(ccport))
            strin = "Control Computer Listening: "+self.ccserver.bind_addr
            # self.ccserver = devServer.ServerCc("", 2021)
            # strin = "Control Computer Listening: 192.168.76.23"
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
            thcport = self.thcConfig["tcp"]["port"]
            self.hcserver = thServer.ServerHc("", int(thcport))
            # self.hcserver = thServer.ServerHc("", 2022)
            strin = "Host Computer Listening: "+self.hcserver.bind_addr
            # strin = "Host Computer Listening: 192.168.76.23"
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

    def action_reset(self):
        """
        Resets the action counter to zero.

        """
        self.action = 0

    def action_count(self):
        """
        Increments the action counter and returns the updated count.

        Returns:
            int: The updated action count.

        """
        self.action += 1
        return self.action

    def action_summary(self):
        """
        Prints a summary message indicating the total number of matches found.

        """
        self.print_on_log("Total match found : "+str(self.action)+"\n")

    def get_batch_location(self):
        """
        Returns the batch location from the configuration data.

        Returns:
            str: The batch location.

        """
        return self.config_data["batch"]["location"]

    def show_warning_dlg(self):
        """
        Displays the warning dialog.

        """
        dlg = WarningDialog(self, self)
        dlg.ShowModal()
        dlg.Destroy()
    
    def show_warning_dlg_new(self):
        """
        Displays a simple warning message box.

        """
        # warning dialog
        wx.MessageBox('Operation could not be completed', 'Warning', wx.OK | wx.ICON_INFORMATION)


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