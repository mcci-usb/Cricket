# -*- coding: utf-8 -*-
##############################################################################
#
# Module: wdpLogin.py
#
# Description:
#     Windows Device Portal (WDP) Login Credentials Dialog.
#
#     This module provides a wxPython dialog window to collect and store
#     Windows Device Portal login credentials (Username & Password).
#     Credentials are securely saved into the global configuration
#     using the configdata module.
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
# Own modules
import configdata

##############################################################################
# Utilities
##############################################################################
class LoginFrame(wx.Dialog):
    """
    Summary:
        Windows Device Portal Login Dialog.

    Longer Description:
        Provides a credential input window for Windows Device Portal (WDP)
        authentication.

        The dialog allows users to:

        - Enter Username
        - Enter Password (masked)
        - Save credentials to configuration storage

        Stored credentials are later used for:

        - USB4 scanning services
        - Device Portal communication
        - Remote device management

    Args:
        parent (wx.Window):
            Parent window reference.

        top (object):
            Top-level controller / main frame reference.

    Attributes:
        panel (wx.Panel):
            Main container panel.

        username_text (wx.TextCtrl):
            Username input field.

        password_text (wx.TextCtrl):
            Password input field (masked).

        login_button (wx.Button):
            Save credentials button.

        username (str):
            Entered username value.

        password (str):
            Entered password value.
    """
    def __init__(self, parent, top):
        """
        Initialize Login Dialog UI.

        Args:
            parent (wx.Window):
                Parent window.

            top (object):
                Top-level controller reference.

        Returns:
            None
        """
        super(LoginFrame, self).__init__(parent, title="Login Window", size=(350, 280))
        self.panel = wx.Panel(self)
        self.top = top

        self.username_label = wx.StaticText(self.panel, label="Username")
        self.username_text = wx.TextCtrl(self.panel, size=(150, -1))
        
        self.password_label = wx.StaticText(self.panel, label="Password")
        self.password_text = wx.TextCtrl(self.panel, style=wx.TE_PASSWORD, size=(150, -1))
        
        self.login_button = wx.Button(self.panel, label="Save")
        self.login_button.Bind(wx.EVT_BUTTON, self.on_save)

        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.username_text.SetFont(font)
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.password_text.SetFont(font)

        self.username = None
        self.password = None

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.username_label, 0, wx.ALL, 10)
        sizer.Add(self.username_text, 0, wx.ALL | wx.EXPAND, 10)
        sizer.Add(self.password_label, 0, wx.ALL, 10)
        sizer.Add(self.password_text, 0, wx.ALL | wx.EXPAND, 10)
        sizer.Add(self.login_button, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 20)

        self.panel.SetSizer(sizer)
        self.CenterOnParent(wx.BOTH)

    def on_save(self, event):
        """
        Handle Save Button Event.

        Description:
            - Reads username and password input values.
            - Validates empty credentials.
            - Updates configuration storage.
            - Closes the dialog window.

        Args:
            event (wx.Event):
                Button click event.

        Returns:
            None
        """
        self.username = self.username_text.GetValue()
        self.password = self.password_text.GetValue()

        if self.username.strip() == '' or self.password.strip() == '':
            wx.MessageBox("Please enter the user credentials")

        # Update credentials in config
        udict = {
            "msudp": {
                "uname": self.username,
                "pwd": self.password
            }
        }

        configdata.updt_portal_credentials(udict)

        # Optional callback to main frame
        # self.top.set_user_credentials(self.username, self.password)

        self.Close()