# -*- coding: utf-8 -*-
##############################################################################
# 
# Module: usbChange.py
#
# Description:
#     Print the device added/removed information.
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
import copy

# Own modules
from uiGlobals import *

def get_usb_change(top):
    """
    Get the information of USB Tree view window.

    Args:
        top: Top-level UI object.

    Returns:
        dict | None: USB change details if applicable.
    """
    top.usbenum.enumerate_usb_devices()
    result = top.usbenum.get_result()

    usb3tree = result["usb3list"]
    usb3diff = get_usb3_change(top, result["usb3list"])
    usb4diff = get_usb4_change(top, result["usb4tblist"])
    top.update_usb_status(result["usb3type"])

    if top.myrole['uc']:
        prepare_tree_change(top, usb3diff, usb4diff)

    if result["usb4tbjson"] is not None and len(result["usb4tbjson"]) > 0:
        if top.myrole['uc']:
            top.store_usb4_win_info(result["usb4tbjson"])
            top.store_usb3_win_info(usb3tree)
        else:
            resdict = {
                "usb3d": usb3diff,
                "usb4d": usb4diff,
                "tbjson": result["usb4tbjson"],
            }
            return resdict
    else:
        resdict = {
            "usb3d": usb3diff,
            "usb4d": [],
            "tbjson": [],
        }
        top.store_usb3_win_info(usb3tree)
        return resdict

def get_usb3_change(top, newlist):
    """
    Get USB3 device change information.

    Args:
        top: Top-level UI object.
        newlist: Current USB3 device list.

    Returns:
        dict: Added and removed USB3 devices.
    """
    oldlist = top.get_usb_list()
    if oldlist is None:
        oldlist = newlist

    top.save_usb_list(newlist)

    newset = [i for n, i in enumerate(newlist) if i not in newlist[n + 1:]]
    unewlist = copy.deepcopy(newlist)

    for i in newset:
        rcnt = 0
        for j in unewlist:
            if i == j:
                rcnt += 1
                if "count" in j:
                    j["count"] = rcnt

    oldset = [i for n, i in enumerate(oldlist) if i not in oldlist[n + 1:]]
    uoldlist = copy.deepcopy(oldlist)

    for i in oldset:
        rcnt = 0
        for j in uoldlist:
            if i == j:
                rcnt += 1
                if "count" in j:
                    j["count"] = rcnt

    adlist = [i for i in unewlist if i not in uoldlist]
    rmlist = [i for i in uoldlist if i not in unewlist]

    return {"added": adlist, "removed": rmlist}

def get_usb4_change(top, newlist):
    """
    Get USB4 device change information.

    Args:
        top: Top-level UI object.
        newlist: Current USB4 device list.

    Returns:
        dict: Added and removed USB4 devices.
    """
    oldlist = top.get_tb_list()
    if oldlist is None:
        oldlist = newlist

    top.save_tb_list(newlist)

    newset = [i for n, i in enumerate(newlist) if i not in newlist[n + 1:]]
    unewlist = copy.deepcopy(newlist)

    for i in newset:
        rcnt = 0
        for j in unewlist:
            if i == j:
                rcnt += 1
                if "count" in j:
                    j["count"] = rcnt

    oldset = [i for n, i in enumerate(oldlist) if i not in oldlist[n + 1:]]
    uoldlist = copy.deepcopy(oldlist)

    for i in oldset:
        rcnt = 0
        for j in uoldlist:
            if i == j:
                rcnt += 1
                if "count" in j:
                    j["count"] = rcnt

    adlist = [i for i in unewlist if i not in uoldlist]
    rmlist = [i for i in uoldlist if i not in unewlist]

    return {"added": adlist, "removed": rmlist}

def prepare_tree_change(top, usb3dict, usb4dict):
    """
    Prepare and print USB tree change information.

    Args:
        top: Top-level UI object.
        usb3dict: USB3 change dictionary.
        usb4dict: USB4 change dictionary.
    """
    strout = ""
    addedlist = []
    rmdlist = []

    for dev in usb3dict["added"]:
        addedlist.append(dev)

    if usb4dict is not None and len(usb4dict):
        for dev in usb4dict["added"]:
            addedlist.append(dev)

    for dev in usb3dict["removed"]:
        rmdlist.append(dev)

    if usb4dict is not None and len(usb4dict):
        for dev in usb4dict["removed"]:
            rmdlist.append(dev)

    if len(addedlist) == 0 and len(rmdlist) == 0:
        strout = "No Change\n"

    if len(rmdlist):
        strout += "Removed\n"
        strout += convert_usb_info(top, rmdlist)

    if len(addedlist):
        strout += "Added\n"
        strout += convert_usb_info(top, addedlist)

    top.print_on_log(strout)

def convert_usb_info(top, udlist):
    """
    Convert USB device list into printable string format.

    Args:
        top: Top-level UI object.
        udlist: USB device list.

    Returns:
        str: Formatted device information string.
    """
    usb3_list = []
    usb4_list = []

    for dev in udlist:
        if dev["type"] == "usb3":
            usb3_list.append(dev)
        elif dev["type"] == "usb4":
            usb4_list.append(dev)

    cnt = 0
    strdev = ""

    # USB3 Devices
    for dev3 in usb3_list:
        try:
            hvid = ("%X" % int(dev3.get('vid'))).zfill(4)
            hpid = ("%X" % int(dev3.get('pid'))).zfill(4)
            vpid = (
                " (VID_" + hvid + "; PID_" + hpid + "; " +
                usbSpeed.get(dev3.get('speed') - 1) + ")"
            )

            usb_class = get_usb_class([dev3])
            strdev += f"{cnt + 1}. {', '.join(usb_class[0])}({vpid}) \n"
            cnt += 1

        except Exception:
            hvid = ("%X" % int(dev3.get('vid'))).zfill(4)
            hpid = ("%X" % int(dev3.get('pid'))).zfill(4)
            vpid = f" (VID_{hvid}; PID_{hpid}) USB3 Device Error\n"
            strdev += f"{cnt + 1}. {vpid}\n"
            cnt += 1

    # USB4 Devices (Platform based)
    for dev4 in usb4_list:
        thcostype = sys.platform
        if not top.myrole['thc']:
            thcostype = top.ucConfig['mynodes']["mythc"]["os"]

        try:
            if thcostype == 'win32':
                hvid = ("%X" % int(dev4.get('vid'))).zfill(4)
                hpid = ("%X" % int(dev4.get('pid'))).zfill(4)
                hmn = dev4.get('mname')
                htls = dev4.get('ufpTLS')
                htlw = dev4.get('ufpTLW')

                vpid = f"{hmn} (VID_{hvid}; PID_{hpid}; SPEED_{htls} x {htlw}))"

            elif thcostype == 'linux':
                hwid = dev4.get('uuid')
                htls = dev4.get('tx speed')
                hmn = dev4.get('name')
                vpid = f"{hmn} ({hwid}, Speed {htls}))"

            elif thcostype == 'darwin':
                hwid = dev4.get('hwid')
                htls = dev4.get('speed')
                hmn = dev4.get('name')
                vname = dev4.get('vendorName')
                vpid = f"{hmn} ({vname}, {hwid}, Speed {htls}))"
            else:
                continue

        except Exception:
            vpid = "USB4 Device Error"

        strdev += f"{cnt + 1}. {vpid}\n"
        cnt += 1

    return strdev

def get_usb_class(clist):
    """
    Get class of the USB device.

    Args:
        clist: List containing USB devices.

    Returns:
        list: Class list of given USB devices.
    """
    nlist = []

    for i in range(len(clist)):
        try:
            nlis = clist[i].get('ifc')
            res = []
            for k in nlis:
                if k not in res:
                    res.append(k)
            nlist.append(res)
        except Exception:
            nlist.append("Class Error")

    flist = []
    for i in range(len(nlist)):
        try:
            flis = nlist[i]
            res = []
            for k in flis:
                res.append(usbClass.get(k))
            flist.append(res)
        except Exception:
            flist.append("Class Error")

    return flist