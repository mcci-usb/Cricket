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
"""
Open Serial Port of the selected device (3141/3201/2101)
Args:
    top: create a object
Returns:
    return True, False
"""
def open_serial_device(top):

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
"""
Send Port Control Command
Args:
    phnad:send Serial port
    cmd:cmd with string
Returns:
    return res, rstr
"""
def send_port_cmd(phand,cmd):
    res = write_serial(phand, cmd)
    if res == 0:
        res, rstr = read_serial(phand)
        if res == 0:
            return res, rstr
    rstr = "Comm Error\n"
    return res, rstr
"""
Send Status Command to check Orientation
Args:
       phnad:send the serial cmd for check orientation
Returns:
    return res, strin
"""
def send_status_cmd(phand):
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
"""
Send Volts Command
Args:
    phnad:volts command
Returns:
    return res, rstr
"""
def send_volts_cmd(phand):
    cmd = 'volts\r\n'
    res = write_serial(phand, cmd)
    if res == 0:
        res, rstr = read_serial(phand)
        if res == 0:
            return res, rstr
    rstr = "Comm Error\n"
    return res, rstr
"""
Send Amps Command
Args:
    phnad:argument for send Amps command
Returns:
    return res, rstr
"""
def send_amps_cmd(phand):
    cmd = 'amps\r\n'
    res = write_serial(phand, cmd)
    if res == 0:
        res, rstr = read_serial(phand)
        if res == 0:
            return res, rstr
    rstr = "Comm Error\n"
    return res, rstr 
"""
Send Serial Number Command
Args:
    phnad:argument for device serial number
Returns:
    return res, rstr
"""
def send_sn_cmd(phand):
    cmd = 'sn\r\n'
    res = write_serial(phand, cmd)
    if res == 0:
        res, rstr = read_serial(phand)
        if res == 0:
            return res, rstr
    rstr = "Comm Error\n"
    return res, rstr
"""
Read Port Command, to check port status of the 3141/3201/2101
    phnad:read serial port
Returns:
    return res, str
"""
def read_port_cmd(phand):
    cmd = 'port\r\n'
    res = write_serial(phand, cmd)
    if res == 0:
        res, rstr = read_serial(phand)
        if res == 0:
            return res, rstr
    rstr = "Comm Error\n"
    return res, rstr
"""
Send data over the Serial Port
Args:
    phnad:argument for sending the serial data
    cmd:cmd for serial data with string format
Returns:
    return -1
"""
def write_serial(phand, cmd):
    try:
        phand.write(cmd.encode())
        return 0
    except:
        return -1
"""
    Read data from the Serial Port
    Args:
       phnad:argument for read data from serail port 
    Returns:
        return None
"""
def read_serial(phand):
    try:
        return  0, phand.readline().decode('utf-8')
    except:
        return -1