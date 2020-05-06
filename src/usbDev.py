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
    
    cnt = 0
    if(len(rmlist)):
        strout = strout + "Removed\n"
        dlist = get_usb_class(rmlist)
        for dev in rmlist:
            s = ','
            strin = s.join(dlist[cnt])
            cnt = cnt + 1
            hvid = ("%X"%int(dev.get('vid'))).zfill(4)
            hpid = ("%X"%int(dev.get('pid'))).zfill(4)
            vpid = " (VID_"+hvid+"; PID_"+hpid+")"
            strout = strout + str(cnt)+ ". " + strin + vpid + "\n"
    
    cnt = 0
    if(len(adlist)):
        strout = strout + "Added\n"
        dlist = get_usb_class(adlist)
        for dev in adlist:
            s = ','
            strin = s.join(dlist[cnt])
            cnt = cnt + 1
            hvid = ("%X"%int(dev.get('vid'))).zfill(4)
            hpid = ("%X"%int(dev.get('pid'))).zfill(4)
            vpid = " (VID_"+hvid+"; PID_"+hpid+")"
            strout = strout + str(cnt)+ ". " + strin + vpid + "\n"
    top.save_usb_list(newlist)
    top.print_on_usb(strout)
        
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