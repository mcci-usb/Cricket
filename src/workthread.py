##############################################################################
# 
# Module: workthread.py
#
# Description:
#     Running several threads is similar to running 
#     several different programs concurrently
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
#     V2.4.0 Wed July 14 2021 15:20:05   Seenivasan V
#       Module created
##############################################################################
# Lib imports
import wx

# Own modules
import devControl

from threading import *

from uiGlobals import *

##############################################################################
# Utilities
##############################################################################

class ResultEvent(wx.PyEvent):
    """
    A  class AboutWindow with init method
    Simple event to carry arbitrary result data.
    """
    def __init__(self, data):
        """
        Init Result Event.

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            date : result data
        Returns:
            None
        """
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

class WorkerThread(Thread):
    """
    A  class AboutWindow with init method
    Worker Thread Class. 
    """
    def __init__(self, notify_window, top, gparent):
        """
        Init Worker Thread Class.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            notify_window: windows is notified
            gparent: Pointer to a parent window.
            top: creates an object
        Returns:
            None
        """
        Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = 0
        self.top = top
        self.gparent = gparent
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def run(self):
        """
        Run Worker Thread.

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            evt: The event parameter in the AutoButton() method is an 
            object specific to a particular event type.
        Returns:
            None
        """
        # This is the code executing in the new thread. Simulation of
        # a long process (well, 10s here) as a simple loop - you will
        # need to structure your processing so that you periodically
        # peek at the abort variable
        plist = devControl.search_device(self.gparent)
        try:
            wx.PostEvent(self._notify_window, ResultEvent(plist))
        except:
            pass

    def abort(self):
        """
        abort worker thread.

        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            evt: The event parameter in the AutoButton() method is an 
            object specific to a particular event type.
        Returns:
            None
        """
        # Method for use by main thread to signal an abort
        self._want_abort = 1