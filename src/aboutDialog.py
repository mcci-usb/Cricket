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
#     V4.0.0 Wed May 25 2023 17:00:00   Seenivasan V 
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
class AboutWindow(wx.Window):
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

        self.top = top

        base = os.path.abspath(os.path.dirname(__file__))
        bmp = wx.Image(base+"/icons/"+IMG_LOGO).ConvertToBitmap()
        
        self.image = wx.StaticBitmap(self, ID_ABOUT_IMAGE, bmp,
                                     wx.DefaultPosition, wx.DefaultSize)
        
        # Dialog to display copyright, version name information.
        self.text = [ wx.StaticText(self, -1, VERSION_NAME),
                      wx.StaticText(self, -1, VERSION_ID ),
                      wx.StaticText(self, -1,  VERSION_STR),
                      wx.StaticText(self, -1, VERSION_COPY, style=wx.ALIGN_CENTER),
                      wx.StaticText(self, -1, "\nAll rights reserved.\n\n")
                    ]
        self.image.Bind(wx.EVT_LEFT_UP, self.OnClick)
        for i in self.text:
        # i.SetBackgroundColour('White')
            i.Bind(wx.EVT_LEFT_UP, self.OnClick)

        # Associate some events with methods of this class
        # To call OnClick() method of the program on a button’s click event,
        # The following statement is required
        self.Bind(wx.EVT_LEFT_UP, self.OnClick)

        # This method is called by the system when the window is resized,
        # Because of the association above.
        self.Bind(wx.EVT_SIZE, self.OnSize)

        # A vertical box sizer is applied to a panel object, 
        # which is placed inside wxFrame window.
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        widgets = [ (self.image, 1, wx.CENTER) ]
        for i in self.text:
            widgets.extend([ (i, 0, wx.CENTER) ])
        
        self.sizer.AddMany(widgets)

        # Associate the sizer with the window and set the,
        # Window size and minimal size accordingly.
        self.SetSizerAndFit(self.sizer)

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

class AboutDialog(wx.Dialog):
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
        wx.Dialog.__init__(self, parent, -1, "About",
                           size=wx.Size(100, 100),
                           style=wx.STAY_ON_TOP|wx.DEFAULT_DIALOG_STYLE,
                           name="About Dialog")

        self.top = top
        self.win = AboutWindow(self, top)

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