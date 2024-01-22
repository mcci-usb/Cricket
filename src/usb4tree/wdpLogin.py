##############################################################################
# 
# Module: wdpLogin.py
#
# Description:
#     Dialog to display windows device portal Login credentials window.
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
#     V4.2.0 Wed Nov 2023 17:00:00   Seenivasan V 
#       Module created
##############################################################################

import wx
import configdata

# from main import Mywin

class LoginFrame(wx.Dialog):
    """
    Represents a login window in the wxPython application.

    This class provides a simple login window with a username and password 
    input for user authentication.

    Parameters:
        parent (wx.Window): The parent window.
        top: The top-level object or controller that manages this login window.

    Attributes:
        panel (wx.Panel): The panel containing the components of the login window.
        top: The top-level object or controller that manages this login window.
    """
    def __init__(self, parent, top):
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

    def on_save(self, event):
        """
            Handles the save event by extracting username and password from text input fields,
            checking for empty values, updating portal credentials, and closing the window.

            Parameters:
               event (wx.Event): The save event triggering this method.
        """
        self.username = self.username_text.GetValue()
        self.password = self.password_text.GetValue()
        if self.username.strip() == '' or self.password.strip() == '':
            wx.MessageBox("Please enter the user credentials")
        
        udict = {"msudp": {"uname": self.username, "pwd": self.password}}
        configdata.updt_portal_credentials(udict)

        # self.top.set_user_credentials(self.username, self.password)  # Use self.top here
        self.Close()