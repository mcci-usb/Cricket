# -*- coding: utf-8 -*-
##############################################################################
# 
# Module: thServer.py
#
# Description:
#     Server socket module, which listens for the client
#     Based on the command from Clinet, control device which is connected
#     Send the response back to Clinet in JSON format (JSON Object)
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
# Built-in imports

import socket
import threading
import time
import wx
import json
import usbDev

keywords = {'Python',
            'wxpython',
            'SocketProgramming'
            }

class ServerEvent(wx.PyEvent):
    """
    A class ServerEvent with init method
    wxWindow is the base class for all windows and 
    represents any visible object on screen.
    """
    def __init__(self, data):
        
        """
        here the server sets the event type. 
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
            data: creates an object
        Returns:
            None
        """
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data
        

class ServerHc:
    """
    A class ServerHc with init method
    wxWindow is the base class for all windows and 
    represents any visible object on screen.
    """
    def __init__(self, host='', port: int = 5567):
        """
        here the server sets Ip address, port. 
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
            host: host ip address ipaddress 
            port : port number of that particular ipaddress.
        Returns:
            None
        """
        self.IP = ""
        self.PORT = port
        self.ADDR = ((self.IP, self.PORT))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.bind((host, port))
            self.socket.listen(5)
        except:
            print("Server Init failed")
        #print('Test Host Server Listeneing port: ' + host + ':' + str(port))
        self.bind_addr = host + ':' + str(port)
        self.conn_socket = None
        self.addr = None

    def close(self):
        """
        Close the server connection
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
        Returns:
            None
        """
        self.socket.close()
        

class StayAccept(threading.Thread):
    """
    A class StayAccept with init method
    wxWindow is the base class for all windows and 
    represents any visible object on screen.
    """
    def __init__(self, parent):
        """
        here the server is wait the connection. 
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
        Returns:
            None
        """
        super(StayAccept, self).__init__()
        self.window = parent
        self.wait = True
        self.rs = None
    
    def run(self) -> None:
        """
        here the server is running connection
        establsihed to new connection info. 
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
            data: creates an object
        Returns:
            None
        """
        while self.wait:
            try:
                self.window.hcserver.conn_socket, self.window.hcserver.addr = \
                        self.window.hcserver.socket.accept()
                new_conn_info = '\nnew connection: ' + \
                        str(self.window.hcserver.addr)
                self.rs = RequestSync(self.window)
                self.rs.start()
            except:
                pass

    def close_connection(self):
        """
        here the server connection is close.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
        Returns:
            None
        """
        self.wait = False

   
class RequestSync(threading.Thread):
    """
    A class RequestSync with init method
    wxWindow is the base class for all windows and 
    represents any visible object on screen.
    """
    def __init__(self, parent):
        """
        here the server requesting using threading.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            parent: Pointer to a parent window.
        Returns:
            None
        """
        super(RequestSync, self).__init__()
        self.window = parent
        self._running = True
    
    def terminate(self):
        """
        here the server connection is terminate.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self._running = False

    def run(self) -> None:
        """
        This message sent to client, when it gets connected with this server
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        # This message sent to client, when it gets connected with this server
        while self._running:
            try:
                creq = self.window.hcserver.conn_socket.recv(1024)
                data = json.loads(creq.decode())
            except ConnectionResetError:
                self.window.hcserver.conn_socket.close()
                disconnect_info = str(self.window.hcserver.addr) + ' socket\n'
                wx.CallAfter(self.window.panel.PrintLog,
                                        "\n P2: "+disconnect_info)
                break
            if data:
                result = self.verify_command(data)
                data= json.dumps(result)
                self.window.hcserver.conn_socket.sendall(data.encode('utf-8'))
                self.terminate()          
    
    def verify_command(self, reqdict):
        """
        this function is verified USB Tree view command "usb", and "lsusb".
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            reqdict: request the command
        Returns:
            rdict: device info
        """
           
        ctype = reqdict["ctype"]
        cmd = reqdict["cmd"]
        if(ctype == "usb"):
            if (cmd == "lsusb"):
                result = usbDev.get_usb_tree()
                rdict = {}
                rdict["data"] = list(result)
                return rdict
        else:
            rdict = {}
            rdict["data"] = "Invalid command"
            return rdict