# -*- coding: utf-8 -*-
##############################################################################
#
# Module: Firmwareupdate.py
#
# Description:
#     Firmware Update Utility for Supported MCCI Switch Models.
#
# Detailed Description:
#     This module provides functionality to perform firmware updates
#     on supported switch devices through bootloader mode using
#     serial communication.
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
#
##############################################################################

import wx

# Serial Communication
import serial
import serial.tools.list_ports

# System Utilities
import sys
import os
from time import sleep, time

# Thread Handling
import threading

# USB Device Access
import usb.core
import usb.util

# Data Parsing
import re

# Project Globals
from uiGlobals import *

DO_RESET         = 1
INIT_AVR_PORT = 2
READ_AVAIL_PORTS = 3
GET_SW_IDENTIFIER = 4
GET_PROG_TYPE = 5
GET_SW_VERSION = 6
CHECK_AUTO_INC = 7
CHECK_BLOCK_SUPPORT = 8
GET_DEV_CODE = 9
SELECT_DEV_TYPE = 10
GET_INTO_PROGMODE = 11
READ_DEV_SIGNATURE = 12
READ_LFUSE = 13
READ_HFUSE = 14
READ_EFUSE = 15
SET_ADDRESS = 16
WRITE_BLOCK = 17
LEAVE_PROGMODE = 18
EXIT_BOOTLOADER = 19

CMD_GET_SWIDENTIFIER = 'S'  # 0x53
CMD_GET_SWVERSION = 'V'     # 0x56
CMD_GET_PROGTYPE = 'p'      # 0x53
CMD_CHECK_AUTOINCR = 'a'    # 0x61
CMD_CHECK_BLOCKSUPP = 'b'   # 0x62
CMD_GET_DEVCODE = 't'       # 0x74
CMD_GET_PROGMODE = 'P'      # 0x50
CMD_READ_DEVSIG = 's'       # 0x73     # 's'
CMD_READ_LFUSE = 'F'        # 0x46      # 'F'
CMD_READ_HFUSE = 'N'        # 0x4E      # 'N'
CMD_READ_EFUSE = 'Q'        # 0x51      # 'Q'
CMD_LEAVE_PROGMODE = 'L'    # 0x4C
CMD_EXIT_BOOTLOADER = 'E'   # 0x45

CMD_SET_ADDRESS = 0x41     # 'A'
CMD_WRITE_FLASH = 0x42     # 'B'
CMD_READ_FLASH = 0x67      # 'g'
CMD_LEAVE_PROGMODE = 0x4C  # 'C

DEVICE_VID = 0x045E
DEVICE_PID = 0x0646

# REV mapping for supported models
MODEL_REVS = {
    "3141": "0011",  # Model 3141 → REV 0011
    "3142": "0012",  # Model 3142 → REV 0012
}

# class firmwareupdate():
class FirmwareUpdate():
    """
    Initialize Firmware Update Controller.

    Detailed Description:
        Initializes the firmware update engine
        with default runtime parameters, memory
        buffers, device handles, and execution
        state variables required for firmware
        flashing operations.

        It also registers an optional logging
        callback used to stream update logs
        to UI or console interfaces.

    Args:
        self :
            Reference to FirmwareUpdate instance.

        log_callback :
            Optional function reference used
            for logging firmware update messages.

    Returns:
        None
    """

    def __init__(self, log_callback=None):
        # existing fields
        self.wait_flg = True
        self.hex_file = None
        self.avrHand = None
        self.avrport = None
        self.fw_seq = DO_RESET   # start state
        self.fw_port = None
        self.sw = None
        self.rx_flg = False
        self.pageSize = 0
        self.hexPath = None
        self.mem_flash = {}
        self.mem_addr = []
        self.flash_addr = 0
        self.byte_addr = 0
        self.flash_flg = False
        self.dlist = []
        self.clist = []
        self.switchlist = []
        self.addswitchlist = []
        self.removeswitchlist = []
        self.timer_fu = None
        self.fw_port = None

        # new: logger callback
        # log_callback should be a callable that accepts a single string
        self._log_cb = log_callback

    # simple logger helper
    def log(self, msg):
        """
        Log Firmware Update Messages.

        Detailed Description:
            Sends log messages to the registered
            logging callback function.

            If callback is unavailable, the
            message is safely ignored.

        Args:
            self :
                Reference to FirmwareUpdate instance.

            msg :
                Log message text.

        Returns:
            None
        """

        if self._log_cb:
            try:
                self._log_cb(str(msg))
            except Exception:
                pass
        else:
            pass

    # All your methods with prints replaced by self.log(...)
    def parse_set_address(self):
        """
        Parse Flash Address Set Response.

        Detailed Description:
            Validates the device response after
            sending flash memory address.

            Confirms whether address setting
            was accepted successfully.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            bool :
                True  → Address set success  
                False → Address set failed
        """

        resp = self.read_avr_oned()
        if resp == b'\r':
            return True
        else:
            self.log("Error when setting flash address")
            return False

    def exit_boot_loader(self):
        """
        Exit Bootloader Mode.

        Detailed Description:
            Sends exit command to the device
            bootloader to terminate firmware
            programming mode.

            Updates firmware sequence to
            bootloader exit stage.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            None
        """

        self.write_avr('E')
        self.fw_seq = EXIT_BOOTLOADER

    def load_block_flash(self):
        """
        Load Flash Memory Block.

        Detailed Description:
            Prepares and writes a block of firmware
            data into device flash memory.

            It builds a flash write buffer,
            fills data from HEX memory map,
            and pads missing bytes with 0xFF.

            Updates firmware sequence to
            block write stage.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            None
        """

        mybarr = []
        mybarr.append(0x42)
        mybarr.append(0x00)
        mybarr.append(0x80)
        mybarr.append(0x46)
        for i in range(128):
            try:
                mybarr.append(self.mem_flash[self.byte_addr])
            except:
                mybarr.append(0xFF)
            self.byte_addr += 1
        self.write_avr_hba(mybarr)
        self.fw_seq = WRITE_BLOCK

    def leave_prog_mode(self):
        """
        Leave Programming Mode.

        Detailed Description:
            Sends command to exit the device
            programming mode after firmware
            flashing is completed.

            Updates firmware sequence to
            leave-program mode stage.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            None
        """

        self.write_avr('L')
        self.fw_seq = LEAVE_PROGMODE

    def set_address(self):
        """
        Set Flash Memory Address.

        Detailed Description:
            Prepares and sends the flash memory
            address to the programmer before
            writing firmware data.

            Converts the target flash address
            into byte format and transmits it
            using AVR write command.

            Updates firmware sequence to
            address-set stage.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            None
        """

        addstr = (self.flash_addr).to_bytes(2, byteorder='big').hex()
        addbyte = bytes.fromhex(addstr)
        mybyte = []
        mybyte.append(0x41)
        for byte in addbyte:
            mybyte.append(byte)
        self.write_avr_hba(mybyte)
        self.fw_seq = SET_ADDRESS

    def read_efuse(self):
        """
        Read Extended Fuse Byte.

        Detailed Description:
            Sends command to read the Extended
            Fuse configuration byte from the
            AVR device.

            Used to verify extended device
            fuse settings during firmware
            update validation.

            Updates firmware sequence to
            EFUSE read stage.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            None
        """

        self.write_avr(CMD_READ_EFUSE)
        self.fw_seq = READ_EFUSE

    def read_lfuse(self):
        """
        Read Low Fuse Byte.

        Detailed Description:
            Sends command to read the Low Fuse
            configuration byte from the AVR device.

            This fuse value helps validate device
            configuration before firmware flashing.

            Updates firmware sequence to
            LFUSE read stage.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            None
        """
        self.write_avr(CMD_READ_LFUSE)
        self.fw_seq = READ_LFUSE

    def read_hfuse(self):
        """
        Read High Fuse Byte.

        Detailed Description:
            Sends command to read the High Fuse
            configuration byte from the AVR device.

            This value is used to verify fuse
            settings before firmware programming.

            Updates firmware sequence to
            HFUSE read stage.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            None
        """
        self.write_avr(CMD_READ_HFUSE)
        self.fw_seq = READ_HFUSE

    def read_dev_signature(self):
        """
        Read Device Signature.

        Detailed Description:
            Sends command to read the target
            device signature bytes from AVR.

            Used to verify device identity
            before firmware flashing.

            Updates firmware sequence to
            device signature read stage.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            None
        """

        self.write_avr(CMD_READ_DEVSIG)
        self.fw_seq = READ_DEV_SIGNATURE

    def get_into_progmode(self):
        """
        Enter Programming Mode.

        Detailed Description:
            Sends command to place the target
            device into programming mode to
            allow firmware flashing operations.

            Updates firmware sequence to
            programming mode stage.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            None
        """

        self.write_avr(CMD_GET_PROGMODE)
        self.fw_seq = GET_INTO_PROGMODE

    def select_dev_type(self):
        """
        Select Target Device Type.

        Detailed Description:
            Sends device type selection command
            to the programmer to configure the
            target device for firmware flashing.

            Updates firmware sequence to device
            type selection stage.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            None
        """

        self.write_avr_ba("TD")
        self.fw_seq = SELECT_DEV_TYPE

    def get_dev_code(self):
        """
        Get Supported Device Code.

        Detailed Description:
            Sends command to retrieve the list of
            device codes supported by the programmer
            for firmware programming operations.

            Updates firmware sequence to device
            code verification stage.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            None
        """

        self.write_avr(CMD_GET_DEVCODE)
        self.fw_seq = GET_DEV_CODE

    def check_block_support(self):
        """
        Check Block Write Support.

        Detailed Description:
            Sends command to verify whether the
            programmer supports buffered block
            flash memory operations.

            Updates firmware state to block
            support validation stage.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            None
        """

        self.write_avr(CMD_CHECK_BLOCKSUPP)
        self.fw_seq = CHECK_BLOCK_SUPPORT

    def check_auto_incr(self):
        """
        Check Auto Address Increment Support.

        Detailed Description:
            Sends command to verify whether the
            programmer supports automatic address
            increment during flash operations.

            Updates firmware state to auto-increment
            validation stage.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            None
        """

        self.write_avr(CMD_CHECK_AUTOINCR)
        self.fw_seq = CHECK_AUTO_INC

    def get_sw_version(self):
        """
        Request Programmer Software Version.

        Detailed Description:
            Sends command to the AVR programmer to
            retrieve the software/firmware version.

            Updates firmware state machine to
            software version validation stage.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            None
        """

        self.write_avr(CMD_GET_SWVERSION)
        self.fw_seq = GET_SW_VERSION

    def get_programmer_type(self):
        """
        Request Programmer Type Information.

        Detailed Description:
            Sends command to the AVR programmer to
            read the programmer hardware/type details.

            Updates firmware state machine to
            programmer type validation stage.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            None
        """

        self.write_avr(CMD_GET_PROGTYPE)
        self.fw_seq = GET_PROG_TYPE

    def get_sw_identifier(self):
        """
        Request Programmer Software Identifier.

        Detailed Description:
            Sends command to the AVR programmer to
            retrieve the software identifier string.

            Enables receive flag and updates firmware
            state machine to identifier read stage.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            None
        """

        self.rx_flg = True
        self.write_avr(CMD_GET_SWIDENTIFIER)
        self.fw_seq = GET_SW_IDENTIFIER

    def parse_efuse(self):
        """
        Parse Extended Fuse (EFUSE) Value.

        Detailed Description:
            Reads the Extended Fuse byte from the AVR device
            and logs the retrieved fuse configuration.

            Used to verify extended fuse settings during
            firmware update validation.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            bool :
                True if EFUSE read successful,
                otherwise False.
        """

        resp = self.read_avr_ba()
        if resp and len(resp) > 0:
            bsize = format(resp[0], '#x')
            self.log("efuse reads as: " + str(bsize))
            return True
        else:
            self.log("Error when reading efuse (empty response)")
            return False

    def parse_hfuse(self):
        """
        Parse High Fuse (HFUSE) Value.

        Detailed Description:
            Reads the High Fuse byte from the AVR device
            and logs the retrieved fuse configuration.

            Used to validate device fuse settings during
            firmware update process.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            bool :
                True if HFUSE read successful,
                otherwise False.
        """

        resp = self.read_avr_ba()
        if resp and len(resp) > 0:
            bsize = format(resp[0], '#x')
            self.log("hfuse reads as: "+str(bsize))
            return True
        else:
            self.log("Error when reading hfuse")
            return False

    def parse_lfuse(self):
        """
        Parse Low Fuse (LFUSE) Value.

        Detailed Description:
            Reads the Low Fuse byte from the AVR device
            and logs the retrieved fuse configuration.

            Used to verify device fuse settings during
            firmware update operations.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            bool :
                True if LFUSE read successful,
                otherwise False.
        """

        resp = self.read_avr_ba()
        if resp and len(resp) > 0:
            bsize = format(resp[0], '#x')
            if self.flash_flg:
                self.log("")
            self.log("lfuse reads as: "+str(bsize))
            return True
        else:
            self.log("Error when reading lfuse")
            return False

    def parse_dev_signature(self):
        """
        Parse Device Signature Response.

        Detailed Description:
            Reads and interprets the device signature
            returned by the AVR device.

            Extracts signature bytes and logs the
            detected device identification details.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            bool :
                True if signature read successfully,
                otherwise False.
        """

        resp = self.read_avr_ba()
        if resp != None:
            bsize1 = (format(resp[0], '#x'))
            bsize2 = (format(resp[1], '#x'))
            bsize3 = (format(resp[2], '#x'))
            self.log("Device Signature = "+bsize1+bsize2+bsize3)
            return True
        else:
            self.log("Error when reading dev signature")
            return False

    def parse_get_progmode(self):
        """
        Parse Enter Program Mode Response.

        Detailed Description:
            Validates the acknowledgement received
            after issuing the command to enter
            programming mode.

            Confirms whether the device successfully
            switched into firmware programming state.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            bool :
                True if program mode entered successfully,
                otherwise False.
        """

        resp = self.read_avr_oned()
        if resp == b'\r':
            self.log("Enter into Program mode success")
            return True
        else:
            self.log("Error when entering into prog mode")
            return False

    def parse_dev_type(self):
        """
        Parse Selected Device Type.

        Detailed Description:
            Validates the acknowledgement response
            after selecting the target device type
            in programmer mode.

            Confirms whether the device code selection
            was accepted successfully.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            bool :
                True if device type selection successful,
                otherwise False.
        """
        resp = self.read_avr_oned()
        if resp == b'\r':
            self.log("Dev code selected = 0x44")
            return True
        else:
            self.log("Error when checking the supported device list")
            return False

    def parse_dev_code(self):
        """
        Parse Supported Device Code.

        Detailed Description:
            Reads the programmer response to identify
            the supported target device codes.

            Logs the detected device information
            for firmware compatibility verification.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            bool :
                True if device code read successfully,
                otherwise False.
        """

        resp = self.read_avr_ba()
        if resp != None:
            bsize = (format(resp[0], '#x'))
            self.log("Programmer supports the following devices: "+bsize)
            return True
        else:
            self.log("Error when checking the supported device list")
            return False

    def parse_block_support(self):
        """
        Parse Block Memory Support.

        Detailed Description:
            Reads programmer response to determine
            buffered memory (block write) support and
            extracts the supported page size.

            The detected buffer size is stored for
            use during firmware flashing operations.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            bool :
                True if block support detected successfully,
                otherwise False.
        """

        resp = self.read_avr_ba()
        if resp != None:
            bsize = resp[1:3]
            bsize = bsize.hex()
            self.pageSize = bsize
            self.log("Programmer supports buffered memory access with buffer size = "+str(int(bsize, 16))+" bytes")
            return True
        else:
            self.log("Error when checking block support")
            return False

    def parse_auto_incr(self):
        """
        Parse Auto Address Increment Support.

        Detailed Description:
            Reads the programmer response to verify
            whether auto address increment feature
            is supported and logs the capability status.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            bool :
                True if response received successfully,
                otherwise False.
        """

        resp = self.read_avr()
        if resp != None:
            if resp and len(resp) > 0 and resp[0] == 'Y':
                self.log("Programmer supports auto addr increment")
            else:
                self.log("Programmer supports auto addr increment!")
            return True
        else:
            self.log("Error when checking auto addr incement support")
            return False

    def parse_sw_version(self):
        """
        Parse Programmer Software Version.

        Detailed Description:
            Reads the software version from the AVR
            programmer, converts the received hex
            value into a readable version format,
            and logs the result.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            bool :
                True if version is parsed successfully,
                otherwise False.
        """

        resp = self.read_avr()
        if resp != None:
            try:
                resp = int(resp, 16)
                resp = resp / 16
                self.log("Software Version = "+str(resp))
                return True
            except Exception:
                self.log("Software Version parse error")
                return False
        else:
            self.log("Software Version read error")
            return False

    def parse_programmer_type(self):
        """
        Parse Programmer Type.

        Detailed Description:
            Reads the programmer type information
            from the AVR device and logs the detected
            programmer type.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            bool :
                True if programmer type is read successfully,
                otherwise False.
        """

        resp = self.read_avr()
        if resp != None:
            self.log("Programmer Type:  "+resp)
            return True
        else:
            self.log("Programmer type not found")
            return False

    def parse_sw_identifier(self):
        """
        Parse Programmer Software Identifier.

        Detailed Description:
            Reads the programmer ID from the device
            and verifies whether it matches the
            expected signature ("CATERIN").

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            bool :
                True if identifier is valid,
                otherwise False.
        """

        resp = self.read_avr()
        if resp and "CATERIN" in resp:
            self.log("Found Programmer Id: " + resp)
            return True
        else:
            self.log("Programmer Id read error")
            # keep behavior but do not sys.exit in GUI; set seq to EXIT to abort
            return False

    def run_update(self, progress_callback=None):
        """
        Execute Firmware Update State Machine.

        Detailed Description:
            This function runs one cycle of the firmware
            update state machine sequence.

            It controls the complete bootloader workflow
            including device reset, programmer detection,
            flash erase/write, fuse reads, and exit from
            programming mode.

            The function is designed to be called repeatedly
            until the firmware update process reaches the
            EXIT_BOOTLOADER state.

        Args:
            self :
                Reference to FirmwareUpdate instance.

            progress_callback :
                Optional callback function used to
                update firmware flashing progress.

        Returns:
            None
        """

        if self.fw_seq == DO_RESET:
            self.send_reset()
            self.fw_seq = READ_AVAIL_PORTS
            sleep(1.5)
        elif self.fw_seq == READ_AVAIL_PORTS:
            plist = list(serial.tools.list_ports.comports())
            self.fw_port = self.get_avrdude(plist)
            if self.fw_port != None:
                self.fw_seq = INIT_AVR_PORT
                sleep(0.5)
            else:
                self.log("No AVRdude found!!")
                # abort: set to EXIT_BOOTLOADER to stop loop
                self.fw_seq = EXIT_BOOTLOADER
        elif self.fw_seq == INIT_AVR_PORT:
            if self.open_avr_port():
                self.get_sw_identifier()
                sleep(0.5)
            else:
                self.log("Failed to open AVR port")
                self.fw_seq = EXIT_BOOTLOADER
        elif self.fw_seq == GET_SW_IDENTIFIER:
            if self.parse_sw_identifier():
                self.get_programmer_type()
                sleep(0.2)
            else:
                self.log("parse_sw_identifier failed")
                self.fw_seq = EXIT_BOOTLOADER
        elif self.fw_seq == GET_PROG_TYPE:
            if self.parse_programmer_type():
                self.get_sw_version()
                sleep(0.2)
        elif self.fw_seq == GET_SW_VERSION:
            if self.parse_sw_version():
                self.check_auto_incr()
                sleep(0.1)
        elif self.fw_seq == CHECK_AUTO_INC:
            if self.parse_auto_incr():
                self.check_block_support()
                sleep(0.1)
        elif self.fw_seq == CHECK_BLOCK_SUPPORT:
            if self.parse_block_support():
                self.get_dev_code()
                sleep(0.1)
        elif self.fw_seq == GET_DEV_CODE:
            if self.parse_dev_code():
                self.select_dev_type()
                sleep(0.1)
        elif self.fw_seq == SELECT_DEV_TYPE:
            if self.parse_dev_type():
                self.get_into_progmode()
                sleep(0.1)
        elif self.fw_seq == GET_INTO_PROGMODE:
            if self.parse_get_progmode():
                self.read_dev_signature()
                sleep(0.1)
        elif self.fw_seq == READ_DEV_SIGNATURE:
            if self.parse_dev_signature():
                self.read_lfuse()
                sleep(0.1)
        elif self.fw_seq == READ_LFUSE:
            if self.parse_lfuse():
                self.read_hfuse()
                sleep(0.1)
        elif self.fw_seq == READ_HFUSE:
            if self.parse_hfuse():
                self.read_efuse()
                sleep(0.1)
        elif self.fw_seq == READ_EFUSE:
            if self.parse_efuse():
                if self.flash_flg:
                    self.flash_flg = False
                    self.leave_prog_mode()
                    sleep(0.1)
                else:
                    self.log("writing flash ("+ str(len(self.mem_addr))+ ") bytes")
                    if len(self.mem_addr) == 0:
                        self.log("No address/data to write. Aborting.")
                        self.fw_seq = EXIT_BOOTLOADER
                        return
                    self.flash_addr = self.mem_addr[0]
                    self.byte_addr = self.mem_addr[0]
                    # self.log("-")
                    self.set_address()
                    sleep(0.3) #sleep(0.5)
        elif self.fw_seq == SET_ADDRESS:
            if self.parse_set_address():
                self.load_block_flash()
                sleep(0.3) #sleep(0.5)
        elif self.fw_seq == WRITE_BLOCK:
            if self.parse_set_address():
                # condition adjust: mem_addr is list of addresses; use byte_addr vs max addr
                if self.byte_addr <= max(self.mem_addr):
                    self.flash_addr += 0x40
                    self.set_address()
                    sleep(0.3) #sleep(0.5)
                else:
                    self.flash_flg = True
                    self.read_lfuse()
                    sleep(0.3) #sleep(0.5)
        elif self.fw_seq == LEAVE_PROGMODE:
            if self.parse_set_address():
                self.exit_boot_loader()
                sleep(0.3) #sleep(0.5)
        elif self.fw_seq == EXIT_BOOTLOADER:
            if self.parse_set_address():
                self.log("Firmware update success!")

        # If progress callback provided, estimate percent (simple estimate)
        if progress_callback and len(self.mem_addr) > 0:
            try:
                # percent by byte_addr relative to max address in mem_addr
                written = (self.byte_addr - min(self.mem_addr))
                total = (max(self.mem_addr) - min(self.mem_addr) + 1)
                if total > 0:
                    pct = int((written / total) * 100)
                    if pct > 100:
                        pct = 100
                    progress_callback(pct)
            except Exception:
                pass

    def open_avr_port(self):
        """
        Open AVR Bootloader Serial Port.

        Detailed Description:
            This function attempts to open the AVR
            bootloader communication port required
            for firmware update operations.

            It performs multiple retry attempts to
            handle temporary port access issues.

            Execution Flow:

                • Try opening the configured firmware port
                • Use 115200 baud rate for communication
                • Retry up to 10 attempts on failure
                • Log warning message for each retry
                • Log error if all attempts fail

            Returns success status based on
            port open result.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            bool :
                True  → Port opened successfully  
                False → Failed after retry attempts
        """

        for attempt in range(10):
            try:
                self.avrHand = serial.Serial(port=self.fw_port, baudrate=115200, timeout=1)
                return True
            except serial.SerialException as e:
                self.log(f"[WARN] Attempt {attempt+1}: Cannot open {self.fw_port}, retrying... {e}")
                sleep(0.5)
        self.log(f"[ERROR] Could not open {self.fw_port}")
        return False

    def find_normal_port(self):
        """
        Find Normal Mode Device COM Port.

        Detailed Description:
            This function scans all available serial
            communication ports and identifies the
            device operating in normal application mode.

            Detection is performed using port metadata
            such as device description, VID, or PID
            information.

            Identification Logic:

                • Enumerate all available COM ports
                • Check port description for USB device match
                • Validate using VID/PID hardware ID string
                • Return the first matching device port

            If no matching device is found, the function
            returns None.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            str / None :
                Detected normal mode COM port name
                or None if no device is found.
        """
        plist = list(serial.tools.list_ports.comports())
        for port in plist:
            # match using description, VID, or PID
            if "USB Serial Device" in port.description or "VID:045E" in port.hwid:
                return port.device
        return None

    def send_reset(self):
        """
        Send Device Reset and Detect Bootloader Port.

        Detailed Description:
            This function sends a reset command to the
            connected device and detects whether the
            device has entered bootloader mode.

            It performs VID/PID-based port filtering
            before and after reset to identify newly
            appeared bootloader ports.

            Detection Flow:

                • Capture VID/PID matched ports before reset
                • Send reset command to active device port
                • Wait for device reboot
                • Capture VID/PID matched ports after reset
                • Identify newly enumerated bootloader port
                • Update firmware port reference

            If no new port is detected, an error is logged.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            bool :
                True  → Bootloader port detected successfully  
                False → Bootloader detection failed
        """

        before = set(p.device for p in serial.tools.list_ports.comports()
                    if p.vid == DEVICE_VID and p.pid == DEVICE_PID)
        self.log("[DEBUG] VID/PID  ports before reset: " + str(before))

        self.send_reset_to_port(self.fw_port)
        sleep(4)

        after = set(p.device for p in serial.tools.list_ports.comports()
                    if p.vid == DEVICE_VID and p.pid == DEVICE_PID)
        self.log("[DEBUG] VID/PID  ports after reset: " + str(after))

        new_ports = after - before
        if new_ports:
            self.fw_port = new_ports.pop()
        elif self.fw_port in after:
            pass
        else:
            self.log("[ERROR] Bootloader port not detected!")
            return False

        self.log(f"[INFO] Bootloader port ready: {self.fw_port}")
        return True

    def read_avr_ba(self):
        """
        Read Byte Array from AVR Serial Interface.

        Detailed Description:
            This function reads a block of data (byte array)
            from the connected AVR device through the active
            serial interface.

            It is generally used to retrieve multi-byte
            responses such as fuse values, signatures,
            and device information.

            Any serial communication error encountered
            during the read operation is captured and logged.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            bytes / None :
                Byte array response from AVR device,
                or None if the read operation fails.
  """
        rxdata = None
        try:
            rxdata = self.avrHand.read(10)
        except serial.SerialException as serr:
            self.log("Issue in Serial port: " + str(serr))
        return rxdata

    def read_avr_oned(self):
        """
        Read Single Byte from AVR Serial Interface.

        Detailed Description:
            This function reads one byte of data from the
            connected AVR device via the active serial port.

            It is typically used for command acknowledgements
            or status responses where only a single byte
            confirmation is expected.

            Any serial communication error encountered during
            the read operation is logged.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            bytes / None :
                Single byte response from AVR device,
                or None if the read operation fails.
        """
        rxdata = None
        try:
            rxdata = self.avrHand.read(1)
        except serial.SerialException as serr:
            self.log("Issue in Serial port: "+str(serr))
        return rxdata

    def read_avr(self):
        """
        Read Line Data from AVR Serial Interface.

        Detailed Description:
            This function reads a single line of data from
            the AVR device through the active serial port.

            The received byte stream is stripped of trailing
            characters and decoded into UTF-8 string format
            for further processing and logging.

            If decoding fails, a serial parsing error is logged.
            Any serial communication exception is also captured
            and recorded.

        Args:
            self :
                Reference to FirmwareUpdate instance.

        Returns:
            str / None :
                Decoded response string from AVR device,
                or None if read operation fails.
        """
        rxdata = None
        try:
            rxdata = self.avrHand.readline()
            try:
                rxdata = rxdata.rstrip().decode('utf-8')
            except:
                self.log("Serial Parsing Error")
        except serial.SerialException as serr:
            self.log("Issue in Serial port: " + str(serr))
        return rxdata

    def write_avr_hba(self,param):
        """
        Write Raw Bytearray Data to AVR Device.

        Detailed Description:
            This function converts the provided list or
            sequence of hexadecimal/byte values into a
            bytearray and writes it directly to the AVR
            serial interface.

            It is mainly used for low-level flash write
            operations such as block programming where
            raw binary data transmission is required.

            Any serial communication exception occurring
            during the write process is captured and logged.

        Args:
            self :
                Reference to FirmwareUpdate instance.

            param :
                List or sequence of byte values to be
                transmitted to the AVR device.

        Returns:
            None
        """
        ba = bytearray(param)
        try:
            self.avrHand.write(ba)
        except serial.SerialException as serr:
            self.log(str(serr))

    def write_avr_ba(self,param):
        """
        Write Data to AVR Device (Bytearray Encoded).

        Detailed Description:
            This function encodes the given string
            parameter into bytearray format and writes
            it to the connected AVR serial device.

            It is typically used for sending command
            strings that require bytearray transmission.

            Any serial communication error encountered
            during the write operation is logged.

        Args:
            self :
                Reference to FirmwareUpdate instance.

            param :
                Command string to be encoded and sent
                to the AVR device.

        Returns:
            None
       """
        ba = bytearray(param.encode())
        try:
            self.avrHand.write(ba)
        except serial.SerialException as serr:
            self.log(str(serr))

    def write_avr(self,param):
        """
        Write Data to AVR Device.

        Detailed Description:
            This function encodes the provided command
            string into bytes and transmits it to the
            connected AVR serial interface.

            It is used for sending standard AVR
            communication commands during firmware
            update operations.

            Serial exceptions occurring during the
            transmission process are captured and logged.

        Args:
            self :
                Reference to FirmwareUpdate instance.

            param :
                Command string to be written to
                the AVR device.

        Returns:
            None
        """
        try:
            self.avrHand.write(param.encode())
        except serial.SerialException as serr:
            self.log(str(serr))

    def get_avrdude(self, plist):
        """
        Detect AVR Programmer Port.

        Detailed Description:
            This function searches the available serial
            port list to identify the AVR programmer port.

            It first checks whether the configured firmware
            port is present in the detected port list.

            If not found, it scans for ports whose description
            contains identifiers such as “USB” or “AVR”
            to automatically select a compatible programmer port.

            Returns None if no suitable port is detected.

        Args:
            self :
                Reference to FirmwareUpdate instance.

            plist :
                List of detected serial ports.

        Returns:
            str / None :
                Detected AVR programmer port name
                or None if not found.
       """

        for port in plist:
            if port.device == self.fw_port:
                return port.device
        for port in plist:
            if "USB" in port.description or "AVR" in port.description:
                return port.device
        return None

    def load_hex_file(self, hex_path):
        """
        Load and Parse HEX Firmware File.

        Detailed Description:
            This function reads the provided Intel HEX file
            and extracts firmware data records.

            It parses byte count, memory address, record type,
            and data bytes, then stores the firmware content
            into internal flash memory structures for
            programming operations.

            Only valid data records (record type 00)
            are processed and indexed sequentially.

        Args:
            self :
                Reference to FirmwareUpdate instance.

            hex_path :
                File path of the firmware HEX file.

        Returns:
            None
        """
        self.mem_flash = {}
        self.mem_addr = []
        with open(hex_path, 'r') as f:
            for line in f:
                if not line.startswith(':'):
                    continue
                byte_count = int(line[1:3], 16)
                addr = int(line[3:7], 16)
                record_type = int(line[7:9], 16)
                data = line[9:9+byte_count*2]
                if record_type == 0:  # data record
                    for i in range(byte_count):
                        b = int(data[i*2:i*2+2], 16)
                        self.mem_flash[addr] = b
                        self.mem_addr.append(addr)
                        addr += 1
        # sort mem_addr
        self.mem_addr = sorted(self.mem_addr)

    # Get all ports matching VID/PID
    def get_candidate_ports(self, vid, pid):
        """
        Get Candidate Device Ports by VID and PID.

        Detailed Description:
            This function scans all available serial ports
            and filters the ports matching the specified
            Vendor ID (VID) and Product ID (PID).

            It is used to identify potential device ports
            connected to the system based on USB identifiers.

        Args:
            self :
                Reference to FirmwareUpdate instance.

            vid :
                Vendor ID of the target USB device.

            pid :
                Product ID of the target USB device.

        Returns:
            list :
                List of COM port device names matching
                the given VID and PID.
       """
        candidates = []
        for port in serial.tools.list_ports.comports():
            if port.vid == vid and port.pid == pid:
                candidates.append(port.device)
        return candidates
    
    def send_reset_to_port(self, port):
        """
        Send Reset Command to Device Port.

        Detailed Description:
            This function sends a reset command to the specified
            device COM port to force the device into bootloader mode.

            It opens the serial port, transmits the reset command,
            and handles port access errors such as port already
            being in use by another application.

        Args:
            self :
                Reference to FirmwareUpdate instance.

            port :
                Target COM port used to send the reset command.

        Returns:
            None

        Raises:
            RuntimeError :
                If the port is busy or already in use.
        """
        try:
            with serial.Serial(port, 115200, timeout=1) as ser:
                cmd = b"reset -b\r\n"
                ser.write(cmd); ser.flush()
                ser.write(cmd); ser.flush()

        except Exception as e:
            self.log(f"[WARN] Failed to send reset: {e}")
            err_str = str(e)

            # Detect "port already open" condition
            if "PermissionError" in err_str or "Access is denied" in err_str:
                # Show popup only once
                if not hasattr(self, "port_busy_shown") or not self.port_busy_shown:
                    self.port_busy_shown = True
                    wx.CallAfter(
                        wx.MessageBox,
                        "We couldn't connect to the port because it is already open "
                        "in another program (e.g., Tera Term).\n\n"
                        "Please close it and try again.",
                        "Port Already In Use",
                        wx.OK | wx.ICON_ERROR
                    )
                # Stop further attempts
                raise RuntimeError("Port is busy")

            # Other errors — just log, don’t show popup
            raise
    
    def detect_bootloader_device(self, normal_port, max_attempts=2):
        """
        Detect Bootloader Mode Device Port.

        Detailed Description:
            This function checks whether the device is already
            in bootloader mode or forces it into bootloader mode
            using a reset command.

            It detects the bootloader COM port by monitoring
            VID / PID changes and returns the identified port
            along with device USB details.

        Args:
            self :
                Reference to FirmwareUpdate instance.

            normal_port :
                Active device COM port in normal mode.

            max_attempts :
                Number of retry attempts for detection.

        Returns:
            tuple :
                (bootloader_port, vid, pid, revision)
        """
        new_port = None
        vid = pid = rev = None

        # Get current VID/PID info
        ports = [p for p in serial.tools.list_ports.comports() if p.device == normal_port]
        if ports:
            p = ports[0]
            vid, pid = p.vid, p.pid

            # Check if already in bootloader (REV 0004)
            for dev in usb.core.find(find_all=True, idVendor=vid, idProduct=pid):
                try:
                    rev = f"{dev.bcdDevice:04x}"
                    if rev == "0004" or rev == "0008":  # already bootloader
                        # self.log(f"[BOOT MODE] PORT={normal_port}, VID={vid:04X}, PID={pid:04X}, REV={rev}")
                        self.log(f"[BOOT MODE] PORT={normal_port}, VID={vid:04X}, PID={pid:04X}")
                        return normal_port, vid, pid, rev
                finally:
                    try:
                        usb.util.dispose_resources(dev)
                    except:
                        pass
                    del dev

        # If not already in bootloader, do reset + detect new port
        for attempt in range(1, max_attempts + 1):
            self.log(f"[INFO] Bootloader detection attempt {attempt} on {normal_port}...")

            before_ports = {
                p.device
                for p in serial.tools.list_ports.comports()
                if p.vid == DEVICE_VID and p.pid == DEVICE_PID
            }

            try:
                self.send_reset_to_port(normal_port)
            except RuntimeError:
                return None, None, None, None
            except Exception:
                pass
            sleep(3)
            # Detect new port
            all_ports = [p for p in serial.tools.list_ports.comports() if p.vid == DEVICE_VID and p.pid == DEVICE_PID]
            after_ports = {p.device for p in all_ports}
            appeared_ports = after_ports - before_ports

            if appeared_ports:
                new_port = list(appeared_ports)[0]
                new_port_info = next(p for p in all_ports if p.device == new_port)
                vid = new_port_info.vid
                pid = new_port_info.pid

                rev = None
                for dev in usb.core.find(find_all=True, idVendor=vid, idProduct=pid):
                    try:
                        rev = f"{dev.bcdDevice:04x}"
                        break
                    except Exception:
                        continue

                self.log(f"[BOOT MODE] PORT={new_port}, VID={vid:04X}, PID={pid:04X}")
                return new_port, vid, pid, rev
            else:
                self.log("[WARN] Bootloader not detected. Retrying...")
                sleep(1)

        self.log("[ERROR] Bootloader not detected after 2 attempts.")
        return None, None, None, None
   
# ------------------------------------------------------------------------------------
# wxPython GUI
# ------------------------------------------------------------------------------------
class FirmwareFrame(wx.Frame):
    """
    Initialize Firmware Update Main Window UI.

    Detailed Description:
        This constructor initializes the Firmware Update
        graphical user interface used for upgrading firmware
        of supported switch models (3141 / 3142).


    Args:
        self :
            Reference to FirmwareFrame instance.

        parent :
            Parent window reference.

        top :
            Top-level application controller reference.

    Returns:
        None
    """
    def __init__(self, parent, top):
        super().__init__(None, title="Model3141/3142 Firmware update", size=(760, 520),
                         style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        panel = wx.Panel(self)
        
        base = os.path.abspath(os.path.dirname(__file__))
        iconpath = os.path.abspath(os.path.join(base, os.pardir, os.pardir))
        icon_file_path = os.path.join(iconpath+"/icons/"+ IMG_ICON)
        # Create a wx.Icon object with the specified icon file path
        icon = wx.Icon(icon_file_path)
        # Set the icon for the wx.Frame (assuming 'self' is an instance of wx.Frame)
        self.SetIcon(icon)

        # Top controls
        port_lbl = wx.StaticText(panel, label="Select Model:")
        self.port_combo = wx.ComboBox(panel, style=wx.CB_READONLY)
        self.search_btn = wx.Button(panel, label="Search")
        # self.detect_btn = wx.Button(panel, label="Detect Bootloader")
        self.browse_btn = wx.Button(panel, label="Load File")
        
        self.st_text = wx.StaticText(panel, label="                         ")
        self.hex_text = wx.TextCtrl(panel)
        self.update_btn = wx.Button(panel, label="Update Firmware")
        
        self.st_log = wx.StaticText(panel, label="Log Window:")
        self.cancel_btn = wx.Button(panel, label="Cancel")
        self.clr_log_btn = wx.Button(panel, label="Clear")
        self.save_log_btn = wx.Button(panel, label="Save")
        self.cancel_btn.Disable()

        # Progress and logs
        self.gauge = wx.Gauge(panel, range=100)
        self.log_box = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)

        # Layout
        hs1 = wx.BoxSizer(wx.HORIZONTAL)
        hs1.Add(port_lbl, 0, wx.ALL | wx.CENTER, 10)
        hs1.Add(self.port_combo, 1, wx.ALL | wx.EXPAND, 6)
        hs1.Add(self.search_btn, 0, wx.ALL, 6)
        # hs1.Add(self.detect_btn, 0, wx.ALL, 6)

        hs2 = wx.BoxSizer(wx.HORIZONTAL)
        hs2.Add(wx.StaticText(panel, label="Select Hex File:"), 0, wx.ALL | wx.CENTER, 6)
        hs2.Add(self.hex_text, 1, wx.ALL | wx.EXPAND, 6)
        hs2.Add(self.browse_btn, 0, wx.ALL, 6)

        hs3 = wx.BoxSizer(wx.HORIZONTAL)
        hs3.Add(self.st_text, 0, wx.ALL, 6)
        hs3.Add(self.update_btn, 0, wx.ALL, 6)
        # hs3.Add(self.cancel_btn, 0, wx.ALL, 6)
        hs3.Add(self.gauge, 1, wx.ALL | wx.EXPAND | wx.CENTER, 6)

        hs4 = wx.BoxSizer(wx.HORIZONTAL)
        hs4.Add(self.st_log, 0, wx.ALL, 6)
        hs4.Add(self.cancel_btn, 0, wx.ALL, 6)
        hs4.Add(self.clr_log_btn, 0, wx.ALL, 6)
        hs4.Add(self.save_log_btn, 0, wx.ALL, 6)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hs1, 0, wx.EXPAND)
        vbox.Add(hs2, 0, wx.EXPAND)
        vbox.Add(hs3, 0, wx.EXPAND)
        vbox.Add(hs4, 0, wx.EXPAND)
        # vbox.Add(wx.StaticText(panel, label="Log Window:"), 0, wx.LEFT | wx.TOP, 6)
        
        vbox.Add(self.log_box, 1, wx.ALL | wx.EXPAND, 6)
        panel.SetSizer(vbox)

        # Events
        self.search_btn.Bind(wx.EVT_BUTTON, self.on_search)
        self.browse_btn.Bind(wx.EVT_BUTTON, self.on_browse)
        self.update_btn.Bind(wx.EVT_BUTTON, self.on_update)
        # self.detect_btn.Bind(wx.EVT_BUTTON, self.on_detect_bootloader)
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        self.port_combo.Bind(wx.EVT_COMBOBOX, self.on_port_selected)
        
        # Bind buttons
        self.clr_log_btn.Bind(wx.EVT_BUTTON, self.on_clear_log)
        self.save_log_btn.Bind(wx.EVT_BUTTON, self.on_save_log)

        self._fw = None
        self._worker_thread = None
        self._stop_request = threading.Event()
        self.Centre()
        self.Show()

    # UI helpers
    def ui_log(self, msg):
        """
        Update Log Window Safely from Worker Threads.

        Detailed Description:
            This function appends log messages to the
            firmware update log window in a thread-safe manner.

            Since firmware operations run in background threads,
            direct UI updates may cause runtime issues. Therefore,
            wx.CallAfter is used to safely post log updates to
            the main GUI thread.

        Args:
            self :
                Reference to FirmwareFrame instance.

            msg :
                Log message string to be displayed
                in the log window.

        Returns:
            None
        """
        # append safely to wx main thread
        wx.CallAfter(self.log_box.AppendText, str(msg) + "\n")
    

    def get_model_from_hex(self, hexfile):
        """
        Extract Model Information from HEX Filename.

        Detailed Description:
            This function determines the firmware model
            by analyzing the selected HEX file name.

            It scans the file name string and checks
            for supported model identifiers. If a match
            is found, the corresponding model number
            is returned for compatibility validation.

        Args:
            self :
                Reference to FirmwareFrame instance.

            hexfile :
                Full path of the selected HEX file.

        Returns:
            str / None :
                Returns detected model number
                (e.g., "3141", "3142").

                Returns None if no supported
                model identifier is found.
        """
        name = os.path.basename(hexfile).lower()
        if "3141" in name:
            return "3141"
        if "3142" in name:
            return "3142"
        return None

    def get_device_model_from_usb(self, vid, pid):
        
        """
        Detect Device Model from USB VID/PID.

        Detailed Description:
            This function identifies the connected device
            model and revision using USB VID and PID.

            It scans USB devices matching the provided
            identifiers and maps the detected revision
            to the corresponding supported switch model.

        Args:
            self :
                Reference to FirmwareFrame instance.

            vid :
                USB Vendor ID of the device.

            pid :
                USB Product ID of the device.

        Returns:
            tuple :
                Returns detected (model, revision).
                Returns (None, None) if detection fails.
        """
        try:
            for dev in usb.core.find(find_all=True, idVendor=vid, idProduct=pid):
                try:
                    rev = f"{dev.bcdDevice:04x}"

                    # <<< UPDATE MAPPING IF REQUIRED >>>
                    if rev in ("0004", "0005"):
                        return "3141", rev
                    elif rev in ("0006","0008"):
                        return "3142", rev

                finally:
                    usb.util.dispose_resources(dev)
        except Exception:
            pass

        return None, None

    def ui_progress(self, pct):
        """
        Update Firmware Update Progress Bar.

        Detailed Description:
            This function updates the GUI progress gauge
            based on the firmware flashing percentage.

            It safely invokes the gauge update from
            the worker thread using wx.CallAfter.

        Args:
            self :
                Reference to FirmwareFrame instance.

            pct :
                Firmware update completion percentage.

        Returns:
            None
        """
        wx.CallAfter(self.gauge.SetValue, pct)
    
    def on_search(self, evt):
        """
        Search and Detect Connected Devices.

        Detailed Description:
            This function scans all available serial ports
            and filters supported devices based on VID/PID.

            It communicates with each detected device to
            identify the model and firmware version.

            Detected devices are populated into the
            port selection dropdown list, and a default
            device is auto-selected if available.

        Args:
            self :
                Reference to FirmwareFrame instance.

            evt :
                Button click event triggering device search.

        Returns:
            None
        """
        self.port_combo.Clear()
        ports = list(serial.tools.list_ports.comports())

        if not ports:
            self.ui_log("[WARN] No serial ports detected")
            return

        for p in ports:
            # --- FILTER: Only allow devices with VID=045E and PID=0646 ---
            if not (p.vid and p.pid and f"{p.vid:04X}" == "045E" and f"{p.pid:04X}" == "0646"):
                continue
            model_name = None
            version_info = None
            try:
                with serial.Serial(p.device, 115200, timeout=0.2) as ser:
                    ser.reset_input_buffer()
                    ser.write(b'status\r\n')
                    start_time = time()

                    # Wait up to 1s for "Model" line
                    while time() - start_time < 1:
                        if ser.in_waiting:
                            line = ser.readline()
                            try:
                                line_str = line.decode('utf-8').strip()
                                
                                if "Model 3141" in line_str:
                                    model_name = "3141"
                                elif "Model 3142" in line_str:
                                    model_name = "3142"
                            except Exception:
                                continue

                    #  Only check version if model detected (normal mode)
                    if model_name:
                        ser.reset_input_buffer()
                        ser.write(b'version\r\n')
                        sleep(0.1)
                        resp = ser.read(100).decode(errors="ignore")
                        # self.ui_log(f"[INFO] {model_name} on {p.device} → Version {version_info}")
                        if resp:
                            # version_info = resp.split("Version")[-1].strip()
                            self.ui_log(f"Connected Model {model_name}({p.device}) -> Version(FW:HW):{resp}")
                        else:
                            self.ui_log(f"[INFO] Model {model_name} on {p.device} → Version not detected (bootloader mode?)")
                            # self.ui_log(f"Connected Model {model_name}({p.device}) [BOOTLOADER MODE]")
                    else:
                        self.ui_log(f"[INFO] {p.device}: No model response (possibly bootloader mode)")

            # except Exception as e:
            #     self.ui_log(f"[WARNING] {p.device} cannot open: {e}")
            except serial.SerialException as e:
                if "PermissionError(13" in str(e) or "Access is denied" in str(e):
                    msg = f"{p.device} port could not open because it is already connected.\nPlease disconnect the other connection or continue anyway."
                    dlg = wx.MessageDialog(
                        None,
                        message=msg,
                        caption="Port In Use",
                        style=wx.OK | wx.ICON_WARNING
                    )
                    result = dlg.ShowModal()
                    dlg.Destroy()

            # Build display name for dropdown
            if model_name:
                if version_info:
                    display_name = f"{model_name} v{version_info} ({p.device})"
                else:
                    display_name = f"{model_name}({p.device})"
            else:
                display_name = p.device

            self.port_combo.Append(display_name)

        if self.port_combo.GetCount() > 0:
            default_index = 0
            for i in range(self.port_combo.GetCount()):
                text = self.port_combo.GetString(i)
                if "3142" in text:  # Prefer 3142 if available
                    default_index = i
                    break

            self.port_combo.SetSelection(default_index)
            self.ui_log(f"[OK] Default port selected: {self.port_combo.GetString(default_index)}")
        else:
            self.ui_log("[WARN] No serial ports detected")

    def on_browse(self, evt):
        """
        Browse Firmware HEX File.

        Detailed Description:
            This function opens a file dialog allowing
            users to select a firmware HEX file
            for update.

        Args:
            self :
                Reference to FirmwareFrame instance.

            evt :
                Button click event.

        Returns:
            None
       """
        with wx.FileDialog(self, "Select HEX file", wildcard="HEX files (*.hex)|*.hex",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fd:
            if fd.ShowModal() == wx.ID_OK:
                path = fd.GetPath()
                self.hex_text.SetValue(path)
                self.ui_log(f"[OK] Selected HEX file: {path}")
    
    def on_port_selected(self, event):
        """
        Handle Device Selection from Port Dropdown.

        Detailed Description:
            This function triggers when the user selects
            a device from the port selection combo box.

            It extracts the model name and COM port
            from the selected string and logs the
            selected device information.

        Args:
            self :
                Reference to FirmwareFrame instance.

            event :
                ComboBox selection event.

        Returns:
            None
        """
        selected_text = self.port_combo.GetStringSelection()  # e.g. "3141(COM6)"
        if not selected_text:
            return

        # Extract COM port and device name
        if "(" in selected_text and ")" in selected_text:
            model_name = selected_text.split("(")[0].strip()
            port_name = selected_text.split("(")[-1].split(")")[0]
        else:
            model_name = selected_text
            port_name = "Unknown"

        self.ui_log(f"[INFO] Selected device: {model_name} ({port_name})")

    def detect_normal_device(self):
        """
        Detect Connected Device in Normal Mode.

        Detailed Description:
            This function scans available USB devices
            matching supported VID and PID values.

            It identifies the device revision and
            determines whether the device is in
            NORMAL mode or BOOTLOADER mode.

        Args:
            self :
                Reference to FirmwareFrame instance.

        Returns:
            Tuple :
                (port, vid, pid, revision)

                Returns None values if no device found.
        """
        for port in serial.tools.list_ports.comports():
            if port.vid == DEVICE_VID and port.pid == DEVICE_PID:
                dev = usb.core.find(idVendor=port.vid, idProduct=port.pid)
                rev = f"{dev.bcdDevice:04x}" if dev else None
                mode = "BOOTLOADER" if rev == "0004" else "NORMAL" if rev == "0005" else "UNKNOWN"
                self.ui_log(f"[INFO] PORT={port.device}, REV={rev}, MODE={mode}")
                return port.device, port.vid, port.pid, rev
        return None, None, None, None
 
    def on_update(self, evt):
        """
        Start Firmware Update Process.

        Detailed Description:
            This function validates device selection,
            loads firmware, detects bootloader mode,
            and starts the firmware update thread.

        Args:
            self :
                Reference to FirmwareFrame instance.

            evt :
                Button click event.

        Returns:
            None
        """
        sel_index = self.port_combo.GetSelection()
        if sel_index == wx.NOT_FOUND:
            wx.MessageBox("Please select a device first.", "Info", wx.ICON_INFORMATION)
            return

        # Extract COM port
        selected_text = self.port_combo.GetString(sel_index)
        if "(" in selected_text and ")" in selected_text:
            port = selected_text.split("(")[-1].split(")")[0].strip()
        else:
            port = selected_text.strip()

        hexfile = self.hex_text.GetValue()
        if not hexfile or not os.path.exists(hexfile):
            wx.MessageBox("Please select a valid HEX file.", "Error", wx.ICON_ERROR)
            return

        # Disable UI buttons during update
        # self.update_btn.Disable()
        self.search_btn.Disable()
        self.browse_btn.Disable()
        self.cancel_btn.Enable()
        self._stop_request.clear()
        self.gauge.SetValue(0)
        self.log_box.Clear()

        # Create firmware updater instance
        self._fw = FirmwareUpdate(log_callback=self.ui_log)
        self._fw.hex_file = hexfile
        self._fw.fw_port = port

        def worker():
            try:
                # Step 1: Detect bootloader port
                self.ui_log(f"[INFO] Detecting bootloader port on {port} (sending reset)...")
                bootport, vid, pid, rev = self._fw.detect_bootloader_device(port)
                
                # ---------- NEW: DEVICE vs FIRMWARE VALIDATION ----------
                hex_model = self.get_model_from_hex(hexfile)

                # Validate VID / PID first
                if vid != 0x045E or pid != 0x0646:
                    wx.CallAfter(
                        wx.MessageBox,
                        f"Unsupported device detected!\n\nVID={vid:04X} PID={pid:04X}",
                        "Invalid Device",
                        wx.OK | wx.ICON_ERROR
                    )
                    return

                device_model, device_rev = self.get_device_model_from_usb(vid, pid)

                # Unknown revision → block update
                if not device_model:
                    wx.CallAfter(
                        wx.MessageBox,
                        f"Unknown device revision detected.\n\nREV={device_rev}",
                        "Invalid Device Revision",
                        wx.OK | wx.ICON_ERROR
                    )
                    return

                # HEX vs Device model mismatch
                if hex_model and hex_model != device_model:
                    wx.CallAfter(
                        wx.MessageBox,
                        f"Firmware update compatibility check failed.\n\n"
                        # f"Connected Device : Model {device_model} (REV {device_rev})\n"
                        f"Selected MCCI Model {device_model}\n"
                        f"Selected MCCI Model {hex_model} FW Hex File\n\n"
                        f"Please Select Model {device_model} Firmware Hex file to proceed.",
                        "Firmware Update Compatibility Error",
                        wx.OK | wx.ICON_ERROR
                    )
                    self.ui_log("[ERR] Firmware update aborted due to compatibility check failure.")
                    return

                if not bootport:
                    self.ui_log("[ERR] Bootloader port detection failed. Aborting.")
                    return

                # Step 2: Revision check and fallback
                if rev not in ("0004", "0008"):
                    # self.ui_log(f"[WARN] Unexpected revision {rev}. Device may still be in bootloader mode.")
                    # self.ui_log(f"[FORCE] Proceeding with firmware update on {bootport} (REV={rev})")
                    self.ui_log(f"[FORCE] Proceeding with firmware update on {bootport}")
                else:
                    self.ui_log(f"[OK] Bootloader detected on {bootport} (REV={rev}) — proceeding with update.")

                # Update firmware port to the new bootloader port
                self._fw.fw_port = bootport

                # Step 3: Load HEX file
                self.ui_log("[INFO] Loading HEX file into memory...")
                try:
                    self._fw.load_hex_file(hexfile)
                except Exception as e:
                    self.ui_log(f"[ERR] Failed to load hex file: {e}")
                    return

                # Step 4: Start firmware update
                self.ui_log("[INFO] Starting firmware update...")
                loop_guard = 0
                max_loops = 10000

                while (
                    self._fw.fw_seq != EXIT_BOOTLOADER
                    and not self._stop_request.is_set()
                    and loop_guard < max_loops
                ):
                    self._fw.run_update(progress_callback=self.ui_progress)
                    loop_guard += 1

                # Step 5: Handle completion or abort
                if self._stop_request.is_set():
                    self.ui_log("[WARN] Update cancelled by user.")
                elif loop_guard >= max_loops:
                    self.ui_log("[ERR] Update loop exceeded max iterations; aborting.")
                else:
                    self.ui_log("[OK] Firmware update finished successfully.")
                    self.ui_progress(100)
                    sleep(2)
                    # Try to reconnect and check version
                    try:
                        ser.close()
                    except Exception:
                        pass
    
                    # Reopen the port to check version
                    try:
                        # Extract COM port name from combo (e.g., "3141(COM6)" → "COM6")
                        port_name = self.port_combo.GetValue().split('(')[-1].replace(')', '')

                        ser = serial.Serial(port=port_name, baudrate=115200, timeout=1)
                        sleep(0.3)
                        ser.reset_input_buffer()

                        # Send version command
                        ser.write(b"version\r\n")
                        sleep(0.2)

                        version_resp = ""
                        while ser.in_waiting:
                            try:
                                line = ser.readline().decode("utf-8").strip()
                                if line:
                                    version_resp += line
                            except Exception:
                                break

                        if version_resp:
                            self.ui_log(f"[INFO] Checking for updated version...")
                            self.ui_log(f"[INFO] Updated Version(FW:HW): {version_resp}")
                        else:
                            self.ui_log("[WARN] Could not read version after update (device may still be rebooting).")
                    except:
                        self.ui_log("Thank you...!")

                    # except Exception:
                    #     self.ui_log("[INFO] Device reboot verification skipped or not supported.")

            except Exception as e:
                self.ui_log(f"[EXC] {e}")

            finally:
                wx.CallAfter(self.update_btn.Enable)
                wx.CallAfter(self.search_btn.Enable)
                wx.CallAfter(self.browse_btn.Enable)
                wx.CallAfter(self.cancel_btn.Disable)

        # Start the worker thread
        self._worker_thread = threading.Thread(target=worker, daemon=True)
        self._worker_thread.start()

    def on_cancel(self, evt):
        """
        Cancel Firmware Update Process.

        Detailed Description:
            This function stops the running firmware
            update thread upon user request.

        Args:
            self :
                Reference to FirmwareFrame instance.

            evt :
                Button click event.

        Returns:
            None
        """
        if self._worker_thread and self._worker_thread.is_alive():
            self._stop_request.set()
            self.ui_log("[INFO] Cancel requested. Waiting for thread to stop...")
        else:
            self.ui_log("[INFO] Nothing to cancel.")
    
    def on_clear_log(self, event):
        """
        Clear Firmware Update Logs.

        Detailed Description:
            This function clears all messages
            displayed in the log window.

        Args:
            self :
                Reference to FirmwareFrame instance.

            event :
                Button click event.

        Returns:
            None
        """
        self.log_box.Clear()
        self.ui_log("[INFO] Log cleared.")
    
    # --- Save log function ---
    def on_save_log(self, event):
        """
        Save Firmware Update Logs to File.

        Detailed Description:
            This function saves the firmware
            update log content into a text file
            selected by the user.

        Args:
            self :
                Reference to FirmwareFrame instance.

            event :
                Button click event.

        Returns:
            None
        """
        
        with wx.FileDialog(self, "Save log as", wildcard="Text files (*.txt)|*.txt",
                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fd:
            if fd.ShowModal() == wx.ID_OK:
                path = fd.GetPath()
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(self.log_box.GetValue())
                    wx.MessageBox(f"Log saved successfully:\n{path}", "Saved", wx.OK | wx.ICON_INFORMATION)
                except Exception as e:
                    wx.MessageBox(f"Failed to save log:\n{e}", "Error", wx.OK | wx.ICON_ERROR)