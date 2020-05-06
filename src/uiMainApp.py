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

import serial
import webbrowser

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

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox2 = wx.BoxSizer(wx.VERTICAL)
        vbox3 = wx.BoxSizer(wx.VERTICAL)
        
        self.hboxtop = wx.BoxSizer(wx.HORIZONTAL)
        lvbox = wx.BoxSizer(wx.VERTICAL)
        rvbox = wx.BoxSizer(wx.VERTICAL)
        
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)

        self.dev3141Pan = dev3141Window.Dev3141Window(self, parent)
        self.loopPan = loopWindow.LoopWindow(self, parent)
        self.comPan = comWindow.ComWindow(self, parent)
        self.logPan = logWindow.LogWindow(self, parent)
        self.treePan = treeWindow.UsbTreeWindow(self, parent)
        self.dev3201Pan = dev3201Window.Dev3201Window(self, parent)
         
        hbox1.Add(30,50,0)
        hbox1.Add(self.logPan, 1, wx.EXPAND, 1)
        hbox1.Add(30,50,0)

        self.hboxd1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxd2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxloop = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox12 = wx.BoxSizer(wx.HORIZONTAL)
        
        self.hboxd1.Add(self.dev3141Pan,1,wx.ALIGN_CENTER)
        self.hboxd2.Add(self.dev3201Pan,1,wx.ALIGN_CENTER)
        self.hboxloop.Add(self.loopPan,1,wx.ALIGN_CENTER)

        self.hbox12.Add(self.hboxd1,0,wx.ALIGN_LEFT)
        self.hbox12.Add(self.hboxd2,0,wx.ALIGN_LEFT)
        self.remove_3201()

        self.hboxtop.Add(30,50,0)
        self.hboxtop.Add(self.hbox12,1,wx.ALIGN_LEFT)
        self.hboxtop.Add(50,50,0)
        self.hboxtop.Add(self.hboxloop,1, wx.ALIGN_RIGHT)
        self.hboxtop.Add(0,50,0)

        lvbox.Add(0,20,0)
        lvbox.Add(self.hboxtop, 1, wx.ALIGN_LEFT)
        lvbox.Add(0,30,0)
        lvbox.Add(hbox1, 1, wx.ALIGN_LEFT | wx.EXPAND, 1)
        lvbox.Add(0,10,0)

        rvbox.Add(self.comPan, 1, wx.ALIGN_RIGHT)
        rvbox.Add(30,0,0)
        rvbox.Add(self.treePan,1, wx.ALIGN_RIGHT)
        rvbox.Add(30,10,0)

        self.hbox.Add(lvbox,1, wx.EXPAND, 10)
        self.hbox.Add(rvbox,1, wx.ALIGN_RIGHT)
        self.hbox.Add(20,30,0)

        self.SetSizer(self.hbox)
        self.SetAutoLayout(True)
        self.hbox.Fit(self)
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

    def enable_start(self):
        self.loopPan.enable_start()

    def disable_start(self):
        self.loopPan.disable_start()

    def remove_3201(self):
        self.hbox12.Hide(self.hboxd2)

    def remove_3141(self):
        self.hbox12.Hide(self.hboxd1)

    def show_3201(self):
        self.hbox12.Hide(self.hboxd1)
        self.hbox12.Show(self.hboxd2)
        self.Layout()
        
    def show_3141(self):
        self.hbox12.Hide(self.hboxd2)
        self.hbox12.Show(self.hboxd1)

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

    def enable_model(self):
        self.dev3141Pan.enable_model()
        self.dev3201Pan.enable_model()

    def disable_model(self):
        self.dev3141Pan.disable_model()
        self.dev3201Pan.disable_model()

    def disable_usb_scan(self):
        self.treePan.disable_usb_scan()


class UiMainFrame (wx.Frame):
    def __init__ (self, parent, title):
        #super(UiMainFrame, self).__init__(parent, title=title)
        wx.Frame.__init__(self, None, -1, "MCCI USB Switch 3141/3201 - "+
                          VERSION_STR, pos=wx.Point(80,40), 
                          size=wx.Size(1020,720))

        self.Bind(wx.EVT_CLOSE, self.WinClose)

        self.SetMinSize((980,600))

        self.init_flg = True

        self.selPort = None

        self.selDevice = None

        self.devHand = serial.Serial()

        self.auto_flg = False

        self.con_flg = False

        self.masterList = []
        
        self.panel = UiPanel(self)

        fileMenu = wx.Menu()
        fileMenu.Append(ID_MENU_FILE_NEW,   "&New Window\tCtrl+N",
                                            "New window")
        fileMenu.Append(ID_MENU_FILE_CLOSE, "&Close \tAlt+F4",
                                            "Close this window")
        # create the help menu
        helpMenu = wx.Menu()
        helpMenu.Append(ID_MENU_HELP_3141, "Visit Model 3141")
        helpMenu.Append(ID_MENU_HELP_3201, "Visit Model 3201")
        helpMenu.AppendSeparator()
        helpMenu.Append(ID_MENU_HELP_WEB, "MCCI Website")
        helpMenu.Append(ID_MENU_HELP_PORT, "MCCI Support Portal")
        helpMenu.AppendSeparator()
        helpMenu.Append(ID_MENU_HELP_ABOUT, "About...")

        # create menubar
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu,    "&File")
        menuBar.Append(helpMenu,    "&Help")

        self.SetMenuBar(menuBar)

        # create the statusbar
        self.statusbar = MultiStatus(self)
        
        self.SetStatusBar(self.statusbar)

        self.UpdateAll(["Port", "", ""])

        self.Bind(wx.EVT_MENU, self.MenuHandler)

        self.SetIcon(wx.Icon("mcci_logo.ico"))

        self.Show()

        td, usbList = getusb.scan_usb()
        self.save_usb_list(usbList)
        self.update_usb_status(td)
        
    def MenuHandler(self, e):
        id = e.GetId()
        if(id == ID_MENU_FILE_CLOSE):
            self.OnCloseWindow()
        elif(id == ID_MENU_FILE_EXIT):
            self.OnExitApplication()
        elif(id == ID_MENU_HELP_ABOUT):
            self.OnAboutWindow()
        elif(id == ID_MENU_HELP_3141):
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
        elif(id == ID_MENU_SCRIPT_NEW):
            self.OnScriptWindow()

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

    def OnAboutWindow(self):
        dlg = AboutDialog(self, self)
        dlg.ShowModal()
        dlg.Destroy()

    def OnCloseWindow (self):
        # Close this window
        self.Close(True)

    def OnExitApplication (self):
        self.Close(True)

    def WinClose(self, evt):
        self.Destroy()

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

    def remove_3201(self):
        self.panel.remove_3201()

    def remove_3141(self):
        self.panel.remove_3141()

    def show_3201(self):
        self.panel.show_3201()

    def show_3141(self):
        self.panel.show_3141()

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
        self.locale = wx.Locale(wx.Locale.GetSystemLanguage())
        

#======================================================================
# MAIN PROGRAM
#======================================================================
def run():
    
    app = UiApp()
    app.CustInit()
    app.MainLoop()