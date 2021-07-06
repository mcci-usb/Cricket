##############################################################################
# 
# Module: devClient.py
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

def send_request(host, port, reqdict):
    cs =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cs.settimeout(20)
    rdict = {}
    rlist = []
    sdict = {}
    try:
        result = cs.connect((host, port))
        #rcvdata = cs.recv(1024)
        data= json.dumps(reqdict)
        cs.send(data.encode('utf-8'))
        rcvdata = cs.recv(1024)
        rcvdict = json.loads(rcvdata.decode())
        sdict["status"] = "OK"
        rlist.append(sdict)
        rlist.append(rcvdict)
    except:
        sdict["status"] = "fail"
        rlist.append(sdict)
    rdict["result"] = rlist
    return rdict

def get_device_list(host, port):
    reqdict = {}
    reqdict["ctype"] = "device"
    reqdict["cmd"] = "search"
    return send_request(host, port, reqdict)

def open_serial_device(host, port, sport, baud):
    reqdict = {}
    reqdict["ctype"] = "device"
    reqdict["cmd"] = "open"
    reqdict["itype"] = "serial"
    reqdict["port"] = sport
    reqdict["baud"] = str(baud)
    return send_request(host, port, reqdict)

def select_usb_device(host, port, sport):
    reqdict = {}
    reqdict["ctype"] = "device"
    reqdict["cmd"] = "open"
    reqdict["itype"] = "usb"
    reqdict["port"] = sport
    return send_request(host, port, reqdict)

def close_serial_device(host, port):
    reqdict = {}
    reqdict["ctype"] = "device"
    reqdict["cmd"] = "close"
    return send_request(host, port, reqdict)

def send_port_cmd(host, port, cmd):
    reqdict = {}
    reqdict["ctype"] = "control"
    reqdict["itype"] = "serial"
    reqdict["cmd"] = "switch"
    reqdict["stat"] = cmd
    return send_request(host, port, reqdict)

def read_port_cmd(host, port):
    reqdict = {}
    reqdict["ctype"] = "control"
    reqdict["itype"] = "serial"
    reqdict["cmd"] = "read"
    return send_request(host, port, reqdict)

def send_status_cmd(host, port):
    reqdict = {}
    reqdict["ctype"] = "control"
    reqdict["itype"] = "serial"
    reqdict["cmd"] = "status"
    return send_request(host, port, reqdict)

def send_volts_cmd(host, port):
    reqdict = {}
    reqdict["ctype"] = "control"
    reqdict["itype"] = "serial"
    reqdict["cmd"] = "volts"
    return send_request(host, port, reqdict)

def send_amps_cmd(host, port):
    reqdict = {}
    reqdict["ctype"] = "control"
    reqdict["itype"] = "serial"
    reqdict["cmd"] = "amps"
    return send_request(host, port, reqdict)

def control_port(host, port,cmd):
    reqdict = {}
    reqdict["ctype"] = "control"
    reqdict["itype"] = "usb"
    reqdict["cmd"] = str(cmd)
    return send_request(host, port, reqdict)