# -*- coding: utf-8 -*-
##############################################################################
#
# Module: usb4TreeWindow.py
#
# Description:
#     USB4 / Thunderbolt Tree View Window.
#
#     This module provides a graphical tree view representation of
#     connected USB4 and Thunderbolt devices.
#
#     Features:
#         • Displays hierarchical USB4 topology
#         • Shows device Vendor ID (VID) & Product ID (PID)
#         • Multi-level routing visualization
#         • Port-wise expansion
#         • Tooltip device information
#         • Windows Device Portal credential configuration (Windows only)
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
# Revision history:
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
#
##############################################################################

# Lib imports
import wx
import wx.adv
import sys
from datetime import datetime

# Own modules
from uiGlobals import *
from .wdpLogin import LoginFrame
from usb4tree import usb4parse

##############################################################################
# USB4 / Thunderbolt Constants
##############################################################################

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
    Summary:
        USB4 / Thunderbolt Tree Visualization Window.

    Description:
        Provides a hierarchical tree representation of USB4 and
        Thunderbolt topology detected on the host system.

        The tree displays:

        • Routers
        • End devices
        • Ports
        • Vendor & product identifiers
        • Multi-level routing paths

        Windows-specific features include:

        • Device Portal credential configuration
        • USB4 speed data integration

    Args:
        parent (wx.Window):
            Parent container window.

        top (object):
            Main frame / controller reference.

    Attributes:
        tree (wx.TreeCtrl):
            Tree control displaying USB4 hierarchy.

        root (wx.TreeItemId):
            Root node (“My Computer USB4 Tree View”).

        usb4parse (object):
            Platform-specific USB4 parser instance.

        btn_config (wx.Button):
            Credential configuration button (Windows only).
    """
    def __init__(self, parent, top):
        """
        Initialize USB4 Tree Window UI.

        Args:
            parent (wx.Window):
                Parent window reference.

            top (object):
                Top-level frame/controller reference.

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
       
        self.usb4parse = usb4parse.create_usb4tb_parser(mythcos)
        # Set size of frame
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.Layout()

    def update_usb4_tree(self, usb4data):
        """
        Update USB4 / Thunderbolt tree data.

        Args:
            usb4data (dict):
                Parsed USB4 event data.

        Returns:
            None
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
        Remove all USB4 / Thunderbolt devices from the Tree View.

        Description:
            This method clears the existing USB4 topology displayed
            in the TreeCtrl by deleting all child nodes under the
            root item.

            It is typically invoked before redrawing or refreshing
            the USB4 / Thunderbolt tree to ensure that outdated or
            previously scanned device entries are removed.

            The root node itself remains intact while all connected
            routers, ports, and peripheral devices beneath it are
            deleted.

        Workflow:
            1. Retrieve the root tree item.
            2. Validate that the root item exists.
            3. Delete all child nodes under the root.

        Args:
            None

        Returns:
            None

        Notes:
            • Used during USB4 rescan / refresh operations.
            • Prevents duplicate or stale topology entries.
            • Root label (e.g., "MY COMPUTER USB4 Tree View")
            is preserved.
        """
        root = self.tree.GetRootItem()
        if root.IsOk():
            self.tree.DeleteChildren(root)

    def OnItemSelect(self, event):
        """
        Handle USB4 Tree item selection events.

        Description:
            This event handler is triggered whenever a user selects
            an item in the USB4 / Thunderbolt Tree View.

            The method retrieves the selected tree node and extracts
            its display text. This information can be used for:

                • Displaying device/router details
                • Updating status/log panels
                • Showing VID/PID or topology metadata
                • Triggering additional UI actions

            Currently, the function captures the selected item and
            its label text for further processing or debugging.

        Args:
            event (wx.TreeEvent):
                The tree selection event generated when a user clicks
                or navigates to a node in the TreeCtrl.

        Returns:
            None

        Notes:
            • Item metadata (VID/PID) can be retrieved using
            self.tree.GetItemPyData(item) if previously set.
            • This handler can be extended to show device details
            in log/status panels.
        """
        item = event.GetItem()
        text = self.tree.GetItemText(item)

    def redrawu4tree(self, idata, ldata):
        """
        Redraw the complete USB4 / Thunderbolt Tree View hierarchy.

        Description:
            This method reconstructs the entire USB4 / Thunderbolt routing
            tree in the UI based on parsed topology data.

            The function performs the following steps:

                1. Clears all existing tree nodes except the root.
                2. Identifies available topology levels from parsed data.
                3. Draws Level-0 (Root / Host Routers).
                4. Iteratively renders deeper routing levels (Level-1 → N).
                5. Links child routers/devices to their parent ports.

            This ensures the tree view always reflects the latest
            USB4 / Thunderbolt topology after a scan/update.

        Args:
            idata (dict):
                Parsed USB4 item dictionary containing device/router
                metadata such as model, vendor, VID, PID and ports.

            ldata (dict):
                Level-organized topology dictionary where:

                    • 'level0' → Root routers
                    • 'level1' → Downstream routers/devices
                    • ...
                    • 'levelN' → Deep routing hierarchy

        Returns:
            None

        Notes:
            • MAX_LEVEL controls the deepest routing level rendered.
            • draw_level0_data() handles root rendering.
            • draw_leveln_data() handles deeper hierarchy rendering.
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
        Draw the Tree view for Level-0 and Level-1 USB4 / Thunderbolt devices.

        Description:
            This method renders the top hierarchy of the USB4 / Thunderbolt
            routing tree.

            • Level-0 represents Root / Host routers.
            • Level-1 represents directly connected downstream ports.

            The function:

                - Creates root child nodes for each detected router/device
                - Displays Model Name and Vendor Name
                - Attaches VID & PID as tooltip metadata
                - Adds child port nodes under each router

            This forms the base structure for deeper level rendering.

        Args:
            ddict (dict):
                Parsed USB4 device item dictionary containing
                model, vendor, VID, PID and port details.

            dlist (list):
                List of topology index keys representing
                Level-0 routing devices.

        Returns:
            dict:
                Dictionary mapping topology keys to
                wx.TreeCtrl item object references.

                This object map is later used to attach
                deeper routing levels.
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
    
    ## Draw level 1 to 6 data
    def draw_leveln_data(self, ddict, dlist, riobj, lidx):
        """
        Draw the Tree view for deeper USB4 routing levels.

        Description:
            This method renders hierarchical USB4 / Thunderbolt routing
            devices beyond Level-0 in the tree structure.

            It updates:

                • Port routing labels
                • Device names
                • Vendor & Product IDs
                • Child port nodes

            The hierarchy is derived from topology index paths.

        Args:
            ddict (dict):
                Parsed USB4 device item dictionary.

            dlist (list):
                List of routing topology keys for the level.

            riobj (dict):
                Previously created tree node object references.

            lidx (int):
                Current hierarchy level index.

        Returns:
            dict:
                Updated tree object reference dictionary.
        """
        
        objlist = list(riobj.keys())
        for item in dlist:
            if item in objlist:
                cidx = item.split(',')[lidx]
                self.tree.SetItemText(riobj[item], "Port-"+cidx+", "+ddict[item]["mname"]+" ("+ddict[item]["vname"]+")")
                if 'vid' in ddict[item] and 'pid' in ddict[item]:
                    device_data = f"VID: {ddict[item]['vid']}, PID: {ddict[item]['pid']}"
                    print("device_data:", device_data)
                    self.tree.SetItemPyData(riobj[item], device_data)
                if len(ddict[item]["ports"]) > 0:
                    for pno in ddict[item]["ports"]:
                        riobj[item+","+str(pno)] = self.tree.AppendItem(riobj[item], "Port-"+str(pno))
        return riobj