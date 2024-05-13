# usbenum.py
##############################################################################
# 
# Module: usb3parse.py
#
# Description:
#     parsing the USB3 Tree view data
#
# Author:
#     Vinay N, MCCI Corporation Mar 2024
#
# Revision history:
#      V4.3.1 Mon Apr 15 2024 17:00:00   Seenivasan V 
#       Module created
##############################################################################
import sys

class USB3Parser:
    """
    A base class for parsing USB 3.0 data.
    """
    def __init__(self):
        pass

    def parse_usb3tb_data(self):
        """
        Abstract method to be implemented by subclasses for parsing USB 4 Thunderbolt devices.
        """
        raise NotImplementedError("Subclasses must implement parse usb4 tb devices")

def create_usb3tb_parser(mythos):
    """
    Factory function to create an instance of a USB 4 Thunderbolt parser based on the platform.

    Args:
        mythos (str): The platform identifier ('win32', 'linux', or 'darwin').

    Returns:
        USB4TBParser: An instance of a USB 4 Thunderbolt parser based on the platform.

    Raises:
        NotImplementedError: If the platform is not supported.
    """
    if mythos == 'win32':
        from .winusb3parse import WinUsb3TreeParse as OS_USB4TBParser
    elif mythos == 'linux':
        from .linuxusb3parse import LinuxUsb3TreeParse as OS_USB4TBParser
    elif mythos == 'darwin':
        from .macusb3parse import MacUsb3TreeParse as OS_USB4TBParser
    else:
        raise NotImplementedError(f"Platform '{sys.platform}' not supported")

    # if sys.platform == 'win32' or sys.platform == 'linux' or sys.platform == 'darwin':
    if mythos == 'win32' or mythos == 'linux' or mythos == 'darwin':
        return OS_USB4TBParser()
    else:
        raise NotImplementedError(f"Platform '{mythos}' not supported")