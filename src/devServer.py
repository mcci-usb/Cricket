# -*- coding: utf-8 -*-
##############################################################################
# 
# Module: devServer.py
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
#     V2.4.0-2 Wed June 14 2021 18:50:10 seenivasan
#       Module created
##############################################################################
# Built-in imports

import socket
import threading
import time
import wx
import json
import search

from uiGlobals import *

keywords = {'Python',
            'wxpython',
            'SocketProgramming'
            }

class ServerEvent(wx.PyEvent):
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

class ServerCc:
    def __init__(self, host='', port: int = 5566):
        self.IP = ""
        self.PORT = port
        self.ADDR = ((self.IP, self.PORT))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(5)
        #print('Server Listeneing port: ' + host + ':' + str(port))
        self.bind_addr = host + ':' + str(port)
        self.conn_socket = None
        self.addr = None

    def close(self):
        self.socket.close()
        

class StayAccept(threading.Thread):
    def __init__(self, parent):
        super(StayAccept, self).__init__()
        self.window = parent
        self.wait = True
        self.rs = None
    
    def run(self) -> None:
        while self.wait:
            try:
                self.window.ccserver.conn_socket, self.window.ccserver.addr = self.window.ccserver.socket.accept()
                new_conn_info = '\nnew connection: ' + str(self.window.ccserver.addr)
                self.rs = RequestSync(self.window)
                self.rs.start()
            except:
                pass

    def close_connection(self):
        self.wait = False

   
class RequestSync(threading.Thread):
    def __init__(self, parent):
        super(RequestSync, self).__init__()
        self.window = parent
        self._running = True
    
    def terminate(self):
        self._running = False

    def run(self) -> None:
        # This message sent to client, when it gets connected with this server
        while self._running:
            try:
                #data = self.window.ccserver.conn_socket.recv(1024).decode('utf-8')
                creq = self.window.ccserver.conn_socket.recv(1024)
                data = json.loads(creq.decode())
            except ConnectionResetError:
                self.window.ccserver.conn_socket.close()
                disconnect_info = str(self.window.ccserver.addr) + ' socket\n'
                wx.CallAfter(self.window.panel.PrintLog, "\n P2: "+disconnect_info)
                break
            if data:
                result = self.verify_command(data)
                data= json.dumps(result)
                self.window.ccserver.conn_socket.sendall(data.encode('utf-8'))
                self.terminate()
    
    def verify_command(self, reqdict):
        ctype = reqdict["ctype"]
        cmd = reqdict["cmd"]
        if(ctype == "device"):
            if(cmd == "search"):
                wx.PostEvent(self.window, ServerEvent("search"))
                #result = search.search_port(self.window.usbHand)
                result = None
                while(1):
                    if self.window.usbHand.ready:
                        break
                self.window.usbHand.ready = False
                result = self.window.dev_list
                wx.CallAfter(self.window.panel.PrintLog, "\nDevice Search")
                return result
            elif(cmd == "open"):
                #print("Connect device")
                itype = reqdict["itype"]
                result = False
                if(itype == "serial"):
                    port = reqdict["port"]
                    baud = reqdict["baud"]
                    result = self.window.devHand.open_serial_device(port, int(baud))
                elif(itype == "usb"):
                    port = reqdict["port"]
                    #print("connect usb")
                    result = self.window.usbHand.select_usb_device(port)
                rdict = {}
                if result:
                    rdict["data"] = "success"
                else:  
                    rdict["data"] = "fail"
                wx.CallAfter(self.window.panel.PrintLog, "\nPort Open: "+rdict["data"]+"\n")
                return rdict
            elif(cmd == "close"):
                result = self.window.devHand.close()
                rdict = {}
                if result:
                    rdict["data"] = "success"
                else:
                    rdict["data"] = "fail"
                wx.CallAfter(self.window.panel.PrintLog, "\nPort Close: "+rdict["data"]+"\n")
                return rdict
        elif(ctype == "control"):
            itype = reqdict["itype"]
            if(itype == "serial"):
                cmd = reqdict["cmd"]
                if(cmd == "switch"):
                    result = self.window.devHand.send_port_cmd(reqdict["stat"])
                    wx.CallAfter(self.window.panel.PrintLog, reqdict["stat"])
                    rdict = {}
                    rdict["data"] = result
                    return rdict
                elif(cmd == "read"):
                    result = self.window.devHand.read_port_cmd()
                    rdict = {}
                    rdict["data"] = result
                    return rdict
                elif(cmd == "status"):
                    result = self.window.devHand.send_status_cmd()
                    rdict = {}
                    rdict["data"] = result
                    return rdict
                elif(cmd == "volts"):
                    result = self.window.devHand.send_volts_cmd()
                    rdict = {}
                    rdict["data"] = result
                    wx.CallAfter(self.window.panel.PrintLog, "\nVolts")
                    return rdict
                elif(cmd == "amps"):
                    result = self.window.devHand.send_amps_cmd()
                    rdict = {}
                    rdict["data"] = result
                    wx.CallAfter(self.window.panel.PrintLog, "\nAmps")
                    return rdict
            elif(itype == "usb"):
                cmd = reqdict["cmd"]
                result = self.window.usbHand.control_port(int(cmd))
                rdict = {}
                rdict["data"] = str(result)
                wx.CallAfter(self.window.panel.PrintLog, "\n2101 Port: "+rdict["data"]+"\n")
                return rdict
        else:
            rdict = {}
            rdict["data"] = "Invalid command"
            return rdict