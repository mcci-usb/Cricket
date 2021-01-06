#======================================================================
# (c) 2020  MCCI, Inc.
#----------------------------------------------------------------------
# Project : UI3141/3201 GUI Application
# File    : serialDev.py
#----------------------------------------------------------------------
# Handle serial comm script for 3141 and 3201 USB switch
#======================================================================

#======================================================================
# IMPORTS
#======================================================================

import wx
import serial


#======================================================================
# COMPONENTS
#======================================================================

# Open Serial Port of the selected device (3141/3201)
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

# Send Port Control Command
def send_port_cmd(phand,cmd):
    res = write_serial(phand, cmd)
    if res == 0:
        res, rstr = read_serial(phand)
        if res == 0:
            return res, rstr
    rstr = "Comm Error\n"
    return res, rstr

# Send Status Command to check Orientation
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

# Send Volts Command
def send_volts_cmd(phand):
    cmd = 'volts\r\n'
    res = write_serial(phand, cmd)
    if res == 0:
        res, rstr = read_serial(phand)
        if res == 0:
            return res, rstr
    rstr = "Comm Error\n"
    return res, rstr

# Send Amps Command
def send_amps_cmd(phand):
    cmd = 'amps\r\n'
    res = write_serial(phand, cmd)
    if res == 0:
        res, rstr = read_serial(phand)
        if res == 0:
            return res, rstr
    rstr = "Comm Error\n"
    return res, rstr 

# Send Serial Number Command
def send_sn_cmd(phand):
    cmd = 'sn\r\n'
    res = write_serial(phand, cmd)
    if res == 0:
        res, rstr = read_serial(phand)
        if res == 0:
            return res, rstr
    rstr = "Comm Error\n"
    return res, rstr

# Read Port Command, to check port status of the 3141/3201
def read_port_cmd(phand):
    cmd = 'port\r\n'
    res = write_serial(phand, cmd)
    if res == 0:
        res, rstr = read_serial(phand)
        if res == 0:
            return res, rstr
    rstr = "Comm Error\n"
    return res, rstr

# Send data over the Serial Port
def write_serial(phand, cmd):
    try:
        phand.write(cmd.encode())
        return 0
    except:
        return -1

# Read data from the Serial Port
def read_serial(phand):
    try:
        return  0, phand.readline().decode('utf-8')
    except:
        return -1