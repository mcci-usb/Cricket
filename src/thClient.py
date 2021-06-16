##############################################################################
# 
# Module: thClient.py
#
# Description:
#     Client Socket module - Communicates with the Server where device is connected
#     Interface between devControl and device module
#     Send device control command to Server and receive response from the server
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
#     V2.4.0-2 Wed June 14 2021 18:50:10 seenivasan
#       Module created
##############################################################################
# Built-in imports

import socket
import json

def send_request(host, port, cmd):
    cs =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cs.settimeout(20)
    rdict = {}
    rlist = []
    sdict = {}
    try:
        result = cs.connect((host, port))
        #rcvdata = cs.recv(1024)
        cs.send(cmd.encode())
        rcvdata = cs.recv(1024)
        nwdata = json.loads(rcvdata.decode())
        #return json.loads(rcvdata.decode())
        sdict["status"] = "OK"
        rlist.append(sdict)
        rlist.append(nwdata)
    except:
        sdict["status"] = "fail"
        rlist.append(sdict)
    rdict["result"] = rlist
    return rdict

def get_usb_tree(host, port):
    cmd = "usb,lsusb"
    return send_request(host, port, cmd)