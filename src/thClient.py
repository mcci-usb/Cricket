# -*- coding: utf-8 -*-
##############################################################################
#
# Module: thClient.py
#
# Description:
#     Client Socket module used to communicate with the Server where
#     the device is connected.
#
#     Acts as an interface between devControl and device modules.
#     Sends device control commands to the Server and receives
#     responses in JSON format.
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
#
##############################################################################

# Built-in imports
import socket
import json

##############################################################################
# Client Request Handling
##############################################################################

def send_request(host, port, reqdict):
    """
    Send request to Test Host Server.

    Establishes socket connection with the server,
    sends JSON request data, and waits for response.

    Args:
        host: Server IP address.
        port: Server port number.
        reqdict: Request dictionary containing command data.

    Returns:
        dict:
            Response dictionary containing:
            - status (OK / fail)
            - response data (if available)

    Raises:
        socket.timeout:
            If server response exceeds timeout duration.
        Exception:
            For any communication failure.
    """

    # Create socket connection
    hs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hs.connect((host, port))
    hs.settimeout(6)

    rdict = {}
    rlist = []
    sdict = {}

    try:
        # Convert request to JSON and send
        data = json.dumps(reqdict)
        hs.send(data.encode("utf-8"))

        rcvd_data = b""  # Response buffer

        while True:
            rcvchunk = hs.recv(1024)
            if not rcvchunk:
                break
            hs.settimeout(1)
            rcvd_data += rcvchunk

    except socket.timeout:
        # Decode received response
        rcvd_json = rcvd_data.decode("utf-8")
        rcvd_obj = json.loads(rcvd_json)

        sdict["status"] = "OK"
        rlist.append(sdict)
        rlist.append(rcvd_obj)

    except Exception:
        sdict["status"] = "fail"
        rlist.append(sdict)

    finally:
        hs.close()

    rdict["result"] = rlist
    return rdict

def get_usb_tree(host, port):
    """
    Retrieve USB tree information from Host Server.

    Sends 'lsusb' command request to the server
    and receives connected USB device details.

    Args:
        host: Host computer IP address.
        port: Host server port number.

    Returns:
        dict:
            USB tree information response
            received from the server.

    Raises:
        None
    """

    reqdict = {}
    reqdict["ctype"] = "usb"
    reqdict["cmd"] = "lsusb"

    return send_request(host, port, reqdict)
