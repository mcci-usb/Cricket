import wx
import sys

# Own modules
from uiGlobals import *
from datetime import datetime
from usb3tree import usb3parse

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
        # print("usb3parse--->", self.usb3parse)

        # Set size of frame
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.Layout()

    def update_usb3_tree(self, usb3data):
        self.usb3parse.parse_usb3tb_data(usb3data)

        # Redraw the USB3 Tree View with the new data
        self.redraw_usb3_tree(self.usb3parse.idata, self.usb3parse.ldata)

    def redraw_usb3_tree(self, idata, ldata):
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
        # Define OnItemSelect method here
        item = event.GetItem()
        text = self.tree.GetItemText(item)
    
    def draw_level0_data(self, ddict, dlist):
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
        for item in dlist:
            cidx = item.split(',')[lidx]
            vid = ddict[item]['vid']
            pid = ddict[item]['pid']
            node_text = f"{item} (VID: {vid}, PID: {pid})"
            parent_item = self.get_parent_item(self.root, item, lidx)
            self.tree.AppendItem(parent_item, node_text)

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

    def delete_all_items(self):
        root = self.tree.GetRootItem()
        if root.IsOk():
            self.tree.DeleteChildren(root)
