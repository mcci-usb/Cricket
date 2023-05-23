
##############################################################################
# 
# Module: warningMessage.py
#
# Description:
#     Dialog to display copyright information
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
#     V4.0.0 Wed May 25 2023 17:00:00   Seenivasan V 
#       Module created
##############################################################################

# Built-in imports
import os

# Lib imports
import wx

# Own modules
from uiGlobals import *
# from uiGlobals import IMG_ICON

import configdata

##############################################################################
# Utilities
##############################################################################
class warningWindow(wx.Window):
    """
    A  class AboutWindow with init method
    The AboutWindow navigate to MCCI Logo with naming of 
    application UI "Criket",Version and copyright info.  
    """
    """
    A  class AboutWindow with init method
    The AboutWindow navigate to MCCI Logo with naming of 
    application UI "Criket",Version and copyright info.  
    """
    def __init__ (self, parent, top):
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
                           size=wx.Size(100,100),
                           style=wx.CLIP_CHILDREN,
                           name="About")
        
        self.SetBackgroundColour('White')

        self.top = top
        self.parent = parent
        self.wait_flg = True

        self.hbox_text = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox_chkbox = wx.BoxSizer(wx.HORIZONTAL)
        self.Epty_box = wx.BoxSizer(wx.HORIZONTAL)

        base = os.path.abspath(os.path.dirname(__file__))
        bmp = wx.Image(base+"/icons/"+IMG_WARNING).ConvertToBitmap()
        
        self.image = wx.StaticBitmap(self, ID_ABOUT_IMAGE, bmp,
                                     wx.DefaultPosition, wx.DefaultSize)

        
        self.text = wx.StaticText(self, -1 ,"For Device safety, it is recommended to keep \n"
                       "Port ON/OFF time > 1000 msec."
                       )
        self.empt_text = wx.StaticText(self, -1 ," ")
                       
        self.chk_box = wx.CheckBox(self, -1, "Don't show this information again",
                                  size=(220,25))
        self.btn_ok = wx.Button(self, -1 , "Ok")
        self.empt_text2 = wx.StaticText(self, -1 ," ")

        self.tc_box = wx.StaticText(self, -1 , " ")

        self.hbox_text.Add(self.image, 0, flag=wx.ALIGN_LEFT | wx.LEFT | 
                       wx.ALIGN_CENTER_VERTICAL, border=20)

        self.hbox_text.Add(self.text, 0, flag=wx.ALIGN_LEFT | wx.LEFT | 
                       wx.ALIGN_CENTER_VERTICAL, border=10)
        self.hbox_text.Add(self.empt_text, 0, flag=wx.ALIGN_LEFT | wx.LEFT | 
                       wx.ALIGN_CENTER_VERTICAL, border=20)

        self.hbox_chkbox.Add(self.chk_box, 0, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 20)
        
        self.hbox_chkbox.Add(self.btn_ok, 0, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 50)
        self.hbox_chkbox.Add(self.empt_text2, 0, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 20)
        
        self.Epty_box.Add(self.tc_box, 0, flag=wx.ALIGN_CENTER_VERTICAL |
                       wx.LEFT, border = 50)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.vbox.AddMany ([
            (0,10,0),
            (self.hbox_text, 1, wx.EXPAND | wx.ALL),
            (0,20,0),
            (self.hbox_chkbox, 1, wx.EXPAND | wx.ALL),
            (0,5,0),
            (self.Epty_box, 1, wx.EXPAND | wx.ALL)])
            
        
        self.chk_box.Bind(wx.EVT_CHECKBOX, self.OnCheckBox)
        self.btn_ok.Bind(wx.EVT_BUTTON, self.OnClose)
        self.image.Bind(wx.EVT_LEFT_UP, self.OnClick)
        
        self.SetSizerAndFit(self.vbox)
        # Determines whether the Layout function will be called 
        # Automatically when the window is resized.
        self.SetAutoLayout(True)
    
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
        pass
        # self.GetParent().OnOK(evt)
    
    def OnCheckBox(self, evt):
        pass
        
    
    def OnClose(self, evt):
        dlgchoice = False
        if(self.chk_box.GetValue() == True):
            dlgchoice = True
        configdata.updt_warning_dialog({"wdialog": dlgchoice})    
        self.GetParent().OnOK(evt)

class WarningDialog(wx.Dialog):
    """
    wxWindows application must have a class derived from wx.Dialog.
    """
    def __init__ (self, parent, top):
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
        wx.Dialog.__init__(self, parent, -1, "General instruction",
                           size=wx.Size(100, 100),
                           style=wx.STAY_ON_TOP|wx.DEFAULT_DIALOG_STYLE,
                           name="Warning Dialog")

        self.top = top
        self.win = warningWindow(self, top)

        # Sizes the window to fit its best size.
        self.Fit()
        # Centre frame using CentreOnParent() function,
        # Show window in the center of the screen.
        # Centres the window on its parent.
        self.CenterOnParent(wx.BOTH)
    
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
