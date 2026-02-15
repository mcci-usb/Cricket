# -*- coding: utf-8 -*-
##############################################################################
#
# Module: dutThread.py
#
# Description:
#     DUT Monitoring Thread module.
#
#     Implements threaded serial monitoring for DUT devices.
#     Continuously reads DUT data, pushes logs to UI queues,
#     detects configured fault sequences, and triggers
#     automated UI fault handling actions.
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
# Revision history:
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
    DUT Fault Stop Event.

    Description:
        Custom wxPython event used to notify the UI when
        a configured DUT fault sequence is detected.

        This event carries fault match data and the
        configured action to be executed by the UI.

    Attributes:
        data:
            Dictionary containing fault match details
            and action information.
    """

    def __init__(self, data):
        """
        Initialize StopEvent instance.

        Detailed Description:
            Creates a custom wxPython event object
            for communicating DUT fault detection
            results to the UI layer.

        Args:
            self:
                Reference to the current StopEvent instance.

            data:
                Dictionary payload containing:

                    • fault match string
                    • configured action type

        Returns:
            None

        Raises:
            None
        """
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_DUT_SL_ERR_ID)
        self.data = data


class DutThread(threading.Thread):
    """
    DUT Serial Monitoring Thread.

    Description:
        Implements continuous serial monitoring for
        DUT devices using a background worker thread.

        Responsibilities include:

            • Reading serial data from DUT
            • Pushing logs into UI queue
            • Detecting configured fault sequences
            • Triggering UI fault events
            • Handling communication failures
    """
    def __init__(self, cbf, top, inqueue, dut, devHand):
        """
        Initialize DUT monitoring thread.

        Detailed Description:
            Sets up thread execution context, including
            DUT configuration, serial handler, monitoring
            queue, and fault detection parameters.

        Args:
            self:
                Reference to the current thread instance.

            cbf:
                Callback function invoked when
                COM port failure occurs.

            top:
                Main UI controller reference used
                for posting wx events.

            inqueue:
                Queue object used to transfer DUT
                log data to UI thread.

            dut:
                DUT configuration dictionary containing
                fault sequences and monitoring settings.

            devHand:
                Active serial device handler instance.

        Returns:
            None

        Raises:
            None
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
        Execute DUT monitoring loop.

        Detailed Description:
            Continuously monitors incoming serial data
            from the DUT device.

            Processing steps:

                • Check serial buffer availability
                • Read incoming line data
                • Decode UTF-8 serial stream
                • Push logs to UI queue
                • Detect configured fault sequences
                • Trigger fault stop events if matched
                • Handle serial communication failures

        Args:
            self:
                Thread instance reference.

        Returns:
            None
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
        Stop DUT monitoring thread.

        Detailed Description:
            Safely terminates thread execution
            by disabling the run flag.

            Monitoring loop exits gracefully
            on next iteration.

        Args:
            self:
                Thread instance reference.

        Returns:
            None

        Raises:
            None
        """
        self.run_flg = False

    def checkForFault(self, instr):
        """
        Detect configured DUT fault patterns.

        Detailed Description:
            Scans incoming DUT log strings against
            preconfigured fault sequence patterns
            using regular expression matching.

            If a match is found, the corresponding
            fault string is returned.

        Args:
            self:
                Thread instance reference.

            instr:
                Incoming DUT log string.

        Returns:
            str | None:

                • Matched fault string → if detected
                • None → if no fault match found

        Raises:
            re.error:
                If invalid regex pattern exists
                in configured fault list.
        """
        for fault in self.fault_list:
            if(re.search(fault, instr)):
                return fault
        return None