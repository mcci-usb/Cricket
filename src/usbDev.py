##############################################################################
# 
# Module: usbDev.py
#
# Description:
#     USB Device Tree changes implementation
#
# Copyright notice:
#     This file copyright (c) 2020 by
#
#         MCCI Corporation
#         3520 Krums Corners Road
#         Ithaca, NY  14850
#
#     Released under the MCCI Corporation.
#
# Author:
#     Seenivasan V, MCCI Corporation Mar 2020
#
# Revision history:
#     V2.0.0 Fri Jan 15 2021 18:50:59 seenivasan
#       Module created
##############################################################################
# Own modules
import getusb
from uiGlobals import *

##############################################################################
# Utilities
##############################################################################
"""
Get USB Device Tree changes list 
Args:
    top: create a object
Returns:
    return None
"""
def get_tree_change(top):
    # usb scanning 
    dl, newlist = getusb.scan_usb()
    top.update_usb_status(dl)
    oldlist = top.get_usb_list()
    # save usb data list
    top.save_usb_list(newlist)
    strchg = None

    adlist = [i for i in newlist if i not in oldlist]
    rmlist = [i for i in oldlist if i not in newlist]

    strout = ""
    
    if(len(adlist) == 0 and len(rmlist) == 0):
        # no device added removed from port print "No change"
        strout = ("No Change\n")
    
    if(len(rmlist)):
        # Usb removed from the port print "Removed"
        strout = strout + "Removed\n"
        strout = strout + get_usb_device_info(rmlist)

    if(len(adlist)):   
        # Usb Added from the port print "Added"
        strout = strout + "Added\n"
        strout = strout + get_usb_device_info(adlist)

    top.print_on_usb(strout)
"""
Show VID, PID and Speed info of added/removed USB devices 
Args:
    udlist: usb device list
Returns:
    return None
"""
def get_usb_device_info(udlist):
    dlist = get_usb_class(udlist)
    cnt = 0
    strdev = ""
    for dev in udlist:
        try:
            s = ','
            strin = s.join(dlist[cnt])
            cnt = cnt + 1
            hvid = ("%X"%int(dev.get('vid'))).zfill(4)
            hpid = ("%X"%int(dev.get('pid'))).zfill(4)
            vpid = " (VID_"+hvid+"; PID_"+hpid+"; "+usbSpeed.get(dev.get('speed')-1)+")"
            strdev = strdev + str(cnt)+ ". " + strin + vpid + "\n"
        except:
            cnt = cnt + 1
            hvid = ("%X"%int(dev.get('vid'))).zfill(4)
            hpid = ("%X"%int(dev.get('pid'))).zfill(4)
            vpid = " (VID_"+hvid+"; PID_"+hpid+")"
            strdev = strdev + str(cnt)+ ". " + vpid + " Device Error\n"
    
    return strdev
"""
Get USB class 
Args:
    clist:usb class list
Returns:
    return None
"""        
def get_usb_class(clist):
    nlist = []
    for i in range(len(clist)):
        try:
            nlis = clist[i].get('ifc')
            res = []
            for k in nlis:
                if k not in res:
                    res.append(k)
            nlist.append(res)
        except:
            nlist.append("Class Error")

    flist = []
    for i in range(len(nlist)):
        try:
            flis = nlist[i]
            res = []
            for k in flis:
                res.append(usbClass.get(k))
            flist.append(res)
        except:
            flist.append("Class Error")
    return flist