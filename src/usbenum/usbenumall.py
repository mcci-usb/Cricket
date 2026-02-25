# -*- coding: utf-8 -*-
##############################################################################
# 
# Module: usnenumall.py
#
# Description:
#     Base USB Enumeration module.
#     Provides an abstract class for enumerating USB devices across
#     different operating systems. Subclasses must implement the
#     enumeration logic specific to the target OS.
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

# Lib imports
# None

# Own modules
# (OS-dependent modules imported dynamically below)

##############################################################################
# Utilities
##############################################################################
class USBDeviceEnumerator:
    """
    Summary:
        Base class for USB device enumeration.

    Longer Description:
        This abstract class defines the structure for USB device
        enumeration. Operating system–specific subclasses must
        implement the enumeration logic.

    Attributes:
        usb_devices: List storing enumerated USB device details.
    """
    def __init__(self):
        """
        Initialize USBDeviceEnumerator class.

        Args:
            None

        Returns:
            None
        """
        self.usb_devices = []

    def enumerate_usb_devices(self):
        """
        Enumerate USB devices.

        Description:
            This method must be implemented by subclasses to perform
            USB device enumeration based on the operating system.

        Args:
            None

        Returns:
            None

        Raises:
            NotImplementedError:
                If subclass does not implement this method.
        """
        raise NotImplementedError("Subclasses must implement enumerate_usb_devices")


# Import OS-dependent classes
if sys.platform == 'win32':
    from .winusbenum import WindowsUSBDeviceEnumerator as OS_USBDeviceEnumerator
elif sys.platform == 'linux':
    from .linuxusbenum import LinuxUSBDeviceEnumerator as OS_USBDeviceEnumerator
elif sys.platform == 'darwin':
    from .macusbenum import MacOSUSBDeviceEnumerator as OS_USBDeviceEnumerator
else:
    raise NotImplementedError(f"Platform '{sys.platform}' not supported")

def create_usb_device_enumerator():
    """
    Create USB Device Enumerator instance.

    Description:
        Creates and returns an OS-specific USB device enumerator
        instance based on the current platform.

    Args:
        None

    Returns:
        OS_USBDeviceEnumerator:
            Instance of the platform-specific enumerator.

    Raises:
        NotImplementedError:
            If the current platform is not supported.
    """
    if sys.platform == 'win32' or sys.platform == 'linux' or sys.platform == 'darwin':
        return OS_USBDeviceEnumerator()
    else:
        raise NotImplementedError(f"Platform '{sys.platform}' not supported")