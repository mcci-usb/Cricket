# -*- coding: utf-8 -*-
##############################################################################
#
# Module: aboutDialog.py
#
# Description:
#     Dialog to display application information including
#     logo, version details, and copyright text.
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
# Revision history:
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
##############################################################################

# Built-in imports
import os

# Lib imports
import wx

# Own modules
from uiGlobals import *

##############################################################################
# Utilities
##############################################################################

class AboutWindow(wx.Window):
    """
    About dialog content window.

    Displays application logo, version,
    and copyright information.

    Attributes:
        top: Reference to top-level UI controller.
        image: Logo bitmap widget.
        text: List of static text widgets.
    """

    def __init__(self, parent, top):
        """
        Initialize About window UI components.

        Args:
            self: Reference to the current instance.
            parent: Parent dialog window.
            top: Top-level application object.

        Returns:
            None

        Raises:
            None
        """
        wx.Window.__init__(
            self,
            parent,
            -1,
            size=wx.Size(100, 100),
            style=wx.CLIP_CHILDREN,
            name="About",
        )

        self.top = top

        base = os.path.abspath(os.path.dirname(__file__))
        bmp = wx.Image(base + "/icons/" + IMG_LOGO).ConvertToBitmap()

        self.image = wx.StaticBitmap(
            self, ID_ABOUT_IMAGE, bmp, wx.DefaultPosition, wx.DefaultSize
        )

        # Copyright / Version Text
        self.text = [
            wx.StaticText(self, -1, VERSION_NAME),
            wx.StaticText(self, -1, VERSION_ID),
            wx.StaticText(self, -1, VERSION_STR),
            wx.StaticText(self, -1, VERSION_COPY, style=wx.ALIGN_CENTER),
            wx.StaticText(self, -1, "\nAll rights reserved.\n\n"),
        ]

        self.image.Bind(wx.EVT_LEFT_UP, self.OnClick)

        for i in self.text:
            i.Bind(wx.EVT_LEFT_UP, self.OnClick)

        self.Bind(wx.EVT_LEFT_UP, self.OnClick)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        # Layout
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        widgets = [(self.image, 1, wx.CENTER)]

        for i in self.text:
            widgets.extend([(i, 0, wx.CENTER)])

        self.sizer.AddMany(widgets)

        self.SetSizerAndFit(self.sizer)
        self.SetAutoLayout(True)

    def OnClick(self, evt):
        """
        Handle click events on About dialog widgets.

        Args:
            self: Reference to the current instance.
            evt: Mouse click event object.

        Returns:
            None

        Raises:
            None
        """
        self.GetParent().OnOK(evt)

    def OnSize(self, evt):
        """
        Handle window resize events.

        Args:
            self: Reference to the current instance.
            evt: Size event object.

        Returns:
            None

        Raises:
            None
        """
        self.Layout()

class AboutDialog(wx.Dialog):
    """
    About dialog container window.

    Wraps AboutWindow and manages dialog
    behavior such as centering and closing.
    """

    def __init__(self, parent, top):
        """
        Initialize About dialog.

        Args:
            self: Reference to the current instance.
            parent: Parent frame window.
            top: Top-level application object.

        Returns:
            None

        Raises:
            None
        """
        wx.Dialog.__init__(
            self,
            parent,
            -1,
            "About",
            size=wx.Size(100, 100),
            style=wx.STAY_ON_TOP | wx.DEFAULT_DIALOG_STYLE,
            name="About Dialog",
        )

        self.top = top
        self.win = AboutWindow(self, top)

        self.Fit()
        self.CenterOnParent(wx.BOTH)

    def OnOK(self, evt):
        """
        Handle OK / close action for About dialog.

        Args:
            self: Reference to the current instance.
            evt: Event object triggering the close.

        Returns:
            None

        Raises:
            None
        """
        self.EndModal(wx.ID_OK)

    def OnSize(self, evt):
        """
        Handle dialog resize events.

        Args:
            self: Reference to the current instance.
            evt: Size event object.

        Returns:
            None

        Raises:
            None
        """
        self.Layout()
