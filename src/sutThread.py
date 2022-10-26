##############################################################################
# 
# Module: sutThread.py
#
# Description:
#     Scan the USB bus and get the list of devices attached
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
#    V2.6.0 Wed Apr 20 2022 17:00:00   Seenivasan V
#       Module created
##############################################################################

import threading
import serial
import time
import wx

import re

from uiGlobals import *


class StopEvent(wx.PyEvent):
    """A class ServerEvent with init method"""

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_SUT_SL_ERR_ID)
        self.data = data


class SutThread(threading.Thread):
    def __init__(self, cbf, top, inqueue, sut):
        super(SutThread, self).__init__()
        self.queue = inqueue
        self.buffer = ''
        self.holder = ''
        self.devHand = serial.Serial()
        self.name = list(sut.keys())[0]
        self.sut = sut[self.name]
        self.itype = self.sut["interface"]
        self.sconfig = self.sut[self.itype]
        self.devHand.port = self.sconfig["port"]
        self.devHand.baudrate = self.sconfig["baud"]
        self.devHand.bytesize = serial.EIGHTBITS
        self.devHand.parity = serial.PARITY_NONE
        self.devHand.timeout = 0
        self.devHand.stopbits = serial. STOPBITS_ONE
        self.queue = inqueue
        print("SutThread Init done")
        self.run_flg = True
        self.fault_list = self.sut["faultseq"]
        self.action = self.sut["action"]
        self.top = top
        self.fault = None
        self.port_flg = False
        self.cbf = cbf


    def run(self):
        print("Sut Thread Port Open and Run")
        try:
            self.devHand.open()
            self.port_flg = True
            while self.run_flg:
                if(self.devHand.in_waiting > 0):
                    serstring = self.devHand.readline()
                    try:
                        # self.buffer = serstring.decode("Ascii").strip()
                        self.buffer = serstring.decode('utf-8')
                        self.queue.put(self.buffer)
                        self.fault = self.checkForFault(self.buffer)
                        if(self.fault != None):
                            # self.run_flg = False
                            # wx.PostEvent(self.top, StopEvent(self.fault))
                            wx.PostEvent(self.top, StopEvent({"match": self.fault, "action": self.action}))
                    except:
                        pass
                time.sleep(0.01)
        except:
            self.queue.put("\nCouldn't open the port")
            if self.port_flg:
                self.cbf()
        # wx.PostEvent(self.top, StopEvent(self.fault))
          
                           
    def stop(self):
        self.run_flg = False

    def checkForFault(self, instr):
        for fault in self.fault_list:
            if(re.search(fault, instr)):
                return fault
        return None

    # def checkForFault(self, instr):
    #     self.holder += instr
    #     for fault in self.fault_list:
    #         if(self.holder.find(fault) != -1):
    #             return fault
        
    #     if(len(self.holder) >= 200):
    #         self.holder = self.holder[100:]
    #     return None
