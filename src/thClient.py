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
    hs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hs.connect((host, port))
 
    hs.settimeout(5)

    rdict = {}
    rlist = []
    sdict = {}

    try:
        data = json.dumps(reqdict)
        hs.send(data.encode('utf-8'))

        rcvd_data = b''  # Initialize outside the loop

        while True:
            rcvchunk = hs.recv(1024)
            if not rcvchunk:
                break
            hs.settimeout(1)
            rcvd_data += rcvchunk
    except socket.timeout:
        # print("Socket timeout occurred. Connection might be too slow or no data is being sent.")
        rcvd_json = rcvd_data.decode('utf-8')
        rcvd_obj = json.loads(rcvd_json)

        sdict["status"] = "OK"
        rlist.append(sdict)
        rlist.append(rcvd_obj)
    except Exception as err:
        # print(f"An error occurred: {err}")
        sdict["status"] = "fail"
        rlist.append(sdict)
    finally:
        hs.close() 

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