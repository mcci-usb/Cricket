#======================================================================
# (c) 2020  MCCI, Inc.
#----------------------------------------------------------------------
# Project : UI3141/3201 GUI Application
# File    : usbDev.py
#----------------------------------------------------------------------
# USB Device Tree changes implementation
#======================================================================

#======================================================================
# IMPORTS
#======================================================================

import getusb

from uiGlobals import *


#======================================================================
# COMPONENTS
#======================================================================

# Get USB Device Tree changes list
def get_tree_change(top):
    dl, newlist = getusb.scan_usb()
    top.update_usb_status(dl)
    oldlist = top.get_usb_list()
    strchg = None

    adlist = [i for i in newlist if i not in oldlist]
    rmlist = [i for i in oldlist if i not in newlist]

    strout = ""
    
    if(len(adlist) == 0 and len(rmlist) == 0):
        strout = ("No Change\n")
    
    if(len(rmlist)):
        strout = strout + "Removed\n"
        strout = strout + get_usb_device_info(rmlist)

    if(len(adlist)):   
        strout = strout + "Added\n"
        strout = strout + get_usb_device_info(adlist)

    top.save_usb_list(newlist)
    top.print_on_usb(strout)

# Show VID, PID and Speed info of added/removed USB devices
def get_usb_device_info(udlist):
    dlist = get_usb_class(udlist)
    cnt = 0
    strdev = ""
    for dev in udlist:
        s = ','
        strin = s.join(dlist[cnt])
        cnt = cnt + 1
        hvid = ("%X"%int(dev.get('vid'))).zfill(4)
        hpid = ("%X"%int(dev.get('pid'))).zfill(4)
        vpid = " (VID_"+hvid+"; PID_"+hpid+"; "+usbSpeed.get(dev.get('speed')-1)+")"
        strdev = strdev + str(cnt)+ ". " + strin + vpid + "\n"
    return strdev

# Get USB class        
def get_usb_class(clist):
    nlist = []
    for i in range(len(clist)):
        nlis = clist[i].get('ifc')
        res = []
        for k in nlis:
            if k not in res:
                res.append(k)
        nlist.append(res)

    flist = []
    for i in range(len(nlist)):
        flis = nlist[i]
        res = []
        for k in flis:
            res.append(usbClass.get(k))
        flist.append(res)
    return flist