##############################################################################
# 
# Module: rightPanel.py
#
# Description:
#     Manage USB tree views and DUT log panels.
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
# Revision history:
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
##############################################################################

# Lib imports
import wx

# Own modules
from features.dut import dutLogWindow
from usb4tree import usb4TreeWindow
from usb4tree import usb3TreeWindow

##############################################################################
# Utilities
##############################################################################
class RightPanel(wx.Panel):
    """
    Right panel UI container.

    Displays USB4/USB3 tree views and DUT log
    windows using notebook layouts.

    Attributes:
        parent: Parent window reference.
        usb_notebook: Notebook for USB trees.
        dut_notebook: Notebook for DUT logs.
    """

    def __init__(self, parent):
        """
        Initialize RightPanel layout.

        Args:
            parent: Parent window reference.
        """
        super(RightPanel, self).__init__(parent)

        self.SetBackgroundColour("White")
        self.parent = parent

        # USB Tree Notebook (Top Section)
        self.usb_notebook = wx.Notebook(self)

        # DUT Notebook (Bottom Section)
        self.dut_notebook = wx.Notebook(self)

        # Layout Sizers
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.top_sizer.Add(self.usb_notebook, 1, wx.EXPAND)
        self.bottom_sizer.Add(self.dut_notebook, 1, wx.EXPAND)

        self.main_sizer.Add(
            self.top_sizer,
            1,
            wx.EXPAND | wx.ALL,
            5,
        )
        self.main_sizer.Add(
            self.bottom_sizer,
            1,
            wx.EXPAND | wx.ALL,
            5,
        )

        self.SetSizer(self.main_sizer)
        self.Layout()

    # ------------------------------------------------------------------
    # Panel Initialization
    # ------------------------------------------------------------------
    def init_my_panel(self, pdict):
        """
        Initialize right panel notebooks.

        Args:
            pdict: Panel configuration dictionary.
        """
        rpdict = pdict["rpanel"]
        dutdict = pdict["dut"]

        # Clear notebooks
        self.usb_notebook.DeleteAllPages()
        self.dut_notebook.DeleteAllPages()

        usb4_selected = True
        usb3_selected = True

        dut_selected = any(
            rpdict.get(dut, False)
            for dut in dutdict.keys()
        )

        # Populate USB tree notebook
        if usb4_selected:
            usb4_page = usb4TreeWindow.Usb4TreeWindow(
                self.usb_notebook,
                self.parent,
            )
            self.usb_notebook.AddPage(
                usb4_page,
                "USB4 Tree Window",
            )

        if usb3_selected:
            usb3_page = usb3TreeWindow.Usb3TreeWindow(
                self.usb_notebook,
                self.parent,
            )
            self.usb_notebook.AddPage(
                usb3_page,
                "USB Tree Window",
            )

        # Populate DUT notebook
        if dut_selected:
            for dut in dutdict.keys():
                if rpdict.get(dut, False):
                    dut_page = dutLogWindow.DutLogWindow(
                        self.dut_notebook,
                        self.parent,
                        {dut: dutdict[dut]},
                    )
                    self.dut_notebook.AddPage(
                        dut_page,
                        dut.upper(),
                    )

        # Adjust layout
        self.main_sizer.Show(
            self.top_sizer,
            usb4_selected or usb3_selected,
        )
        self.main_sizer.Show(
            self.bottom_sizer,
            dut_selected,
        )

        if dut_selected and not (
            usb4_selected or usb3_selected
        ):
            self.main_sizer.SetItemMinSize(
                self.bottom_sizer,
                -1,
                -1,
            )
        else:
            self.main_sizer.SetItemMinSize(
                self.bottom_sizer,
                -1,
                100,
            )

        self.Layout()

    # ------------------------------------------------------------------
    # Updates
    # ------------------------------------------------------------------
    def update_my_panel(self, pdict):
        """
        Refresh right panel layout.

        Args:
            pdict: Panel configuration dictionary.
        """
        self.init_my_panel(pdict)

    def update_usb4_tree(self, msusb4):
        """
        Update USB4 tree view.

        Args:
            msusb4: USB4 device data.
        """
        for i in range(self.usb_notebook.GetPageCount()):
            page = self.usb_notebook.GetPage(i)

            if isinstance(
                page,
                usb4TreeWindow.Usb4TreeWindow,
            ):
                page.update_usb4_tree(msusb4)
                break

    def update_usb3_tree(self, msusb3):
        """
        Update USB3 tree view.

        Args:
            msusb3: USB3 device data.
        """
        for i in range(self.usb_notebook.GetPageCount()):
            page = self.usb_notebook.GetPage(i)

            if isinstance(
                page,
                usb3TreeWindow.Usb3TreeWindow,
            ):
                page.update_usb3_tree(msusb3)
                break

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    def print_on_log(self, data):
        """
        Print data to DUT log panels.

        Args:
            data: Log message.
        """
        pass
