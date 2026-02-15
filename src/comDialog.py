# -*- coding: utf-8 -*-
##############################################################################
# 
# Module: comDialog.py
#
# Description:
#     Dialog to display list of available MCCI USB Switch devices
#     (3141, 3201, 2101, 2301). Provides functionality to search,
#     view, select, add, and connect USB switch devices through GUI.
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
#
##############################################################################
# Lib imports
from random import choices
from matplotlib import style
import wx
from sys import platform

# Own modules
from uiGlobals import *
import devControl

##############################################################################
# Utilities
##############################################################################

class SearchSwitch(wx.PyEvent):
    """
    Custom event class used to handle USB switch search events.

    This event is posted during device search operations
    and carries search status or trigger information.

    Attributes:
        data: Event payload containing search action details.
    """

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

class ComWindow(wx.Window):
    """
    Communication dialog window for USB switch management.

    This window allows users to search available USB switches,
    select devices, add them to connection list, and establish
    communication with selected switches.

    Attributes:
        top: Reference to main application controller.
        parent: Parent dialog window.
        dlist: Detected device list.
        clist: Selected connection list.
        switchlist: Available switch collection.
        addswitchlist: Added switch collection.
    """
    def __init__ (self, parent, top):
        """
        AboutWindow that contains the about dialog elements.

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
            top: creates an object
        Returns:
            None
        """
        wx.Window.__init__(self, parent, -1,
                           size=wx.Size(100,100),
                           style=wx.CLIP_CHILDREN,
                           name="About")

        self.top = top
        self.parent = parent
        self.wait_flg = True

        self.dlist = []
        self.clist = []
        self.switchlist = []
        self.addswitchlist = []
        
        self.btn_scan = wx.Button(self, ID_BTN_DEV_SCAN, "Search",
                                  size=(77,25))

        self.fst_lb = wx.ListBox(self, size=(160, 120), style=wx.LB_EXTENDED, choices = self.dlist)

        self.scnd_lb = wx.ListBox(self, size=(160,120), style=wx.LB_MULTIPLE, choices = self.clist)
        
        self.btn_add = wx.Button(self, ID_BTN_CONNECT, "ADD", size = (50,-1))
        
        self.btn_connect = wx.Button(self, ID_BTN_ADD, "Connect", 
                                     size=(80,-1))
        
        self.btn_top = wx.BoxSizer(wx.HORIZONTAL)
        self.szr_top = wx.BoxSizer(wx.HORIZONTAL)
        
        wx.BoxSizer(wx.HORIZONTAL)

        self.btn_top.AddMany([
            (165,10,0),
            (self.btn_scan, 0, wx.LEFT),
            (10,50,0)
        ])
        
        self.szr_top.AddMany([
            (10,50,0),
            (self.fst_lb, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL),
            (10,50,0),
            (self.btn_add, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL),
            (10,50,0),
            (self.scnd_lb, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL),
            (10,50,0),
            (self.btn_connect, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL),
            (10,50,0)
            ])
        # Creates a boxsizer as vertical
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.vbox.AddMany([
            (10,10,0),
            (self.btn_top, 0, wx.EXPAND | wx.ALL),
            (10,10,0),
            (self.szr_top, 0, wx.EXPAND | wx.ALL),
            (10,10,0)
            ])
        
        # Set size of frame
        self.SetSizer(self.vbox)
        # Set size of frame
        self.vbox.Fit(self)
        self.Layout()

        
        # Tooltips display text over an widget elements
        # Set tooltip for switching search button.
        self.btn_scan.SetToolTip(wx.ToolTip("Search for the attached USB"
                                            "MCCI USB Switch(3141, 3201, 2101,2301)"))  
        # Bind the button event to handler
        self.btn_scan.Bind(wx.EVT_BUTTON, self.ScanDevice)

        #Add list from scan list to add list
        self.btn_add.Bind(wx.EVT_BUTTON, self.DeviceAdd)
        # Bind the button event to handler
        self.btn_connect.Bind(wx.EVT_BUTTON, self.ConnectDevice)

        self.btn_connect.Disable()   
        # The Timer class allows you to execute code at specified intervals.
        self.timer_lp = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.SearchTimer, self.timer_lp)

        EVT_RESULT(self, self.SearchEvent)
        # self.timer_lp.Start(1500)
        self.load_initial()

    def load_initial(self):
        """
        Load initially detected devices into the list box.

        Args:
            self: Reference to the current class instance.

        Returns:
            None
        """
        
        for i in range(len(self.top.dev_list)):
            lt = self.top.dev_list[i]["model"]+"("+ self.top.dev_list[i]["port"] +")"
            self.fst_lb.Append([lt])

        if(len(self.top.dev_list)):
            self.fst_lb.Select(0)
            self.btn_connect.Enable()
    
    def SearchTimer(self, evt):
        """
        while Searching the Device timer start.

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            evt: event start for Search timer.
        Returns:
            None
        """
        wx.PostEvent(self, SearchSwitch("search"))
        self.timer_lp.Stop()
        
    def ScanDevice(self, evt):
        """
        Trigger USB switch device scanning.

        Args:
            self: Reference to the current class instance.
            evt: Button click event object.

        Returns:
            None
        """
        wx.PostEvent(self, SearchSwitch("print"))
        wx.PostEvent(self, SearchSwitch("search"))
        wx.BeginBusyCursor()
    

    def SearchEvent(self, event):
        """
        Handle search event actions and update UI/logs.

        Args:
            self: Reference to the current class instance.
            event: Custom search event object.

        Returns:
            None
        """
        if event.data is None:
            self.top.print_on_log("No Search event\n")
        elif event.data == "search":
            #self.btn_scan.Enable(False)
            self.btn_scan.Unbind(wx.EVT_BUTTON)
            self.get_devices()
            wx.GetApp().Yield()
            self.btn_scan.Bind(wx.EVT_BUTTON, self.ScanDevice)
        elif event.data == "print":
            self.top.print_on_log("Searching Devices ...\n")
        
    def get_devices(self):
        """
        Retrieve connected USB switch devices.

        Args:
            self: Reference to the current class instance.

        Returns:
            None
        """ 
        devlist = devControl.search_device(self.top)
        if (wx.IsBusy()):
            wx.EndBusyCursor()

        dev_list = devlist["switches"]
        if(len(dev_list) == 0):
            self.top.print_on_log("No Devices found\n")
            self.fst_lb.Clear()
        else:
            key_list = []
            val_list = []
            
            for i in range(len(dev_list)):
                key_list.append(dev_list[i]["port"])
                val_list.append(dev_list[i]["model"])
        
            self.fst_lb.Clear()
            for i in range(len(key_list)):
                str1 = val_list[i]+"("+key_list[i]+")"
                self.fst_lb.Append([str1])
                self.top.print_on_log(str1+"\n")

            if(len(key_list)):
                self.fst_lb.Select(0)
                self.btn_connect.Enable()
                # Device is found update in status bar Model(s) found
                self.top.UpdateSingle("Switch(s) found", 3)
            else:
                self.btn_connect.Disable()
                # Device is not found update in status bar No Models found
                self.top.UpdateSingle("No Switch found", 3)
    
    def DeviceAdd(self, evt):
        """
        Add selected devices to connection list.

        Args:
            self: Reference to the current class instance.
            evt: Button click event object.

        Returns:
            None
        """
        
        ilist = self.fst_lb.GetItems()
        slist = self.fst_lb.GetSelections()
        flist = []
        temp_list = []
        self.top.switch_list.clear()
        for i in slist:
            if i not in temp_list:
                temp_list.append(ilist[i])
                self.top.switch_list.append(ilist[i])

                self.scnd_lb.Clear()
                self.scnd_lb.AppendItems(self.top.switch_list)

   
    def ConnectDevice(self, evt):
        """
        Handle connect button action to initiate device connection.

        Args:
            self: Reference to the current class instance.
            evt: Button click event object.

        Returns:
            None
        """
        self.parent.EndModal(True)
        self.btn_connect.Disable()
        self.top.add_switch_dialogs()
       
    def connect_device(self):
        """
        Establish communication with selected USB switch.

        Args:
            self: Reference to the current class instance.

        Returns:
            None
        """
        # Combo box, device list is disable
        # self.fst_lb.Disable()
        self.scnd_lb.Disable()
        self.top.selPort, devname = self.get_selected_com()
        if devname == DEVICES[DEV_2301]:
            self.top.selBaud = 9600
        else:
            self.top.selBaud = 115200
        for i in range(len(DEVICES)):
            if devname == DEVICES[i]:
                self.top.selDevice = i
                break
        if devControl.connect_device(self.top):
            self.device_connected()
    
    def get_selected_com(self):
        """
        Retrieve selected COM port and device model.

        Args:
            self: Reference to the current class instance.

        Returns:
            tuple: (COM port, device model)
        """
        self.cval = self.fst_lb.GetItems()
        txt = self.cval.split("(")
        return txt[1].replace(")",""), txt[0]

    def device_connected(self):
        """
        Update UI and state after successful device connection.

        Args:
            self: Reference to the current class instance.

        Returns:
            None
        """
        # Set label button name as Disconnect
        self.btn_connect.SetLabel("Disconnect")
        self.top.device_connected()
        self.parent.EndModal(True)
           

    def OnClick (self, evt):
        """
        Handle mouse click event on dialog.

        Args:
            self: Reference to the current class instance.
            evt: Mouse event object.

        Returns:
            None
        """
        self.GetParent().OnOK(evt)
   
    def OnSize (self, evt):
        """
        Handle dialog resize event.

        Args:
            self: Reference to the current class instance.
            evt: Size event object.

        Returns:
            None
        """
        self.Layout()

def EVT_RESULT(win, func):
    """
    Bind custom result event to a handler function.

    Args:
        win: Target window object.
        func: Event handler function.

    Returns:
        None
    """
    win.Connect(-1, -1, EVT_RESULT_ID, func)    

# def get_devices(top):
#     devlist = devControl.search_device(top)
#     dev_list = devlist["devices"]

class ComDialog(wx.Dialog):
    """
    Dialog wrapper for USB switch communication window.

    This dialog embeds the ComWindow panel and manages
    modal interaction for USB switch search and connection.

    Attributes:
        top: Reference to main application controller.
        win: Embedded communication window instance.
    """
    def __init__ (self, parent, top):
        """
        Initialize USB switch communication dialog.

        Args:
            self: Reference to the current class instance.
            parent: Parent window reference.
            top: Application controller reference.

        Returns:
            None
        """
        wx.Dialog.__init__(self, parent, -1, "MCCI USB Switch",
                           size=wx.Size(100, 100),
                           style=wx.STAY_ON_TOP|wx.DEFAULT_DIALOG_STYLE,
                           name="MCCI USB Switch Search Dialog")

        self.top = top
        self.win = ComWindow(self, top)

        # Sizes the window to fit its best size.
        self.Fit()
        self.CenterOnParent(wx.BOTH)
    
    def OnOK (self, evt):
        """
        Handle dialog confirmation event.

        Args:
            self: Reference to the current class instance.
            evt: Event object.

        Returns:
            None
        """
    # Returns numeric code to caller
        self.EndModal(wx.ID_OK)
     
    def OnSize (self, evt):
        """
        Handle dialog resize event.

        Args:
            self: Reference to the current class instance.
            evt: Size event object.

        Returns:
            None
        """
        self.Layout()