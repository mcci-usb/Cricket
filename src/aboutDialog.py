#======================================================================
# (c) 2020  MCCI Inc.
#----------------------------------------------------------------------
# Project : UI3141/3201 GUI Application
# File    : aboutDialog.py
#----------------------------------------------------------------------
# Dialog to display copyright information
#======================================================================

#======================================================================
# IMPORTS
#======================================================================
import wx
import os

from uiGlobals import *

#======================================================================
# COMPONENTS
#======================================================================

class AboutWindow(wx.Window):
    """
    Window that contains the about dialog elements.
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
        self.Bind(wx.EVT_LEFT_UP, self.OnClick)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        # Define layout
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        widgets = [ (self.image, 1, wx.EXPAND) ]
        for i in self.text:
            widgets.extend([ (i, 0, wx.CENTER) ])
        
        self.sizer.AddMany(widgets)

        self.SetSizerAndFit(self.sizer)
        self.SetAutoLayout(True)

    def OnClick (self, evt):
        self.GetParent().OnOK(evt)

    def OnSize (self, evt):
        self.Layout()


class AboutDialog(wx.Dialog):
    def __init__ (self, parent, top):
        wx.Dialog.__init__(self, parent, -1, "About",
                           size=wx.Size(100, 100),
                           style=wx.STAY_ON_TOP|wx.DEFAULT_DIALOG_STYLE,
                           name="About Dialog")

        self.top = top
        self.win = AboutWindow(self, top)

        self.Fit()
        self.CenterOnParent(wx.BOTH)

    def OnOK (self, evt):
        self.EndModal(wx.ID_OK)

    def OnSize (self, evt):
        self.Layout()