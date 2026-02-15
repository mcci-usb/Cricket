# -*- coding: utf-8 -*-
##############################################################################
#
# Module: thServer.py
#
# Description:
#     Server socket module which listens for client connections.
#     Based on commands received from the client, controls connected
#     devices and sends responses back in JSON format.
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
#
##############################################################################

# Built-in imports
import socket
import threading
import time
import json

# Lib imports
import wx

# Own modules
import usbChange
from uiGlobals import *

##############################################################################
# Global Keywords
##############################################################################

keywords = {
    "Python",
    "wxpython",
    "SocketProgramming"
}

##############################################################################
# Server Event
##############################################################################

class ServerEvent(wx.PyEvent):
    """
    Custom wx event used to pass server data
    to the UI thread safely.

    Attributes:
        data: Event payload information.
    """

    def __init__(self, data):
        """
        Initialize server event.

        Args:
            self: Reference to current instance.
            data: Data payload for the event.

        Returns:
            None

        Raises:
            None
        """
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

##############################################################################
# Server Host Controller
##############################################################################

class ServerHc:
    """
    Host controller server socket manager.

    Handles socket creation, binding,
    listening, and connection tracking.
    """

    def __init__(self, host="", port: int = 5567):
        """
        Initialize server socket.

        Args:
            self: Reference to current instance.
            host: Host IP address.
            port: Port number.

        Returns:
            None

        Raises:
            None
        """
        self.IP = ""
        self.PORT = port
        self.ADDR = (self.IP, self.PORT)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.bind((host, port))
            self.socket.listen(5)
        except Exception:
            print("Server Init failed")

        self.bind_addr = host + ":" + str(port)
        self.conn_socket = None
        self.addr = None

    def close(self):
        """
        Close the server socket.

        Args:
            self: Reference to current instance.

        Returns:
            None

        Raises:
            None
        """
        self.socket.close()

##############################################################################
# Connection Accept Thread
##############################################################################
class StayAccept(threading.Thread):
    """
    Thread that continuously accepts
    incoming client connections.
    """

    def __init__(self, parent):
        """
        Initialize accept thread.

        Args:
            self: Reference to current instance.
            parent: Parent UI window.

        Returns:
            None

        Raises:
            None
        """
        super(StayAccept, self).__init__()
        self.window = parent
        self.wait = True
        self.rs = None

    def run(self) -> None:
        """
        Listen and accept incoming connections.

        Args:
            self: Reference to current instance.

        Returns:
            None

        Raises:
            None
        """
        while self.wait:
            try:
                (
                    self.window.hcserver.conn_socket,
                    self.window.hcserver.addr,
                ) = self.window.hcserver.socket.accept()

                new_conn_info = "\nnew connection: " + str(
                    self.window.hcserver.addr
                )

                self.rs = RequestSync(self.window)
                self.rs.start()

            except Exception:
                pass

    def close_connection(self):
        """
        Stop accepting new connections.

        Args:
            self: Reference to current instance.

        Returns:
            None

        Raises:
            None
        """
        self.wait = False

##############################################################################
# Request Sync Thread
##############################################################################

class RequestSync(threading.Thread):
    """
    Thread that processes client requests
    and sends responses.
    """
    def __init__(self, parent):
        """
        Initialize request handler thread.

        Args:
            self: Reference to current instance.
            parent: Parent UI window.

        Returns:
            None
        Raises:
            None
        """
        super(RequestSync, self).__init__()
        self.window = parent
        self._running = True

    def terminate(self):
        """
        Terminate the request thread.

        Args:
            self: Reference to current instance.

        Returns:
            None

        Raises:
            None
        """
        self._running = False

    def run(self) -> None:
        """
        Receive, process, and respond to
        client requests.

        Args:
            self: Reference to current instance.

        Returns:
            None

        Raises:
            None
        """
        while self._running:
            try:
                creq = self.window.hcserver.conn_socket.recv(1024)
                data = json.loads(creq.decode())

            except ConnectionResetError:
                self.window.hcserver.conn_socket.close()
                disconnect_info = (
                    str(self.window.hcserver.addr) + " socket\n"
                )

                wx.CallAfter(
                    self.window.panel.PrintLog,
                    "\n P2: " + disconnect_info,
                )
                break
            if data:
                result = self.verify_command(data)
                data = json.dumps(result)
                self.window.hcserver.conn_socket.sendall(
                    data.encode("utf-8")
                )
                self.terminate()

    def verify_command(self, reqdict):
        """
        Verify and process client command.

        Args:
            self: Reference to current instance.
            reqdict: Request dictionary from client.
        Returns:
            dict: Response data.
        Raises:
            None
        """
        ctype = reqdict["ctype"]
        cmd = reqdict["cmd"]
        if ctype == "usb":
            if cmd == "lsusb":
                wx.CallAfter(
                    self.window.panel.PrintLog, "Read USB"
                )

                result = usbChange.get_usb_change(self.window)

                wx.CallAfter(
                    self.window.panel.PrintLog, "USB Result "
                )
                rdict = {}
                rdict["data"] = result
                return rdict

        else:
            rdict = {}
            rdict["data"] = "Invalid command"
            return rdict
