##############################################################################
# 
# Module: serialDev.py
#
# Description:
#     Handle serial comm script for 3141 and 3201 USB switch
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
#     Seenivasan V, MCCI Corporation Mar 2020
#
# Revision history:
#     V2.0.0 Fri Jan 15 2021 18:50:59 seenivasan
#       Module created
##############################################################################
# Lib imports
import wx
import serial

##############################################################################
# Utilities
##############################################################################
def open_serial_device(top):
    """
    Open Serial Port of the selected device (3141/3201/2101)
    Args:
        top: create a object
    Returns:
        return True, False
    """

    top.devHand.port = top.selPort
    top.devHand.baudrate = 115200
    top.devHand.bytesize = serial.EIGHTBITS
    top.devHand.parity = serial.PARITY_NONE
    top.devHand.timeout = 1
    top.devHand.stopbits =serial. STOPBITS_ONE

    try:
        top.devHand.open()
        return True
            
    except serial.SerialException as e:
        wx.MessageBox(""+str(e), "Com Port Error", wx.OK, top)
        return False

def send_port_cmd(phand,cmd):
    """
    Send Port Control Command
    Args:
        phnad:send Serial port
        cmd:cmd with string
    Returns:
        return res, rstr
    """
    res = write_serial(phand, cmd)
    if res == 0:
        res, rstr = read_serial(phand)
        if res == 0:
            return res, rstr
    rstr = "Comm Error\n"
    return res, rstr

def send_status_cmd(phand):
    """
    Send Status Command to check Orientation
    Args:
        phnad:send the serial cmd for check orientation
    Returns:
        return res, strin
    """
    cnt = 0
    strin = ""
    cmd = 'status\r\n'
    res = write_serial(phand, cmd)
    if res == 0:
        while(cnt < 14):
            res, rstr = read_serial(phand)
            if res == 0:
                strin = strin + rstr
                cnt = cnt + 1
            else:
                strin = "Com Error"
                cnt = 14
        return res, strin
    else:
        srrin = "Comm Error\n"
        return res, strin

def send_volts_cmd(phand):
    """
    Send Volts Command
    Args:
        phnad:volts command
    Returns:
        return res, rstr
    """
    cmd = 'volts\r\n'
    res = write_serial(phand, cmd)
    if res == 0:
        res, rstr = read_serial(phand)
        if res == 0:
            return res, rstr
    rstr = "Comm Error\n"
    return res, rstr

def send_amps_cmd(phand):
    """
    Send Amps Command
    Args:
        phnad:argument for send Amps command
    Returns:
        return res, rstr
    """
    cmd = 'amps\r\n'
    res = write_serial(phand, cmd)
    if res == 0:
        res, rstr = read_serial(phand)
        if res == 0:
            return res, rstr
    rstr = "Comm Error\n"
    return res, rstr 

def send_sn_cmd(phand):
    """
    Send Serial Number Command
    Args:
        phnad:argument for device serial number
    Returns:
        return res, rstr
    """
    cmd = 'sn\r\n'
    res = write_serial(phand, cmd)
    if res == 0:
        res, rstr = read_serial(phand)
        if res == 0:
            return res, rstr
    rstr = "Comm Error\n"
    return res, rstr

def read_port_cmd(phand):
    """
    Read Port Command, to check port status of the 3141/3201/2101
    Args:
        phnad:read serial port
    Returns:
        return res, str
    """
    cmd = 'port\r\n'
    res = write_serial(phand, cmd)
    if res == 0:
        res, rstr = read_serial(phand)
        if res == 0:
            return res, rstr
    rstr = "Comm Error\n"
    return res, rstr

def write_serial(phand, cmd):
    """
    Send data over the Serial Port
    Args:
        phnad:argument for sending the serial data
        cmd:cmd for serial data with string format
    Returns:
        return -1
    """
    try:
        phand.write(cmd.encode())
        return 0
    except:
        return -1

def read_serial(phand):
    """
    Read data from the Serial Port
    Args:
       phnad:argument for read data from serail port 
    Returns:
        return None
    """
    try:
        return  0, phand.readline().decode('utf-8')
    except:
        return -1