##############################################################################
# 
# Module: serialLogWindow.py
#
# Description:
#     Scan the USB bus and get the list of devices attached
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
#    V4.3.0 Mon Jan 22 2024 17:00:00   Seenivasan V
#       Module created
##############################################################################

# Lib imports
import wx
import wx.adv
import sys


# Own modules
from uiGlobals import *
from datetime import datetime

import wx

from .wdpLogin import LoginFrame
from usb4tree import usb4parse
# import dummyusb4 as dumusb4

EADR = 'EvtAddDeviceRouter'
ERDR = 'EvtRemoveDeviceRouter'

PNPDD = 'pnpDeviceDescription'
MODEL = 'modelName'
PID = 'productId'
VID = 'vendorId'
VNAME = 'vendorName'
TID = 'topologyId'

DID = 'domainId'
CLS = 'currentLinkSpeed'
TLS = 'targetLinkSpeed'
TLW = 'targetLinkWidth'
NLW = 'negotiatedLinkWidth'

USB4RR = 'USB4 Root Router'
USB4R = 'USB4 Router'
USB4HR = 'USB4(TM) Host Router (Microsoft)'
TB3R = 'Thunderbolt 3(TM) Router'

IMG_LOGO = "mcci_logo.png"

SPEED_DICT = {"Unknown 0": "0 Gbp/s", "Gen 2": "10 Gbp/s", "Gen 3": "20 Gbp/s"}
WIDTH_DICT = {"Unknown 0": "0", "Single Lane": "1", "Dual Lane": "2", "Two Single Lanes": "2"}

MAX_LEVEL = 7

##############################################################################
# Utilities
##############################################################################
class Usb4TreeWindow(wx.Window):
    """
    A class logWindow with init method

    To show the all actions while handling ports of devices 
    """
    def __init__(self, parent, top):
        """
        logWindow values displayed for all Models 3201, 3141,2101 
        Args:
            self: The self parameter is a reference to the current .
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
            top: creates an object
        Returns:
            None
        """
        wx.Window.__init__(self, parent)
        # SET BACKGROUND COLOUR TO White
        self.SetBackgroundColour("White")
        self.SetMinSize((480,330))

        self.top = top
        self.parent = parent
        self.name = "usb4tree"

        self.totline = 0

        sb = wx.StaticBox(self, -1, "")

        self.vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)
        
        if sys.platform == "win32":

            self.btn_config = wx.Button(self, ID_BTN_SL_CONFIG, "Config",
                                        size=(60, -1))
            self.tool_tip = "Provide Windows Device Portal Login Credentials."
            self.btn_config.SetToolTip(self.tool_tip)
            self.btn_config.Bind(wx.EVT_BUTTON, self.OnLoginConfig)

        
        # self.tree = wx.TreeCtrl(self, style=wx.TR_DEFAULT_STYLE | wx.TR_MULTIPLE)
        # self.panel = wx.Panel(self)
        self.tree = wx.TreeCtrl(self,wx.TR_DEFAULT_STYLE)
        
        self.root = self.tree.AddRoot("MY COMPUTER USB4 Tree View")

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnItemSelect, self.tree)

        self.device_item = None
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.wait_flg = False

        # self.btn_config.Bind(wx.EVT_BUTTON, self.OnLoginConfig)
        # Bind the tooltip event
        self.tree.Bind(wx.EVT_TREE_ITEM_GETTOOLTIP, self.OnToolTip)
        
        if sys.platform == "win32":
            self.hbox.Add(30,0,0)
            self.hbox.Add(self.btn_config, 0, wx.ALIGN_LEFT | 
                                            wx.ALIGN_CENTER_VERTICAL)
       
        self.szr_top = wx.BoxSizer(wx.VERTICAL)
        
        self.szr_top.AddMany([
            (5,0,0),
            (self.tree, 1, wx.EXPAND),
            (5,0,0)
            ])

        self.vbox.AddMany([
            (self.hbox, 0, wx.ALIGN_LEFT),
            (10,5,0),
            (self.szr_top, 1, wx.EXPAND),
            (0,0,0)
            ])
        
        mythcos = sys.platform
        # if not top.parent.myrole['thc']:
        #     mythcos = self.top.parent.ucConfig['mynodes']["mythc"]["os"]

        self.usb4parse = usb4parse.create_usb4tb_parser(mythcos)


        # Set size of frame
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.Layout()

    def update_usb4_tree(self, usb4data):
        """
        Update the USB4 and Thunderbolt list based on List 
        """
        self.usb4parse.parse_usb4tb_data(usb4data)
        self.redrawu4tree(self.usb4parse.idata, self.usb4parse.ldata)
        
    def OnLoginConfig(self, e):
        """
        Opens the login configuration dialog.

        Parameters:
            e: The event triggering the method (not explicitly used).
        """
        dlg = LoginFrame(self, self)
        dlg.Show()

    # Tool tip 
    def OnToolTip(self, event):
        """
        Shows the VID and PID of attached USB4 tree view
        """
        item = event.GetItem()
        item_data = self.tree.GetItemPyData(item)
        if item_data:
            tooltip_text = str(item_data)
            event.SetToolTip(tooltip_text)

    # Delete all items except root items
    def DeleteAllItems(self):
        """
        Delete all item and TH4 or USB4 devices from Tree View 
        """
        root = self.tree.GetRootItem()
        if root.IsOk():
            self.tree.DeleteChildren(root)

    def OnItemSelect(self, event):
        """
        Handles the tree item selection event.

        Parameters:
            event (wx.TreeEvent): The tree selection event.
        """
        item = event.GetItem()
        text = self.tree.GetItemText(item)

    def redrawu4tree(self, idata, ldata):
        """
        Redrraw the Tree view N Levels of USB4 and Thunderbolt
        """
        self.DeleteAllItems()
        lkeys = list(ldata.keys())
        if 'level0' in lkeys:
            lobjdict = self.draw_level0_data(idata, ldata['level0'])
            for level in range(1,MAX_LEVEL):
                if 'level'+str(level) in lkeys:
                    lobjdict = self.draw_leveln_data(idata, ldata['level'+str(level)], lobjdict, level)

    # # Draw level 0 data
    def draw_level0_data(self, ddict, dlist):
        """
        Draw the Tree view 0 and 1 Levels of USB4 and Thunderbolt
        """
        objdict = {}
        for l0item in dlist:
            objdict[l0item] = self.tree.AppendItem(self.root, ""+ddict[l0item]["mname"]+" ("+ddict[l0item]["vname"]+")")
            if 'vid' in ddict[l0item] and 'pid' in ddict[l0item]:
                device_data = f"VID: {ddict[l0item]['vid']}, PID: {ddict[l0item]['pid']}"
                self.tree.SetItemPyData(objdict[l0item], device_data)
            if len(ddict[l0item]["ports"]) > 0:
                for pno in ddict[l0item]["ports"]:
                    objdict[l0item+","+str(pno)] = self.tree.AppendItem(objdict[l0item], "Port-"+str(pno))
        return objdict
    
    # # Draw level 1 to 6 data
    def draw_leveln_data(self, ddict, dlist, riobj, lidx):
        """
        Draw the Tree view N Levels of USB4 and Thunderbolt
        """
        
        objlist = list(riobj.keys())
        for item in dlist:
            if item in objlist:
                cidx = item.split(',')[lidx]
                self.tree.SetItemText(riobj[item], "Port-"+cidx+", "+ddict[item]["mname"]+" ("+ddict[item]["vname"]+")")
                if 'vid' in ddict[item] and 'pid' in ddict[item]:
                    device_data = f"VID: {ddict[item]['vid']}, PID: {ddict[item]['pid']}"
                    self.tree.SetItemPyData(riobj[item], device_data)
                if len(ddict[item]["ports"]) > 0:
                    for pno in ddict[item]["ports"]:
                        riobj[item+","+str(pno)] = self.tree.AppendItem(riobj[item], "Port-"+str(pno))
        return riobj