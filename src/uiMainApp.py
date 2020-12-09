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
import serial
import webbrowser
from sys import platform

from uiGlobals import *

import dev3141Window
import dev3201Window
import loopWindow
import comWindow
import logWindow
import treeWindow

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

        self.parent = parent

        self.SetBackgroundColour('White')

        self.font_size = DEFAULT_FONT_SIZE

        if platform == "darwin":
            self.font_size = MAC_FONT_SIZE

        self.SetFont(wx.Font(self.font_size, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.dev3141Pan = dev3141Window.Dev3141Window(self, parent)
        self.loopPan = loopWindow.LoopWindow(self, parent)
        self.comPan = comWindow.ComWindow(self, parent)
        self.logPan = logWindow.LogWindow(self, parent)
        self.treePan = treeWindow.UsbTreeWindow(self, parent)
        self.dev3201Pan = dev3201Window.Dev3201Window(self, parent)

        self.hboxdl = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxdl.Add(self.dev3141Pan, 0, 0)
        self.hboxdl.Add(self.dev3201Pan, 0, 0)
        self.hboxdl.Add((20,0), 1, wx.EXPAND)
        self.hboxdl.Add(self.loopPan, 0, wx.EXPAND)

        self.hboxdl.Hide(self.dev3141Pan)

        self.vboxl = wx.BoxSizer(wx.VERTICAL)

        self.vboxl.Add(self.hboxdl, 0 ,wx.ALIGN_LEFT | wx.EXPAND)
        self.vboxl.Add((0,20), 0, 0)
        self.vboxl.Add(self.logPan, 1, wx.EXPAND)

        self.vboxr = wx.BoxSizer(wx.VERTICAL)
        self.vboxr.Add(self.comPan, 0 ,wx.ALIGN_RIGHT)
        self.vboxr.Add((0,20), 0, 0)
        self.vboxr.Add(self.treePan, 1, wx.ALIGN_RIGHT)

        self.hboxm = wx.BoxSizer(wx.HORIZONTAL)

        self.hboxm.Add((20,0), 1, wx.EXPAND)
        self.hboxm.Add(self.vboxl, 1, wx.EXPAND)
        self.hboxm.Add((20,0), 1, wx.EXPAND)
        self.hboxm.Add(self.vboxr, 1, wx.EXPAND)
        self.hboxm.Add((20,0), 1, wx.EXPAND)

        self.vboxm = wx.BoxSizer(wx.VERTICAL)
        self.vboxm.Add((0,20), 0, wx.EXPAND)
        self.vboxm.Add(self.hboxm, 1, wx.EXPAND)
        self.vboxm.Add((0,20), 0, wx.EXPAND)
        
        self.SetSizer(self.vboxm)
        self.SetAutoLayout(True)
        self.vboxm.Fit(self)
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

    def update_controls(self):
        if self.parent.selDevice == '3201':
            self.dev3201Pan.update_controls()
        else:
            self.dev3141Pan.update_controls()
        self.loopPan.update_controls()

    def disable_auto(self):
        if(self.parent.selDevice == '3201'):
            self.dev3201Pan.disable_auto()
        else:
            self.dev3141Pan.disable_auto()

    def enable_auto(self):
        if(self.parent.selDevice == '3201'):
            self.dev3201Pan.enable_auto()
        else:
            self.dev3141Pan.enable_auto()

    def get_interval(self):
        if(self.parent.selDevice == '3141'):
            return self.dev3141Pan.get_interval()
        else:
            return self.dev3201Pan.get_interval()

    def set_interval(self, strval):
        if(self.parent.selDevice == '3141'):
            self.dev3141Pan.set_interval(strval)
        else:
            self.dev3201Pan.set_interval(strval)

    def enable_start(self):
        self.loopPan.enable_start()

    def disable_start(self):
        self.loopPan.disable_start()

    def show_3201(self):
        self.hboxdl.Hide(self.dev3141Pan)
        self.hboxdl.Show(self.dev3201Pan)
        self.Layout()
        
    def show_3141(self):
        self.hboxdl.Hide(self.dev3201Pan)
        self.hboxdl.Show(self.dev3141Pan)
        self.Layout()

    def get_switch_port(self):
        if(self.parent.selDevice == '3141'):
            return self.dev3141Pan.get_switch_port()
        else:
            return self.dev3201Pan.get_switch_port()

    def port_led_update(self, pno, stat):
        if self.parent.selDevice == '3141':
            self.dev3141Pan.port_led_update(pno, stat)
        else:
            self.dev3201Pan.port_led_update(pno, stat)

    def disconnect_device(self):
        self.comPan.disconnect_device()
        self.dev3141Pan.update_controls()
        self.loopPan.update_controls()

    def enable_model(self, stat):
        self.dev3141Pan.enable_model(stat)
        self.dev3201Pan.enable_model(stat)

    def disable_usb_scan(self):
        self.treePan.disable_usb_scan()

    def get_loop_param(self):
        return self.loopPan.get_loop_param()

    def set_period(self, strval):
        self.loopPan.set_period(strval)
    def set_port_list(self, port):
        self.loopPan.set_port_list(port)

    def enable_enum_controls(self, stat):
        self.treePan.enable_enum_controls(stat)


class UiMainFrame (wx.Frame):
    def __init__ (self, parent, title):
        #super(UiMainFrame, self).__init__(parent, title=title)
        wx.Frame.__init__(self, None, id = wx.ID_ANY, title = "MCCI USB Switch 3141/3201 - "+
                          VERSION_STR, pos=wx.Point(80,80),
                          size=wx.Size(980,720))

        self.SetMinSize((980,600))

        self.init_flg = True

        self.selPort = None

        self.selDevice = None

        self.devHand = serial.Serial()

        self.auto_flg = False

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
        self.helpMenu.AppendSeparator()
        self.helpMenu.Append(ID_MENU_HELP_WEB, "MCCI Website")
        self.helpMenu.Append(ID_MENU_HELP_PORT, "MCCI Support Portal")
        self.helpMenu.AppendSeparator()
        
        if sys.platform == 'darwin':
            self.helpMenu.Append(wx.ID_ABOUT, "About UI-3141-3201")
        else:
            self.helpMenu.Append(ID_MENU_HELP_ABOUT, "About...")
        
        if sys.platform == 'darwin':
            self.winMenu = wx.Menu()
            self.winMenu.Append(ID_MENU_WIN_MIN, "&Minimize\tCtrl+M")
            self.winMenu.AppendCheckItem(ID_MENU_WIN_SHOW, "&UI-3141-3201\tAlt+Ctrl+1")
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

    def OnClickHelp(self, event):
        id = event.GetId()
        if(id == ID_MENU_HELP_3141):
            webbrowser.open("https://mcci.com/usb/dev-tools/model-3141/",
                            new=0, autoraise=True)
        elif(id == ID_MENU_HELP_3201):
            webbrowser.open("https://mcci.com/usb/dev-tools/3201-enhanced"
                            "-type-c-connection-exerciser/",
                            new=0, autoraise=True)
        elif(id == ID_MENU_HELP_WEB):
            webbrowser.open("https://mcci.com/", new=0, autoraise=True)
        elif(id == ID_MENU_HELP_PORT):
            webbrowser.open("https://portal.mcci.com/portal/home", new=0,
                            autoraise=True)
        elif(id == ID_MENU_HELP_ABOUT):
            self.OnAboutWindow(event)

    def UpdateStatusBar (self):
        self.statusbar.Refresh()
        self.statusbar.Update()

    def UpdateAll (self, textList):
        for i in range(len(textList)):
            self.SetStatusText(textList[i], i)
        self.UpdateStatusBar()

    def UpdatePort (self):
        self.SetStatusText(self.selPort, SB_PORT_ID)
        self.UpdateStatusBar()

    def UpdateDevice (self):
        self.SetStatusText(self.selDevice, SB_DEV_ID)
        self.UpdateStatusBar()

    def UpdateSingle(self, newStr, idx):
        self.SetStatusText(newStr, idx)
        self.UpdateStatusBar()

    def OnScriptWindow(self):
        #print("Script Window")
        pass

    def OnAboutWindow(self, event):
        dlg = AboutDialog(self, self)
        dlg.ShowModal()
        dlg.Destroy()

    def OnCloseWindow (self, event):
        # Close this window
        self.Close(True)
    
    def OnIconize (self, event):
        # Close this window
        if self.IsIconized():
            self.winMenu.Check(ID_MENU_WIN_SHOW, False)
        else:
            self.winMenu.Check(ID_MENU_WIN_SHOW, True)
        event.Skip()
    
    def OnHideWindow (self, event):
        # Close this window
        self.winMenu.Check(ID_MENU_WIN_SHOW, False)
        self.Iconize(True)

    def OnShowWindow (self, event):
        # Close this window
        self.winMenu.Check(ID_MENU_WIN_SHOW, True)
        self.Iconize(False)

    def print_on_log(self, strin):
        self.panel.PrintLog(strin)

    def save_usb_list(self, mlist):
        self.masterList = mlist[:]

    def get_usb_list(self):
        return self.masterList

    def print_on_usb(self, strin):
        self.panel.print_on_usb(strin)

    def get_enum_delay(self):
        return self.panel.get_enum_delay()

    def get_delay_status(self):
        return self.panel.get_delay_status()

    def update_controls(self):
        self.panel.update_controls()

    def enable_auto(self):
        self.panel.enable_auto()

    def disable_auto(self):
        self.panel.disable_auto()

    def enable_start(self):
        self.panel.enable_start()

    def disable_start(self):
        self.panel.disable_start()

    def get_loop_param(self):
        return self.panel.get_loop_param()

    def set_period(self, strval):
        self.panel.set_period(strval)

    def show_3201(self):
        self.panel.show_3201()
        self.panel.set_port_list(4)
    def show_3141(self):
        self.panel.show_3141()
        self.panel.set_port_list(2)

    def get_interval(self):
        return self.panel.get_interval()

    def set_interval(self, strval):
        self.panel.set_interval(strval)

    def get_switch_port(self):
        return self.panel.get_switch_port()

    def port_led_update(self, pno, stat):
        self.panel.port_led_update(pno, stat)

    def disconnect_device(self):
        self.panel.disconnect_device()

    def enable_model(self):
        self.panel.enable_model()

    def disable_model(self):
        self.panel.disable_model()

    def disable_usb_scan(self):
        self.panel.disable_usb_scan()

    def enable_auto_controls(self, stat):
        self.panel.enable_model(stat)

    def enable_enum_controls(self, stat):
        self.panel.enable_enum_controls(stat)

    def update_usb_status(self, dl):
        strUsb = " USB Devices     Host Controller: {d1}     ".\
                 format(d1=str(dl[0])) + \
                 "Hub: {d2}     ".format(d2=str(dl[1])) + \
                 "Peripheral: {d3}".format(d3=str(dl[2]))
        
        self.UpdateSingle(strUsb, 4)

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
