#======================================================================
# (c) 2020  MCCI, Inc.
#----------------------------------------------------------------------
# Project : UI3141/3201 GUI application
# File    : uiMainApp.py
#----------------------------------------------------------------------
# Main Application body for the 3141/3201 GUI Application
#======================================================================

#======================================================================
# IMPORTS
#======================================================================
import wx

import os
import sys
from sys import platform


import serial
import webbrowser
import shelve

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

#======================================================================
# COMPONENTS
#======================================================================

class MultiStatus (wx.StatusBar):
    def __init__ (self, parent):
        wx.StatusBar.__init__(self, parent, -1)
        self.SetFieldsCount(5)
        self.SetStatusWidths([-1, -1, -3, -2, -8])

class UiPanel(wx.Panel):
    def __init__(self, parent):
        super(UiPanel, self).__init__(parent)

        wx.GetApp().SetAppName("CricketUI")

        self.parent = parent

        self.SetBackgroundColour('White')

        self.font_size = DEFAULT_FONT_SIZE

        if platform == "darwin":
            self.font_size = MAC_FONT_SIZE

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
        self.devObj.append(self.dev3141Pan)
        self.devObj.append(self.dev3201Pan)
        self.devObj.append(self.dev2101Pan)

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

        self.hboxm = wx.BoxSizer(wx.HORIZONTAL)

        self.hboxm.Add((20,0), 1, wx.EXPAND)
        self.hboxm.Add(self.vboxl, 1, wx.EXPAND)
        self.hboxm.Add((20,0), 1, wx.EXPAND)
        self.hboxm.Add(self.vboxr, 1, wx.EXPAND)
        self.hboxm.Add((20,0), 1, wx.EXPAND)

        self.SetSizer(self.hboxm)
        self.SetAutoLayout(True)
        self.hboxm.Fit(self)
        self.Layout()
        

    def PrintLog(self, strin):
        self.logPan.print_on_log(strin)

    def print_on_usb(self, strin):
        self.treePan.print_on_usb(strin)
        if(self.logPan.is_usb_enabled()):
            self.logPan.print_on_log(strin+"\n")

    def get_enum_delay(self):
        return self.treePan.get_enum_delay()
        
    def get_delay_status(self):
        return self.treePan.get_delay_status()

    def get_interval(self):
        return self.autoPan.get_interval()
 
    def set_interval(self, strval):
        self.autoPan.set_interval(strval)

    def disable_usb_scan(self):
        self.treePan.disable_usb_scan()

    def get_loop_param(self):
        return self.loopPan.get_loop_param()

    def get_auto_param(self):
        return self.autoPan.get_auto_param()

    def set_period(self, strval):
        self.loopPan.set_period(strval)
    
    def set_port_list(self, ports):
        self.loopPan.set_port_list(ports)
        self.autoPan.set_port_count(ports)

    def port_on(self, port, stat):
        self.devObj[self.parent.selDevice].port_on(port, stat)
    
    def update_controls(self, mode):
        self.devObj[self.parent.selDevice].update_controls(mode)
        self.loopPan.update_controls(mode)
        self.autoPan.update_controls(mode)
        self.treePan.update_controls(mode)

    def device_connected(self):
        for dev in range(len(DEVICES)):
            if dev == self.parent.selDevice:
                self.vboxdl.Show(self.devObj[self.parent.selDevice])
            else:
                self.vboxdl.Hide(self.devObj[dev])
        self.Layout()
        self.devObj[self.parent.selDevice].device_connected()

    def device_disconnected(self):
        self.devObj[self.parent.selDevice].device_disconnected()
        self.loopPan.device_disconnected()
        self.autoPan.device_disconnected()

    def auto_connect(self):
        self.comPan.auto_connect()


class UiMainFrame (wx.Frame):
    def __init__ (self, parent, title):
        #super(UiMainFrame, self).__init__(parent, title=title)
        wx.Frame.__init__(self, None, id = wx.ID_ANY, title = "MCCI "+APP_NAME+" - "+
                          VERSION_STR, pos=wx.Point(80,5),
                          size=wx.Size(1020,680))

        self.ytop = 5
        if sys.platform == 'darwin':
            self.ytop = 25

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
        
        
        if sys.platform != 'darwin':
           self.fileMenu = wx.Menu()
           #fileMenu.Append(ID_MENU_FILE_NEW,   "&New Window\tCtrl+N")
           self.fileMenu.Append(ID_MENU_FILE_CLOSE, "&Close \tAlt+F4")

        # create the help menu
        self.helpMenu = wx.Menu()
        self.helpMenu.Append(ID_MENU_HELP_3141, "Visit Model 3141")
        self.helpMenu.Append(ID_MENU_HELP_3201, "Visit Model 3201")
        self.helpMenu.Append(ID_MENU_HELP_2101, "Visit Model 2101")
        self.helpMenu.AppendSeparator()
        self.helpMenu.Append(ID_MENU_HELP_WEB, "MCCI Website")
        self.helpMenu.Append(ID_MENU_HELP_PORT, "MCCI Support Portal")
        self.helpMenu.AppendSeparator()
        
        if sys.platform == 'darwin':
            self.helpMenu.Append(wx.ID_ABOUT, "About CricketUI")
        else:
            self.helpMenu.Append(ID_MENU_HELP_ABOUT, "About...")
        
        if sys.platform == 'darwin':
            self.winMenu = wx.Menu()
            self.winMenu.Append(ID_MENU_WIN_MIN, "&Minimize\tCtrl+M")
            self.winMenu.AppendCheckItem(ID_MENU_WIN_SHOW, "&CricketUI\tAlt+Ctrl+1")
            self.winMenu.Check(ID_MENU_WIN_SHOW, True)
        
        
        # create menubar
        if sys.platform != 'darwin':
            self.menuBar.Append(self.fileMenu,    "&File")
        else:
            self.menuBar.Append(self.winMenu,    "&Window")
        self.menuBar.Append(self.helpMenu,    "&Help")
        
        self.SetMenuBar(self.menuBar)

        # create the statusbar
        self.statusbar = MultiStatus(self)
        
        self.SetStatusBar(self.statusbar)

        self.UpdateAll(["Port", "", ""])

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

        self.SetIcon(wx.Icon("./icons/mcci_logo.ico"))

        self.Show()
        
        td, usbList = getusb.scan_usb()
        self.save_usb_list(usbList)
        self.update_usb_status(td)

        try:
            self.LoadDevice()
            self.panel.auto_connect()
        except:
            pass

    # Event Handler for Help Menu
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
            webbrowser.open("https://mcci.com/usb/dev-tools/2101-usb-connection-exerciser/",
                                    new=0, autoraise=True)
        elif(id == ID_MENU_HELP_WEB):
            webbrowser.open("https://mcci.com/", new=0, autoraise=True)
        elif(id == ID_MENU_HELP_PORT):
            webbrowser.open("https://portal.mcci.com/portal/home", new=0,
                            autoraise=True)
        elif(id == ID_MENU_HELP_ABOUT):
            self.OnAboutWindow(event)

    # Status bar update
    def UpdateStatusBar (self):
        self.statusbar.Refresh()
        self.statusbar.Update()
    
    # Status bar update - All fields
    def UpdateAll (self, textList):
        for i in range(len(textList)):
            self.SetStatusText(textList[i], i)
        self.UpdateStatusBar()

    # Status bar update - Port
    def UpdatePort (self):
        if self.selDevice == DEV_2101:
            self.SetStatusText("USB", SB_PORT_ID)
        else:
            self.SetStatusText(self.selPort, SB_PORT_ID)
        self.UpdateStatusBar()

    # Status bar update - Device
    def UpdateDevice (self):
        self.SetStatusText(DEVICES[self.selDevice], SB_DEV_ID)
        self.UpdateStatusBar()

    # Status bar update - Any of One field
    def UpdateSingle(self, newStr, idx):
        self.SetStatusText(newStr, idx)
        self.UpdateStatusBar()

    # Event Handler for About
    def OnAboutWindow(self, event):
        dlg = AboutDialog(self, self)
        dlg.ShowModal()
        dlg.Destroy()

    # Event Handler for Window Close
    def OnCloseWindow (self, event):
        # Close this window
        self.Close(True)
    
    # Event Handler
    def OnIconize (self, event):
        # Close this window
        if self.IsIconized():
            self.winMenu.Check(ID_MENU_WIN_SHOW, False)
        else:
            self.winMenu.Check(ID_MENU_WIN_SHOW, True)
        event.Skip()
    
    # Event Handler
    def OnHideWindow (self, event):
        # Close this window
        self.winMenu.Check(ID_MENU_WIN_SHOW, False)
        self.Iconize(True)

    # Event Handler
    def OnShowWindow (self, event):
        # Close this window
        self.winMenu.Check(ID_MENU_WIN_SHOW, True)
        self.Iconize(False)

    # Keep USB device list in a list
    def save_usb_list(self, mlist):
        self.masterList = mlist[:]

    # Get usb device list
    def get_usb_list(self):
        return self.masterList

    # Show content in Log Window
    def print_on_log(self, strin):
        self.panel.PrintLog(strin)

    # Show content in USB Device Tree View
    def print_on_usb(self, strin):
        self.panel.print_on_usb(strin)

    # Get USB device Enumeration delay
    def get_enum_delay(self):
        return self.panel.get_enum_delay()

    # Checkbox status of USB Enumeration delay option
    def get_delay_status(self):
        return self.panel.get_delay_status()

    # Get Loop Window delay parameters
    def get_loop_param(self):
        return self.panel.get_loop_param()

    # Get Auto Window delay parameters
    def get_auto_param(self):
        return self.panel.get_auto_param()
    
    # Set Loop Mode period
    def set_period(self, strval):
        self.panel.set_period(strval)

    # Set Port list for loop Window port selection
    def set_port_list(self, ports):
        self.panel.set_port_list(ports)
    
    # Get Auto mode time interval
    def get_interval(self):
        return self.panel.get_interval()

    # Set Auto mode time interval when override by USB delay warning
    def set_interval(self, strval):
        self.panel.set_interval(strval)

    # Called by Loop Window, Device Window and COM Window
    # When Normal-Auto-Loop trasition
    def set_mode(self, mode):
        self.mode = mode
        self.panel.update_controls(mode)

    # Called by device window based on USB delay warning selection
    def disable_usb_scan(self):
        self.panel.disable_usb_scan()

    # Port ON/OFF command from Loop Window
    def port_on(self, port, stat):
        self.panel.port_on(port, stat)

    # Called by COM Window when devide get connected
    def device_connected(self):
        self.panel.device_connected()
        self.StoreDevice()

    # Called by COM Window when the device get disconnected
    def device_disconnected(self):
        self.panel.device_disconnected()

    # Update plugged USB device list in Status bar.
    # Called by usbDev.py
    def update_usb_status(self, dl):
        strUsb = " USB Devices     Host Controller: {d1}     ".\
                 format(d1=str(dl[0])) + \
                 "Hub: {d2}     ".format(d2=str(dl[1])) + \
                 "Peripheral: {d3}".format(d3=str(dl[2]))
        
        self.UpdateSingle(strUsb, 4)

    # Export the LogWindow/USBTreeWindow content to a file
    # Called by LogWindow and USB Tree View Window
    def save_file (self, contents, extension):
        """ save a file """
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
        ds = shelve.open('config.txt')
        ds['port'] = self.selPort
        ds['device'] = self.selDevice
        ds.close()

    def LoadDevice(self):
        ds = shelve.open('config.txt')
        self.ldata['port'] = ds['port']
        self.ldata['device'] = ds['device']
        ds.close()        
        

class UiApp(wx.App):

    def OnInit (self):
        return True

    def CustInit(self):
        self.frame = UiMainFrame(parent=None, title="MCCI - UI3141")
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)

        

#======================================================================
# MAIN PROGRAM
#======================================================================
def run():
    app = UiApp()
    app.CustInit()
    app.MainLoop()
