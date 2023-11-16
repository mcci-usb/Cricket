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
#    V4.0.0 Wed May 25 2023 17:00:00   Seenivasan V
#       Module created
##############################################################################

# Lib imports
import wx
import wx.adv

import threading

import usbDev
import thControl

# import wx
import json


# Own modules
from uiGlobals import *
from datetime import datetime

import wx

from wdpLogin import LoginFrame


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

        self.totline = 0

        sb = wx.StaticBox(self, -1, "USB4 Tree View")

        self.vbox = wx.StaticBoxSizer(sb, wx.VERTICAL)

        self.btn_config = wx.Button(self, ID_BTN_SL_CONFIG, "Config",
                                        size=(60, -1))

        
        # self.tree = wx.TreeCtrl(self, style=wx.TR_DEFAULT_STYLE | wx.TR_MULTIPLE)
        # self.panel = wx.Panel(self)
        self.tree = wx.TreeCtrl(self,wx.TR_DEFAULT_STYLE)
        
        self.root = self.tree.AddRoot("MY COMPUTER USB4 Tree View")

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnItemSelect, self.tree)

        self.device_item = None
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.wait_flg = False

        self.btn_config.Bind(wx.EVT_BUTTON, self.OnLoginConfig)
        # Bind the tooltip event
        self.tree.Bind(wx.EVT_TREE_ITEM_GETTOOLTIP, self.OnToolTip)
        

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

        print("USB4 Tree View Layout Added")
        # self.btn_ref.Bind(wx.EVT_BUTTON, self.RefreshUsbBus)

        # Set size of frame
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.Layout()


    def OnItemSelect(self, event):
        """
        Handles the tree item selection event.

        Parameters:
            event (wx.TreeEvent): The tree selection event.
        """
        item = event.GetItem()
        text = self.tree.GetItemText(item)
        # print("SELECTED ITEM: {text}")

    
    def print_on_log(self, data):
        """
        Prints data on the log and updates the UI tree.

        Parameters:
            data: The raw data to be processed and displayed.
        """
        idata = self.get_item_data(data)
        ldata = self.get_level_data(idata)
        self.redrawu4tree(idata, ldata)


    def OnLoginConfig(self, e):
        """
        Opens the login configuration dialog.

        Parameters:
            e: The event triggering the method (not explicitly used).
        """
        dlg = LoginFrame(self, self)
        dlg.Show()

    def get_level_data(self, u4tbuf):
        """
        Organizes data based on levels and returns a dictionary.

        Parameters:
            u4tbuf: The input data dictionary to be processed.

        Returns:
            dict: A dictionary organizing data items based on their level.
        """
        rkarr = list(u4tbuf.keys())
        pdict = {}
        for rkitem in rkarr:
            lcnt = rkitem.count(',')
            kl = list(pdict.keys())
            if 'level'+str(lcnt) in kl:
                pdict['level'+str(lcnt)].append(rkitem)
            else:
                pdict['level'+str(lcnt)] = [rkitem]
        return pdict
    

    def redrawu4tree(self, idata, ldata):
        """
        Redraws the UI tree based on item and level data.

        Parameters:
            idata: The item data dictionary.
            ldata: The level data dictionary.
        """
        self.DeleteAllItems()
        lkeys = list(ldata.keys())
        if 'level0' in lkeys:
            lobjdict = self.draw_level0_data(idata, ldata['level0'])
            for level in range(1,MAX_LEVEL):
                if 'level'+str(level) in lkeys:
                    lobjdict = self.draw_leveln_data(idata, ldata['level'+str(level)], lobjdict, level)

    
    def draw_level0_data(self, ddict, dlist):
        """
        Draws level 0 data in the UI tree.

        Parameters:
            ddict: The item data dictionary.
            dlist: The list of items at level 0.

        Returns:
            dict: A dictionary mapping item identifiers to their corresponding UI tree nodes.
        """
        objdict = {}
        for l0item in dlist:
            objdict[l0item] = self.tree.AppendItem(self.root, ""+ddict[l0item]["mname"]+" ("+ddict[l0item]["vname"]+")")
            device_data = f"VID: {ddict[l0item]['vid']}, PID: {ddict[l0item]['pid']}"
            self.tree.SetItemData(objdict[l0item], device_data)
            if len(ddict[l0item]["ports"]) > 1:
                for pno in ddict[l0item]["ports"]:
                    objdict[l0item+","+str(pno)] = self.tree.AppendItem(objdict[l0item], "Port-"+str(pno))
        return objdict
    
    
    def draw_leveln_data(self, ddict, dlist, riobj, lidx):
        """
        Draws data for levels greater than 0 in the UI tree.

        Parameters:
            ddict: The item data dictionary.
            dlist: The list of items at the current level.
            riobj: The dictionary of existing UI tree nodes from the previous level.
            lidx: The index representing the current level.

        Returns:
            dict: A dictionary mapping updated item identifiers to their corresponding UI tree nodes.
        """
        objlist = list(riobj.keys())
        for item in dlist:
            if item in objlist:
                # print("Obj already there: need to edit Label", item)
                cidx = item.split(',')[lidx]
                self.tree.SetItemText(riobj[item], "Port-"+cidx+", "+ddict[item]["mname"]+" ("+ddict[item]["vname"]+")")
                device_data = f"VID: {ddict[item]['vid']}, PID: {ddict[item]['pid']}"
                self.tree.SetItemData(riobj[item], device_data)
                if len(ddict[item]["ports"]) > 1:
                    for pno in ddict[item]["ports"]:
                        riobj[item+","+str(pno)] = self.tree.AppendItem(riobj[item], "Port-"+str(pno))
        return riobj
    
    
    def get_item_data(self, msg):
        """
        Extracts USB4 item data from the input message.

        Parameters:
            msg (dict): The input message containing USB4 events.

        Returns:
            dict: A dictionary mapping unique identifiers to USB4 item data.
        """
        usb4e = msg["events"]
        pu4dict = {}

        for i in range(0, len(usb4e)):
            if usb4e[i]["eventKind"] == EADR:
                if PNPDD in usb4e[i] and "ufp" in usb4e[i]:
                    if not "Root Router" in usb4e[i][PNPDD] and not "Host Router" in usb4e[i][PNPDD]:
                        mydict = {}
                        mydict["desc"] = usb4e[i][PNPDD]
                        mydict["mname"] = usb4e[i][MODEL]
                        mydict["vname"] = usb4e[i][VNAME]
                        mydict["vid"] = usb4e[i][VID]
                        mydict["pid"] = usb4e[i][PID]
                        mydict["ports"] = []

                        ikeys = list(usb4e[i].keys())
                        if 'dfps' in ikeys:
                            plist =  usb4e[i]['dfps']
                            if len(plist) > 1:
                                for item in plist:
                                    mydict["ports"].append(item["portNumber"])
                        
                        # u4dict["item"+str(icnt)] = mydict
                        # icnt = icnt + 1
                        
                        tarr = usb4e[i][TID]
                        tarr = tarr[:tarr.index(0)]
                        idxstr = ','.join([str(aitem) for aitem in tarr])
                        pu4dict[idxstr] = mydict
        return pu4dict
    
        
    def OnToolTip(self, event):
        """
        Displays tooltips for tree items based on stored item data.

        Parameters:
            event (wx.TreeEvent): The tree event triggering the tooltip display.
        """
        item = event.GetItem()
        item_data = self.tree.GetItemData(item)
        if item_data:
            tooltip_text = str(item_data)
            event.SetToolTip(tooltip_text)


    def DeleteAllItems(self):
        """
        Deletes all child items under the root in the tree control.

        Clears the tree control by removing all child items under the root.

        Note: This method does not delete the root item itself.

       """
        root = self.tree.GetRootItem()
        if root.IsOk():
            self.tree.DeleteChildren(root)
