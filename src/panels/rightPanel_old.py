##############################################################################
# 
# Module: right.py
#
# Description:
#     Update the Right panel
#
# Author:
#     Seenivasan V, MCCI Corporation Mar 2020
#
# Revision history:
#    V4.3.1 Mon Apr 15 2024 17:00:00   Seenivasan V 
#       Module created
##############################################################################

from uiGlobals import *
from usb4tree import usb4TreeWindow
from usb3tree import usb3TreeWindow

# from features.mode import loopWindow
# from features.mode import autoWindow
# from features.mode import batchWindow

from features.mode import dutLogWindow

# from features.dut import dutLogWindow
from sys import platform

class RightPanel(wx.Panel):
    """
    A class UiPanel with init method
    the UiPanel navigate to UIApp name
    """ 
    def __init__(self, parent, top, portno):
        super(RightPanel, self).__init__(parent)

        self.SetMinSize((600, 400))  # Set minimum size to control resizing

        wx.GetApp().SetAppName("Cricket")

        self.parent = top
        self.SetBackgroundColour('White')
        
        #-----------------------------------
        self.slobj = []
        self.objtype = []
        self.objdict = {"dut1": False, "dut2": False}
        
        #-----------------------------------

        self.font_size = DEFAULT_FONT_SIZE

        if platform == "darwin":
            self.font_size = MAC_FONT_SIZE

        self.SetFont(wx.Font(self.font_size, wx.SWISS, wx.NORMAL, wx.NORMAL, False,'MS Shell Dlg 2'))

        self.portno = portno

        self.hboxdl = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxdll = wx.BoxSizer(wx.HORIZONTAL)
        
        # p = wx.Panel(self)
        nb = wx.Notebook(self)

        self.usb4Pan = usb4TreeWindow.Usb4TreeWindow(nb, top)
        self.usbPan = usb3TreeWindow.Usb3TreeWindow(nb, top)
        # self.usbPan = None
        
        

        nb.AddPage(self.usb4Pan, "USB4 Tree View")
        nb.AddPage(self.usbPan, "USB3 Tree View")
        
        
        
        nb2 = wx.Notebook(self)
        # self.autoPan = autoWindow.AutoWindow(nb2, top)
        # self.loopPan = loopWindow.LoopWindow(nb2, top)
        self.dutPan = dutLogWindow.DutLogWindow(nb2, top, None)
        
        # nb2.AddPage(self.autoPan, "DUT Logwindow-1")
        # nb2.AddPage(self.loopPan, "DUT Logwindow-2")
        nb2.AddPage(self.dutPan, "DUT Logwindow-1")
        nb2.AddPage(self.dutPan, "DUT Logwindow-2")
        
        
        self.hboxdl.Add(nb, 1, wx.EXPAND)
        self.hboxdll.Add(nb2, 1, wx.EXPAND)
        # self.hboxdll = wx.BoxSizer(wx.HORIZONTAL)
        
        self.vboxl = wx.BoxSizer(wx.VERTICAL)
        self.vboxl.Add((0, 20), 0, wx.EXPAND)
        self.vboxl.Add(self.hboxdl, 1, wx.ALIGN_LEFT | wx.EXPAND)
        self.vboxl.Add((0, 10), 0, 0)
        self.vboxl.Add(self.hboxdll, 1, wx.ALIGN_LEFT | wx.EXPAND)
        self.vboxl.Add((0, 10), 0, 0)
        
        self.hboxm = wx.BoxSizer(wx.HORIZONTAL)
        self.hboxm.Add((20, 0), 0, wx.EXPAND)
        self.hboxm.Add(self.vboxl, 1, wx.EXPAND)
        self.hboxm.Add((20, 0), 0, wx.EXPAND)
        
        self.SetSizer(self.hboxm)
        
        self.SetAutoLayout(True)
        self.hboxm.Fit(self)
        self.Layout()

    def update_usb4_tree(self, msusb4):
        self.usb4Pan.update_usb4_tree(msusb4)
        # self.usbPan.update_usb4_tree(msusb4)
    
    def update_usb3_tree(self, msusb3):
        self.usbPan.update_usb3_tree(msusb3)
        # self.usbPan.update_usb4_tree(msusb4)

    def add_switches(self, swlist):
        self.Layout()
    
    
    def print_on_log(self, data):
        pass
