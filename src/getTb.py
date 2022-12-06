# -*- coding: utf-8 -*-
##############################################################################
# 
# Module: devServer.py
#
# Description:
#     Server socket module, which listens for the client
#     Based on the command from Clinet, control device which is connected
#     Send the response back to Clinet in JSON format (JSON Object)
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
#     Seenivasan V, MCCI Corporation June 2021
#
# Revision history:
#    V2.6.0 Wed Apr 20 2022 17:00:00   Seenivasan V
#       Module created
##############################################################################
# Built-in imports
import json

import sys
import os

# Own modules
import xml.dom.minidom 

DOM_ELEMENT = 1
NODE_TEXT = 3
DOCUMENT_TYPE = 10

# Key Macros
BUSNAME = "_name"
DEVNAME = "device_name_key"
UID = "switch_uid_key"
VENDORNAME = "vendor_name_key"

NODEKEY = "_items"

##############################################################################
# Utilities
##############################################################################

def filterTextNodes(inpDE):
    fnodes = []
    for elem in inpDE.childNodes:
        if elem.nodeType == DOM_ELEMENT:
            fnodes.append(elem)
    return fnodes

def checkDataType(inpDE):
    dtypeIdx = None
    for idx, elem in enumerate(inpDE):
        if(elem.nodeName == "key"):
            if(elem.firstChild.nodeValue == "_dataType"):
                dtypeIdx = idx + 1

    dataType = inpDE[dtypeIdx].firstChild.nodeValue
    
    if(dataType == "SPThunderboltDataType"):
        return True
    return False

def pickArrayElementFromItem(inpDE):
    dtypeIdx = None
    for idx, elem in enumerate(inpDE):
        if(elem.nodeName == "key"):
            if(elem.firstChild.nodeValue == "_items"):
                dtypeIdx = idx + 1

    dataType = inpDE[dtypeIdx].nodeName
    if(dataType == "array"):
        return inpDE[dtypeIdx]
    else:
        return None

# Function to calculate number of buses
# Number of buses = number of Dict elements in the imAE
def getTotalBuses(imAE):
    fnodes = filterTextNodes(imAE)
    rnodes = []
    for ie in fnodes:
        if ie.nodeName == "dict":
            rnodes.append(ie)
    return rnodes

def getBusProperties(sbe):
    busparam = []
    busidx = []
    rnodes = filterTextNodes(sbe)
    for idx, elem in enumerate(rnodes):
        if(elem.nodeName == "key"):
            if(elem.firstChild.nodeValue == BUSNAME):
                busidx.append(idx+1)
            elif(elem.firstChild.nodeValue == DEVNAME):
                busidx.append(idx+1)
            elif(elem.firstChild.nodeValue == UID):
                busidx.append(idx+1)
            elif(elem.firstChild.nodeValue == VENDORNAME):
                busidx.append(idx+1)
    for idx in busidx:
        busparam.append(rnodes[idx].firstChild.nodeValue)
    return busparam

def getTotalBusNames(tbe):
    busparam = []
    for ide in tbe:
        busparam.append(getBusProperties(ide))
    return busparam

def getBusHubPtrs(sbe):
    sbushubptrs = []
    busidx = None
    hae = None
    rnodes = filterTextNodes(sbe)
    for idx, elem in enumerate(rnodes):
        if(elem.nodeName == "key"):
            if(elem.firstChild.nodeValue == NODEKEY):
                busidx = idx+1
    if(busidx != None):
        dataType = rnodes[busidx].nodeName
        if(dataType == "array"):
            hae = rnodes[busidx]
        if(hae != None):
            hrnodes = filterTextNodes(hae)
            for elem in hrnodes:
                if elem.nodeName == "dict":
                    sbushubptrs.append(elem)
    
    return sbushubptrs

def getTotalBusHubPtrs(tbe):
    tbushubptrs = []
    for ide in tbe:
        tbushubptrs.append(getBusHubPtrs(ide))
    return tbushubptrs

def fetchNameAndItem(she):
    nhe = None
    chn = None
    nameidx = None
    itemidx = None
    for idx, elem in enumerate(she):
        if(elem.nodeName == "key"):
            if(elem.firstChild.nodeValue == BUSNAME):
                nameidx = idx + 1
            elif(elem.firstChild.nodeValue == NODEKEY):
                itemidx = idx + 1
            elif(elem.firstChild.nodeValue == UID):
                uididx = idx + 1

    chn = she[nameidx].firstChild.nodeValue
    uid = she[uididx].firstChild.nodeValue
    nodename = chn+","+uid
    if(itemidx != None):
        nhe = she[itemidx]
    return nodename, nhe

def getDictNodeFromArray(inpDN):
    dnode = None
    rnodes = filterTextNodes(inpDN)
    for idx, elem in enumerate(rnodes):
        if(elem.nodeName == "dict"):
            dnode = elem
    return dnode

def getBusHubs(sbhptr):
    sbushubs = []
    if(len(sbhptr) == 0):
        return sbushubs
    
    # Hub pointer is a Dict Element which may contains nested hubs and ports
    # In which there should be a name key and item key which is optional
    # if name key found, append the name string to the list
    # then if item key found do the nested operation until no item key found
    
    # Remove the Text Nodes
    trhptr = []
    for elem in sbhptr:
        trhptr.append(filterTextNodes(elem))

    hname, nitem = fetchNameAndItem(trhptr[0])
        
    # Fetch Name and Item
    for she in trhptr:
        hname, nitem = fetchNameAndItem(she)
        sbushubs.append(hname)
        while(nitem != None):
            rnodes = getDictNodeFromArray(nitem)
            rrnodes = filterTextNodes(rnodes)
            hname, nitem = fetchNameAndItem(rrnodes)
            sbushubs.append(hname)
    return sbushubs

def scan_tb():
    buses = []  # contains Dict Elements
    busNames = [] # [["bus0 busname", "deviceName", "UID", "Vendor Name"],["bus1 busname", "deviceName", "UID", "Vendor Name"]]
    busHubPtrs = [] # [[bus_0 hub1, hub2,...,hubn],[bus_1 hub1, hub2,...,hubn]]
    busHubs = []
    
    tbdict = {}
    
    xmldoc = os.popen("system_profiler -xml SPThunderboltDataType")
    # Use the parse() function to load and parse an XML file
    xmlobj = xml.dom.minidom.parseString(xmldoc.read())

    childobj = None
    child = xmlobj.childNodes
    childobj = child[1]

    # Plist should contains 2 DOM text nodes and one array element
    fnodes = filterTextNodes(childobj)
    mAE = fnodes[0]

    # This DOM Element (array) contains 2 DOM text nodes and one DOM Element (dict)
    fnodes = filterTextNodes(mAE)
    mDE = fnodes[0]

    fmDE = filterTextNodes(mDE)
    if checkDataType(fmDE):
        
        imAE = pickArrayElementFromItem(fmDE)
        
        buses = getTotalBuses(imAE)
        busNames = getTotalBusNames(buses)
        
        busHubPtrs = getTotalBusHubPtrs(buses)
        
        for hptr in busHubPtrs:
            busHubs.append(getBusHubs(hptr))

        fbnames = []
        for bus in busNames:
            try:
                fbnames.append(bus[0])
            except:
                pass

        for idx, hubs in enumerate(busHubs):
            try:
                tbdict[fbnames[idx]] = hubs
            except:
                pass
    else:
        print("Thunderbolt Data type fail")

    return tbdict