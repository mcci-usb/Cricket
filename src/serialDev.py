##############################################################################
# 
# Module: serialDev.py
#
# Description:
#     Handle serial comm script for 3141, 3201 and 2301 USB switch
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
#     V2.3.0 Wed April 28 2021 18:50:10 seenivasan
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
    Open Serial Port of the selected device (3141/3201/2301)
    
    Args:
        top: creates an object
    Returns:
        True: A list of the serial ports available on the system     
    """
    top.devHand.port = top.selPort
    top.devHand.baudrate = top.selBaud
    
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
        cmd:cmd in String format
    Returns:
        res: interger - length of data read from or write to serial
        rstr: data read from the serial port in String format
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
    Send status command to read the status of the connected Model

    Args:
        phnad: status command in String format
    Returns:
        res: interger - length of data read from or write to serial
        rstr: data read from the serial port in String format
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
    Send command to read the Volt parameter from the model 3201

    Args:
        phnad: Volt read command in String format
    Returns:
        res: interger - length of data read from or write to serial
        rstr: data read from the serial port in String format
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
    Send command to read the Ampere parameter from the model 3201

    Args:
        phnad: Amp read command in String format 
    Returns:
        res: interger - length of data read from or write to serial
        rstr: data read from the serial port in String format
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
    Send Serial Number Command for the attached Model (3141/3201)
    
    Args:
        phnad: Serial number read command in String format 
    Returns:
        res: interger - length of data read from or write to serial
        rstr: data read from the serial port in String format
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
    Read Port Command, to check port status of the Port in 3141/3201

    Args:
        phnad: Serial port handler
    Returns:
        res: interger - length of data read from or write to serial
        rstr: data read from the serial port in String format
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
    Send data over the Serial Port to the connected model

    Args:
        phnad: Serial port handler
        cmd: Data to be written in string format
    Returns:
        0  - When write success
        -1 - When write failed 
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
       phnad: Serial port handler
    Returns:
        0  - When read success
        -1 - When read  failed
    """
    try:
        return  0, phand.readline().decode('utf-8')
    except:
        return -1