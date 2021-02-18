##############################################################################
# 
# Module: uiGlobal.py
#
# Description:
#     Define all global variables for the entire UI Cricket App.
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
# Lib imports
import wx

##############################################################################
# GLOBAL VARIABLES
##############################################################################
APP_NAME = "Cricket"
APP_VERSION = "2.0.0"

# StatusBar ID
SB_PORT_ID   = 0
SB_DEV_ID    = 1
SB_SERIAL_ID = 2
SB_STATUS_ID = 3

MODE_MANUAL = 0
MODE_AUTO   = 1
MODE_LOOP   = 2

DEV_3141    = 0
DEV_3201    = 1
DEV_2101    = 2

DEVICES    = ["3141", "3201", "2101"]

IMG_ICON = "mcci_logo.ico"
IMG_LOGO = "mcci_logo.png"
IMG_BTN_ON = "btn_on.png"
IMG_BTN_OFF = "btn_off.png"

# Font Size
DEFAULT_FONT_SIZE = 8
MAC_FONT_SIZE = 10

# Window Position fron Top
DEFAULT_YPOS = 5
YPOS_MAC = 25

# Base directory (populated by main module)
BASE_DIR = None

# Maximum manually generated ID
ID_MAX = 9999
wx.RegisterId(ID_MAX)

# ComWindow Widgets
ID_BTN_DEV_SCAN = 1000
ID_BTN_CONNECT = 1001

# LoopWindow Widgets
ID_TC_PERIOD = 1002
ID_TC_DUTY = 1003
ID_TC_CYCLE = 1004

ID_BTN_START  = 1005

ID_MENU_SHOW_APP  = 1006
# Menu
ID_MENU_FILE_NEW    = 1011
ID_MENU_FILE_CLOSE  = 1012
ID_MENU_FILE_EXIT   = 1013
ID_MENU_SCRIPT_NEW = 1014

ID_MENU_HELP_3141 = 1015
ID_MENU_HELP_3201 = 1016
ID_MENU_HELP_2101 = 1017
ID_MENU_HELP_WEB = 1018
ID_MENU_HELP_PORT = 1019
ID_MENU_HELP_ABOUT = 1020

# Dev3141-3201 Window
ID_BTN_AUTO = 1030
ID_BTN_ONOFF = 1031

# Radio Buttons
ID_RBTN_SS0 = 1040
ID_RBTN_SS1 = 1041

ID_TC_INTERVAL = 1042
ID_BTN_VOLTS = 1043
ID_BTN_AMPS = 1044

# About Dialog
ID_ABOUT_IMAGE = 1045

# Log Window
ID_BTN_CLEAR = 1046

# USB Window
ID_BTN_REF = 1047
ID_BTN_UCLEAR = 1048

# Menu for Mac
ID_MENU_WIN_MIN = 1049
ID_MENU_WIN_SHOW = 1050


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


##############################################################################
# GLOBAL STRINGS
##############################################################################
VERSION_NAME  = "\nMCCI"+u"\u00AE "+APP_NAME
VERSION_ID    = ""
VERSION_COPY  = "\nCopyright "+u"\u00A9"+" 2020 MCCI Corporation"
VERSION_STR = "Version "+APP_VERSION


##############################################################################
# GLOBAL FUNCTIONS
##############################################################################
class NumericValidator(wx.Validator):
    """
    Validator associated NumericValidator Control.
    """
    def __init__(self):
        """
        Only digits are allowed in the address.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        wx.Validator.__init__(self)
        self.Bind(wx.EVT_CHAR, self.OnChar)

        #wx.EVT_CHAR(self, self.OnChar)
    
    def Clone(self, arg=None):
        """
        clone Only digits are allowed in the address. 
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            NumericValidator(): return True if all characters in the string are
            numaric charecters    

        """
        return NumericValidator()
   
    def Validate(self, win):
        """
        Only digits are allowed in the address. 
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            win: window object is created.
        Returns:
           val.isdigit - "True" if all characters in the string are digits.
        """
        # Returns the window associated with the validator.
        tc  = self.GetWindow()
        val = tc.GetValue()
        return val.isdigit()
   
    def OnChar(self, evt):
        """
        all key names and charachters dirctly can use. 
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            evt:evt handler to display the characters
        Returns:
            None
        """
        # Returns the window associated with the validator.
        tc = self.GetWindow()
        key = evt.GetKeyCode()

        # For the case of delete and backspace, pass the key
        if (key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255):
            evt.Skip()
            return

        if chr(key).isdigit():
            evt.Skip()
            return
