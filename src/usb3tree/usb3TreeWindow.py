##############################################################################
# 
# Module: USB3Treewindow.py
#
# Description:
#     Scan the USB bus and get the list of devices attached
#
# Author:
#     Vinay N, MCCI Corporation Mar 2024
#
# Revision history:
#      V4.3.1 Mon Apr 15 2024 17:00:00   Seenivasan V 
#       Module created
##############################################################################
import wx
import sys

# Own modules
from uiGlobals import *
from datetime import datetime
from usb3tree import usb3parse

MAX_LEVEL = 20

usbSpeed = {0: "LowSpeed", 1: "FullSpeed", 2: "HighSpeed", 3: "SuperSpeed", 4:"SuperSpeed Plus",5:"SuperSpeed Plus"}
usbClass = {
    0: "Unknown", 1: "Audio", 2: "CDC-COM", 3: "HID", 5: "Physical",
    6: "Image", 7: "Printer", 8: "Mass Storage", 9: "Hub",
    10: "CDC-Data", 11: "Smart Card", 13: "Content Security",
    14: "Video", 15: "Personal Healthcare", 16: "Audio/Video Devices",
    17: "Billboard Device", 18: "Type-C Bridge", 
    220: "Diagnostic Devices", 224: "Wireless Controller", 
    239: "Miscellaneous", 254: "Application Specific",
    255: "Vendor Specific",
    # Add new class IDs and their names here
    # For example:
    # 220: "Diagnostic Devices",
    # 224: "Wireless Controller",
    # 239: "Miscellaneous",
    # 254: "Application Specific",
    # 255: "Vendor Specific"
}


##############################################################################
# Utilities
##############################################################################
class Usb3TreeWindow(wx.Window):

    def __init__(self, parent, top):

        wx.Window.__init__(self, parent)
        # SET BACKGROUND COLOUR TO White
        self.SetBackgroundColour("White")
        self.SetMinSize((480, 330))

        self.top = top
        self.parent = parent
        self.name = "usb3tree"

        # Create the tree control
        self.tree = wx.TreeCtrl(self, wx.TR_DEFAULT_STYLE)
        self.root = self.tree.AddRoot("MY COMPUTER USB3 Tree View")

        # Bind events
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnItemSelect, self.tree)

        self.device_item = None
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.tree, 1, wx.EXPAND)

        # Create USB3 parser instance
        mythcos = sys.platform
        self.usb3parse = usb3parse.create_usb3tb_parser(mythcos)
        # Set size of frame
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.Layout()

    def update_usb3_tree(self, usb3data):
        self.usb3parse.parse_usb3tb_data(usb3data)
        self.redraw_usb3_tree(self.usb3parse.idata, self.usb3parse.ldata)
    
    def delete_all_items(self):
        root = self.tree.GetRootItem()
        if root.IsOk():
            self.tree.DeleteChildren(root)
        
    def OnItemSelect(self, event):
        # Define OnItemSelect method here
        item = event.GetItem()
        text = self.tree.GetItemText(item)

    def redraw_usb3_tree(self, idata, ldata):
        self.delete_all_items()
        lkeys = list(ldata.keys())
        if 'level1' in lkeys:  # Check for USB3 devices under the correct key
            lobjdict = self.draw_level0_data(idata, ldata['level1'])  # Call draw_level0_data with USB3 devices
            for level in range(2, MAX_LEVEL):
                if 'level'+str(level) in lkeys:
                    lobjdict = self.draw_leveln_data(idata, ldata['level'+str(level)], lobjdict, level)
        else:
            print("No USB3 devices found in ldata")
    
    def draw_level0_data(self, ddict, dlist):
        parsed_data = []
        for key, info in ddict.items():
            vid = hex(int(info.get('vid')))
            pid = hex(int(info.get('pid')))
            speed = usbSpeed.get(info["speed"] - 1, "unknown")
            mport = info.get('mport', '')
            parsed_data.append((vid, pid, speed, mport))
            
        for key, info in ddict.items():
            vid = hex(int(info.get('vid')))
            pid = hex(int(info.get('pid')))
            speed = usbSpeed.get(info["speed"] - 1, "unknown")
            mport = info.get('mport', '')
            
            node_text = f"VID:{vid}, PID:{pid}, Speed:{speed}"
            ports = [port.strip() for port in mport.strip('()').split(',') if port.strip()]
            node_text = f"VID:{vid}, PID:{pid}, Speed:{speed}"
            
            parent = self.tree.GetRootItem()  # Assuming self.tree is your TreeCtrl instance
            for port in ports:
                item, cookie = self.tree.GetFirstChild(parent)
                found = False
                while item.IsOk():
                    text = self.tree.GetItemText(item)
                    if text.startswith(f"Port: {port}"):
                        parent = item
                        found = True
                        break
                    item, cookie = self.tree.GetNextChild(parent, cookie)
                if not found:
                    # parent = self.tree.AppendItem(parent, f"Port: {port}")
                    parent = self.tree.AppendItem(parent, f"Port: {port} {node_text}")
        return parent
    
    def draw_leveln_data(self, ddict, dlist, riobj, lidx):
        objlist = list(riobj.keys())
        for item in dlist:
            if item in objlist:
                cidx = item.split(',')[lidx]
                vid = ddict[item]['vid']
                pid = ddict[item]['pid']
                node_text = f"{item} (VID: {vid}, PID: {pid})"
                parent_item = self.get_parent_item(self.root, item, lidx)
                self.tree.AppendItem(parent_item, node_text)
        return riobj

    def get_parent_item(self, parent, item, level):
        if level == 0:
            return parent
        else:
            parent_text = item.split(',')[level-1]
            children, cookie = self.tree.GetFirstChild(parent)
            while children.IsOk():
                if self.tree.GetItemText(children).split(',')[level-1] == parent_text:
                    return children
                children, cookie = self.tree.GetNextChild(parent, cookie)
            return self.get_parent_item(parent, item, level-1)