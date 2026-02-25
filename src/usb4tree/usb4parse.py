# -*- coding: utf-8 -*-
##############################################################################
# 
# Module: usb4parse.py
#
# Description:
#     USB4 Tree View Parsing module.
#     Provides base parser interface and factory method
#     to create OS-specific USB4 / Thunderbolt tree parsers.
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
# Revision history:
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
#
##############################################################################
# Built-in imports
import sys

##############################################################################
# Utilities
##############################################################################
class USB4TBParser:
    """
    Summary:
        Base USB4 / Thunderbolt Parser class.

    Longer Description:
        Defines the interface for parsing USB4 / Thunderbolt
        tree topology data. OS-specific subclasses must
        implement the parsing logic.

    Attributes:
        None
    """
    def __init__(self):
        """
        Initialize USB4TBParser.

        Args:
            None

        Returns:
            None
        """
        pass

    def parse_usb4tb_data(self):
        """
        Parse USB4 / Thunderbolt tree data.

        Description:
            Abstract method that must be implemented
            by OS-specific parser subclasses.

        Args:
            None

        Returns:
            Parsed USB4 topology data.

        Raises:
            NotImplementedError:
                If subclass does not implement parser.
        """
        raise NotImplementedError("Subclasses must implement parse usb4 tb devices")

def create_usb4tb_parser(mythos):
    """
    Create OS-specific USB4 parser instance.

    Description:
        Factory function that returns the appropriate
        USB4 / Thunderbolt parser implementation
        based on the operating system.

    Args:
        mythos (str):
            Operating system identifier.
            Supported values:
                - 'win32'
                - 'linux'
                - 'darwin'

    Returns:
        USB4TBParser:
            Instance of OS-specific parser class.

    Raises:
        NotImplementedError:
            If the platform is not supported.
    """
    if mythos == 'win32':
        from .winusb4parse import WinUsb4TreeParse as OS_USB4TBParser

    elif mythos == 'linux':
        from .linuxusb4parse import LinuxUsb4TreeParse as OS_USB4TBParser

    elif mythos == 'darwin':
        from .macusb4parse import MacUsb4TreeParse as OS_USB4TBParser

    else:
        raise NotImplementedError(
            f"Platform '{sys.platform}' not supported"
        )

    if mythos in ('win32', 'linux', 'darwin'):
        return OS_USB4TBParser()

    else:
        raise NotImplementedError(
            f"Platform '{mythos}' not supported"
        )