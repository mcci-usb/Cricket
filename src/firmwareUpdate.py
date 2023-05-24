##############################################################################
# 
# Module: Firmwareupdate.py
#
# Description:
#     Update firmware
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
# Lib imports
from random import choices
from matplotlib import style
import wx
import os
import sys
import serial.tools.list_ports

# Own modules
from uiGlobals import *
from cricketlib import switch3141
from cricketlib import switch3142

import devControl

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


##############################################################################
# Utilities
##############################################################################

class FirmwareUpdate(wx.PyEvent):

    def __init__(self, data):
        
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

class firmwareWindow(wx.Window):
 
    def __init__ (self, parent, top):
       
        wx.Window.__init__(self, parent, -1,
                           size=wx.Size(100,100),
                           style=wx.CLIP_CHILDREN,
                           name="About")

        self.top = top
        self.parent = parent
        self.wait_flg = True

        self.fw_seq = None
        self.fw_port = None
        self.sw = None

        self.avrHand = None
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
        
        self.btn_scan = wx.Button(self, ID_BTN_DEV_SCAN, "Search",
                                  size=(77,25))
        
        self.st_Sw = wx.StaticText(self, -1, "Select Switch: ")

        self.fst_lb = wx.ComboBox(self, size=(120, -1), choices = self.dlist,style=wx.CB_DROPDOWN)
        
        self.st_seqname = wx.StaticText(self, -1, "Browse the hex file")
        self.tc_bloc = wx.TextCtrl(self, -1, size=(250,-1), 
                                            style = wx.TE_CENTRE |
                                            wx.TE_PROCESS_ENTER,
                                            validator=NumericValidator())
        self.btn_load = wx.Button(self, -1, "Load", size=(60,25))
        self.st_mty = wx.StaticText(self, -1, " ")

        # self.st_fw = wx.StaticText(self, -1, "Update Start")
        self.btn_up_start = wx.Button(self, -1, "Update", size=(70,25))
        self.btn_cancel = wx.Button(self, -1, "Cancel", size=(70,25))

        # self.btn_top = wx.BoxSizer(wx.HORIZONTAL)
        self.szr_top = wx.BoxSizer(wx.HORIZONTAL)
        self.szr_load = wx.BoxSizer(wx.HORIZONTAL)
        self.szr_update = wx.BoxSizer(wx.HORIZONTAL)
        
        wx.BoxSizer(wx.HORIZONTAL)
 
        self.szr_top.AddMany([
            (10,50,0),
            (self.st_Sw, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL),
            (20,80,0),
            (self.fst_lb, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL),
            (10,50,0),
            (self.btn_scan, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL),
            (10,50,0)
            ])
        
        self.szr_load.AddMany([
            (10,50,0),
            (self.st_seqname, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL),
            (10,50,0),
            (self.tc_bloc, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL),
            (10,50,0),
            (self.btn_load, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL),
            (10,10,0),
            (self.st_mty, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
            ])
        
        self.szr_update.AddMany([
            (200,40,0),
            (self.btn_up_start, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER),
            (10,0,0),
            (self.btn_cancel, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER)
            ])
        # Creates a boxsizer as vertical
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.vbox.AddMany([
            (10,10,0),
            (self.szr_top, 0, wx.EXPAND | wx.ALL),
            (10,10,0),
            (self.szr_load, 0, wx.EXPAND | wx.ALL),
            (10,10,0),
            (self.szr_update, 0, wx.EXPAND | wx.ALL),
            (10,10,0)
            ])
        
        # Set size of frame
        self.SetSizer(self.vbox)
        # Set size of frame
        self.vbox.Fit(self)
        self.Layout()

        self.btn_load.Bind(wx.EVT_BUTTON, self.LoadBatch)
        self.btn_scan.Bind(wx.EVT_BUTTON, self.ScanDevice)
        self.btn_up_start.Bind(wx.EVT_BUTTON, self.update_start)
        self.btn_cancel.Bind(wx.EVT_BUTTON, self.update_cancel)

        # The Timer class allows you to execute code at specified intervals.
        self.timer_lp = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.SearchTimer, self.timer_lp)

        self.timer_fu = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.FwUpdateTimer, self.timer_fu)

        EVT_RESULT(self, self.SearchEvent)
    
    def updateBatchLocation(self, pathname):
        self.hexPath = pathname

    def LoadBatch(self, event):
        pathname = self.load_file()
        self.updateBatchLocation(pathname)
        

    def load_file(self):
        self.dirname=""
        dlg = wx.FileDialog(self, "Load File", self.dirname, "", "*.hex", 
                                wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        
        pathname = dlg.GetPath()
        self.tc_bloc.SetValue(pathname)
        try:
            self.mappedSw = {}
            self.main_flg = False
            self.end_flg = False
            self.finseq = []
            if os.path.exists(pathname):
                with open(pathname) as fobj:
                    for line in fobj:
                        pass
        except IOError:
            wx.LogError("Can not open file '%s', " % pathname)
        return pathname
    

    def FwUpdateTimer(self, evt):
        self.timer_fu.Stop()
        if self.fw_seq == DO_RESET:
            self.sw.do_reset()
            self.fw_seq = READ_AVAIL_PORTS
            self.timer_fu.Start(1500)
        elif self.fw_seq == READ_AVAIL_PORTS:
            plist = devControl.get_avail_ports(self.top)
            self.fw_port = self.get_avrdude(plist)
            if self.fw_port != None:
                self.fw_seq = INIT_AVR_PORT
                self.timer_fu.Start(500)
            else:
                print("No AVRdude found!!")
        elif self.fw_seq == INIT_AVR_PORT:
            if self.open_avr_port():
                self.get_sw_identifier()
                self.timer_fu.Start(500)
        elif self.fw_seq == GET_SW_IDENTIFIER:
            if self.parse_sw_identifier():
                self.get_programmer_type()
                self.timer_fu.Start(100)
        elif self.fw_seq == GET_PROG_TYPE:
            if self.parse_programmer_type():
                self.get_sw_version()
                self.timer_fu.Start(100)
        elif self.fw_seq == GET_SW_VERSION:
            if self.parse_sw_version():
                self.check_auto_incr()
                self.timer_fu.Start(100)
        elif self.fw_seq == CHECK_AUTO_INC:
            if self.parse_auto_incr():
                self.check_block_support()
                self.timer_fu.Start(100)
        elif self.fw_seq == CHECK_BLOCK_SUPPORT:
            if self.parse_block_support():
                self.get_dev_code()
                self.timer_fu.Start(100)
        elif self.fw_seq == GET_DEV_CODE:
            if self.parse_dev_code():
                self.select_dev_type()
                self.timer_fu.Start(100)
        elif self.fw_seq == SELECT_DEV_TYPE:
            if self.parse_dev_type():
                self.get_into_progmode()
                self.timer_fu.Start(100)
        elif self.fw_seq == GET_INTO_PROGMODE:
            if self.parse_get_progmode():
                self.read_dev_signature()
                self.timer_fu.Start(100)
        elif self.fw_seq == READ_DEV_SIGNATURE:
            if self.parse_dev_signature():
                self.read_lfuse()
                self.timer_fu.Start(100)
        elif self.fw_seq == READ_LFUSE:
            if self.parse_lfuse():
                self.read_hfuse()
                self.timer_fu.Start(100)
        elif self.fw_seq == READ_HFUSE:
            if self.parse_hfuse():
                self.read_efuse()
                self.timer_fu.Start(100)
        elif self.fw_seq == READ_EFUSE:
            if self.parse_efuse():
                if self.flash_flg:
                    self.flash_flg = False
                    self.leave_prog_mode()
                    self.timer_fu.Start(100)
                else:
                    self.top.print_on_log("writing flash ("+ str(len(self.mem_addr))+ ") bytes\n")
                    self.flash_addr = self.mem_addr[0]
                    self.byte_addr = self.mem_addr[0]
                    self.top.print_on_log(".")
                    self.set_address()
                    self.timer_fu.Start(100)
        elif self.fw_seq == SET_ADDRESS:
            if self.parse_set_address():
                self.load_block_flash()
                self.timer_fu.Start(100)
        elif self.fw_seq == WRITE_BLOCK:
            if self.parse_set_address():
                if self.byte_addr <= len(self.mem_addr):
                    self.top.print_on_log(".")
                    self.flash_addr += 0x40
                    self.set_address()
                    self.timer_fu.Start(100)
                else:
                    self.flash_flg = True
                    self.read_lfuse()
                    self.timer_fu.Start(100)
        elif self.fw_seq == LEAVE_PROGMODE:
            if self.parse_set_address():
                self.exit_boot_loader()
                self.timer_fu.Start(100)
        elif self.fw_seq == EXIT_BOOTLOADER:
            if self.parse_set_address():
                self.top.print_on_log("Firmware update success!\n")
        

    def load_block_flash(self):
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

    def exit_boot_loader(self):
        self.write_avr('E')
        self.fw_seq = EXIT_BOOTLOADER
  
    def leave_prog_mode(self):
        self.write_avr('L')
        self.fw_seq = LEAVE_PROGMODE

    def set_address(self):
        addstr = (self.flash_addr).to_bytes(2, byteorder='big').hex()
        addbyte = bytes.fromhex(addstr)
        mybyte = []
        mybyte.append(0x41)
        for byte in addbyte:
            mybyte.append(byte)
        self.write_avr_hba(mybyte)

        self.fw_seq = SET_ADDRESS        
        

    def read_efuse(self):
        self.write_avr(CMD_READ_EFUSE)
        self.fw_seq = READ_EFUSE

    def read_lfuse(self):
        self.write_avr(CMD_READ_LFUSE)
        self.fw_seq = READ_LFUSE

    def read_hfuse(self):
        self.write_avr(CMD_READ_HFUSE)
        self.fw_seq = READ_HFUSE
    
    def read_dev_signature(self):
        self.write_avr(CMD_READ_DEVSIG)
        self.fw_seq = READ_DEV_SIGNATURE

    def get_into_progmode(self):
        self.write_avr(CMD_GET_PROGMODE)
        self.fw_seq = GET_INTO_PROGMODE
    
    def select_dev_type(self):
        self.write_avr_ba("TD")
        self.fw_seq = SELECT_DEV_TYPE
                
    def get_dev_code(self):
        self.write_avr(CMD_GET_DEVCODE)
        self.fw_seq = GET_DEV_CODE

    def check_block_support(self):
        self.write_avr(CMD_CHECK_BLOCKSUPP)
        self.fw_seq = CHECK_BLOCK_SUPPORT

    def check_auto_incr(self):
        self.write_avr(CMD_CHECK_AUTOINCR)
        self.fw_seq = CHECK_AUTO_INC

    def get_sw_version(self):
        self.write_avr(CMD_GET_SWVERSION)
        self.fw_seq = GET_SW_VERSION

    def get_programmer_type(self):
        self.write_avr(CMD_GET_PROGTYPE)
        self.fw_seq = GET_PROG_TYPE

    def get_sw_identifier(self):
        self.rx_flg = True
        self.write_avr(CMD_GET_SWIDENTIFIER)
        self.fw_seq = GET_SW_IDENTIFIER


    def parse_set_address(self):
        resp = self.read_avr_oned()
        if resp == b'\r':
            return True
        else:
            self.top.print_on_log("Error when setting flash address\n")
            return False


    def parse_efuse(self):
        resp = self.read_avr_ba()
        if resp != None:
            # bsize = resp[0]
            bsize = (format(resp[0], '#x'))
            self.top.print_on_log("efuse reads as: "+str(bsize)+"\n")
            return True
        else:
            self.top.print_on_log("Error when reading efuse\n")
            return False
 
    def parse_hfuse(self):
        resp = self.read_avr_ba()
        if resp != None:
            # bsize = resp[0]
            bsize = (format(resp[0], '#x'))
            self.top.print_on_log("hfuse reads as: "+str(bsize)+"\n")
            return True
        else:
            self.top.print_on_log("Error when reading hfuse\n")
            return False

    def parse_lfuse(self):
        resp = self.read_avr_ba()
        if resp != None:
            # bsize = resp[0]
            bsize = (format(resp[0], '#x'))
            if self.flash_flg:
                self.top.print_on_log("\n")
            self.top.print_on_log("lfuse reads as: "+str(bsize)+"\n")
            return True
        else:
            self.top.print_on_log("Error when reading lfuse\n")
            return False
    
    def parse_dev_signature(self):
        resp = self.read_avr_ba()
        if resp != None:
            bsize1 = (format(resp[0], '#x'))
            bsize2 = (format(resp[1], '#x'))
            bsize3 = (format(resp[2], '#x'))
            self.top.print_on_log("Device Signature = "+bsize1+bsize2+bsize3+"\n")
            return True
        else:
            self.top.print_on_log("Error when reading dev signature\n")
            return False
        
    
    def parse_get_progmode(self):
        resp = self.read_avr_oned()
        if resp == b'\r':
            self.top.print_on_log("Enter into Program mode success\n")
            return True
        else:
            self.top.print_on_log("Error when entering into prog mode\n")
            return False

    def parse_dev_type(self):
        resp = self.read_avr_oned()
        if resp == b'\r':
            self.top.print_on_log("Dev code selected = 0x44\n")
            return True
        else:
            self.top.print_on_log("Error when checking the supported device list\n")
            return False

    def parse_dev_code(self):
        resp = self.read_avr_ba()
        if resp != None:
            # bsize = resp[0]
            bsize = (format(resp[0], '#x'))
            self.top.print_on_log("Programmer supports the following devices: "+bsize+"\n")
            return True
        else:
            self.top.print_on_log("Error when checking the supported device list\n")
            return False

    def parse_block_support(self):
        resp = self.read_avr_ba()
        if resp != None:
            bsize = resp[1:3]
            bsize = bsize.hex()
            self.pageSize = bsize
            self.top.print_on_log("Programmer supports buffered memory access with buffer size = "+str(int(bsize, 16))+" bytes\n")
            return True
        else:
            self.top.print_on_log("Error when checking block support\n")
            return False

    def parse_auto_incr(self):
        resp = self.read_avr()
        if resp != None:
            if resp[0] == 'Y':
                self.top.print_on_log("Programmer supports auto addr increment\n")
            else:
                self.top.print_on_log("Programmer supports auto addr increment!\n")
            return True
        else:
            self.top.print_on_log("Error when checking auto addr incement support\n")
            return False

    def parse_sw_version(self):
        resp = self.read_avr()
        if resp != None:
            resp = int(resp, 16)
            resp = resp / 16
            self.top.print_on_log("Software Version = "+str(resp)+"\n")
            return True
        else:
            self.top.print_on_log("Software Version read error\n")
            return False

    def parse_programmer_type(self):
        resp = self.read_avr()
        if resp != None:
            self.top.print_on_log("Programmer Type:  "+resp+"\n")
            return True
        else:
            self.top.print_on_log("Programmer type not found\n")
            return False

    def parse_sw_identifier(self):
        resp = self.read_avr()
        if resp == "CATERIN":
            self.top.print_on_log(" --------------   Firmware update   ------------------\n")
            self.top.print_on_log("Found Programmer Id = "+resp+"\n")
            return True
        else:
            self.top.print_on_log("Programmer Id read error = "+resp+"\n")
            return False

    def open_avr_port(self):
        self.avrHand = serial.Serial()
        self.avrHand.port = self.fw_port
        self.avrHand.baudrate = 57600
        self.avrHand.bytesize = 8
        self.avrHand.parity = serial.PARITY_NONE
        self.avrHand.timeout = 0
        self.avrHand.stopbits = serial.STOPBITS_ONE

        try:
            self.avrHand.open()
            return True
        except:
            self.avrHand = None
            return False
        pass


    def read_avr_ba(self):
        rxdata = None
        try:
            rxdata = self.avrHand.read(10)
        except serial.SerialException as serr:
            print("Issue in Serial port: ", serr)
        return rxdata


    def read_avr_oned(self):
        rxdata = None
        try:
            rxdata = self.avrHand.read(1)
        except serial.SerialException as serr:
            self.top.print_on_log("Issue in Serial port: "+str(serr)+"\n")
        return rxdata


    def read_avr(self):
        rxdata = None
        try:
            rxdata = self.avrHand.readline()
            try:
                rxdata = rxdata.rstrip().decode('utf-8')
            except:
                print("Serial Parsing Error\n")
        except serial.SerialException as serr:
            print("Issue in Serial port: ", serr)
        return rxdata
    

    def write_avr_hba(self,param):
        ba = bytearray(param)
        try:
            self.avrHand.write(ba)
        except serial.SerialException as serr:
            print(serr)

    def write_avr_ba(self,param):
        ba = bytearray(param.encode())
        try:
            self.avrHand.write(ba)
        except serial.SerialException as serr:
            print(serr)

    def write_avr(self,param):
        try:
            self.avrHand.write(param.encode())
        except serial.SerialException as serr:
            print(serr)

    def get_avrdude(self, plist):
        for port in plist:
            if sys.platform == "win32": 
                hwid = port[0]
                strlst = hwid.split('SER')[1].split('LOCATION')[0].rstrip(' ')
                if len(strlst) == 1 and '=' in strlst:
                    return port[1]
            else:
                if port[2].rstrip(' ') == "USB IO board":
                    return port[1]
        return None

    def SearchTimer(self, evt):
        wx.PostEvent(self, FirmwareUpdate("search"))
        self.timer_lp.Stop()
        
    def ScanDevice(self, evt):
        wx.PostEvent(self, FirmwareUpdate("print"))
        wx.PostEvent(self, FirmwareUpdate("search"))
        wx.BeginBusyCursor()
    

    def SearchEvent(self, event):
        if event.data is None:
            self.top.print_on_log("No Search event\n")
        elif event.data == "search":
            #self.btn_scan.Enable(False)
            self.btn_scan.Unbind(wx.EVT_BUTTON)
            self.get_devices()
            wx.GetApp().Yield()
            self.btn_scan.Bind(wx.EVT_BUTTON, self.ScanDevice)
        elif event.data == "print":
            self.top.print_on_log("Searching Devices ...\n")
        
    def get_devices(self):    
        devlist = devControl.search_device(self.top)
        if (wx.IsBusy()):
            wx.EndBusyCursor()

        dev_list = devlist["switches"]
        if(len(dev_list) == 0):
            self.top.print_on_log("No Devices found\n")
            self.fst_lb.Clear()
        else:
            key_list = []
            val_list = []

            nlist = []
            
            for i in range(len(dev_list)):
                key_list.append(dev_list[i]["port"])
                val_list.append(dev_list[i]["model"])

            self.fst_lb.Clear()

            for i in range(len(val_list)):
                str1 = val_list[i]+"("+key_list[i]+")"
                if val_list[i] == '3141' or val_list[i] == '3142':
                    self.fst_lb.Clear()
                    nlist.append(val_list[i]+"("+key_list[i]+")")
                    self.fst_lb.Append(nlist)
                    self.top.print_on_log(str1+"\n")
    
    def get_selected_com(self):        
        scval = self.fst_lb.GetValue()
        txt = scval.split("(")
        return txt[1].replace(")","")
    
    def update_start(self, event):
        self.bloc = self.tc_bloc.GetValue()
        if os.path.exists(self.bloc):
            if not self.validate_hex_file(self.bloc):
                title = ("3141/3142 Firmware upload")
                msg = ("Please select a valid hex file!")
                dlg = wx.MessageDialog(self, msg, title, wx.OK)
                dlg.ShowModal()
            else:
                self.unpack_hex_file(self.bloc)
                self.mem_addr = list(self.mem_flash.keys())
                self.mem_addr.sort()
                selcom = self.get_selected_com()
                self.sw = switch3141.Switch3141(selcom)
                self.sw2 = switch3142.Switch3142(selcom)
                if(self.sw.connect() or self.sw2.connect()):
                    self.fw_seq = DO_RESET
                    self.timer_fu.Start(1000)

    def update_start_old(self, event):
        self.bloc = self.tc_bloc.GetValue()
        if os.path.exists(self.bloc):
            selcom = self.get_selected_com()
            self.sw = switch3141.Switch3141(selcom)
            if(self.sw.connect()):
                self.sw.do_reset()
                dports = devControl.get_avail_ports(self.top)
        else:
            print("File Not available")

    def update_cancel(self, event):
        self.fw_seq = READ_AVAIL_PORTS
        self.timer_fu.Start(500)
        

    def OnClick (self, evt):
        self.GetParent().OnOK(evt)
   
    def OnSize (self, evt):
        self.Layout()

    def unpack_hex_file(self, hfloc):
        lines = tuple(open(hfloc, "r"))

        self.mem_flash = {}
        for line in lines:
            self.unpack_line(line)
        


    def unpack_line(self, line):
        if line[0] == ":" and line[-1] == "\n":
            data_len = int(line[1:3], 16)
            addr_hex = int(line[3:7], 16)
            data_type = int(line[7:9], 16)
            data_str = line[9:-3]

            if data_len * 2 == len(data_str) and data_type == 0:
                barr = bytearray.fromhex(data_str)

                for bhex in barr:
                    self.mem_flash[addr_hex] = bhex
                    addr_hex += 1


    def validate_hex_file(self, hfloc):
        lines = tuple(open(hfloc, "r"))
        status = False
        for line in lines:
            if line[0] == ":" and line[-1] == "\n":
                status = True
            else:
                return False
        return status


def EVT_RESULT(win, func):
    win.Connect(-1, -1, EVT_RESULT_ID, func)    

def get_devices(top):
    devlist = devControl.search_device(top)
    dev_list = devlist["devices"]

class FirmwareDialog(wx.Dialog):
    
    def __init__ (self, parent, top):
        
        wx.Dialog.__init__(self, parent, -1, "Switch 3141 Firmware Update",
                           size=wx.Size(100, 100),
                           style=wx.STAY_ON_TOP|wx.DEFAULT_DIALOG_STYLE,
                           name="MCCI USB Switch Search Dialog")

        self.top = top
        self.win = firmwareWindow(self, top)

        # Sizes the window to fit its best size.
        self.Fit()
        self.CenterOnParent(wx.BOTH)
    
    def OnOK (self, evt):
        
    # Returns numeric code to caller
        self.EndModal(wx.ID_OK)
     
    def OnSize (self, evt):
       
        self.Layout()