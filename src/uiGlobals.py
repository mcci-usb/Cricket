#======================================================================
# (c) 2020  MCCI Inc.
#----------------------------------------------------------------------
# Project : UI3141/3201 GUI application
# File    : uiGlobals.py
#----------------------------------------------------------------------
# Define all global variables for the entire UI 3141/3201 App.
#======================================================================

#======================================================================
# IMPORTS
#======================================================================
import wx

#======================================================================
# GLOBAL VARIABLES
#======================================================================

# StatusBar ID
SB_PORT_ID   = 0
SB_DEV_ID    = 1
SB_SERIAL_ID = 2
SB_STATUS_ID = 3

# Font Size
DEFAULT_FONT_SIZE = 8
MAC_FONT_SIZE = 10

# Base directory (populated by main module)
BASE_DIR = None

# Maximum manually generated ID
ID_MAX = 9999
wx.RegisterId(ID_MAX)

# ComWindow Widgets
ID_BTN_DEV_SCAN = 1000
ID_BTN_CONNECT = 1001

# LoopWindow Widgets
ID_TC_PERIOD = 1004
ID_TC_DUTY = 1005
ID_TC_CYCLE = 1006

ID_BTN_START  = 1007

ID_MENU_SHOW_APP  = 1008
# Menu
ID_MENU_FILE_NEW    = 1011
ID_MENU_FILE_CLOSE  = 1012
ID_MENU_FILE_EXIT   = 1013
ID_MENU_SCRIPT_NEW = 1014

ID_MENU_HELP_3141 = 1015
ID_MENU_HELP_3201 = 1016
ID_MENU_HELP_WEB = 1017
ID_MENU_HELP_PORT = 1018

ID_MENU_HELP_ABOUT = 1019

# Dev3141-3201 Window
ID_BTN_AUTO = 1020
ID_BTN_DC = 1021
ID_BTN_ONOFF = 1022
    # Radio Buttons
ID_RBTN_P0 = 1023
ID_RBTN_P1 = 1024
ID_RBTN_P2 = 1025
ID_RBTN_P3 = 1026
ID_RBTN_P4 = 1027

ID_RBTN_SS0 = 1028
ID_RBTN_SS1 = 1029

ID_TC_INTERVAL = 1030
ID_BTN_VOLTS = 1031
ID_BTN_AMPS = 1032

# About Dialog
ID_ABOUT_IMAGE = 1033

# Log Window
ID_BTN_CLEAR = 1034

# USB Window
ID_BTN_REF = 1035
ID_BTN_UCLEAR = 1036

# Menu for Mac
ID_MENU_WIN_MIN = 1037
ID_MENU_WIN_SHOW = 1038


usbClass1 = ["None", "Audio", "CDC-COM", "HID", "Physical",
            "Image", "Printer", "Mass Storage", "Hub",
            "CDC-DATA", "Smart Card", "Content Security",
            "Video", "Personal Healthcare", "Audio/Video Devices",
            "Billboard Device", "Type-C Bridge", "Diagnostic Device",
            ]

usbClass = {1: "Audio", 2: "CDC-COM", 3: "HID", 5: "Physical",
            6: "Image", 7: "Printer", 8: "Mass Storage", 9: "Hub",
            10: "CDC-Data", 11: "Smart Card", 13: "Content Security",
            14: "Video", 15: "Personal Healthcare", 16: "Audio/Video Devices",
            17: "Billboard Device", 18: "Type-C Bridge", 
            220: "Diagnostic Devices", 224: "Wireless Controller", 
            239: "Miscellaneous", 254: "Application Specific",
            255: "Vendor Specific"}

usbSpeed = {0: "LowSpeed", 1: "FullSpeed", 2: "HighSpeed", 3: "SuperSpeed"}


#======================================================================
# GLOBAL STRINGS
#======================================================================
VERSION_NAME  = "\nMCCI"+u"\u00AE"+" USB Switch - 3141/3201"
VERSION_ID    = ""
VERSION_COPY  = "\nCopyright "+u"\u00A9"+" 2020 MCCI Corporation"
VERSION_STR = "Version 1.2.0"


#======================================================================
# GLOBAL FUNCTIONS
#======================================================================

class NumericValidator(wx.Validator):
    def __init__(self):
        """
        Only digits are allowed in the address.
        """
        wx.Validator.__init__(self)
        self.Bind(wx.EVT_CHAR, self.OnChar)

        #wx.EVT_CHAR(self, self.OnChar)

    def Clone(self, arg=None):
        return NumericValidator()

    def Validate(self, win):
        tc  = self.GetWindow()
        val = tc.GetValue()
        return val.isdigit()

    def OnChar(self, evt):
        tc = self.GetWindow()
        key = evt.GetKeyCode()

        # For the case of delete and backspace, pass the key
        if (key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255):
            evt.Skip()
            return

        if chr(key).isdigit():
            evt.Skip()
            return