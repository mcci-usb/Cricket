# -*- coding: utf-8 -*-
##############################################################################
# 
# Module: usb3parse.py
#
# Description:
#     This module provides parsing utilities for USB 3.x topology data.
#
#     It defines a base parser class and a platform-specific factory
#     loader used to instantiate USB3 Tree parsers for:
#
#         • Windows
#         • Linux
#         • macOS
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
# Revision history:
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
#
##############################################################################
import sys
##############################################################################
# Utilities
##############################################################################
class USB3Parser:
    """
    Base USB3 Parser Class.

    Description:
        Provides an abstract interface for parsing USB 3.x
        topology data.

        Platform-specific subclasses must implement the
        parsing logic to interpret USB enumeration results
        and convert them into structured tree data.

    Methods:
        parse_usb3tb_data():
            Abstract method that must be implemented
            by derived parser classes.
    """
    def __init__(self):
        pass

    def parse_usb3tb_data(self):
        """
        Parse USB3 topology data.

        Description:
            Abstract method intended to be implemented by
            platform-specific subclasses.

            The implementation should:

                • Process raw USB3 enumeration data
                • Extract device hierarchy
                • Organize nodes level-wise
                • Prepare data for Tree View rendering

        Raises:
            NotImplementedError:
                If the subclass does not implement this method.
        """
        raise NotImplementedError("Subclasses must implement parse usb4 tb devices")

def create_usb3tb_parser(mythos):
    """
    USB3 Parser Factory Function.

    Description:
        Dynamically creates and returns a platform-specific
        USB3 Tree parser instance.

        This enables OS-dependent USB parsing without
        hard-coding platform logic in UI modules.

    Args:
        mythos (str):
            Operating system identifier.

            Supported values:
                • 'win32'   → Windows parser
                • 'linux'   → Linux parser
                • 'darwin'  → macOS parser

    Returns:
        USB3Parser:
            Instance of the platform-specific USB3 parser.

    Raises:
        NotImplementedError:
            If the provided platform is unsupported.
    """
    if mythos == 'win32':
        from .winusb3parse import WinUsb3TreeParse as OS_USB3TBParser
    elif mythos == 'linux':
        from .linuxusb3parse import LinuxUsb3TreeParse as OS_USB3TBParser
    elif mythos == 'darwin':
        from .macusb3parse import MacUsb3TreeParse as OS_USB3TBParser
    else:
        raise NotImplementedError(f"Platform '{sys.platform}' not supported")

    # if sys.platform == 'win32' or sys.platform == 'linux' or sys.platform == 'darwin':
    if mythos == 'win32' or mythos == 'linux' or mythos == 'darwin':
        return OS_USB3TBParser()
    else:
        raise NotImplementedError(f"Platform '{mythos}' not supported")