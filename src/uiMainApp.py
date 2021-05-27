##############################################################################
# 
# Module: uiMainApp.py
#
# Description:
#     Main Application body for the Model3201,Model3141 
#     and Model2101 GUI Application
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
#     V2.3.0 Wed April 28 2021 18:50:10 seenivasan
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

# Own modules
from uiGlobals import *
import dev3141Window
import dev3201Window
import dev2101Window
import dev2301Window
import loopWindow
import comWindow
import logWindow
import treeWindow
import autoWindow

import serialDev
import getusb

from aboutDialog import *
from comDialog import *

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
        self.SetStatusWidths([-1, -1, -3, -2, -8])

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
        self.comPan = comWindow.ComWindow(self, parent)
        self.treePan = treeWindow.UsbTreeWindow(self, parent)
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
        
        # Hide the dev3201Window and dev2101Window
        self.vboxdl.Hide(self.dev3201Pan)
        self.vboxdl.Hide(self.dev2101Pan)
        self.vboxdl.Hide(self.dev2301Pan)

        self.vboxl = wx.BoxSizer(wx.VERTICAL)
        self.vboxl.Add((0,20), 0, wx.EXPAND)
        self.vboxl.Add(self.hboxdl, 0 ,wx.ALIGN_LEFT | wx.EXPAND)
        self.vboxl.Add((0,10), 0, 0)
        self.vboxl.Add(self.logPan, 1, wx.EXPAND)
        self.vboxl.Add((0,20), 0, wx.EXPAND)

        self.vboxr = wx.BoxSizer(wx.VERTICAL)
        self.vboxr.Add((0,20), 0, wx.EXPAND)
        self.vboxr.Add(self.comPan, 0 ,wx.ALIGN_RIGHT | wx.EXPAND)
        #self.vboxr.Add((0,10), 0, 0)
        self.vboxr.Add(self.treePan, 1, wx.ALIGN_RIGHT | wx.EXPAND)
        self.vboxr.Add((0,20), 0, wx.EXPAND)

        self.vboxr.Hide(self.comPan)
        
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
    
    def print_on_usb(self, strin):
        """
        print usb device info on treewindow and Logwindow.

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            strin: String which contains list of devices with VID, PID and 
            Speed info
        Returns:
            None
        """
        self.treePan.print_on_usb(strin)
        if(self.logPan.is_usb_enabled()):
            self.logPan.print_on_log(strin+"\n")
    
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
        return self.treePan.get_enum_delay()
      
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
        return self.treePan.get_delay_status()
    
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
        self.treePan.disable_usb_scan()
    
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
        self.treePan.update_controls(mode)
    
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
                          size=wx.Size(1020,680))

        self.ytop = DEFAULT_YPOS
        if sys.platform == 'darwin':
            self.ytop = YPOS_MAC

        self.SetPosition((80,self.ytop))

        self.SetMinSize((1020,680))

        self.init_flg = True

        self.ldata = {}

        self.selPort = None
        self.selBaud = None
        self.selDevice = None

        self.devHand = serial.Serial()

        self.mode = MODE_MANUAL

        self.con_flg = False

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

        # Creating the help menu
        self.helpMenu = wx.Menu()
        self.helpMenu.Append(ID_MENU_HELP_3141, "Visit Model 3141")
        self.helpMenu.Append(ID_MENU_HELP_3201, "Visit Model 3201")
        self.helpMenu.Append(ID_MENU_HELP_2101, "Visit Model 2101")
        self.helpMenu.Append(ID_MENU_HELP_2301, "Visit Model 2301")
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
        self.menuBar.Append(self.comMenu,     "&Manage Model")
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

        if sys.platform == 'darwin':
            self.Bind(wx.EVT_MENU, self.OnAboutWindow, id=wx.ID_ABOUT)
            self.Bind(wx.EVT_ICONIZE, self.OnIconize)

        base = os.path.abspath(os.path.dirname(__file__))
        self.SetIcon(wx.Icon(base+"/icons/"+IMG_ICON))
        self.Show()
        
        td, usbList = getusb.scan_usb()
        self.save_usb_list(usbList)
        self.update_usb_status(td)

        try:
            self.LoadDevice()
            self.panel.auto_connect()
        except:
            pass
    
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
        dlg = ComDialog(self, self)
        dlg.ShowModal()
        dlg.Destroy()

    def OnDisconnect (self, event):
        self.device_disconnected()
        self.selPort = None
        self.con_flg = False
        self.devHand.close()
        # Set label button name as Connect
        srlist = []
        srlist.append("Port")
        srlist.append("")
        srlist.append("")
        srlist.append("Disconnected")
        self.UpdateAll(srlist)
        # Print on logwindow
        self.print_on_log("Model "+DEVICES[self.selDevice]
                              +" Disconnected!\n")
        self.menuBar.Enable(ID_MENU_MODEL_CONNECT, True)
        self.menuBar.Enable(ID_MENU_MODEL_DISCONNECT, False)    
    
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
    
    def print_on_usb(self, strin):
        """
        Show data in USB Device Tree View

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            strin: data in String format
        Returns:
            None
        """
        self.panel.print_on_usb(strin)
    
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
        self.panel.device_connected()
        self.StoreDevice()
        self.update_connect_menu(False)

    def update_connect_menu(self, status):
        if status:
            self.menuBar.Enable(ID_MENU_MODEL_CONNECT, True)
            self.menuBar.Enable(ID_MENU_MODEL_DISCONNECT, False)
        else:
            self.menuBar.Enable(ID_MENU_MODEL_CONNECT, False)
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
        ds = shelve.open('config.txt')
        ds['port'] = self.selPort
        ds['device'] = self.selDevice
        ds.close()
    
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
        # This is also a base class of shelve and it accepts
        # the filename as it’s parameter not a dict object like others. 
        # This is the base class of shelve which stores pickled object values 
        # in dict objects and string objects as key.
        ds = shelve.open('config.txt')
        self.ldata['port'] = ds['port']
        self.ldata['device'] = ds['device']
        ds.close()  

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
