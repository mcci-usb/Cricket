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
#    V4.0.0 Wed May 25 2023 17:00:00   Seenivasan V
#       Module created
##############################################################################
# Built-in imports

import socket
import json

def send_request(host, port, reqdict):
    """
    sending the host computer request from client
    Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        port: when added the port in to the test host side.
        reqdict: sending the request command.
    Return:
        return: sending the request with command "lsusb" in dictionary form

    """
    hs =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hs.settimeout(20)
    rdict = {}
    rlist = []
    sdict = {}
    try:
        result = hs.connect((host, port))
        #rcvdata = cs.recv(1024)
        data = json.dumps(reqdict)
        hs.send(data.encode('utf-8'))
        rcvdata = hs.recv(1024)
        rcvdict = json.loads(rcvdata.decode())
        sdict["status"] = "OK"
        rlist.append(sdict)
        rlist.append(rcvdict)
    except:
        sdict["status"] = "fail"
        rlist.append(sdict)
    rdict["result"] = rlist
    return rdict

def get_usb_tree(host, port):
    """
    getting usb device info from host computer server with the command lsusb.

    Args:
        host: hostcmputer allows only new device info
        port: when added the port in to the test host side.
        return: sending the request with command "lsusb" in dictionary form
    Returns:
        None
        """
    reqdict = {}
    reqdict["ctype"] = "usb"
    reqdict["cmd"] = "lsusb"
    return send_request(host, port, reqdict)