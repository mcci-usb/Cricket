##############################################################################
# 
# Module: devClient.py
#
# Description:
#     Client Socket module - Communicates with the Server where device is connected
#     Interface between devControl and device module
#     Send device control command to Server and receive response from the server
#
# Author:
#     Seenivasan V, MCCI Corporation June 2021
#
# Revision history:
#    V4.3.1 Mon Apr 15 2024 17:00:00   Seenivasan V 
#       Module created
##############################################################################
# Built-in imports

import socket
import json

def send_request(host, port, reqdict):
    """
    sending the request with same port number

    Args:
        host: host ipaddress.
        port: send with port number
        reqdict: request with dict
    Returns:
        rdict: its shows the status fail and Ok
    """
    cs =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cs.settimeout(20)
    rdict = {}
    rlist = []
    sdict = {}
    try:
        result = cs.connect((host, port))
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
    """
    get the device list with connecting server 
    with ipaddress and same port number
    Args:
        Args:
        host: host ipaddress.
        port: send with port number
    Returns:
        send_request(host, port, reqdict)
    """
    reqdict = {}
    reqdict["ctype"] = "device"
    reqdict["cmd"] = "search"
    return send_request(host, port, reqdict)

def open_serial_device(host, port, swname, sport, baud):
    """
    once connecting the sevrer client search serial device list 
    Args:
        Args:
        host: host ipaddress.
        port: send with port number
        sport: serial port command.
        baud: baudrate of serial device.
    Returns:
        send_request(host, port, reqdict)
    """
    reqdict = {}
    reqdict["ctype"] = "device"
    reqdict["cmd"] = "open"
    reqdict["itype"] = "serial"
    reqdict["swname"] = swname
    reqdict["port"] = sport
    reqdict["baud"] = str(baud)
    return send_request(host, port, reqdict)

def select_usb_device(host, port, sport):
    """
    select the usb device and then open the port
    Args:
        Args:
        host: host ipaddress.
        port: send with port number
        sport: serialport command
    Returns:
        send_request(host, port, reqdict)
    """
    reqdict = {}
    reqdict["ctype"] = "device"
    reqdict["itype"] = "usb"
    reqdict["cmd"] = "open"
    reqdict["port"] = sport
    return send_request(host, port, reqdict)

def close_serial_device(host, port, sport):
    """
    closing the serial port device.
    Args:
        Args:
        host: host ipaddress.
        port: send with port number
    Returns:
        send_request(host, port, reqdict)
    """
    reqdict = {}
    reqdict["ctype"] = "device"
    reqdict["cmd"] = "close"
    reqdict["port"] = sport
    return send_request(host, port, reqdict)

def send_port_cmd(host, port, cmd):
    """
    sending the port command
    Args:
        Args:
        host: host ipaddress.
        port: send with port number
        cmd: cmd with send control , serial, switching.
    Returns:
        send_request(host, port, reqdict)
    """
    reqdict = {}
    reqdict["ctype"] = "control"
    reqdict["itype"] = "serial"
    reqdict["cmd"] = "switch"
    reqdict["stat"] = cmd
    return send_request(host, port, reqdict)

def read_port_cmd(host, port, swid):
    """
    read the port command
    Args:
        host: host ipaddress.
        port: send with port number
    Returns:
        send_request(host, port, reqdict)
    """
    reqdict = {}
    reqdict["ctype"] = "control"
    reqdict["itype"] = "serial"
    reqdict["port"] = swid
    reqdict["cmd"] = "read"
    
    return send_request(host, port, reqdict)

def send_status_cmd(host, port, swid):
    """
    sending the serial status command.
    Args:
        host: host ipaddress.
        port: send with port number
    Returns:
        send_request(host, port, reqdict)
    """
    reqdict = {}
    reqdict["ctype"] = "control"
    reqdict["itype"] = "serial"
    reqdict["cmd"] = "status"
    reqdict["port"] = swid
    return send_request(host, port, reqdict)

def send_speed_cmd(host, port, cmd):
    """
    sending the serial status command.
    Args:
        host: host ipaddress.
        port: send with port number
    Returns:
        send_request(host, port, reqdict)
    """
    swid, speed = cmd.split(',')
    reqdict = {}
    reqdict["ctype"] = "control"
    reqdict["itype"] = "serial"
    reqdict["cmd"] = "speed"
    reqdict["port"] = swid
    reqdict["speed"] = speed
    return send_request(host, port, reqdict)

def send_volts_cmd(host, port, swid):
    """
    send the volts command
    Args:
        Args:
        host: host ipaddress.
        port: send with port number
    Returns:
        send_request(host, port, reqdict)
    """
    reqdict = {}
    reqdict["ctype"] = "control"
    reqdict["itype"] = "serial"
    reqdict["cmd"] = "volts"
    reqdict["port"] = swid
    return send_request(host, port, reqdict)

def send_amps_cmd(host, port, swid):
    """
    send the amps command
    Args:
        Args:
        host: host ipaddress.
        port: send with port number
    Returns:
        send_request(host, port, reqdict)
    """
    reqdict = {}
    reqdict["ctype"] = "control"
    reqdict["itype"] = "serial"
    reqdict["cmd"] = "amps"
    reqdict["port"] = swid
    return send_request(host, port, reqdict)

def control_port(host, port, cmd):
    """
    controlling the switching ports
    Args:
        Args:
        host: host ipaddress.
        port: send with port number
    Returns:
        send_request(host, port, reqdict)
    """
    reqdict = {}
    reqdict["ctype"] = "control"
    reqdict["itype"] = "usb"
    reqdict["cmd"] = cmd
    return send_request(host, port, reqdict)