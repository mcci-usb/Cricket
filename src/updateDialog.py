# -*- coding: utf-8 -*-
##############################################################################
# 
# Module: updateDialog.py
#
# Description:
#     Dialog to display latest version of the application.
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
# Revision history:
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
#
##############################################################################

# Built-in imports
import os
import sys
import webbrowser

# Lib imports
import wx
import requests

# Own modules
from uiGlobals import *


##############################################################################
# Classes
##############################################################################
class AutoUpdate(wx.Window):
    """
    Display auto-update information window.

    Shows message about the latest available version
    and provides navigation to GitHub release page.

    Attributes:
        top: Top-level application object.
        parent: Parent window reference.
        latest_version: Latest available version string.
    """

    def __init__(self, parent, top, latest_version):
        """
        Initialize AutoUpdate window.

        Args:
            parent: Parent window.
            top: Top-level application object.
            latest_version: Latest available version.
        """
        wx.Window.__init__(
            self,
            parent,
            -1,
            size=wx.Size(900, 500),
            style=wx.STAY_ON_TOP | wx.DEFAULT_DIALOG_STYLE,
            name="About",
        )

        self.top = top
        self.parent = parent
        self.latest_version = latest_version

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        mytext = (
            "MCCI Cricket UI latest version "
            + latest_version
            + " is available on Github.\n"
            "Click OK for more details."
        )

        self.text = wx.StaticText(self, -1, mytext)

        self.btn_ok = wx.Button(self, -1, "OK")
        self.btn_cancel = wx.Button(self, -1, "Cancel")

        self.hbox1.Add(
            self.text,
            flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL,
            border=20,
        )

        self.hbox2.Add(self.btn_ok, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        self.hbox2.Add(self.btn_cancel, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        self.vbox.Add(self.hbox1, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        self.vbox.Add(self.hbox2, flag=wx.ALIGN_CENTER | wx.ALL, border=5)

        self.SetSizerAndFit(self.vbox)
        self.SetAutoLayout(True)

        self.btn_ok.Bind(wx.EVT_BUTTON, self.click_ok)
        self.btn_cancel.Bind(wx.EVT_BUTTON, self.click_cancel)

    def click_ok(self, event):
        """
        Open GitHub release page of latest version.

        Args:
            event: Button click event.
        """
        webbrowser.open(
            "https://github.com/mcci-usb/COLLECTION-cricket-ui/releases/tag/"
            + self.latest_version
        )
        self.parent.Destroy()

    def click_cancel(self, event):
        """
        Close the update dialog.

        Args:
            event: Button click event.
        """
        self.parent.Destroy()

    def on_click(self, event):
        """
        Handle OK button event from parent.

        Args:
            event: Click event.
        """
        self.GetParent().OnOK(event)

    def on_size(self, event):
        """
        Handle resize event.

        Args:
            event: Size event.
        """
        self.Layout()


class UpdateDialog(wx.Dialog):
    """
    Dialog window to display latest version update.
    """

    def __init__(self, parent, top, latest_version):
        """
        Initialize UpdateDialog.

        Args:
            parent: Parent window.
            top: Top-level application object.
            latest_version: Latest available version.
        """
        wx.Dialog.__init__(
            self,
            parent,
            -1,
            "MCCI Cricket UI Latest Version Update",
            size=wx.Size(500, 500),
            style=wx.STAY_ON_TOP | wx.DEFAULT_DIALOG_STYLE,
            name="MCCI Cricket UI Latest Version Update",
        )

        self.top = top
        self.win = AutoUpdate(self, top, latest_version)

        base = os.path.abspath(os.path.dirname(__file__))
        self.SetIcon(wx.Icon(base + "/icons/" + IMG_ICON))

        self.Fit()
        self.CenterOnParent(wx.BOTH)

    def OnOK(self, event):
        """
        Handle OK event.

        Args:
            event: Click event.
        """
        self.EndModal(wx.ID_OK)

    def OnSize(self, event):
        """
        Handle resize event.

        Args:
            event: Size event.
        """
        self.Layout()


##############################################################################
# Functions
##############################################################################
def check_version():
    """
    Check latest version from GitHub releases.

    Returns:
        str | None: Latest version if newer than
        current version, otherwise None.
    """
    api_url = "https://api.github.com/repos/mcci-usb/Cricket/releases/latest"
    response = requests.get(api_url)

    if response.status_code == 200:
        release_info = response.json()
        latest_version = release_info["tag_name"]

        if latest_version > "v" + APP_VERSION:
            return latest_version

    return None
