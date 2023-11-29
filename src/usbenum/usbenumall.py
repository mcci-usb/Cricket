# usbenum.py
import sys

class USBDeviceEnumerator:
    def __init__(self):
        self.usb_devices = []

    def enumerate_usb_devices(self):
        """
        Enumerate USB devices.

        This method must be implemented by subclasses to perform the enumeration of USB devices.
        Subclasses should provide their own implementation based on the operating system.

        Raises:
            NotImplementedError: This method should be implemented by subclasses.
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
    Create an instance of USB device enumerator based on the current operating system.

    Returns:
        OS_USBDeviceEnumerator: An instance of the appropriate USB device enumerator for the
                               current operating system.

    Raises:
        NotImplementedError: If the platform is not supported.
    """
    if sys.platform == 'win32' or sys.platform == 'linux' or sys.platform == 'darwin':
        return OS_USBDeviceEnumerator()
    else:
        raise NotImplementedError(f"Platform '{sys.platform}' not supported")