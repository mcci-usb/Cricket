import json
import os

speed_tag = ['receptacle_1_tag', 'receptacle_2_tag', 'receptacle_3_tag', 'receptacle_4_tag']
swuid_tag = 'switch_uid_key'
tbdata_tag = 'SPThunderboltDataType'

tbbus = []

finalDict = {}


def grabData(gbus, finalDict):
    childs = None
    if swuid_tag in gbus:
        bdict = {}
        bdict['name'] = gbus['_name']
        bdict['deviceName'] = gbus['device_name_key']
        bdict['vendorName'] = gbus['vendor_name_key']

        for stag in speed_tag:
            if stag in gbus:
                bdict['speed'] = gbus[stag]['current_speed_key']
                # print(stag)
                break
        
        if '_items' in gbus.keys():
            childs = gbus['_items']
            nchild = []
            for ielem in childs:
                nchild.append(ielem[swuid_tag])
            bdict['child'] = nchild
        else:
            bdict['child'] = []
            childs = []
        finalDict[gbus[swuid_tag]] = bdict
    
    kilist = list(gbus.keys())
    for ikey in kilist:
        if ikey != "_items":
            del gbus[ikey]
    
    return childs    
    

def handleBusTree(gbus, tbdict):
    doflg = True
    while doflg:
        gchild = grabData(gbus, tbdict)
        if gchild == None:
            doflg = False
        else:
            # print(len(gchild))
            if len(gchild) > 0:
                gbus = gchild[0]
            else:
                doflg = False


def scan_tb():
    tbbus = []
    tbdict = {}

    # f = open('myspeed.json')
    # mytb = json.load(f)

    xmldoc = os.popen("system_profiler -json SPThunderboltDataType")
    mytb = json.load(xmldoc)
    # Use the parse() function to load and parse an XML file
    # xmlobj = xml.dom.minidom.parseString(xmldoc.read())

    if tbdata_tag in mytb.keys():
        tbbuses = mytb[tbdata_tag]

        for tbus in tbbuses:
            tbbus.append(tbus)

        for i in range(len(tbbus)):
            handleBusTree(tbbus[i], tbdict)
    # print(tbdict)
    return tbdict