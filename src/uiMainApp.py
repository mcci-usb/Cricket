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
#     V2.0.0 Fri Jan 15 2021 18:50:59 seenivasan
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
import loopWindow
import comWindow
import logWindow
import treeWindow
import autoWindow

import serialDev
import getusb

from aboutDialog import *

##############################################################################
# Utilities
##############################################################################
"""
A class Multistatus with init method
This code pattern is run common in all Python files that
to be executed as a script imported in another modules.
"""
class MultiStatus (wx.StatusBar):
    """
    Associates a status bar with the frame.
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        parent: Pointer to a parent window.
    Returns:
        return None
    """
    def __init__ (self, parent):
        wx.StatusBar.__init__(self, parent, -1)
        # Sets the number of field count "5"
        self.SetFieldsCount(5)
        # Sets the widths of the fields in the status bar.
        self.SetStatusWidths([-1, -1, -3, -2, -8])
"""
A class UiPanel with init method
the UiPanel navigate to UIApp name
"""
class UiPanel(wx.Panel):
    """
    Uipanel created
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        parent: Pointer to a parent window.
    Returns:
        return None
    """
    def __init__(self, parent):
        super(UiPanel, self).__init__(parent)

        wx.GetApp().SetAppName("Cricket")

        self.parent = parent
        # set back ground colour White
        self.SetBackgroundColour('White')

        self.font_size = DEFAULT_FONT_SIZE

        # MAC OS X
        if platform == "darwin":
            self.font_size = MAC_FONT_SIZE
        # Stes the font for this window
        self.SetFont(wx.Font(self.font_size, wx.SWISS, wx.NORMAL, wx.NORMAL,\
                             False,'MS Shell Dlg 2'))

        self.logPan = logWindow.LogWindow(self, parent)
        self.loopPan = loopWindow.LoopWindow(self, parent)
        self.comPan = comWindow.ComWindow(self, parent)
        self.treePan = treeWindow.UsbTreeWindow(self, parent)
        self.autoPan = autoWindow.AutoWindow(self, parent)
        
        self.dev3141Pan = dev3141Window.Dev3141Window(self, parent)
        self.dev3201Pan = dev3201Window.Dev3201Window(self, parent)
        self.dev2101Pan = dev2101Window.Dev2101Window(self, parent)

        self.devObj = []
        # device panel added
        self.devObj.append(self.dev3141Pan)
        self.devObj.append(self.dev3201Pan)
        self.devObj.append(self.dev2101Pan)
        # Creating Sizers
        self.vboxdl = wx.BoxSizer(wx.VERTICAL)
        self.vboxdl.Add(self.dev3141Pan, 0, wx.EXPAND)
        self.vboxdl.Add(self.dev3201Pan, 0, wx.EXPAND)
        self.vboxdl.Add(self.dev2101Pan, 0, wx.EXPAND)
        self.vboxdl.Add(0, 10, 0)
        self.vboxdl.Add(self.autoPan, 1, wx.EXPAND)

        self.hboxdl = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxdl.Add(self.vboxdl, 1 ,wx.ALIGN_LEFT | wx.EXPAND)
        self.hboxdl.Add((20,0), 0, wx.EXPAND)
        self.hboxdl.Add(self.loopPan, 0, wx.EXPAND)
        
        # Hide the dev3201Window and dev3141Window
        self.vboxdl.Hide(self.dev3201Pan)
        self.vboxdl.Hide(self.dev2101Pan)

        self.vboxl = wx.BoxSizer(wx.VERTICAL)

        self.vboxl.Add((0,20), 0, wx.EXPAND)
        self.vboxl.Add(self.hboxdl, 0 ,wx.ALIGN_LEFT | wx.EXPAND)
        self.vboxl.Add((0,10), 0, 0)
        self.vboxl.Add(self.logPan, 1, wx.EXPAND)
        self.vboxl.Add((0,20), 0, wx.EXPAND)

        self.vboxr = wx.BoxSizer(wx.VERTICAL)
        self.vboxr.Add((0,20), 0, wx.EXPAND)
        self.vboxr.Add(self.comPan, 0 ,wx.ALIGN_RIGHT | wx.EXPAND)
        self.vboxr.Add((0,10), 0, 0)
        self.vboxr.Add(self.treePan, 1, wx.ALIGN_RIGHT | wx.EXPAND)
        self.vboxr.Add((0,20), 0, wx.EXPAND)
        # BoxSizer fixed with Horizontal
        self.hboxm = wx.BoxSizer(wx.HORIZONTAL)

        self.hboxm.Add((20,0), 1, wx.EXPAND)
        self.hboxm.Add(self.vboxl, 1, wx.EXPAND)
        self.hboxm.Add((20,0), 1, wx.EXPAND)
        self.hboxm.Add(self.vboxr, 1, wx.EXPAND)
        self.hboxm.Add((20,0), 1, wx.EXPAND)
        # set size of frame
        self.SetSizer(self.hboxm)
        # Setting Layouts
        self.SetAutoLayout(True)
        self.hboxm.Fit(self)
        self.Layout()

    """
    print on logwindow data 
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        strin: string format
    Returns:
        return None
    """ 
    def PrintLog(self, strin):
        self.logPan.print_on_log(strin)
    
    """
    print on treewindow usb info 
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        strin: string format
    Returns:
        return None
    """
    def print_on_usb(self, strin):
        self.treePan.print_on_usb(strin)
        if(self.logPan.is_usb_enabled()):
            self.logPan.print_on_log(strin+"\n")
    
    """
    enumaration delay 
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def get_enum_delay(self):
        return self.treePan.get_enum_delay()
    
    """
    delay status
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """  
    def get_delay_status(self):
        return self.treePan.get_delay_status()
    
    """
    get interval is a function or evalutes an auto panel
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def get_interval(self):
        return self.autoPan.get_interval()
    """
    The setInterval () method calls a function or 
    evaluates an expression at specified intervals 
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        strval: string value
    Returns:
        return None
    """
    def set_interval(self, strval):
        self.autoPan.set_interval(strval)
    """
    disable for usb scanning
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def disable_usb_scan(self):
        self.treePan.disable_usb_scan()
    
    """
    this function calls getting the loop window prameters
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def get_loop_param(self):
        return self.loopPan.get_loop_param()
    
    """
    this function calls getting the auto window prameters
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def get_auto_param(self):
        return self.autoPan.get_auto_param()
    
    """
    set the period
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        strval: string value
    Returns:
        return None
    """
    def set_period(self, strval):
        self.loopPan.set_period(strval)

    """
    set the ports list for loopPan and autoPan
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        ports: upated the ports list
    Returns:
        return None
    """
    def set_port_list(self, ports):
        self.loopPan.set_port_list(ports)
        self.autoPan.set_port_count(ports)
    
    """
    to select a device and switching the port
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        port: port number
        stat: port on status will updated 
    Returns:
        return None
    """
    def port_on(self, port, stat):
        self.devObj[self.parent.selDevice].port_on(port, stat)
    
    """
    update the controls for selecting device
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        mode: mode controls
    Returns:
        return None
    """
    def update_controls(self, mode):
        self.devObj[self.parent.selDevice].update_controls(mode)
        self.loopPan.update_controls(mode)
        self.autoPan.update_controls(mode)
        self.treePan.update_controls(mode)
    
    """
    Model device connected
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def device_connected(self):
        for dev in range(len(DEVICES)):
            if dev == self.parent.selDevice:
                self.vboxdl.Show(self.devObj[self.parent.selDevice])
            else:
                self.vboxdl.Hide(self.devObj[dev])
        self.Layout()
        self.devObj[self.parent.selDevice].device_connected()
    
    """
    model device disconnected
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def device_disconnected(self):
        self.devObj[self.parent.selDevice].device_disconnected()
        self.loopPan.device_disconnected()
        self.autoPan.device_disconnected()
    
    """
    device auto connect
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def auto_connect(self):
        self.comPan.auto_connect()

"""
A UiMainFrame is a window of size and position usually changed by user
"""
class UiMainFrame (wx.Frame):
    """
    device auto connect
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        parent: Pointer to a parent window.
        title: Ui title 
    Returns:
        return None
    """
    def __init__ (self, parent, title):
        #super(UiMainFrame, self).__init__(parent, title=title)
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

        self.selDevice = None

        self.devHand = serial.Serial()

        self.mode = MODE_MANUAL

        self.con_flg = False

        self.masterList = []
        
        self.panel = UiPanel(self)
        
        self.menuBar = wx.MenuBar()
        
        # if its not darwin or MAC OS
        if sys.platform != 'darwin':
           # Setting up the menu.
           self.fileMenu = wx.Menu()
           # fileMenu.Append(ID_MENU_FILE_NEW,   "&New Window\tCtrl+N")
           self.fileMenu.Append(ID_MENU_FILE_CLOSE, "&Close \tAlt+F4")

        # creating the help menu
        self.helpMenu = wx.Menu()
        self.helpMenu.Append(ID_MENU_HELP_3141, "Visit Model 3141")
        self.helpMenu.Append(ID_MENU_HELP_3201, "Visit Model 3201")
        self.helpMenu.Append(ID_MENU_HELP_2101, "Visit Model 2101")
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
        # create menubar
        if sys.platform != 'darwin':
            self.menuBar.Append(self.fileMenu,    "&File")
        else:
            self.menuBar.Append(self.winMenu,    "&Window")
        self.menuBar.Append(self.helpMenu,    "&Help")
        # First we create a menubar object.
        self.SetMenuBar(self.menuBar)

        # create the statusbar
        self.statusbar = MultiStatus(self)
        
        self.SetStatusBar(self.statusbar)

        self.UpdateAll(["Port", "", ""])
        
         # Set events to Menu
        #self.Bind(wx.EVT_MENU, self.MenuHandler)
        self.Bind(wx.EVT_MENU, self.OnCloseWindow, id=ID_MENU_FILE_CLOSE)
        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_3141)
        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_3201)
        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_2101)
        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_WEB)
        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_PORT)
        self.Bind(wx.EVT_MENU, self.OnClickHelp, id=ID_MENU_HELP_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnHideWindow, id=ID_MENU_WIN_MIN)
        self.Bind(wx.EVT_MENU, self.OnShowWindow, id=ID_MENU_WIN_SHOW)

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
    
    """
    Virtual event handlers, overide them in your derived class
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        event: event handler for helpmenu
    Returns:
        return None
    """
    def OnClickHelp(self, event):
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
        elif(id == ID_MENU_HELP_WEB):
            webbrowser.open("https://mcci.com/", new=0, autoraise=True)
        elif(id == ID_MENU_HELP_PORT):
            webbrowser.open("https://portal.mcci.com/portal/home", new=0,
                            autoraise=True)
        elif(id == ID_MENU_HELP_ABOUT):
            self.OnAboutWindow(event)
    
    """
    device details update in status bar
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def UpdateStatusBar (self):
        self.statusbar.Refresh()
        self.statusbar.Update()
    
    """
    Status bar update - All fields
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        textList: set the status bar
    Returns:
        return None
    """
    def UpdateAll (self, textList):
        for i in range(len(textList)):
            self.SetStatusText(textList[i], i)
        self.UpdateStatusBar()
    
    """
    Status bar update - Port
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def UpdatePort (self):
        if self.selDevice == DEV_2101:
            self.SetStatusText("USB", SB_PORT_ID)
        else:
            self.SetStatusText(self.selPort, SB_PORT_ID)
        self.UpdateStatusBar()
    
    """
    Status bar update - Device
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def UpdateDevice (self):
        self.SetStatusText(DEVICES[self.selDevice], SB_DEV_ID)
        self.UpdateStatusBar()  
    """
    Status bar update - Any of One field
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        newStr: status updated in strings
        idx: update id
    Returns:
        return None
    """
    def UpdateSingle(self, newStr, idx):
        self.SetStatusText(newStr, idx)
        self.UpdateStatusBar()
    
    """
    Virtual event handlers, overide them in your derived class
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        event:event handler for about menu
    Returns:
        return None
    """
    def OnAboutWindow(self, event):
        dlg = AboutDialog(self, self)
        dlg.ShowModal()
        dlg.Destroy()
    
    """
    Virtual event handlers, overide them in your derived class
    for Window Close
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        event:event handler for window close
    Returns:
        return None
    """
    def OnCloseWindow (self, event):
        # Close this window
        self.Close(True)
    
    """
    Virtual event handlers, overide them in your derived classmenu
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        event: Event Handler for Menu
    Returns:
        return None
    """
    def OnIconize (self, event):
        # Close this window
        if self.IsIconized():
            self.winMenu.Check(ID_MENU_WIN_SHOW, False)
        else:
            self.winMenu.Check(ID_MENU_WIN_SHOW, True)
        event.Skip()
    
    """
    Event Handler hide the window
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        event:hide the win menu
    Returns:
        return None
    """
    # Event Handler
    def OnHideWindow (self, event):
        # Close this window
        self.winMenu.Check(ID_MENU_WIN_SHOW, False)
        self.Iconize(True)
    
    """
    Event Handler for show window
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        event:show window
    Returns:
        return None
    """
    def OnShowWindow (self, event):
        # Close this window
        self.winMenu.Check(ID_MENU_WIN_SHOW, True)
        self.Iconize(False)
    """
    Keep USB device list in a list
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        mlist:save the us list of file
    Returns:
        return None
    """
    def save_usb_list(self, mlist):
        self.masterList = mlist[:]  
    """
    Get usb device list
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def get_usb_list(self):
        return self.masterList
    """
    Show content in Log Window
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        strin: update string format
    Returns:
        return None
    """
    def print_on_log(self, strin):
        self.panel.PrintLog(strin)
    """
    Show content in USB Device Tree View
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        strin: update string format
    Returns:
        return None
    """
    def print_on_usb(self, strin):
        self.panel.print_on_usb(strin)
    
    """
    Get USB device Enumeration delay
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def get_enum_delay(self):
        return self.panel.get_enum_delay()
    """
    Checkbox status of USB Enumeration delay option
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def get_delay_status(self):
        return self.panel.get_delay_status()
    
    """
    Get Loop Window delay parameters
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def get_loop_param(self):
        return self.panel.get_loop_param()
    
    """
    Get Auto Window delay parameters
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def get_auto_param(self):
        return self.panel.get_auto_param()
    
    """
    Set Loop Mode period
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        strin:string format update field
    Returns:
        return None
    """
    def set_period(self, strval):
        self.panel.set_period(strval)
    
    """
    Set Port list for loop Window port selection
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        ports: port list
    Returns:
        return None
    """
    def set_port_list(self, ports):
        self.panel.set_port_list(ports)
    
    """
    Get Auto mode time interval
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def get_interval(self):
        return self.panel.get_interval()
    
    """
    Set Auto mode time interval when override by USB delay warning
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def set_interval(self, strval):
        self.panel.set_interval(strval)
    
    """
    Called by Loop Window, Device Window and COM Window
    When Normal-Auto-Loop trasition
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def set_mode(self, mode):
        self.mode = mode
        self.panel.update_controls(mode)
    
    """
    Called by device window based on USB delay warning selection
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def disable_usb_scan(self):
        self.panel.disable_usb_scan()

    """
    Port ON/OFF command from Loop Window
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        stat:port status update
    Returns:
        return None
    """
    def port_on(self, port, stat):
        self.panel.port_on(port, stat)
    
    """
    intervalCalled by COM Window when devide get connected
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def device_connected(self):
        self.panel.device_connected()
        self.StoreDevice()
    
    """
    Called by COM Window when the device get disconnected
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def device_disconnected(self):
        self.panel.device_disconnected()
    
    """
    Update plugged USB device list in Status bar.
    Called by usbDev.py
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        d1:list updated
    Returns:
        return None
    """
    def update_usb_status(self, dl):
        strUsb = " USB Devices     Host Controller: {d1}     ".\
                 format(d1=str(dl[0])) + \
                 "Hub: {d2}     ".format(d2=str(dl[1])) + \
                 "Peripheral: {d3}".format(d3=str(dl[2]))
        
        self.UpdateSingle(strUsb, 4)
    
    """
    Export the LogWindow/USBTreeWindow content to a file
    Called by LogWindow and USB Tree View Window
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def save_file (self, contents, extension):
        # save a file
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
    """
    store the device configarartion
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def StoreDevice(self):
        # This is also a base class of shelve and it accepts
        # the filename as it’s parameter not a dict object like others. 
        # This is the base class of shelve which stores pickled object values 
        # in dict objects and string objects as key.
        ds = shelve.open('config.txt')
        ds['port'] = self.selPort
        ds['device'] = self.selDevice
        ds.close()
    
    """
    load the device list for last device disconnect 
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def LoadDevice(self):
        # This is also a base class of shelve and it accepts
        # the filename as it’s parameter not a dict object like others. 
        # This is the base class of shelve which stores pickled object values 
        # in dict objects and string objects as key.
        ds = shelve.open('config.txt')
        self.ldata['port'] = ds['port']
        self.ldata['device'] = ds['device']
        ds.close()  
"""
UiApp wx.App object has been created in order to ensure 
that the gui platform and wx Widgets have been fully initialized.
"""
class UiApp(wx.App):
    """
    override OnInit to do applicaition initialization
    to ensure that the system, toolkit and wxWidgets are fully initialized.
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def OnInit (self):
        return True
    
    """
    showing the title on UI frame with UI title name
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
    Returns:
        return None
    """
    def CustInit(self):
        self.frame = UiMainFrame(parent=None, title="MCCI - Cricket UI")
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)

        

##############################################################################
# MainLoop RunProgram 
##############################################################################
def run():
    app = UiApp()
    app.CustInit()
    app.MainLoop()
