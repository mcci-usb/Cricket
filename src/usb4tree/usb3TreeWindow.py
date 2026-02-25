# -*- coding: utf-8 -*-
##############################################################################
#
# Module: usb3TreeWindow.py
#
# Description:
#     This module provides a graphical Tree View representation of
#     USB 3.x topology connected to the host system.
#
#     It scans, parses, and visualizes USB Host Controllers, Hubs,
#     and Peripheral devices in a hierarchical structure using
#     wx.TreeCtrl.
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
# Revision history:
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
#
##############################################################################
import wx
import sys

# Own modules
from uiGlobals import *
from datetime import datetime
from usb4tree import usb3parse

MAX_LEVEL = 7

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
   
}


##############################################################################
# Utilities
##############################################################################
class Usb3TreeWindow(wx.Window):
    """
    USB3 Tree View Window.

    Description:
        This class creates a graphical tree representation of
        USB 3.x device topology connected to the host system.

        The tree displays hierarchical relationships between:

            • Host Controllers
            • USB Hubs
            • Connected Peripheral Devices

        Each node includes device metadata such as:

            • Vendor ID (VID)
            • Product ID (PID)
            • Device Speed
            • USB Class
            • Port Number

    Parameters:
        parent (wx.Window):
            Parent window reference.

        top (object):
            Top-level controller reference used for
            application-level interactions.

    Attributes:
        tree (wx.TreeCtrl):
            Tree control used to render USB topology.

        root (wx.TreeItemId):
            Root node labeled
            "MY COMPUTER USB Tree View".

        usb3parse (object):
            Platform-specific USB3 parser instance.
    """

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
        self.root = self.tree.AddRoot("MY COMPUTER USB Tree View")

        # Bind events
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnItemSelect, self.tree)

        self.device_item = None
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.tree, 1, wx.EXPAND)

        # Create USB3 parser instance
        mythcos = sys.platform
        self.usb3parse = usb3parse.create_usb3tb_parser(mythcos)
        # print("usb3parse--->", self.usb3parse)

        # Set size of frame
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.Layout()

    def update_usb3_tree(self, usb3data):
        """
        Update USB3 Tree View with latest scan data.

        Description:
            Parses the enumerated USB3 device list and redraws
            the Tree View hierarchy.

            This method acts as the entry point for refreshing
            the USB3 topology display.

        Args:
            usb3data (list):
                Raw USB3 enumeration data obtained from
                the USB device enumerator.

        Returns:
            None
        """
        self.usb3parse.parse_usb3tb_data(usb3data)

        # Redraw the USB3 Tree View with the new data
        self.redraw_usb3_tree(self.usb3parse.idata, self.usb3parse.ldata)

    def redraw_usb3_tree(self, idata, ldata):
        """
        Redraw the USB3 topology tree.

        Description:
            Clears the existing Tree View and reconstructs
            it using parsed USB3 hierarchy data.

            Devices are rendered level-wise based on their
            topology depth.

        Args:
            idata (dict):
                Parsed USB3 item data.

            ldata (dict):
                Level-organized USB3 topology data.

        Returns:
            None
        """
        self.delete_all_items()
        lkeys = list(ldata.keys())
        if 'level0' in lkeys:  # Check for USB3 devices under the correct key
            self.draw_level0_data(idata, ldata['level0'])  # Call draw_level0_data with USB3 devices
        elif 'level1' in lkeys:  # Check for USB3 devices under the correct key
            self.draw_level0_data(idata, ldata['level1'])
        elif 'level2' in lkeys:  # Check for USB3 devices under the correct key
            self.draw_level0_data(idata, ldata['level2'])
        elif 'level3' in lkeys:  # Check for USB3 devices under the correct key
            self.draw_level0_data(idata, ldata['level3'])
        elif 'level4' in lkeys:  # Check for USB3 devices under the correct key
            self.draw_level0_data(idata, ldata['level4'])
        else:
            print("No USB3 devices found in ldata")

    def OnItemSelect(self, event):
        """
        Handle Tree Item selection event.

        Description:
            Triggered when a user selects a device node
            in the USB3 Tree View.

            Can be extended to display additional device
            metadata such as descriptors or logs.

        Args:
            event (wx.TreeEvent):
                Tree selection event object.

        Returns:
            None
        """
        # Define OnItemSelect method here
        item = event.GetItem()
        text = self.tree.GetItemText(item)
    
    def draw_level0_data(self, ddict, dlist):
        """
        Draw Level-0 USB3 devices in Tree View.

        Description:
            Renders top-level USB3 devices including
            Host Controllers, Hubs, and Peripherals.

            Each node displays:

                • Port Number
                • USB Class Name
                • VID / PID
                • Device Speed

            Child port nodes are created for hub devices.

        Args:
            ddict (dict):
                Parsed USB3 device dictionary.

            dlist (list):
                List of Level-0 topology keys.

        Returns:
            None
        """

        for item in dlist:
            vid = hex(int(ddict[item]['vid']))  # Convert VID to hexadecimal
            pid = hex(int(ddict[item]['pid']))  # Convert PID to hexadecimal
            speed = usbSpeed.get(ddict[item]['speed'], "Unknown")  # Get speed from usbSpeed dictionary
            ifc = ddict[item]['ifc']  # Get the interface code(s)
            class_name = "Unknown"  # Default USB class name
            port_no = ddict[item].get('port', 'Unknown')  # Get port number or default to 'Unknown' if not present
            # Iterate over interface codes to find the USB class
            for ifc_code in ifc:
                if ifc_code in usbClass:
                    class_name = usbClass[ifc_code]
                    break  # Stop searching if USB class is found
            node_text = f"[port {port_no}] {class_name} (VID: {vid}, PID: {pid}, Speed: {speed})"
            hub_node = self.tree.AppendItem(self.root, node_text)  # Add hub node
            # Check if the device is a hub and has ports
            if 'ports' in ddict[item]:
                for port in ddict[item]['ports']:
                    port_no = port.get('port', 'Unknown')  # Get port number or default to 'Unknown' if not present
                    port_vid = hex(int(port['vid']))
                    port_pid = hex(int(port['pid']))
                    port_speed = usbSpeed.get(port['speed'], "Unknown")
                    port_text = f"[port {port_no}] {class_name} (VID: {port_vid}, PID: {port_pid}, Speed: {port_speed})"
                    self.tree.AppendItem(hub_node, port_text)  # Add port node as child of the hub

    def draw_leveln_data(self, ddict, dlist, lidx):
        """
        Draw deeper USB3 topology levels.

        Description:
            Adds child device nodes under their
            respective parent hubs based on topology
            depth.

        Args:
            ddict (dict):
                Parsed USB3 device data.

            dlist (list):
                Device keys at the specified level.

            lidx (int):
                Current topology level index.

        Returns:
            None
        """
        for item in dlist:
            cidx = item.split(',')[lidx]
            vid = ddict[item]['vid']
            pid = ddict[item]['pid']
            node_text = f"{item} (VID: {vid}, PID: {pid})"
            parent_item = self.get_parent_item(self.root, item, lidx)
            self.tree.AppendItem(parent_item, node_text)

    def get_parent_item(self, parent, item, level):
        """
        Locate parent node for a USB3 device.

        Description:
            Traverses the Tree View hierarchy to
            identify the correct parent node where
            the device should be attached.

        Args:
            parent (wx.TreeItemId):
                Starting parent node.

            item (str):
                Device topology key.

            level (int):
                Current topology depth.

        Returns:
            wx.TreeItemId:
                Matching parent tree node.
        """
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

    def delete_all_items(self):
        """
        Clear all USB3 nodes from Tree View.

        Description:
            Removes all child items under the root
            node before redrawing updated USB3
            topology data.

            The root node remains intact.

        Args:
            None

        Returns:
            None
        """
        root = self.tree.GetRootItem()
        if root.IsOk():
            self.tree.DeleteChildren(root)
