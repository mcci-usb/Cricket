# usbenum.py
import sys

class USB4TBParser:
    def __init__(self):
        pass

    def parse_usb4tb_data(self):
        raise NotImplementedError("Subclasses must implement parse usb4 tb devices")


# # Import OS-dependent classes
# if sys.platform == 'win32':
#     from .winusb4parse import WinUsb4TreeParse as OS_USB4TBParsercreate_usb4tb_parser
# elif sys.platform == 'linux':
#     from .linuxusb4parse import LinuxUsb4TreeParse as OS_USB4TBParser
# elif sys.platform == 'darwin':
#     from .macusb4parse import MacUsb4TreeParse as OS_USB4TBParser
# else:
#     raise NotImplementedError(f"Platform '{sys.platform}' not supported")


# def create_usb4tb_parser(mythos):
#     # if sys.platform == 'win32' or sys.platform == 'linux' or sys.platform == 'darwin':
#     if mythos == 'win32' or mythos == 'linux' or mythos == 'darwin':
#         return OS_USB4TBParser()
#     else:
#         raise NotImplementedError(f"Platform '{mythos}' not supported")
    

def create_usb4tb_parser(mythos):
    if mythos == 'win32':
        from .winusb4parse import WinUsb4TreeParse as OS_USB4TBParser
    elif mythos == 'linux':
        from .linuxusb4parse import LinuxUsb4TreeParse as OS_USB4TBParser
    elif mythos == 'darwin':
        from .macusb4parse import MacUsb4TreeParse as OS_USB4TBParser
    else:
        raise NotImplementedError(f"Platform '{sys.platform}' not supported")

    # if sys.platform == 'win32' or sys.platform == 'linux' or sys.platform == 'darwin':
    if mythos == 'win32' or mythos == 'linux' or mythos == 'darwin':
        return OS_USB4TBParser()
    else:
        raise NotImplementedError(f"Platform '{mythos}' not supported")