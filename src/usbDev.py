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
#    V2.6.0 Wed Apr 20 2022 17:00:00   Seenivasan V
#       Module created
##############################################################################
import copy
from distutils.dep_util import newer

# Own modules
import getusb
import getTb

from uiGlobals import *

##############################################################################
# Utilities
##############################################################################

def get_usb_tree():
    """
    get the information of USB Tree view window.
    Args:
        no argument
    Returns:
        None
    """
    dl, newlist = getusb.scan_usb()
    return dl, newlist

def get_tb_tree():
    newdict = getTb.scan_tb()
    return newdict

def get_tb_tree_change(top, newdict):
    olddict = top.get_tb_list()
    if len(olddict) == 0:
        olddict = newdict
            
    # Save tb device list
    top.save_tb_list(newdict)

    nlist = newdict
    olist = olddict

    keyol = list(nlist.keys())
    keynl = list(olist.keys())
    
    adlist = [i for i in keynl if i not in keyol]
    # print("adlist:", adlist)
    rmlist = [i for i in keyol if i not in keynl]
    # print("rmlist:",rmlist)

    resd = {}

    for bus in keyol:
        ol = olddict[bus]
        nl = newdict[bus]
        ind = {}
        alist = [i for i in nl if i not in ol]
        # print("alist:", alist)
        rlist = [i for i in ol if i not in nl]
        ind["added"] = alist
        ind["removed"] = rlist
        resd[bus] = ind

    print("TB Tree change\n")
    print(resd)

    # addCnt = 0
    # rmdCnt = 0
    # strout = ""

    # for idict in resd:
    #     addCnt = addCnt + len(resd[idict]["added"])
    #     rmdCnt = rmdCnt + len(resd[idict]["removed"])

    # if(addCnt == 0 and rmdCnt == 0):
    #     # No device added removed from port, then print "No change"
    #     strout = ("TB No Change\n")
    
    # if(addCnt > 0):
    #     strout = ("TB Added: "+str(addCnt)+"\n")

    # if(rmdCnt > 0):
    #     strout = strout + ("TB Removed: "+str(rmdCnt)+"\n")

    addLst = []
    rmdLst = []
    strout = ""

    for idict in resd:
        for elem in resd[idict]["added"]:
            addLst.append(elem)
        for elem in resd[idict]["removed"]:
            rmdLst.append(elem)

    if(len(addLst) == 0 and len(rmdLst) == 0):
        # No device added removed from port, then print "No change"
        strout = ("Thunderbolt No Change\n")
    
    if(len(addLst) > 0):
        strout = strout + "Thunderbolt Added\n"
        for elem in addLst:
            strout = strout + elem + "\n"

    if(len(rmdLst) > 0):
        strout = strout + "Thunderbolt Removed\n"
        for elem in rmdLst:
            strout = strout + elem + "\n"

    top.print_on_log(strout)


def get_tree_change(top, dl, newlist):
    """
    Get USB Device Tree changes list and print the list in USB Device Tree
    View Changes Window

    Args:
        top: creates an object
    Returns:
        None
    """
    top.update_usb_status(dl)
    oldlist = top.get_usb_list()
    if len(oldlist) == 0:
        oldlist = newlist
            
    # Save usb device list
    top.save_usb_list(newlist)

    newset =  [i for n, i in enumerate(newlist) if i not in newlist[n + 1:]]

    unewlist = copy.deepcopy(newlist)    
    for i in newset:
        rcnt = 0
        for j in unewlist:
            if(i == j):
                rcnt = rcnt + 1
                j["count"] = rcnt

    oldset =  [i for n, i in enumerate(oldlist) if i not in oldlist[n + 1:]]

    uoldlist = copy.deepcopy(oldlist)

    for i in oldset:
        rcnt = 0
        for j in uoldlist:
            if(i == j):
                rcnt = rcnt + 1
                j["count"] = rcnt
    
    strchg = None

    adlist = [i for i in unewlist if i not in uoldlist]
    rmlist = [i for i in uoldlist if i not in unewlist]

    strout = ""
    
    if(len(adlist) == 0 and len(rmlist) == 0):
        # No device added removed from port, then print "No change"
        strout = ("No Change\n")
    
    if(len(rmlist)):
        # Usb removed from the port, then print "Removed"
        strout = strout + "Removed\n"
        strout = strout + get_usb_device_info(rmlist)

    if(len(adlist)):   
        # Usb Added from the port, then print "Added"
        strout = strout + "Added\n"
        strout = strout + get_usb_device_info(adlist)
    
    # Print the device list USB Device Tree Window
    top.print_on_log(strout)

def get_usb_device_info(udlist):
    """
    Show VID, PID and Speed info of added/removed USB devices 

    Args:
        udlist: USB device list which are removed/added recently
    Returns:
        strdev: String which contains the VID, PID and Speed info of the USB 
        device list
    """
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
            vpid = " (VID_"+hvid+"; PID_"+hpid+"; "+usbSpeed.get(
                      dev.get('speed')-1)+")"
            strdev = strdev + str(cnt)+ ". " + strin + vpid + "\n"
        except:
            cnt = cnt + 1
            hvid = ("%X"%int(dev.get('vid'))).zfill(4)
            hpid = ("%X"%int(dev.get('pid'))).zfill(4)
            vpid = " (VID_"+hvid+"; PID_"+hpid+")"
            strdev = strdev + str(cnt)+ ". " + vpid + " Device Error\n"
    
    return strdev
     
def get_usb_class(clist):
    """
    Get class of the USB device  

    Args:
        clist: List contains the USB devices
    Returns:
        flist: List contains the class of the given USB devices
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