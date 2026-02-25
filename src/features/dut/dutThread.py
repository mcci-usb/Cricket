# -*- coding: utf-8 -*-
##############################################################################
#
# Module: dutThread.py
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

import threading
import time
import wx

import re

from uiGlobals import *


class StopEvent(wx.PyEvent):
    """
    Custom DUT Fault Stop Event.

    This event is posted to the GUI when a configured fault
    pattern is detected in the DUT serial output.

    The event carries fault match details and configured action.

    Inherits:
        wx.PyEvent

    Args:
        data (dict):
            Dictionary containing:
                • match  → Matched fault string
                • action → Configured response action
    """

    def __init__(self, data):
        """
        Initialize Stop Event.

        Args:
            data (dict):
                Fault match and action information.
        """
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_DUT_SL_ERR_ID)
        self.data = data


class DutThread(threading.Thread):
    """
    DUT Serial Monitoring Thread.

    Background worker thread that continuously monitors serial
    data from the Device Under Test (DUT).

    Responsibilities:
        • Read incoming serial data
        • Push log data into shared queue
        • Detect configured fault patterns
        • Notify GUI on fault detection
        • Handle serial port errors

    Inherits:
        threading.Thread

    Args:
        cbf (callable):
            Callback function triggered on port failure.

        top (wx.Window):
            Parent GUI window for event posting.

        inqueue (queue.Queue):
            Queue to push serial log data.

        dut (dict):
            DUT configuration dictionary.

        devHand (serial.Serial):
            Active serial device handle.
    """
    def __init__(self, cbf, top, inqueue, dut, devHand):
        """
        Initialize DUT Monitoring Thread.

        Sets up serial monitoring parameters, fault detection rules,
        and communication handles.

        Args:
            cbf (callable):
                Callback executed when COM port fails.

            top (wx.Window):
                GUI window to receive posted events.

            inqueue (queue.Queue):
                Queue used to transfer serial log data.

            dut (dict):
                DUT configuration including fault patterns.

            devHand (serial.Serial):
                Open serial port handle.
        """
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
        """
        Execute Serial Monitoring Loop.

        Continuously reads serial data from DUT while the thread
        run flag is active.

        Workflow:
            1. Check for incoming serial bytes
            2. Read line from serial port
            3. Decode UTF-8 data
            4. Push data into queue
            5. Check for fault pattern match
            6. Post StopEvent on fault detection

        Error Handling:
            • Serial decode errors are ignored
            • COM port failures trigger callback

        Sleep:
            10 ms delay to reduce CPU usage.
        """
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
        """
        Stop Serial Monitoring Thread.

        Sets the run flag to False, terminating the monitoring loop.
        """
        self.run_flg = False

    def checkForFault(self, instr):
        """
        Detect Fault Pattern in Serial Data.

        Scans incoming serial text for configured fault patterns
        using regular expression matching.

        Args:
            instr (str):
                Incoming serial data string.

        Returns:
            str | None:
                • Matched fault string → If detected
                • None → If no fault match found
        """
        for fault in self.fault_list:
            if(re.search(fault, instr)):
                return fault
        return None