##############################################################################
# 
# Module: updateDialog.py
#
# Description:
#     Dialog to display latest version of the application
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
#     V4.0.0 Wed Nov 09 2023 17:00:00   Seenivasan V 
#       Module created
##############################################################################

# Built-in imports
import os

# Lib imports
import wx

import os
import sys
import webbrowser
import requests


# Own modules
from uiGlobals import *

##############################################################################
# Utilities
##############################################################################
class AutoUpdate(wx.Window):
    """
    A  class AboutWindow with init method
    The AboutWindow navigate to MCCI Logo with naming of 
    application UI "Criket",Version and copyright info.  
    """
    def __init__ (self, parent, top, latest_version):
        """
        AboutWindow that contains the about dialog elements.

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
            top: creates an object
        Returns:
            None
        """
        wx.Window.__init__(self, parent, -1,
                           
                           size=wx.Size(900,500),
                           style=wx.STAY_ON_TOP|wx.DEFAULT_DIALOG_STYLE,
                           name="About")

        self.top = top
        self.parent = parent
        self.latest_version = latest_version
        
        
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        
        mytext = "MCCI Cricket UI latest version " + latest_version + " is available on Github. \n Click OK for more details."

        self.text = wx.StaticText(self, -1, mytext)

        self.btn_ok = wx.Button(self, -1, 'OK')
        self.btn_cancel = wx.Button(self, -1, 'Cancel')

        self.hbox1.Add(self.text, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=20)

        self.hbox2.Add(self.btn_ok, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        self.hbox2.Add(self.btn_cancel, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        self.vbox.Add(self.hbox1, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        self.vbox.Add(self.hbox2, flag=wx.ALIGN_CENTER | wx.ALL, border=5)

        self.SetSizerAndFit(self.vbox)
        self.SetAutoLayout(True)

        self.btn_ok.Bind(wx.EVT_BUTTON, self.ClickOk)
        self.btn_cancel.Bind(wx.EVT_BUTTON, self.ClickCancel)



    def ClickOk(self, e):
        webbrowser.open("https://github.com/mcci-usb/COLLECTION-cricket-ui/releases/tag/"+self.latest_version)  
        self.parent.Destroy()
        
    
    def ClickCancel(self, e):
        self.parent.Destroy()
        
        
    def OnClick (self, evt):
        """
        OnClick() event handler function retrieves the label of 
        source button, which caused the click event. 
        That label is printed on the console.

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            evt: The event parameter in the OnClick() method is an 
            object specific to a particular event type.
        Returns:
            None        
        """
        self.GetParent().OnOK(evt)
   
    def OnSize (self, evt):
        """
        OnSize() event handler function retrieves the about window size. 

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            evt: The event parameter in the OnClick() method is an 
            object specific to a particular event type.
        Returns:
            None        
        """
        self.Layout()

class UpdateDialog(wx.Dialog):
    """
    wxWindows application must have a class derived from wx.Dialog.
    """
    def __init__ (self, parent, top, latest_version):
        """
        A AboutDialog is Window an application creates to 
        retrieve Cricket UI Application input.

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
            top: create a object
        Returns:
            None
        """
        wx.Dialog.__init__(self, parent, -1, "MCCI Cricket UI Latest Version Update",
                           size=wx.Size(500, 500),
                           style=wx.STAY_ON_TOP|wx.DEFAULT_DIALOG_STYLE,
                           name="MCCI Cricket UI Latest Version Update")

        self.top = top
        self.win = AutoUpdate(self, top, latest_version)
        # self.SetBackgroundColour("white")
        base = os.path.abspath(os.path.dirname(__file__))
        self.SetIcon(wx.Icon(base+"/icons/"+IMG_ICON))

        # Sizes the window to fit its best size.
        self.Fit()
        # Centre frame using CentreOnParent() function,
        # Show window in the center of the screen.
        # Centres the window on its parent.
        self.CenterOnParent(wx.BOTH)
        # self.Destroy()
    
    def OnOK (self, evt):
        """
        OnOK() event handler function retrieves the label of 
        source button, which caused the click event. 

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            evt: The event parameter in the OnOK() method is an 
            object specific to a particular event type.
        Returns:
            None        
        """
    # Returns numeric code to caller
        self.EndModal(wx.ID_OK)
     
    def OnSize (self, evt):
        """
        OnSize() event handler function retrieves the about window size. 
        
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            evt: The event parameter in the OnSize() method is an 
            object specific to a particular event type.
        Returns:
            None        
        """ 
        self.Layout()
        
def check_version():
    api_url = f"https://api.github.com/repos/mcci-usb/Cricket/releases/latest"
    response = requests.get(api_url)

    if response.status_code == 200:
        release_info = response.json()
        latest_version = release_info["tag_name"]

        if latest_version > "v"+APP_VERSION:
            return latest_version
            
        else:
            return None

    else:
        return None
