# usbenum.py
import sys

class USB3Parser:
    def __init__(self):
        pass

    def parse_usb3tb_data(self):
        raise NotImplementedError("Subclasses must implement parse usb4 tb devices")

def create_usb3tb_parser(mythos):
    if mythos == 'win32':
        from .winusb3parse import WinUsb3TreeParse as OS_USB4TBParser
    elif mythos == 'linux':
        from .linuxusb3parse import LinuxUsb4TreeParse as OS_USB4TBParser
    elif mythos == 'darwin':
        from .macusb4parse import MacUsb4TreeParse as OS_USB4TBParser
    else:
        raise NotImplementedError(f"Platform '{sys.platform}' not supported")

    # if sys.platform == 'win32' or sys.platform == 'linux' or sys.platform == 'darwin':
    if mythos == 'win32' or mythos == 'linux' or mythos == 'darwin':
        return OS_USB4TBParser()
    else:
        raise NotImplementedError(f"Platform '{mythos}' not supported")