##############################################################################
# 
# Module: dutThread.py
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
#    V4.0.0 Wed May 25 2023 17:00:00   Seenivasan V
#       Module created
##############################################################################

import threading
import time
import wx

import re

from uiGlobals import *


class StopEvent(wx.PyEvent):
    """A class ServerEvent with init method"""

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_DUT_SL_ERR_ID)
        self.data = data


class DutThread(threading.Thread):
    def __init__(self, cbf, top, inqueue, dut, devHand):
        super(DutThread, self).__init__()
        self.queue = inqueue
        self.buffer = ''
        self.holder = ''
        
        self.name = list(dut.keys())[0]
        self.dut = dut[self.name]
        
        self.devHand = devHand
        
        self.run_flg = True
        self.fault_list = self.dut["faultseq"]
        self.action = self.dut["action"]
        self.top = top
        self.fault = None
        self.port_flg = False
        self.cbf = cbf

    
    def run(self):
        while self.run_flg:
            try:
                if(self.devHand.in_waiting > 0):
                    serstring = self.devHand.readline()
                    try:
                        self.buffer = serstring.decode('utf-8')
                        self.queue.put(self.buffer)
                        self.fault = self.checkForFault(self.buffer)
                        if(self.fault != None):
                            wx.PostEvent(self.top, StopEvent({"match": self.fault, "action": self.action}))
                    except:
                       print("Serial Data Parse Error")
                       pass
            except:
                self.queue.put("\nError in COM Port")
                self.cbf()
                
            time.sleep(0.01)

    def stop(self):
        self.run_flg = False

    def checkForFault(self, instr):
        for fault in self.fault_list:
            if(re.search(fault, instr)):
                return fault
        return None