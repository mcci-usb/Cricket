##############################################################################
# 
# Module: aboutDialog.py
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
#     V2.0.0 Fri Jan 15 2021 18:50:59 seenivasan
#       Module created
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
"""
A  class AboutWindow with init method

The AboutWindow navigate to MCCI Logo with naming of 
application UI "Criket",Version and copyright info.  
"""
class AboutWindow(wx.Window):
    """
    AboutWindow that contains the about dialog elements.

    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        parent: Pointer to a parent window.
        top: create a object

    Returns:
        return None
    """
    def __init__ (self, parent, top):
        wx.Window.__init__(self, parent, -1,
                           size=wx.Size(100,100),
                           style=wx.CLIP_CHILDREN,
                           name="About")

        self.top = top

        base = os.path.abspath(os.path.dirname(__file__))
        bmp = wx.Image(base+"/icons/"+IMG_LOGO).ConvertToBitmap()
        
        self.image = wx.StaticBitmap(self, ID_ABOUT_IMAGE, bmp,
                                     wx.DefaultPosition, wx.DefaultSize)
        
        # Dialog to display copyright, version name information.
        self.text = [ wx.StaticText(self, -1, VERSION_NAME),
                      wx.StaticText(self, -1, VERSION_ID ),
                      wx.StaticText(self, -1,  VERSION_STR),
                      wx.StaticText(self, -1, VERSION_COPY),
                      wx.StaticText(self, -1, "All rights reserved.\n\n")
                    ]
        self.image.Bind(wx.EVT_LEFT_UP, self.OnClick)
        for i in self.text:
        #i.SetBackgroundColour('White')
            i.Bind(wx.EVT_LEFT_UP, self.OnClick)

        # Associate some events with methods of this class
        # to call OnClick() method of the program on a button’s click event,
        # the following statement is required
        self.Bind(wx.EVT_LEFT_UP, self.OnClick)

        # This method is called by the system when the window is resized,
        # because of the association above.
        self.Bind(wx.EVT_SIZE, self.OnSize)

       # A vertical box sizer is applied to a panel object, 
       # which is placed inside wxFrame window.
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        widgets = [ (self.image, 1, wx.EXPAND) ]
        for i in self.text:
            widgets.extend([ (i, 0, wx.CENTER) ])
        
        self.sizer.AddMany(widgets)

       # Associate the sizer with the window and set the,
       # window size and minimal size accordingly.
        self.SetSizerAndFit(self.sizer)

       #Determines whether the Layout function will be called 
       #automatically when the window is resized.
        self.SetAutoLayout(True)

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
        return None        
    """
    def OnClick (self, evt):
        self.GetParent().OnOK(evt)
 
    """
    OnSize() event handler function retrieves the about window size. 
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        evt: The event parameter in the OnClick() method is an 
        object specific to a particular event type.
    Returns:
        return None        
    """  
    def OnSize (self, evt):
        self.Layout()
"""
wxWindows application must have a class derived from wx.Dialog.
"""
class AboutDialog(wx.Dialog):

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
        return None
    """
    def __init__ (self, parent, top):
        wx.Dialog.__init__(self, parent, -1, "About",
                           size=wx.Size(100, 100),
                           style=wx.STAY_ON_TOP|wx.DEFAULT_DIALOG_STYLE,
                           name="About Dialog")

        self.top = top
        self.win = AboutWindow(self, top)

        # Sizes the window to fit its best size.
        self.Fit()
        # Centre frame using CentreOnParent() function,
        # show window in the center of the screen.
        # Centres the window on its parent.
        self.CenterOnParent(wx.BOTH)
    """
    OnOK() event handler function retrieves the label of 
    source button, which caused the click event. 
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        evt: The event parameter in the OnClick() method is an 
        object specific to a particular event type.
    Returns:
        return None        
    """
    def OnOK (self, evt):
    # returns numeric code to caller
        self.EndModal(wx.ID_OK)
    
    """
    OnSize() event handler function retrieves the about window size. 
    Args:
        self: The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        evt: The event parameter in the OnClick() method is an 
        object specific to a particular event type.
    Returns:
        return None        
    """  
    def OnSize (self, evt):
        self.Layout()