##############################################################################
# 
# Module: uiGlobal.py
#
# Description:
#     Define all global variables for the entire UI Cricket App.
#
# Author:
#     Seenivasan V, MCCI Corporation Mar 2020
#
# Revision history:
#     V4.3.1 Mon Apr 15 2024 17:00:00   Seenivasan V 
#       Module created
#
##############################################################################
# Lib imports
import wx
##############################################################################
# GLOBAL VARIABLES
##############################################################################
APP_NAME = "Cricket"
APP_VERSION = "4.4.2"

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
DEV_2301    = 3
DEV_3142    = 4


BAUDRATE = [115200, 115200, 0, 9600]

DEVICES    = ["3141","3142", "3201", "2101", "2301"]

READ_CONFIG = 0
AUTO_CONNECT = 1

IMG_ICON = "mcci_logo.ico"
IMG_LOGO = "mcci_logo.png"
IMG_BTN_ON = "btn_on.png"
IMG_BTN_OFF = "btn_off.png"
IMG_WAVE = "wave.png"
IMG_NOSWITCH = "noswitch.png"
IMG_WARNING ="warning.png"
IMG_DISS_ICON = "x_mark.png"

# Font Size
DEFAULT_FONT_SIZE = 8
MAC_FONT_SIZE = 10

# Window Position fron Top
DEFAULT_YPOS = 5
YPOS_MAC = 25

# Default Screen Size
SCREEN_WIDTH = 880
SCREEN_HEIGHT = 780

# Base directory (populated by main module)
BASE_DIR = None

# Maximum manually generated ID
ID_MAX = 9999
wx.RegisterId(ID_MAX)

# ComWindow Widgets
ID_BTN_DEV_SCAN = 1000
ID_BTN_CONNECT = 1001
ID_BTN_ADD = 1111

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
ID_MENU_HELP_2301 = 1051
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

ID_WARNING_IMAGE = 1140

# Log Window
ID_BTN_CLEAR = 1046

# USB Window
ID_BTN_REF = 1047
ID_BTN_UCLEAR = 1048

# Serial Log Window
ID_BTN_SL_SAVE = 1049
ID_BTN_SL_CLEAR = 1050
ID_BTN_SL_CONFIG = 1051
ID_BTN_SL_CONNECT = 1052

# Menu for Mac
ID_MENU_WIN_MIN = 1100
ID_MENU_WIN_SHOW = 1101

ID_MENU_MODEL_CONNECT = 1102
ID_MENU_MODEL_DISCONNECT = 1103

ID_MENU_CONFIG_UC = 1104
ID_MENU_CONFIG_SCC = 1105
ID_MENU_CONFIG_THC = 1106

ID_MENU_SET_SCC = 1107
ID_MENU_SET_THC = 1108
ID_MENU_SET_WARNING = 1109


ID_MENU_GRAPH = 1110
ID_DUT_WINDOW = 1222
ID_3141_FIRMWARE = 1234

ID_MENU_DUT1 = ID_MENU_GRAPH + 1
ID_MENU_DUT2 = ID_MENU_DUT1 + 1

ID_MENU_BATCHMODE = ID_MENU_DUT2 + 1
ID_MENU_SWCONFIG = ID_MENU_BATCHMODE + 1

ID_BTN_3141 = ID_MENU_SWCONFIG + 1
ID_BTN_3201 = ID_BTN_3141 + 1
ID_BTN_2101 = ID_BTN_3201 + 1

EVT_RESULT_ID = ID_MENU_SWCONFIG + 1
EVT_DUT_SL_DATA_ID = EVT_RESULT_ID + 1  # DUT Data arrival 
EVT_DUT_SL_ERR_ID = EVT_DUT_SL_DATA_ID + 1   # DUT Err Msg arrival

ID_MENU_CONFIG_SL1 = EVT_DUT_SL_ERR_ID + 1
ID_MENU_CONFIG_SL2 = ID_MENU_CONFIG_SL1 + 1

ID_RBTN_PC = ID_MENU_CONFIG_SL2 + 1
ID_RBTN_RV = ID_MENU_CONFIG_SL2 + 1
ID_RBTN_RC = ID_MENU_CONFIG_SL2 + 1
ID_RBTN_RT = ID_MENU_CONFIG_SL2 + 1

ID_TC_SEQNAME = ID_RBTN_RT + 1
ID_BTN_SEQSAVE = ID_TC_SEQNAME + 1
ID_USB4_TREEVIEW = ID_BTN_SEQSAVE + 1
ID_MENU_HELP_3142 = ID_USB4_TREEVIEW + 1
ID_MENU_NETWORK = ID_MENU_HELP_3142 + 1
ID_MENU_SET_NETWORK = ID_MENU_NETWORK + 1
ID_NETWORK_MENU = ID_MENU_SET_NETWORK + 1

ID_RBTN_WIN = ID_NETWORK_MENU + 1
ID_RBTN_LINUX = ID_RBTN_WIN + 1
ID_RBTN_MAC = ID_RBTN_LINUX + 1



usbClass1 = ["None", "Audio", "CDC-COM", "HID", "Physical",
            "Image", "Printer", "Mass Storage", "Hub",
            "CDC-DATA", "Smart Card", "Content Security",
            "Video", "Personal Healthcare", "Audio/Video Devices",
            "Billboard Device", "Type-C Bridge", "Diagnostic Device",
            ]

usbClass = {0: "Unknown",
            1: "Audio", 2: "CDC-COM", 3: "HID", 5: "Physical",
            6: "Image", 7: "Printer", 8: "Mass Storage", 9: "Hub",
            10: "CDC-Data", 11: "Smart Card", 13: "Content Security",
            14: "Video", 15: "Personal Healthcare", 16: "Audio/Video Devices",
            17: "Billboard Device", 18: "Type-C Bridge", 
            220: "Diagnostic Devices", 224: "Wireless Controller", 
            239: "Miscellaneous", 254: "Application Specific",
            255: "Vendor Specific"}

# usbClass = {0: "Unknown",
#             1: "Audio", 2: "CDC-COM", 3: "HID", 5: "Physical",
#             6: "Image", 7: "Printer", 8: "Mass Storage", 9: "Hub",
#             10: "CDC-Data", 11: "Smart Card", 13: "Content Security",
#             14: "Video", 15: "Personal Healthcare", 16: "Audio/Video Devices",
#             18: "Type-C Bridge", 
#             220: "Diagnostic Devices", 224: "Wireless Controller", 
#             239: "Miscellaneous", 254: "Application Specific",
#             255: "Vendor Specific"}

usbSpeed = {0: "LowSpeed", 1: "FullSpeed", 2: "HighSpeed", 3: "SuperSpeed", 4:"SuperSpeed Plus"}

portCnt = {"3141": 2,"3142":2, "3201": 4, "2301": 4, "2101": 1}


##############################################################################
# GLOBAL STRINGS
##############################################################################
VERSION_NAME  = "\nMCCI"+u"\u00AE "+APP_NAME
VERSION_ID    = ""
VERSION_COPY  = "\nCopyright "+u"\u00A9"+" 2020-25\nMCCI Corporation"
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

    def Clone(self, arg=None):
        """
        Only digits are allowed in the address. 

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            NumericValidator():return True if all characters in the string are
            numaric charecters    

        """
        return NumericValidator()
   
    def Validate(self, win):
        """
        Only digits are allowed in the textcontrol. 

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
