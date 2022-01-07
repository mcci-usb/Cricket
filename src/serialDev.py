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
#     Seenivasan V, MCCI Corporation June 2021
#
# Revision history:
#    V2.5.0 Fri Jan 07 2022 17:40:05   Seenivasan V
#       Module created
##############################################################################
# Lib imports
import wx
import serial

##############################################################################
# Utilities
##############################################################################

class SerialDev:
    """
    A class SerialDev with init method.
    here serial device uses port, baudrate, bysize.
    """
    def __init__(self, top):
        """
        open serial comport device

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            top: creates the object
        Returns:
            None
        """
        self.devHand = serial.Serial()
        self.devHand.port = None
        self.devHand.baudrate = 9600
        self.devHand.bytesize = serial.EIGHTBITS
        self.devHand.parity = serial.PARITY_NONE
        self.devHand.timeout = 1
        self.devHand.stopbits = serial. STOPBITS_ONE
        self.top = top

    def open_serial_device(self, port, baud):
        """
        open serial comport device

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            port: serial port 
            baud:Bit rate is the transmission of number of bits per second
            here transferring the baudrate 9600, 115200.
        Returns:
            True: device open with comport
            False: device comport error which is device not found
        """
        if self.devHand.is_open:
            self.devHand.close() 
        self.devHand.port = port
        self.devHand.baudrate = baud
        try:
            self.devHand.open()
            return True
        except serial.SerialException as e:
            wx.MessageBox(""+str(e), "Com Port Error", wx.OK, self.top)
        return False

    def close(self):
        """
        close the serial comport device

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            True: close the serial device
        """
        if self.devHand.is_open:
            self.devHand.close()
        return True

    def send_port_cmd(self, cmd):
        """
        Send Port Control Command

        Args:
            phnad:send Serial port
            cmd:cmd in String format
        Returns:
            res: interger - length of data read from or write to serial
            rstr: data read from the serial port in String format
        """
    
        res = self.write_serial(cmd)
        if res == 0:
            res, rstr = self.read_serial()
        if res == 0:
            return res, rstr
        rstr = "Comm Error\n"
        return res, rstr

    def write_serial(self, cmd):
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
            self.devHand.write(cmd.encode())
            return 0
        except:
            return -1
  
    def read_serial(self):
        """
        Read data from the Serial Port

        Args:
            phnad: Serial port handler
        Returns:
            0  - When read success
            -1 - When read  failed
        """
        try:
            return  0, self.devHand.readline().decode('utf-8')
        except:
            return -1

    def send_status_cmd(self):
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
        res = self.write_serial(cmd)
        if res == 0:
            while(cnt < 14):
                res, rstr = self.read_serial()
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

    def send_volts_cmd(self):
        """
        Send command to read the Volt parameter from the model 3201

        Args:
            phnad: Volt read command in String format
        Returns:
            res: interger - length of data read from or write to serial
            rstr: data read from the serial port in String format
        """
        cmd = 'volts\r\n'
        res = self.write_serial(cmd)
        if res == 0:
            res, rstr = self.read_serial()
            if res == 0:
                return res, rstr
        rstr = "Comm Error\n"
        return res, rstr

    def send_amps_cmd(self):
        """
        Send command to read the Ampere parameter from the model 3201

        Args:
            phnad: Amp read command in String format 
        Returns:
            res: interger - length of data read from or write to serial
            rstr: data read from the serial port in String format
        """
        cmd = 'amps\r\n'
        res = self.write_serial(cmd)
        if res == 0:
            res, rstr = self.read_serial()
            if res == 0:
                return res, rstr
        rstr = "Comm Error\n"
        return res, rstr 

    def send_sn_cmd(self):
        """
        Send Serial Number Command for the attached Model (3141/3201)
    
        Args:
            phnad: Serial number read command in String format 
        Returns:
            res: interger - length of data read from or write to serial
            rstr: data read from the serial port in String format
        """
        cmd = 'sn\r\n'
        res = self.write_serial(cmd)
        if res == 0:
            res, rstr = self.read_serial()
            if res == 0:
                return res, rstr
        rstr = "Comm Error\n"
        return res, rstr

    def read_port_cmd(self):
        """
        Read Port Command, to check port status of the Port in 3141/3201

        Args:
            phnad: Serial port handler
        Returns:
            res: interger - length of data read from or write to serial
            rstr: data read from the serial port in String format
        """
        cmd = 'port\r\n'
        res = self.write_serial(cmd)
        if res == 0:
            res, rstr = self.read_serial()
            if res == 0:
                return res, rstr
        rstr = "Comm Error\n"
        return res, rstr