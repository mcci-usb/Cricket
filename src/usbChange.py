import sys
import copy

from uiGlobals import *

def get_usb_change(top):
    """
    get the information of USB Tree view window.
    Args:
        no argument
    Returns:
        None
    """    
    top.usbenum.enumerate_usb_devices()
    result = top.usbenum.get_result()

    usb3diff = get_usb3_change(top, result["usb3list"])
    usb4diff = get_usb4_change(top, result["usb4tblist"])
    top.update_usb_status(result["usb3type"])
    
    if top.myrole['uc']:
        prepare_tree_change(top, usb3diff, usb4diff)

    if result["usb4tbjson"] != None and len(result["usb4tbjson"]) > 0:
        if top.myrole['uc']:
            top.store_usb4_win_info(result["usb4tbjson"])
        else:
            resdict = {}
            resdict["usb3d"] = usb3diff
            resdict["usb4d"] = usb4diff
            resdict["tbjson"] = result["usb4tbjson"]
            return resdict
    else:
        resdict = {}
        resdict["usb3d"] = usb3diff
        resdict["usb4d"] = []
        resdict["tbjson"] = []
        return resdict
        

def get_usb3_change(top, newlist):
    oldlist = top.get_usb_list()
    if oldlist == None:
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
                if "count" in j:
                    j["count"] = rcnt

    oldset =  [i for n, i in enumerate(oldlist) if i not in oldlist[n + 1:]]

    uoldlist = copy.deepcopy(oldlist)

    for i in oldset:
        rcnt = 0
        for j in uoldlist:
            if(i == j):
                rcnt = rcnt + 1
                if "count" in j:
                    j["count"] = rcnt
    
    adlist = [i for i in unewlist if i not in uoldlist]
    rmlist = [i for i in uoldlist if i not in unewlist]

    return {"added": adlist, "removed": rmlist}

    
def get_usb4_change(top, newlist): 
    oldlist = top.get_tb_list()
    if oldlist == None:
        oldlist = newlist
    
    top.save_tb_list(newlist)

    newset =  [i for n, i in enumerate(newlist) if i not in newlist[n + 1:]]

    unewlist = copy.deepcopy(newlist)    
    for i in newset:
        rcnt = 0
        for j in unewlist:
            if(i == j):
                rcnt = rcnt + 1
                if "count" in j:
                    j["count"] = rcnt

    oldset =  [i for n, i in enumerate(oldlist) if i not in oldlist[n + 1:]]

    uoldlist = copy.deepcopy(oldlist)

    for i in oldset:
        rcnt = 0
        for j in uoldlist:
            if(i == j):
                rcnt = rcnt + 1
                if "count" in j:
                    j["count"] = rcnt
    
    adlist = [i for i in unewlist if i not in uoldlist]
    rmlist = [i for i in uoldlist if i not in unewlist]

    return {"added": adlist, "removed": rmlist}

def prepare_tree_change(top, usb3dict, usb4dict):
    strout = ""
    addedlist = []
    rmdlist = []
    for dev in usb3dict["added"]:
        addedlist.append(dev)
    
    if usb4dict != None and len(usb4dict):
        for dev in usb4dict["added"]:
            addedlist.append(dev)

    for dev in usb3dict["removed"]:
        rmdlist.append(dev)

    if usb4dict != None and len(usb4dict):
        for dev in usb4dict["removed"]:
            rmdlist.append(dev)
    
    if(len(addedlist) == 0 and len(rmdlist) == 0):
        # No device added removed from port, then print "No change"
        strout = ("No Change\n")
    
    if(len(rmdlist)):
        strout = strout + "Removed\n"
        strout = strout + convert_usb_info(top, rmdlist)

    if(len(addedlist)):   
        strout = strout + "Added\n"
        strout = strout + convert_usb_info(top, addedlist)
    
    # Print the device list USB Device Tree Window
    top.print_on_log(strout)


def convert_usb_info(top, udlist):
    usb3_list = []
    usb4_list = []

    for dev in udlist:
        if dev["type"] == "usb3":
            usb3_list.append(dev)
        elif dev["type"] == "usb4":
            usb4_list.append(dev)

    cnt = 0
    strdev = ""
    for dev3 in usb3_list:
        
        try:
            hvid = ("%X" % int(dev3.get('vid'))).zfill(4)
            hpid = ("%X" % int(dev3.get('pid'))).zfill(4)
            # vpid = " (VID_" + hvid + "; PID_" + hpid + ")"
            vpid = " (VID_"+hvid+"; PID_"+hpid+"; "+usbSpeed.get(dev3.get('speed')-1)+")"

            usb_class = get_usb_class([dev3])  # Call to get_usb_class function
            # strdev = strdev + f"{cnt + 1}. {vpid}({', '.join(usb_class[0])})\n"
            strdev = strdev + f"{cnt + 1}. {', '.join(usb_class[0])}({vpid}) \n"
            
            cnt += 1
        except:
            hvid = ("%X" % int(dev3.get('vid'))).zfill(4)
            hpid = ("%X" % int(dev3.get('pid'))).zfill(4)
            vpid = " (VID_" + hvid + "; PID_" + hpid + ") USB3 Device Error\n"
            strdev = strdev + str(cnt + 1) + ". " + vpid + "\n"
            cnt += 1

    for dev4 in usb4_list:
        thcostype = sys.platform
        if not top.myrole['thc']:
            thcostype = top.ucConfig['mynodes']["mythc"]["os"]
        if thcostype == 'win32':
            try:
                hvid = ("%X" % int(dev4.get('vid'))).zfill(4)
                hpid = ("%X" % int(dev4.get('pid'))).zfill(4)
                hcls = dev4.get('ufpCLS')
                hnlw = dev4.get('ufpNLW')


                htls = dev4.get('ufpTLS')
                htlw = dev4.get('ufpTLW')

                hmn = dev4.get('mname')
                # vpid = f"{hmn} (VID_{hvid}; PID_{hpid}; SPEED_{htls} x {htlw}; CURRENT_{hcls} x {hnlw}))"
                vpid = f"{hmn} (VID_{hvid}; PID_{hpid}; SPEED_{htls} x {htlw}))"

                strdev = strdev + f"{cnt + 1}. {vpid}\n"
                cnt += 1
            except:
                hvid = ("%X" % int(dev4.get('vid'))).zfill(4)
                hpid = ("%X" % int(dev4.get('pid'))).zfill(4)
                hcls = dev4.get('ufpCLS')
                htls = dev4.get('ufpTLS')
                vpid = f" (VID_{hvid}; PID_{hpid}) USB4 Device Error\n"
                strdev = strdev + f"{cnt + 1}. {vpid}\n"
                cnt += 1
        elif thcostype == 'linux':
            try:
                hwid = dev4.get('uuid')
                htls = dev4.get('tx speed')
                hmn = dev4.get('name')
                vpid = f"{hmn} ({hwid}, Speed {htls}))"
                strdev = strdev + f"{cnt + 1}. {vpid}\n"
                cnt += 1
            except:
                hvid = "NA"
                hpid = "NA"
                htls = dev4.get('tx speed')
                vpid = f" (VID_{hwid}) USB4 Device Error\n"
                strdev = strdev + f"{cnt + 1}. {vpid}\n"
                cnt += 1
        elif thcostype == 'darwin':
            try:
                hwid = dev4.get('hwid')
                htls = dev4.get('speed')
                hmn = dev4.get('name')
                vname = dev4.get('vendorName')
                vpid = f"{hmn} ({vname}, {hwid}, Speed {htls}))"
                strdev = strdev + f"{cnt + 1}. {vpid}\n"
                cnt += 1
            except:
                hvid = "NA"
                hpid = "NA"
                hwid = "NA"
                htls = "NA"
                vpid = f" (VID_{hwid}) USB4 Device Error\n"
                strdev = strdev + f"{cnt + 1}. {vpid}\n"
                cnt += 1
        else:
            pass

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
        # if clist[i].get("type") == 'usb3':
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
