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

def get_device_list(host, port):
    cmd = "device"
    return send_request(host, port, cmd)


def open_serial_device(host, port, sport, baud):
    cmd = "open,"+sport+","+str(baud)
    return send_request(host, port, cmd)


def close_serial_device(host, port):
    cmd = "close"
    return send_request(host, port, cmd)

def send_port_cmd(host, port, cmd):
    ncmd = "port,"+cmd
    return send_request(host, port, ncmd)

def read_port_cmd(host, port):
    cmd = "read"
    return send_request(host, port, cmd)

def send_status_cmd(host, port):
    cmd = "status"
    return send_request(host, port, cmd)

def send_volts_cmd(host, port):
    cmd = "volts"
    return send_request(host, port, cmd)

def send_amps_cmd(host, port):
    cmd = "amps"
    return send_request(host, port, cmd)

def control_port(host, port, dport, cmd):
    ncmd = "c2101,"+dport+","+str(cmd)    
    return send_request(host, port, ncmd)