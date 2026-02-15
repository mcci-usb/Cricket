# -*- coding: utf-8 -*-
##############################################################################
#
# Module: thControl.py
#
# Description:
#     Receives device control commands from respective device windows.
#     Verifies whether the device is available over the network.
#     If available remotely, commands are sent to the server.
#     If available locally, commands are executed directly.
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
#
##############################################################################

# Own modules
import thClient as thnw
import usbChange as thlocal
from uiGlobals import *

##############################################################################
# Device Control Configuration
##############################################################################

def SetDeviceControl(top):
    """
    Configure device control interface.

    Determines whether device control should be
    handled via Serial, TCP Network, or Local mode
    based on system role configuration.

    Args:
        top: Reference to main application instance.

    Returns:
        None

    Raises:
        None
    """
    if not top.myrole["thc"]:
        if top.myrole["uc"]:
            try:
                if (
                    top.ucConfig["mynodes"]["mythc"]["interface"]
                    == "serial"
                ):
                    top.thCtrl = "serial"
                else:
                    top.thCtrl = "tcp"
            except Exception:
                top.thCtrl = "tcp"
    else:
        top.thCtrl = "local"

def ResetDeviceControl(top):
    """
    Reset device control communication.

    Closes active host controller client
    socket connections if available.

    Args:
        top: Reference to main application instance.

    Returns:
        None

    Raises:
        None
    """
    if top.hcclient is not None:
        top.clienthc.close()
        top.hcclient.close()

##############################################################################
# USB Tree Change Handling
##############################################################################

def get_tree_change(top):
    """
    Retrieve USB tree change information.

    Based on configured control mode, retrieves
    USB topology either locally or via network.

    Args:
        top: Reference to main application instance.

    Returns:
        None

    Raises:
        None
    """

    # Local USB tree handling
    if top.thCtrl == "local":
        thlocal.get_usb_change(top)

    # Network USB tree handling
    elif top.thCtrl == "tcp":

        nwip = top.ucConfig["mynodes"]["mythc"]["tcp"]["ip"]
        nwport = top.ucConfig["mynodes"]["mythc"]["tcp"]["port"]

        resdict = thnw.get_usb_tree(nwip, int(nwport))

        if len(resdict) > 0:

            if resdict["result"][0]["status"] == "OK":

                findict = resdict["result"][1]["data"]

                thlocal.prepare_tree_change(
                    top,
                    findict["usb3d"],
                    findict["usb4d"],
                )

                if (
                    findict["tbjson"] is not None
                    and len(findict["tbjson"]) > 0
                ):
                    top.store_usb4_win_info(findict["tbjson"])

            else:
                top.print_on_log(
                    "TH Computer Connection Fail!\n"
                )
                top.device_no_response()

        else:
            top.print_on_log(
                "TH Computer Connection Fail!\n"
            )
            top.device_no_response()